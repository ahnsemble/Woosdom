# 실행 지시서: Engine Watch — 우즈덤 엔진 모니터링 & 교체 평가 CLI

*작성: Brain (Claude Opus 4.6) — 2026-02-18*
*대상 엔진: Codex 5.3*
*프로젝트: `/02_Projects/engine_watch/`*

---

## 목표

Anthropic, Google, OpenAI가 새 모델을 발표할 때 **자동 감지 → 스펙 수집 → 현행 엔진과 비교 평가 → Obsidian에 리포트 저장**하는 Python CLI 도구를 만든다.

**핵심 원칙:**
- 감지와 평가는 자동, **교체 결정은 반드시 사람(사용자)이 한다.**
- 우즈덤 시스템의 "자기 진화 루프" — 시스템이 자기 구성요소를 스스로 모니터링한다.
- 최소 교체 주기: **분기 1회.** 매번 갈아타면 프롬프트 호환성 깨짐.

---

## 현행 엔진 구성 (비교 기준선)

이 정보는 `engine_registry.yaml`로 관리된다. CLI가 참조하는 Ground Truth.

```yaml
# engine_registry.yaml
version: "2026-02-18"
system_name: "Woosdom FDE Unified System"

engines:
  brain_primary:
    name: "Claude Opus 4.6"
    provider: anthropic
    model_id: "claude-opus-4-6"
    role: "Brain (전략 두뇌)"
    context_window: 200000
    strengths: ["deep reasoning", "recursive self-correction", "MCP native"]
    
  brain_sub1:
    name: "GPT-5.2 Thinking"
    provider: openai
    model_id: "gpt-5.2-thinking"
    role: "Sub-Brain 1 (장애 복구)"
    context_window: 400000
    strengths: ["structured reasoning", "expert judgment"]
    
  brain_sub2:
    name: "Gemini 3 Pro"
    provider: google
    model_id: "gemini-3-pro-preview"
    role: "Sub-Brain 2 (장애 복구) + Hands-2"
    context_window: 1000000
    strengths: ["long context", "multimodal", "web search"]

  hands_1:
    name: "Antigravity (Sonnet 4.5 / Opus 4.6)"
    provider: anthropic
    model_id: "claude-sonnet-4-5-20250929"
    role: "Hands-1 (로컬 실행)"
    strengths: ["code execution", "backtesting", "local project"]

  hands_2:
    name: "Antigravity (Gemini 3 Pro)"
    provider: google
    model_id: "gemini-3-pro-preview"
    role: "Hands-2 (웹/멀티모달)"
    strengths: ["web search", "multimodal", "long context"]

  hands_3:
    name: "Codex 5.3"
    provider: openai
    model_id: "codex-5.3"
    role: "Hands-3 (비동기 코드)"
    strengths: ["async code gen", "standalone utilities"]

providers:
  anthropic:
    blog_url: "https://www.anthropic.com/news"
    api_changelog: "https://docs.anthropic.com/en/docs/about-claude/models"
    rss: null  # Anthropic은 RSS 미제공 — HTML 스크래핑 필요
  google:
    blog_url: "https://blog.google/technology/ai/"
    api_changelog: "https://ai.google.dev/gemini-api/docs/models"
    rss: "https://blog.google/technology/ai/rss/"
  openai:
    blog_url: "https://openai.com/blog"
    api_changelog: "https://platform.openai.com/docs/models"
    rss: null  # OpenAI도 RSS 비공식 — HTML 스크래핑 필요
```

---

## 아키텍처

```
engine-watch/
├── engine_watch/
│   ├── __init__.py
│   ├── cli.py              # CLI 진입점 (argparse)
│   ├── scanner.py           # Stage 1: 블로그/changelog 스크래핑 + 새 모델 감지
│   ├── collector.py         # Stage 2: 감지된 모델의 스펙 수집
│   ├── evaluator.py         # Stage 3: 현행 엔진 대비 비교 평가 (LLM 호출)
│   ├── reporter.py          # Stage 4: Obsidian 마크다운 리포트 생성
│   ├── notifier.py          # 알림 (텔레그램 / stdout)
│   ├── registry.py          # engine_registry.yaml 로드/관리
│   └── config.py            # 설정 관리
├── engine_registry.yaml     # 현행 엔진 정의 (Ground Truth)
├── config.yaml              # 사용자 설정
├── tests/
│   └── test_scanner.py
├── requirements.txt
├── setup.py                 # pip install -e . 로 CLI 등록
└── README.md
```

