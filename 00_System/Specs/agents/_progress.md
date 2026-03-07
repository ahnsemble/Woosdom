# Agent Specs v2.0 Upgrade Progress

## 현재 상태: ✅ 40/40 완료
## 완료일: 2026-03-06 (eng-refactorer 추가)

### ✅ P1 — Command + Finance (10)
| # | ID | 부서 | 상태 |
|---|-----|------|------|
| 1 | cmd-orchestrator | Command | ✅ v2.0 |
| 2 | cmd-memory-keeper | Command | ✅ v2.0 |
| 3 | cmd-dispatcher | Command | ✅ v2.0 |
| 4 | cmd-auditor | Command | ✅ v2.0 |
| 5 | fin-portfolio-analyst | Finance | ✅ v2.0 |
| 6 | fin-quant | Finance | ✅ v2.0 |
| 7 | fin-backtester | Finance | ✅ v2.0 |
| 8 | fin-market-scout | Finance | ✅ v2.0 |
| 9 | fin-fire-planner | Finance | ✅ v2.0 |
| 10 | fin-tax-optimizer | Finance | ✅ v2.0 |

### ✅ P2 — Engineering + Research (11)
| # | ID | 부서 | 상태 |
|---|-----|------|------|
| 11 | eng-foreman | Engineering | ✅ v2.0 |
| 12 | eng-engineer | Engineering | ✅ v2.0 |
| 13 | eng-critic | Engineering | ✅ v2.0 |
| 14 | eng-gitops | Engineering | ✅ v2.0 |
| 15 | eng-vault-keeper | Engineering | ✅ v2.0 |
| 16 | eng-debugger | Engineering | ✅ v2.0 |
| 16.5 | eng-refactorer | Engineering | ✅ v2.0 (NEW 2026-03-06, Codex) |
| 17 | res-scout-lead | Research | ✅ v2.0 |
| 18 | res-web-scout | Research | ✅ v2.0 |
| 19 | res-architect | Research | ✅ v2.0 |
| 20 | res-experimenter | Research | ✅ v2.0 |
| 21 | res-deep-researcher | Research | ✅ v2.0 |

### ✅ P3 — Compute + Operations (8)
| # | ID | 부서 | 상태 |
|---|-----|------|------|
| 22 | cmp-compute-lead | Compute | ✅ v2.0 |
| 23 | cmp-sandbox-runner | Compute | ✅ v2.0 |
| 24 | cmp-data-wrangler | Compute | ✅ v2.0 |
| 25 | cmp-parallel-coordinator | Compute | ✅ v2.0 |
| 26 | ops-scheduler | Operations | ✅ v2.0 |
| 27 | ops-infra-manager | Operations | ✅ v2.0 |
| 28 | ops-backup-guard | Operations | ✅ v2.0 |
| 29 | ops-health-monitor | Operations | ✅ v2.0 |

### ✅ P4 — Creative + Life + Career (10)
| # | ID | 부서 | 상태 |
|---|-----|------|------|
| 30 | cre-writer | Creative | ✅ v2.0 |
| 31 | cre-designer | Creative | ✅ v2.0 |
| 32 | cre-content-strategist | Creative | ✅ v2.0 |
| 33 | cre-prompt-engineer | Creative | ✅ v2.0 |
| 34 | life-integrator | Life | ✅ v2.0 |
| 35 | life-health-coach | Life | ✅ v2.0 |
| 36 | life-relationship-advisor | Life | ✅ v2.0 |
| 37 | car-strategist | Career | ✅ v2.0 |
| 38 | car-skill-tracker | Career | ✅ v2.0 |
| 39 | car-network-builder | Career | ✅ v2.0 |

## 엔진 재배치 (2026-03-06)
- eng-critic: CC → **Codex** (PR 리뷰 특화)
- eng-refactorer: **Codex** (신규 — 리팩토링 전용)
- res-experimenter: CC → **Codex** (PoC/벤치마크 샌드박스)
- eng-gitops: CC 유지 + PR 부분만 Codex 하이브리드

## +3 Enhancement Principle (적용됨)
1. **Identity**: 엣지케이스 행동 패턴 2-3개
2. **Expertise**: 도메인별 판단 기준/임계값
3. **Thinking**: 분기 조건 + STOP 트리거

## 저장 위치: /00_System/Specs/agents/
## 베이스 템플릿: /00_System/Specs/agents/_base/
## 총 파일: 40 스펙 + 9 베이스 + 1 프로그레스 = 50 파일