---
name: engine-router
description: >
  Hands 위임, 엔진 선택, to_claude_code, to_codex, to_antigravity, CC, Codex, Antigravity, 
  3자 회의, A2A, 비용, 턴 제한, 라우팅, 서브에이전트, 
  delegate, execute, 실행, 백테스트 위임, 코드 작업 관련 시 트리거.
  Role Gate에서 Hands 판정 시 자동 로드.
---

# Engine Router & Dispatch Protocol

## 3-Engine Architecture

```
Brain (Claude Opus 4.6) — 전략/판단/승인
  ├── Hands-4: Claude Code (로컬 허브) ← 주력 실행 엔진
  ├── Hands-3: Codex (로컬 앱) ← 코드 실행·비동기 연산
  ├── Hands-1: Antigravity Sonnet/Opus (GUI 보조)
  └── Hands-2: Antigravity Gemini (웹 리서치)
```

> 단일 도구 통합은 안티패턴. 느슨한 결합 유지.
> LLM 에이전트에 수학 연산 위임 절대 금지.

## 엔진 선택 최우선 원칙

| 작업 본질 | 적합 엔진 | 이유 |
|----------|----------|------|
| 코드, git, 파일편집, 디버그 | **CC (Hands-4)** | CLI 네이티브 |
| 시각 분석, UI/UX, 타일맵/레이아웃 | **AG (Hands-1)** | 이미지를 보고 판단 가능 |
| 수학 연산, 백테스트, 대규모 데이터 | **Codex (Hands-3)** | GPT-5.3 Extra High + 비동기 |
| 웹 리서치, 멀티모달 검색 | **AG Gemini (Hands-2)** | 검색 + long context |

> ⚠️ CC 편중 금지. 작업 본질을 먼저 판단하고 적합 엔진 선택.
> ⚠️ 시각적 판단 → AG. CC는 픽셀 분석 못 함.

## 패턴 기반 라우터

| 패턴 | 주 엔진 | 보조 |
|------|--------|------|
| A — 백테스팅/대규모 연산 | Codex | CC (코드 생성) |
| B — MCP/코드 개발 | CC | Codex (대규모 빌드) |
| C — 리서치 & 자동화 | CC | AG (웹 브라우징) |
| D — Finance Brief | CC | Brain (최종 판단) |

## 월 비용 상한: $300

| 엔진 | 플랜 | 월 비용 |
|------|-----|--------|
| Claude Code | Max 5x (API 금지) | $100 |
| Codex | ChatGPT Pro | $200 |
| Antigravity | Public Preview | $0 |

## 비용 폭발 방지
- CC: `--max-turns N` 필수
- CC: API 종량제 전환 거절
- Codex: 병렬 서브에이전트 최대 3개
- AG: 동시 에이전트 최대 2개

## Dispatch Protocol — 엔진별 전용 채널

**파일 위치:** `00_System/Templates/`

| 엔진 | 지시서 (Brain→Hands) | 결과 (Hands→Brain) |
|------|---------------------|--------------------|
| CC (Hands-4) | `to_claude_code.md` | `from_claude_code.md` |
| Codex (Hands-3) | `to_codex.md` | `from_codex.md` |
| AG (Hands-1/2) | `to_antigravity.md` | `from_antigravity.md` |

> ⚠️ `to_hands.md` / `from_hands.md`는 **deprecated**. 엔진별 전용 파일 사용.
> ⚠️ MCP 저장이 채팅 응답보다 반드시 선행.
> ⚠️ 병렬 위임 가능: CC + Codex 동시 지시 시 각각의 to_ 파일에 작성.

### CC (주력) — Brain 직접 지시 또는 to_claude_code.md
```
## 💻 Claude Code 직접 실행
**작업:** [한 줄 요약]
**커맨드/지시:** [구체적 지시사항]
**완료 확인:** [기대 결과]
→ 결과: from_claude_code.md에 기록
```

### Codex — to_codex.md 수동 전달
```
## 🔧 Codex 실행 요청
**작업:** [한 줄 요약]
**추천:** Hands-3 (Codex)
**이유:** [비동기/장시간/격리 필요]
→ 결과: from_codex.md에 기록
```

### Antigravity — to_antigravity.md 수동 전달
```
## 🔧 Antigravity 실행 요청
**작업:** [한 줄 요약]
**추천:** Hands-1 또는 Hands-2
**이유:** [GUI/시각/멀티모달 필요]
→ 결과: from_antigravity.md에 기록
```

## LLM 비용 티어링

| 작업 유형 | 추천 모델 |
|-----------|-----------|
| 단순 요약/분류 | Haiku / Flash / 4o-mini |
| 일반 작업 | Sonnet / 4o / Flash |
| 복잡한 판단/코드 | Opus / GPT-5.2 / Gemini 3.1 Pro |
| 재무 교차검증 | 3모델 동시 (선택적) |

## 3자 회의 (A2A Protocol)

**파일:** `00_System/Logs/agent_activity.md`, `00_System/Templates/council_log_template.md`

**4단계:**
1. 독립 분석 (병렬) — GPT + Gemini에 동일 질문
2. 충돌 감지 — 일치→4 / 불일치→3
3. 토론 루프 (최대 2회) — 반론 교차 전달
4. Brain 최종 판정 + council_log 저장

**제한:** 1회 회의당 GPT 최대 4호출, Gemini 최대 4호출.

## 금지 사항 (Hard Rules)

