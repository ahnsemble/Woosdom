---
title: "woosdom-executor MCP 확장 — Gemini Deep Research 통합"
created: 2026-02-28
status: spec-ready
---

# MCP 확장 스펙: Gemini Deep Research 통합

## 1. 배경

기존 `query_gemini` MCP 도구는 `generateContent` (동기) 방식만 지원.
Gemini Interactions API 공개로 Deep Research 에이전트를 API로 직접 호출 가능해짐.

**기존 수동 플로우 (제거 대상):**
```
Brain이 딥리서치 프롬프트 작성
→ 사용자가 Gemini 웹 UI에 복붙
→ 2~20분 대기
→ 결과를 채팅에 복붙
→ Brain 종합
```

**목표 자동화 플로우:**
```
Brain → query_gemini(use_deep_research=true) 호출
→ MCP 서버가 Interactions API 호출 + 폴링
→ 결과 자동 반환
→ Brain 종합
```

## 2. API 레퍼런스

### Interactions API 엔드포인트
```
POST https://generativelanguage.googleapis.com/v1beta/interactions
Header: x-goog-api-key: {GEMINI_API_KEY}
```

### Deep Research 에이전트 호출
```python
from google import genai
client = genai.Client(api_key=GEMINI_API_KEY)

# 시작
interaction = client.interactions.create(
    agent="deep-research-pro-preview-12-2025",
    input=prompt,
    background=True,    # 필수
    store=True           # background=True일 때 필수
)

# 폴링
while True:
    result = client.interactions.get(interaction.id)
    if result.status == "completed":
        report = result.outputs[-1].text
        break
    elif result.status in ("failed", "cancelled"):
        raise Exception(f"Deep Research failed: {result.status}")
    time.sleep(10)  # 10초 간격 폴링
```

### 스트리밍 (선택적)
```python
stream = client.interactions.create(
    agent="deep-research-pro-preview-12-2025",
    input=prompt,
    background=True,
    stream=True,
    agent_config={
        "type": "deep-research",
        "thinking_summaries": "auto"
    }
)
```

### 후속 상호작용 (previous_interaction_id)
```python
# 리서치 결과를 다른 모델로 후처리
summary = client.interactions.create(
    model="gemini-3-flash-preview",
    input="위 리서치를 3줄로 요약해줘",
    previous_interaction_id=interaction.id
)
```

## 3. 설계 옵션

### Option A: 기존 query_gemini에 파라미터 추가
```
query_gemini(
    prompt: str,
    model: str = "gemini-2.5-flash",
    use_deep_research: bool = false,  # 신규
    ...
)
```
- **장점:** 인터페이스 변경 최소
- **단점:** Deep Research는 2~20분 소요 — MCP 타임아웃 문제 가능

### Option B: 별도 도구 신설 ⭐ 추천
```
query_gemini_deep_research(
    prompt: str,
    timeout_minutes: int = 20,
    stream_thinking: bool = false
) → { status, report, sources, interaction_id }
```
- **장점:** 비동기 특성을 명확히 분리, 타임아웃 독립 관리
- **단점:** 새 도구 등록 필요

### Option C: delegate_to_engine으로 CC가 Python 스크립트 실행
```
Brain → delegate_to_engine(task="deep research 실행")
→ CC가 Python 스크립트 실행 → 결과를 from_hands.md에 저장
```
- **장점:** MCP 서버 수정 불필요
- **단점:** 기존 수동 플로우와 단계 수 비슷

### 추천: Option B

## 4. Option B 상세 설계

### 새 MCP 도구 시그니처

```json
{
    "name": "query_gemini_deep_research",
    "description": "Gemini Deep Research 에이전트를 호출해 장시간 멀티스텝 리서치 수행. 2~20분 소요.",
    "parameters": {
        "prompt": {
            "type": "string",
            "description": "리서치 질문/주제 (상세할수록 좋음)",
            "required": true
        },
        "timeout_minutes": {
            "type": "number",
            "description": "최대 대기 시간 (기본: 20, 최대: 60)",
            "default": 20
        },
        "output_format": {
            "type": "string",
            "description": "출력 형식 지시 (예: 'JSON', 'strategic briefing', 'comparison table')",
            "default": null
        }
    }
}
```

### 반환 값
```json
{
    "status": "completed | failed | timeout",
    "report": "리서치 보고서 전문",
    "interaction_id": "후속 상호작용용 ID",
    "elapsed_seconds": 342,
    "error": null
}
```

