# Engine Agent Cards
*updated: 2026-03-07 | FDE Unified System v3.2 — Count Corrected*

Brain이 작업 위임 시 이 파일을 참조하여 최적 엔진 자동 선택.
workflow_engine.py가 에이전트 스펙의 `primary_engine`을 읽어 자동 분기.

---

## 엔진별 에이전트 배치 총괄 (40개)

| 엔진 | 에이전트 수 | 역할 |
|------|-----------|------|
| **CC (Hands-4)** | 11개 | 코드 실행, 파일 R/W, git, bash, MCP, 볼트 조작 |
| **AG (Hands-1/2)** | 18개 | 웹 검색, 멀티모달, 어드바이저리, 시각 검증 |
| **Codex (Hands-3)** | 10개 | 중량 연산, 백테스트, 샌드박스 실행, PR 리뷰, 리팩토링 |
| **하이브리드** | 1개 | 작업 유형별 CC/Codex 분기 |

---

## ⚡ Claude Code (CC) — 11개

로컬 파일 R/W, 코드 실행, git, bash, MCP 허브. headless 자동 실행 가능.

```yaml
name: claude_code
type: CLI_local_orchestrator
model: claude-sonnet-4-6 (headless)
endpoint: "claude -p '...' --max-turns 30"
cost_tier: per-token (--max-turns 필수)
```

| 부서 | 에이전트 | 이유 |
|------|---------|------|
| Command | cmd-dispatcher | to_/from_ 파일 작성, 엔진 라우팅 |
| Command | cmd-memory-keeper | conversation_memory 관리, 볼트 R/W |
| Engineering | eng-foreman | 설계 감독, 작업 분배, 파일 구조 확인 |
| Engineering | eng-engineer | 코드 작성/수정, 테스트 실행, 빌드 |
| Engineering | eng-debugger | 로컬 환경 디버깅, 에러 재현, 로그 분석 |
| Engineering | eng-vault-keeper | Vault 파일 관리, 디렉토리 정리 |
| Operations | ops-scheduler | cron/스케줄 관리, bash 스크립트 |
| Operations | ops-infra-manager | 인프라 설정, 서버 관리 |
| Operations | ops-backup-guard | 파일 백업, 체크섬 검증 |
| Operations | ops-health-monitor | 시스템 헬스 체크, 프로세스 모니터링 |
| Career | car-skill-tracker | 스킬 매트릭스 관리, 파일 R/W |

---

## 🌐 Antigravity (AG) — 18개

GUI 앱. 웹 브라우징, 멀티모델(Claude/GPT/Gemini 페르소나), 멀티모달, 웹 검색.
수동 실행 또는 CC의 query_gemini MCP 대체 실행(트랙 A/B).

```yaml
name: antigravity
type: GUI_agent_manager
models:
  sonnet: claude-sonnet-4-6
  opus: claude-opus-4-6
  gemini: gemini-3.1-pro-preview
cost_tier: free (Public Preview)
```

### AG-Gemini (웹 검색/멀티모달) — 5개

| 부서 | 에이전트 | model | 이유 |
|------|---------|-------|------|
| Research | res-web-scout | gemini-3.1-pro | OSINT, 웹 크롤링, SEO 필터링 |
| Research | res-scout-lead | gemini-3.1-pro | 리서치 총괄, 웹 소스 품질 평가 |
| Research | res-deep-researcher | gemini-3.1-pro (Deep Research) | 심층 리서치, 논문 기반 분석 |
| Research | res-architect | gemini-3.1-pro | 기술 평가 + 웹 리서치 기반 비교 |
| Finance | fin-market-scout | gemini-3.1-pro | 실시간 시세, 매크로 지표, 뉴스 수집 |

> **실행 방식**: agent_runner가 `to_antigravity.md`에 에이전트 스펙 + 태스크를 작성 → 사용자가 AG에서 수동 실행 → 결과를 `from_antigravity.md`에 기록.
> ⚠️ res-architect는 기술 평가 시 코드 구조 분석도 필요하면 CC fallback 가능 (하이브리드 운용).

### AG-Sonnet/Opus (어드바이저리/분석) — 13개

| 부서 | 에이전트 | model | 이유 |
|------|---------|-------|------|
| Command | cmd-orchestrator | opus-4.6 | 복합 작업 분해·DAG·의존성 분석 |
| Command | cmd-auditor | opus-4.6 | 시스템 감사·이상 탐지 |
| Finance | fin-portfolio-analyst | opus-4.6 | 포트폴리오 전략 분석 (심층 추론) |
| Finance | fin-tax-optimizer | opus-4.6 | 세금 전략, 절세 분석 |
| Creative | cre-writer | sonnet-4.6 | 창작, 글쓰기 |
| Creative | cre-designer | sonnet-4.6 | 디자인 + 시각 검증 |
| Creative | cre-content-strategist | sonnet-4.6 | 콘텐츠 전략 |
| Creative | cre-prompt-engineer | sonnet-4.6 | 프롬프트 설계·최적화 |
| Life | life-integrator | sonnet-4.6 | 라이프 통합 어드바이저 |
| Life | life-health-coach | sonnet-4.6 | 건강/운동 코칭 |
| Life | life-relationship-advisor | sonnet-4.6 | 관계 어드바이저 |
| Career | car-strategist | sonnet-4.6 | 커리어 전략 |
| Career | car-network-builder | sonnet-4.6 | 네트워킹 전략 |