| 절대 금지 | 이유 |
|----------|------|
| LLM으로 55B 조합/50K Bootstrap 실행 | 환각 → 재무 치명타 |
| 패턴 A 수식의 LLM 자율 변경 | MDD 계산 오염 |
| CC API 종량제 사용 | 무한 루프 비용 폭발 |
| 단일 도구로 전 패턴 통합 | 엔진 강점 상실 |

## Secondary Router — 상세 특성 매핑

| Task Characteristics | Engine | Reason |
|---------------------|--------|--------|
| 파일 자동 수정 + 빌드 + 테스트 루프 | **CC** | headless -p, 자가 치유 루프 |
| Brain 지시서 자동 실행 (to_hands 트리거) | **CC** | fswatch + headless CLI |
| MCP 서버 개발/디버그 | **CC** | MCP 양방향 + 로컬 파일 제어 |
| Git 워크플로 (commit/branch/merge) | **CC** | 터미널 네이티브 |
| 장시간 비동기 코드 실행 (30min+) | **Codex** | 로컬 백그라운드 |
| 대규모 수학 연산 (백테스팅) | **Codex** (코드 실행만) | 결정론적 실행면 |
| PR 자동 생성/리뷰 | **Codex** | GitHub 통합 |
| **시각 분석, UI/UX 퀄리티 판단** | **AG (Hands-1)** | **이미지 인식 + 시각적 비교 가능** |
| **타일맵/레이아웃/픽셀아트 설계** | **AG (Hands-1)** | **레퍼런스 보고 설계 → CC에 config 전달** |
| GUI 기반 웹 리서치/브라우저 탐색 | **AG (Hands-1/2)** | 브라우저 DOM 제어 |
| 멀티모델 실험/비교 | **AG Gemini (Hands-2)** | IDE 내 멀티모델 |
| 실시간 웹 검색 + 분석 | **AG Gemini (Hands-2)** | Search + long context |
| 멀티모달 입력 | **AG Gemini (Hands-2)** | Multi-modal |

## MCP 호출 시 모델 추천

- `query_gemini`: 단순 → `gemini-3-flash-preview` / 복잡 → `gemini-3.1-pro-preview`
- `query_gemini` (Deep Research): 딜리서치 → `deep-research-pro-preview-12-2025` (Interactions API)
- `query_gpt`: 단순 → `gpt-4o-mini` / 복잡 → `gpt-4o` 또는 `gpt-5.2`

## Gemini Deep Research API 통합 (2026-02-28 추가)

**개요:** Interactions API로 Gemini Deep Research 에이전트 직접 호출 가능. 기존 수동 플로우(프롬프트 작성→웹 복붙→결과 전달) 자동화.

**에이전트 스펙:**
- ID: `deep-research-pro-preview-12-2025`
- 기반: Gemini 3 Pro
- 최대 리서치 시간: 60분 (대부분 20분 이내)
- 실행: `background=True` (비동기 폴링)
- 인증: Gemini API Key

**기존 vs 신규 플로우:**
```
Before: Brain 프롬프트 작성 → 사용자 웹 복붙 → 대기 → 결과 채팅 전달 → Brain 종합
After:  Brain → query_gemini(deep_research) → 비동기 실행 → 결과 자동 수신 → Brain 종합
```

**적용 시나리오:**
- 3자 회의 Gemini 측 분석 → Deep Research로 격상 (단순 query 대비 리서치 품질 대폭 향상)
- Finance Brief Scout 에이전트 대체 가능
- 복구트리거 모니터링 (시장 동향 자동 수집)
- FDE/AEC 리서치 자동화

**통합 방식:** `query_gemini` MCP에 `use_deep_research: true` 파라미터 추가
- `false` (default): 기존 generateContent 호출
- `true`: Interactions API → Deep Research 에이전트 호출 + 폴링 루프

## fswatch 자동 트리거 파이프라인

```
Brain → to_claude_code.md 작성 (Obsidian MCP)
  → fswatch 감지 (to_claude_code.md 모니터링)
    → claude -p --allowedTools "Read,Edit,Bash" --max-turns 15
      → from_claude_code.md + 결과 파일 저장
        → Brain이 MCP로 결과 읽기
```

> Codex/AG는 fswatch 대상 아님. 수동 전달 유지.

## 각 엔진별 적합 작업 목록

**CC (Hands-4):** 파일 편집+빌드+테스트 자가 치유, MCP 서버, Git, to_claude_code 자동 실행, Scout+Quant 병렬 스웜, Obsidian vault I/O

**Codex (Hands-3):** 장시간 백그라운드 코드 실행 (30min+), 백테스팅 Python 스크립트 실행 (코드만, 로직 변경 금지), PR 자동 생성/리뷰, 대규모 빌드/테스트 매트릭스

**AG (Hands-1/2):** 웹 리서치/브라우징 (시각적 검증), 멀티모델 실험/비교, 시각적 아키텍처 검증, 멀티모달 입력 처리

## 에이전트 활동 기록 규칙

- Hands 위임 시 → `agent_activity.md`에 태스크 추가 (태그: 🟢 Active)
- from_[engine] 수신 시 → ✅ Done으로 이동 (from_claude_code / from_codex / from_antigravity)
- 3자 회의 시 → GPT + Gemini 행 추가
- 일상 질의 → 기록 불필요

## Tool DD (Due Diligence)
새 도구 통합 전 반드시: Can Do / Cannot Do / Workarounds 조사.