### 구현 의사코드

```python
@mcp_tool("query_gemini_deep_research")
async def query_gemini_deep_research(
    prompt: str,
    timeout_minutes: int = 20,
    output_format: str | None = None
):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # 프롬프트에 출력 형식 지시 추가
    full_prompt = prompt
    if output_format:
        full_prompt += f"\n\nFormat the output as: {output_format}"
    
    # Deep Research 시작
    interaction = client.interactions.create(
        agent="deep-research-pro-preview-12-2025",
        input=full_prompt,
        background=True,
        store=True
    )
    
    # 폴링 루프
    start = time.time()
    timeout_sec = timeout_minutes * 60
    
    while time.time() - start < timeout_sec:
        result = client.interactions.get(interaction.id)
        
        if result.status == "completed":
            return {
                "status": "completed",
                "report": result.outputs[-1].text,
                "interaction_id": interaction.id,
                "elapsed_seconds": int(time.time() - start),
                "error": None
            }
        elif result.status in ("failed", "cancelled"):
            return {
                "status": "failed",
                "report": None,
                "interaction_id": interaction.id,
                "elapsed_seconds": int(time.time() - start),
                "error": f"Agent status: {result.status}"
            }
        
        await asyncio.sleep(10)  # 10초 간격
    
    return {
        "status": "timeout",
        "report": None,
        "interaction_id": interaction.id,
        "elapsed_seconds": int(time.time() - start),
        "error": f"Timeout after {timeout_minutes} minutes"
    }
```

## 5. 의존성

**현재:** `@google/generative-ai` (구 SDK, generateContent 전용)
**필요:** `@google/genai >= 1.33.0` (신 SDK, Interactions API 지원)

> ⚠️ SDK 전환 필요. 구 SDK는 Interactions API 미지원.
> Option A: 신 SDK로 완전 교체 (breaking change 위험)
> Option B: 신 SDK 추가 설치, Deep Research 전용으로만 사용 ⭐ 추천

## 6. MCP 서버 소스 위치

```
/Users/woosung/Desktop/Dev/Projects/mcp_server/
├── src/
│   ├── index.ts          # 진입점 (도구 등록 + 라우팅)
│   ├── tools/
│   │   ├── gemini.ts     # query_gemini (구 SDK)
│   │   ├── gpt.ts        # query_gpt
│   │   ├── delegate.ts   # delegate_to_engine
│   │   ├── result.ts     # read_hands_result
│   │   └── vault_stats.ts
│   └── utils/
│       ├── config.ts
│       ├── timeout.ts
│       └── logger.ts
├── package.json          # @google/generative-ai (구 SDK)
└── .env                  # GEMINI_API_KEY
```

## 7. 환경 변수

```
GEMINI_API_KEY=your-api-key-here
```

기존 `query_gemini`에서 이미 사용 중 → 동일 키 공유 가능.

## 7. 기존 query_gemini 모델 기본값 업데이트

현재 기본값 `gemini-2.5-flash` → `gemini-3-flash-preview`로 변경 권장.
사용 가능 모델:
- `gemini-3-flash-preview` (단순, 빠름)
- `gemini-3.1-pro-preview` (복잡, 정확)
- `deep-research-pro-preview-12-2025` (딥리서치 전용, Option B로 분리)

## 8. 엔진 라우터 연동

Engine Router SKILL 업데이트 완료 (2026-02-28).
Brain이 딥리서치 필요 판단 시:
- 기존: "딥리서치 프롬프트 작성 → 사용자에게 Gemini 웹에서 실행 요청"
- 신규: `query_gemini_deep_research(prompt)` 직접 호출

### 트리거 조건 (Brain 판단 기준)
- 3자 회의에서 Gemini 측 심층 분석 필요 시
- Finance 복귀 트리거 모니터링 (시장 동향)
- Career 리서치 (AEC/FDE 시장 조사)
- 사용자가 "딥리서치 해줘" / "깊게 조사해" 요청 시

## 9. 실행 계획

### CC 태스크 (to_hands.md)
1. woosdom-executor 소스에서 `query_gemini` 구현 위치 확인
2. `google-genai >= 1.55.0` 의존성 추가
3. `query_gemini_deep_research` 도구 구현
4. `query_gemini` 모델 기본값 업데이트
5. 테스트: 간단한 리서치 쿼리로 end-to-end 확인