---

## CLI 인터페이스

```bash
# 전체 파이프라인 실행 (scan → collect → evaluate → report)
engine-watch run

# 스캔만 (새 모델 있는지 확인)
engine-watch scan
# 출력 예: "🆕 Anthropic: claude-opus-5 detected (2026-03-15)"

# 특정 모델 수동 평가
engine-watch evaluate --model "claude-opus-5" --provider anthropic

# 현행 엔진 목록 확인
engine-watch status

# 레지스트리 업데이트 (교체 승인 후 사용자가 실행)
engine-watch update-registry --slot brain_primary --model "claude-opus-5"

# 드라이런 (리포트 생성하되 저장 안 함)
engine-watch run --dry-run

# 과거 리포트 조회
engine-watch history
```

**설치:**
```bash
cd engine-watch
pip install -e .
```

설치 후 `engine-watch` 명령어가 전역 사용 가능해야 함.

---

## Stage별 상세

### Stage 1: Scanner (감지)

**목적:** 3사 블로그/API docs에서 새 모델 발표를 감지한다.

**방법:**
1. 각 provider의 블로그 URL과 API changelog URL을 HTTP GET
2. HTML 파싱 (BeautifulSoup) → 최근 게시글 제목 + 날짜 + URL 추출
3. 모델명 패턴 매칭:
   - Anthropic: `claude-{tier}-{version}`, `Claude {Tier} {Version}`
   - Google: `gemini-{version}-{tier}`, `Gemini {Version} {Tier}`
   - OpenAI: `gpt-{version}`, `GPT-{Version}`, `o{N}`, `codex-{version}`
4. `scan_history.json`에 이미 감지한 모델 기록 → 중복 알림 방지
5. 새 모델 발견 시 → `detected_models/` 폴더에 JSON 저장

**출력 (detected model JSON):**
```json
{
  "model_id": "claude-opus-5",
  "provider": "anthropic",
  "detected_date": "2026-03-15",
  "source_url": "https://www.anthropic.com/news/claude-opus-5",
  "source_title": "Introducing Claude Opus 5",
  "raw_snippet": "블로그 첫 2문단 텍스트 (스펙 추출용)"
}
```

**주의사항:**
- User-Agent 헤더 적절히 설정 (봇 차단 방지)
- Rate limit: 각 사이트 최소 2초 간격
- 파싱 실패 시 graceful fallback (에러 로그 + 다음 provider로)
- RSS가 있는 경우(Google) RSS 우선, 없으면 HTML 스크래핑

### Stage 2: Collector (스펙 수집)

**목적:** 감지된 모델의 상세 스펙을 수집한다.

**방법:**
1. 감지된 모델의 source_url을 fetch → 전체 블로그 본문 파싱
2. API docs 페이지도 fetch → 모델 스펙 테이블 파싱 시도
3. 위 텍스트를 LLM에 전달 → 구조화된 스펙 추출

**LLM 호출 프롬프트 (스펙 추출):**
```
아래 텍스트는 새로 발표된 AI 모델에 대한 블로그 글과 API 문서입니다.
다음 정보를 JSON으로 추출하세요. 확인 불가한 항목은 null로 두세요.

{
  "model_id": "공식 API 모델 ID (예: claude-opus-5)",
  "display_name": "표시 이름 (예: Claude Opus 5)",
  "provider": "anthropic / google / openai",
  "release_date": "YYYY-MM-DD",
  "context_window": 숫자 (토큰),
  "max_output_tokens": 숫자 또는 null,
  "pricing": {
    "input_per_1m": 달러,
    "output_per_1m": 달러
  },
  "benchmarks": {
    "GPQA_Diamond": 숫자 또는 null,
    "MATH_500": 숫자 또는 null,
    "HumanEval": 숫자 또는 null,
    "SWE_bench_verified": 숫자 또는 null,
    "MMLU_Pro": 숫자 또는 null,
    "MGSM": 숫자 또는 null,
    "other": {"벤치마크명": 숫자}
  },
  "key_features": ["feature1", "feature2"],
  "api_status": "available / preview / waitlist / unknown",
  "multimodal": ["text", "image", "audio", "video"],
  "tool_use": true/false/null,
  "summary": "2줄 한국어 요약"
}
```

**출력:** `collected_specs/` 폴더에 JSON 저장.

