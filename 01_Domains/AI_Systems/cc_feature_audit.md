# Claude Code Feature Audit
*Date: 2026-02-24*
*Version: 2.1.50*

## 현재 사용 가능한 주요 기능
| # | 기능 | 설명 | 우즈덤 활용 가능성 |
|---|------|------|-------------------|
| 1 | `-p / --print` | 비대화형(headless) 실행. 파이프/스크립트 연동 | ✅ 활용 중 (woosdom_bridge.sh) |
| 2 | `--output-format json/stream-json` | JSON/스트리밍 JSON 출력 | ✅ 활용 중 (bridge 데몬) |
| 3 | `--max-turns` | 에이전트 턴 수 제한 | ✅ 활용 중 (15턴 제한) |
| 4 | MCP 서버 관리 (`claude mcp`) | add/remove/list/get/serve | ✅ 활용 중 (obsidian-vault, codex-server) |
| 5 | `claude mcp serve` | CC 자체를 MCP 서버로 노출 | 🟡 미활용. 다른 에이전트가 CC를 도구로 호출 가능 |
| 6 | `--worktree / -w` | 세션별 git worktree 자동 생성 | 🟡 미활용. 격리된 실험 브랜치 자동화에 유용 |
| 7 | `--agents / --agent` | 커스텀 에이전트 정의 및 실행 | 🔴 미활용. Brain/Hands 역할별 에이전트 프리셋 가능 |
| 8 | `--system-prompt / --append-system-prompt` | 세션별 시스템 프롬프트 | 🟡 미활용. 패턴별 전용 프롬프트 주입 가능 |
| 9 | `--allowedTools / --disallowedTools` | 도구 화이트/블랙리스트 | 🟡 부분 활용. 패턴별 도구 제한에 유용 |
| 10 | `--model` | 세션별 모델 선택 | 🟡 미활용. 비용 최적화에 haiku/sonnet 선택적 사용 |
| 11 | `--effort` | 추론 노력 수준 (low/medium/high) | 🟡 미활용. 단순 작업은 low로 비용 절감 가능 |
| 12 | `-c / --continue` | 최근 대화 이어서 진행 | 🟡 미활용. 멀티턴 bridge 세션에 활용 가능 |
| 13 | `-r / --resume` | 세션 ID로 대화 복원 | 🟡 미활용. 장기 작업 중단/재개에 유용 |
| 14 | `--json-schema` | 구조화 출력 강제 | 🔴 미활용. Codex --output-schema와 유사, 결과 파싱 자동화 |
| 15 | `--max-budget-usd` | API 비용 상한 설정 | 🔴 미활용. 비용 안전 규칙에 직접 대응 |
| 16 | `--fallback-model` | 과부하 시 자동 폴백 | 🟡 미활용. opus → sonnet 자동 전환 |
| 17 | `claude plugin` | 플러그인 설치/관리 (마켓플레이스) | 🟡 미활용. 커뮤니티 플러그인 탐색 가능 |
| 18 | `--mcp-config` | JSON 파일로 MCP 설정 주입 | 🟡 미활용. 세션별 동적 MCP 구성 |
| 19 | `--strict-mcp-config` | 외부 MCP만 사용 (기존 설정 무시) | 🟡 미활용. 격리된 테스트 환경 |
| 20 | `--from-pr` | PR 연결 세션 복원 | 🟡 미활용. GitHub 워크플로 자동화 |
| 21 | `--permission-mode` | 권한 모드 (plan/default/bypassPermissions 등) | 🟡 부분 활용. plan 모드 자동화 가능 |
| 22 | `--input-format stream-json` | 실시간 스트리밍 입력 | 🔴 미활용. 양방향 실시간 통신 |
| 23 | Hooks (`~/.claude/hooks/`) | Pre/Post tool 훅 | ✅ 활용 중 (pre_bash.sh 파괴적 명령 차단) |
| 24 | `--tmux` | worktree와 함께 tmux 세션 생성 | 🟡 미활용. 멀티 세션 병렬 작업 |

## 미활용 중인 기능 (우선순위순)

### 즉시 적용 권장 (비용/안전 직접 개선)
1. **`--max-budget-usd`**: bridge 데몬에 `--max-budget-usd 5` 추가 → 단일 실행당 $5 상한
2. **`--effort low`**: 단순 파일 조작/읽기 작업에 effort low 적용 → 토큰 절감
3. **`--model sonnet`**: 패턴 C(리서치) 등 복잡도 낮은 작업에 sonnet 지정 → 비용 50%+ 절감
4. **`--json-schema`**: bridge 결과 파싱 자동화 → from_hands.md 구조 보장

### 중기 도입 권장 (워크플로 개선)
5. **`--agents`**: Brain/Scout/Quant 역할별 에이전트 프리셋 정의
6. **`--system-prompt`**: 패턴별 전용 시스템 프롬프트 (A=연산전용, B=코드전용, C=리서치전용)
7. **`claude mcp serve`**: CC를 MCP 서버로 노출 → 다른 시스템에서 CC를 도구로 호출
8. **`-r / --resume`**: 장시간 작업 중단/재개 파이프라인

### 탐색 가치 있음
9. **`--worktree`**: 실험 브랜치 자동 격리
10. **`claude plugin`**: 커뮤니티 플러그인 생태계 탐색
11. **`--from-pr`**: GitHub PR 기반 자동화

## 권장 사항 (Brain에게)

1. **woosdom_bridge.sh 업그레이드**: `--max-budget-usd 5 --effort medium` 추가하여 비용 안전장치 강화
2. **패턴별 모델 정책 수립**: A=opus, B=opus, C=sonnet, D=sonnet → 월 비용 20~30% 절감 예상
3. **에이전트 프리셋 정의**: `--agents` 플래그로 Scout/Quant/Builder 프리셋 만들어 to_hands.md에서 지정
4. **CC-as-MCP-Server 검토**: `claude mcp serve`로 CC를 MCP 서버화 → Codex/Antigravity에서 CC 도구 직접 호출 가능 (양방향 통신)
5. **구조화 출력 도입**: `--json-schema`로 bridge 결과 포맷 강제 → 파싱 에러 제거