> cmd-orchestrator, cmd-auditor, fin-portfolio-analyst, fin-tax-optimizer만 Opus (심층 추론 필요). 나머지는 Sonnet으로 충분.
> 이 13개 에이전트는 평소 Brain이 판단 시 참조하는 Thinking Framework 제공자이며, AG 오케스트레이션 시에만 Claude/GPT/Gemini 페르소나로 실제 실행된다.

---

## 🧮 Codex (Hands-3) — 10개

비동기 수치 연산, 샌드박스 Python/Node, 백테스트, PR 리뷰, 리팩토링.
GPT-5.3 Extra High 모델. 장시간 격리 실행에 최적.

```yaml
name: codex
type: CLI_local_compute
model: GPT-5.3 Extra High
endpoint: "/opt/homebrew/bin/codex exec --skip-git-repo-check '...'"
cost_tier: flat ($200/mo ChatGPT Pro)
```

| 부서 | 에이전트 | 이유 |
|------|---------|------|
| Compute | cmp-compute-lead | 연산 총괄, 리소스 배분, 결과 검증 |
| Compute | cmp-sandbox-runner | 샌드박스 Python/Node 실행 |
| Compute | cmp-data-wrangler | 데이터 전처리, 클리닝, 포맷 변환 |
| Compute | cmp-parallel-coordinator | 병렬 연산 관리 |
| Finance | fin-quant | 팩터 계산, 수학 모델링, 시그널 생성 |
| Finance | fin-backtester | 백테스트 실행 (장시간 비동기) |
| Finance | fin-fire-planner | FIRE 시뮬레이션 (Monte Carlo 위임) |
| Engineering | eng-critic | PR/코드 리뷰 (읽기 전용, Codex PR 리뷰 네이티브) |
| Engineering | eng-refactorer | 리팩토링 전용 (코드 스멜 진단 + 구조 변경 + 테스트 검증) |
| Research | res-experimenter | PoC/벤치마크 (샌드박스 격리 실행) |

> eng-critic: 코드를 수정하지 않고 읽기만 함(Hard Rule). Codex의 PR 리뷰 기능과 자연스러운 매칭.
> eng-refactorer: 장시간 코드 분석 + 반복 테스트 실행. CC 턴 소모 방지.
> res-experimenter: 스펙에 이미 `fallback_engine: codex` 지정. 프로덕션 격리 필수.

---

## 🔀 하이브리드 — 1개

| 에이전트 | CC 담당 | Codex 담당 | 분기 기준 |
|---------|---------|-----------|---------|
| eng-gitops | 로컬 git (commit/branch/merge/revert) | PR 자동 생성/리뷰 (GitHub 연동) | 작업 유형: `git_local` → CC, `pr_*` → Codex |

> workflow_engine.py가 메시지의 action 필드를 읽어 자동 분기.

---

## 📋 엔진 선택 빠른 참조

| 상황 | 선택 |
|------|------|
| 분석/요약/일반 추론 | AG (sonnet) |
| 심층 설계/복잡 추론 | AG (opus) |
| 웹 리서치/최신 정보 | AG (gemini) |
| 코드 작성/파일 편집/git/디버그 | CC |
| 수치 계산/백테스트/시뮬레이션 | Codex |
| PR 리뷰/코드 리뷰 | Codex |
| 리팩토링/코드 구조 개선 | Codex |
| PoC/벤치마크/실험 | Codex |
| 어드바이저리/코칭 | AG (sonnet) |
| 병렬 처리 | CC + Codex 동시 |

---

## 💰 월 비용 상한: $300

| 엔진 | 플랜 | 월 비용 |
|------|-----|--------|
| CC (Claude Code) | Max 5x (API 금지) | $100 |
| Codex | ChatGPT Pro | $200 |
| AG | Public Preview | $0 |

---

## 🔄 멀티엔진 디스패치 프로토콜

### 실행 모드 (2026-03-07 확정)

| 엔진 | 실행 주체 | agent_runner 역할 |
|---|---|---|
| **CC** | agent_runner 자동 | `claude -p` 직접 실행 |
| **Codex** | 사용자 수동 | `to_codex.md`에 준비만 → 사용자가 Codex에서 실행 |
| **AG** | 사용자 수동 | `to_antigravity.md`에 준비만 → 사용자가 AG에서 실행 |

> CC만 headless 자동. Codex/AG는 사용자가 확인하며 실행 → 품질 관리 + 비용 통제.
> Codex/AG 태스크는 to_ 파일에 에이전트 스펙 + 태스크 본문이 함께 작성됨.
> 사용자가 실행 후 결과를 from_codex.md / from_antigravity.md에 기록.

### 미지정 에이전트 fallback
`primary_engine` 미지정 → 기본값 `claude_code` (기존 동작 보존)

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|---------|
| 2026-03-07 | v3.2 | 카운트 정정: CC 16→11, AG-Gemini 5(헤더)→5(정확), AG-Sonnet/Opus 8(헤더)→13(정확), AG합계 13→18. cmd-orchestrator·cmd-auditor를 CC→AG로 이동. car-skill-tracker CC에 추가. fin-fire-planner Codex에 추가. |
| 2026-03-06 | v3.1 | 멀티엔진 디스패치, eng-refactorer(#40) 추가 |
| 2026-03-05 | v3.0 | 초기 생성 |