### Stage 3: Evaluator (비교 평가)

**목적:** 수집된 스펙을 현행 engine_registry.yaml과 비교, 교체 적합성을 평가한다.

**평가 매트릭스:**

| 기준 | 가중치 (Brain) | 가중치 (Hands) | 측정 방법 |
|------|---------------|---------------|----------|
| 추론 깊이 | 30% | 5% | GPQA, MATH 벤치마크 |
| 코딩 능력 | 10% | 30% | SWE-bench, HumanEval |
| 컨텍스트 윈도우 | 15% | 15% | 공식 스펙 |
| 가격 효율 | 10% | 25% | $/1M token |
| 멀티모달 | 5% | 15% | 지원 모달리티 수 |
| 도구 사용 | 15% | 10% | tool_use 지원 여부 |
| API 안정성 | 15% | 0% | available > preview > waitlist |

**비교 로직:**
1. 새 모델이 대체할 수 있는 슬롯을 판별 (Brain / Hands-1 / Hands-2 / Hands-3 / Sub-Brain)
2. 해당 슬롯의 현행 엔진과 가중 점수 비교
3. LLM에게 최종 판정 요청 (아래 프롬프트)

**LLM 호출 프롬프트 (평가):**
```
당신은 AI 시스템 아키텍트입니다. "우즈덤"이라는 멀티 엔진 시스템의 엔진 교체 여부를 판단합니다.

## 현행 엔진
{현행 엔진 스펙 JSON}

## 신규 후보
{새 모델 스펙 JSON}

## 대상 슬롯: {slot_name} ({slot_role})

## 평가 기준 (가중치)
{위 매트릭스}

아래 JSON으로 응답하세요:
{
  "slot": "brain_primary / hands_1 / hands_2 / hands_3 / brain_sub1 / brain_sub2",
  "current_engine": "현행 모델명",
  "candidate": "신규 모델명",
  "weighted_score_current": 0-100,
  "weighted_score_candidate": 0-100,
  "verdict": "UPGRADE_RECOMMENDED / MONITOR / NO_CHANGE",
  "confidence": "high / medium / low",
  "reasoning": "3줄 이내 한국어 판단 근거",
  "risks": ["교체 시 리스크 1", "리스크 2"],
  "migration_notes": "교체 시 필요한 작업 (프롬프트 수정 등)"
}

판정 기준:
- UPGRADE_RECOMMENDED: 후보 점수가 현행 대비 15%+ 우위 AND api_status=available
- MONITOR: 후보 점수가 5-15% 우위 OR api_status=preview
- NO_CHANGE: 후보 점수가 5% 미만 우위 OR 하위
```

### Stage 4: Reporter (리포트 생성)

**목적:** 평가 결과를 Obsidian 마크다운으로 저장한다.

**저장 경로:** 사용자가 config.yaml에서 지정한 Obsidian 볼트 경로.
기본값: `{vault_path}/00_System/engine_watch/reports/`

**리포트 파일명:** `{date}_{provider}_{model_id}.md`

**리포트 템플릿:**
```markdown
# Engine Watch Report: {display_name}

*감지일: {detected_date} | 평가일: {evaluated_date}*
*출처: [{source_title}]({source_url})*

## 모델 스펙

| 항목 | 값 |
|------|-----|
| Provider | {provider} |
| Model ID | {model_id} |
| Context Window | {context_window} |
| Pricing | ${input}/1M in, ${output}/1M out |
| API Status | {api_status} |
| Multimodal | {multimodal} |

## 벤치마크

| 벤치마크 | 신규 모델 | 현행 ({current_engine}) | 차이 |
|----------|----------|----------------------|------|
| GPQA Diamond | {new} | {current} | {diff} |
| ... | ... | ... | ... |

## 교체 평가

| 슬롯 | 현행 | 판정 | 신뢰도 | 점수 (현행→후보) |
|------|------|------|--------|-----------------|
| {slot} | {current} | {verdict} | {confidence} | {score_current}→{score_candidate} |

### 판단 근거
{reasoning}

### 교체 리스크
{risks as bullet list}

### 마이그레이션 노트
{migration_notes}

---
*Generated by Engine Watch v1.0 — Woosdom FDE System*
*Tags: #engine_watch #{provider} #{verdict}*
```

### Notifier (알림)

**구현:**
- **기본:** stdout 출력 (cron 로그로 충분할 수 있음)
- **옵션 1:** 텔레그램 봇 (TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID 환경변수)
- **옵션 2:** macOS 네이티브 알림 (`osascript` 또는 `terminal-notifier`)

**알림 트리거:**
- 새 모델 감지 시 → "🆕 {provider}: {model_id} 감지됨"
- UPGRADE_RECOMMENDED 판정 시 → "⚡ {model_id} → {slot} 교체 권고. 리포트: {path}"
- 스캔 실패 시 → "⚠️ {provider} 스캔 실패: {error}"

---

## 설정 파일

```yaml
# config.yaml
obsidian_vault_path: "/Users/woosung/Desktop/Dev/Woosdom_Brain"
report_dir: "00_System/engine_watch/reports"

# LLM 설정 (스펙 추출 + 평가용)
llm:
  provider: "anthropic"  # anthropic / google / openai
  model: "claude-sonnet-4-5-20250929"  # 평가엔 Sonnet이면 충분
  # API 키는 환경변수에서: ANTHROPIC_API_KEY / GOOGLE_API_KEY / OPENAI_API_KEY

# 알림
notification:
  telegram:
    enabled: false
    bot_token_env: "TELEGRAM_BOT_TOKEN"
    chat_id_env: "TELEGRAM_CHAT_ID"
  macos_native: true

# 스캔 주기 (cron 참고용, 실제 스케줄은 crontab에서)
scan_interval_hours: 168  # 주 1회 권장

# 교체 보호
min_upgrade_interval_days: 90  # 분기 1회 최소 간격
```

---

## 스케줄링

`crontab -e`로 등록:

```cron
# 매주 월요일 오전 9시에 Engine Watch 실행
0 9 * * 1 /path/to/venv/bin/engine-watch run >> /path/to/logs/engine_watch.log 2>&1
```

또는 launchd plist로 macOS 데몬 등록 (선택).

---

## 기술 요구사항

1. **Python 3.10+**
2. **의존성:**
   - `requests` — HTTP
   - `beautifulsoup4` — HTML 파싱
   - `feedparser` — RSS 파싱
   - `pyyaml` — YAML 설정
   - `anthropic` / `google-genai` / `openai` — LLM API
   - `rich` — CLI 출력 포맷팅
   - `click` — CLI 프레임워크 (argparse 대신, 더 깔끔)
3. **테스트:** pytest + 주요 파서에 대한 유닛 테스트
4. **에러 핸들링:** 각 provider 스캔은 독립적 — 하나 실패해도 나머지 진행

---

## 확장 가능성 (v2 이후)

이 버전(v1)에서는 **구현하지 않는다.** 리포트에 메모만 남긴다.

1. **자체 테스트 프롬프트 벤치마크** — 우즈덤 전용 평가 프롬프트 세트(예: Phase 20 지시서)를 후보 모델에 실제로 돌려보고 품질 비교. 공식 벤치마크보다 실전 정확도 높음.
2. **Antigravity 엔진 자동 추가** — 새 모델이 Antigravity에서 사용 가능해지면 엔진 목록 자동 업데이트.
3. **가격 변동 모니터링** — 기존 모델의 가격 인하/인상도 추적.
4. **brain_directive.md 자동 패치 제안** — 교체 승인 시 directive의 엔진 테이블 diff를 자동 생성.

---

## 완료 기준

1. `engine-watch scan` 실행 시 3사 블로그에서 최근 모델 발표를 감지할 수 있다
2. `engine-watch run` 실행 시 감지 → 수집 → 평가 → 리포트 전체 파이프라인이 작동한다
3. 리포트가 Obsidian 볼트의 지정 경로에 마크다운으로 저장된다
4. `engine-watch status` 로 현행 엔진 목록을 확인할 수 있다
5. 중복 감지 방지가 작동한다 (같은 모델 두 번 리포트 안 함)
6. LLM provider를 config로 전환할 수 있다
7. --dry-run 모드가 작동한다

---

## Brain 후속 작업

1. Codex가 생성한 코드 검토 → 로컬 테스트
2. engine_registry.yaml 초기값 검증
3. 첫 `engine-watch scan` 실행하여 현재 시점 기준선 설정
4. crontab 등록
5. active_context.md에 Engine Watch 운영 시작 기록
6. UPGRADE_RECOMMENDED 리포트 수신 시 → 3자 회의에서 교체 판단
