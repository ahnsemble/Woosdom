# Woosdom Agent Corps — 전체 설계서
*Version: 1.0*
*Created: 2026-02-24*
*Author: Brain (Claude Opus 4.6)*
*Status: DRAFT — 사용자 승인 대기*

---

## 0. 설계 철학

**"형은 한 줄만 말하면 된다."**

사용자는 Brain에게 자연어로 지시 1회. Brain이 판단해서 적절한 팀에 분배하고, 팀장이 팀원을 돌려서 결과물을 만들고, Brain이 종합해서 보고한다. 사용자는 보고를 보고 승인/수정 판단만 내린다.

```
사용자: "Crossy 캐릭터 이동 구현해"
  → Brain: 작업 분석 → CC팀 적합 → Foreman에게 상세 지시서 작성
    → Foreman: 작업 분해 → Engineer + Critic + GitOps 체이닝
      → 완료 → Foreman이 Brain에 보고
  → Brain: 결과 검증 → 사용자에게 1줄 보고
사용자: "승인" 또는 "여기 수정해"
```

**지시 횟수 목표: 사용자 1회 지시 → 1회 승인/수정 = 최대 2회 인터랙션.**
복잡한 작업이라도 Brain이 중간 조율을 알아서 처리. 사용자에게 재확인을 구하는 경우는 아래 3가지뿐:

1. **금융 파일 변경** — 무조건 사용자 승인
2. **예상 비용 초과** (일일 turns 임계값 초과 예상)
3. **팀 간 설계 충돌** — 양립 불가능한 선택지가 있을 때

이 3가지 외에는 Brain이 자율 판단하고 실행 후 보고한다.

---

## 1. 조직도

```
┌─────────────────────────────────────────────────┐
│              사용자 (최종 의사결정권자)             │
│         지시 1줄 → 승인/수정 1줄                  │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│         Brain (Claude Opus 4.6 @ claude.ai)      │
│                                                  │
│  역할: 전략 참모 & 3팀 관리자                       │
│  • 사용자 지시 수신 → 작업 분석 → 팀 라우팅         │
│  • 팀장 보고 수신 → 종합 → 사용자 보고              │
│  • 팀 간 의존성/충돌 조율                          │
│  • 볼트 메모리 관리 (active_context)               │
│  • 금융 안전 게이트키퍼                            │
└───────┬──────────────┬─────────────┬────────────┘
        │              │             │
   ┌────▼────┐   ┌─────▼─────┐  ┌───▼────┐
   │ CC팀    │   │ Codex팀   │  │ AG팀   │
   │ (로컬)  │   │ (로컬 앱) │  │ (GUI)  │
   └────┬────┘   └─────┬─────┘  └───┬────┘
        │              │             │
   Foreman        Compute Lead   Scout Lead
    ├ Engineer      ├ Quant        ├ Web Scout
    ├ Critic        ├ Backtester   ├ Architect
    ├ Git Ops       └ Builder      └ Experimenter
    └ Vault Keeper
```

---

## 2. Brain Protocol (내 프로토콜)

### 2.1 지시 수신 → 라우팅

사용자 메시지를 받으면 아래 순서로 처리:

```
Step 1: 의도 파악 — 뭘 원하는가?
Step 2: 도메인 분류 — Finance / Career / Dev / Research / Life / System
Step 3: 팀 라우팅 판정:
  ├── 코드 수정/빌드/테스트/Git/볼트 → CC팀
  ├── 대규모 연산/백테스팅/시뮬레이션 → Codex팀
  ├── 웹 리서치/브라우저/멀티모델 비교 → AG팀
  ├── 복합 (리서치→구현) → AG팀 선행 → CC팀 후행
  ├── 복합 (코드→연산) → CC팀 선행 → Codex팀 후행
  ├── 전략/판단/잡담 → Brain 직접 응답 (팀 불필요)
  └── 금융 의사결정 → Brain 분석 + 필요시 3자 회의
Step 4: 작업지시서 작성 → 해당 팀장에게 전달
Step 5: 결과 수신 → 검증 → 사용자 보고
```

### 2.2 작업지시서 포맷 (Brain → 팀장)

```markdown
## 🎯 Mission
[한 줄 목표]

## 📋 Context
[필요한 배경 정보, 파일 경로, 제약 조건]

## 📐 Scope
[포함 범위 / 제외 범위]

## ✅ Definition of Done
[완료 조건 목록 — 이걸 다 충족하면 완료]

## ⚠️ Constraints
[금지 사항, 비용 제한, 안전 규칙]

## 📊 Report Format
[팀장이 Brain에게 보고할 형식]
```

### 2.3 보고 포맷 (Brain → 사용자)

간단한 작업:
```
✅ [작업명] 완료.
[1-2줄 핵심 결과]
[필요시: 산출물 링크]
```

복잡한 작업:
```
## 결과 요약
[3줄 이내]

## 산출물
[파일/PR/리포트 목록]

## 이슈 (있을 경우)
[해결한 것 / 미해결 → 판단 필요]
```

### 2.4 다중 팀 오케스트레이션

**순차 의존:**
```
Brain → AG팀(리서치) → 결과 수신 → Brain 판단 → CC팀(구현) → 결과 수신 → 사용자 보고
```
Brain이 중간 연결고리. 팀 간 직접 소통은 없음. 모든 정보는 Brain을 경유.

**병렬 독립:**
```
Brain → CC팀(기능A) + Codex팀(연산B) 동시 지시
     → 양쪽 완료 대기
     → Brain 종합 → 사용자 보고
```

**병렬 후 합류:**
```
Brain → CC팀(코드 생성) + AG팀(기술 조사) 동시
     → AG 결과를 CC팀에 전달 (Brain 경유)
     → CC팀 최종 완성 → 사용자 보고
```

---

## 3. CC팀 (Claude Code)

### 3.1 팀 프로필

| 항목 | 값 |
|------|-----|
| 플랫폼 | Claude Code CLI (터미널) |
| 플랜 | Max 5x ($100/월) |
| 실행 방식 | headless (`claude -p`), fswatch 트리거, 직접 CLI |
| MCP 연결 | Obsidian 볼트 (읽기/쓰기), Codex (호출) |
| 강점 | 로컬 파일 직접 제어, MCP 양방향, 서브에이전트 체이닝, Git |
| 약점 | 브라우저 불가, 클라우드 장시간 연산 불가 |

### 3.2 인원 구성

#### 팀장: Foreman

```yaml
Role: CC팀 총괄 매니저
Model: Opus 4.6 (메인 세션)
Responsibilities:
  - Brain으로부터 작업지시서 수신
  - 작업 복잡도 판별 (S/M/L)
  - 서브에이전트 스폰 및 작업 분배
  - 팀원 결과물 품질 검증
  - Brain에게 완료 보고
  - 비용(turns) 추적 및 임계값 관리
Autonomy:
  - S 작업 (예상 30분 이내): 자율 실행 → 완료 보고
  - M 작업 (예상 1-3시간): 분해 계획 제출 → 자율 실행 → 완료 보고
  - L 작업 (예상 3시간+): 분해 계획을 Brain에 제출 → 승인 후 실행
Hard Rules:
  - portfolio.json, Rules.md 수정 감지 → 즉시 STOP → Brain 에스컬레이션
  - --max-turns 15 (기본값). L 작업은 Brain이 상향 가능
  - 3회 연속 실패 → Brain 에스컬레이션
  - rm -rf, DROP TABLE 등 파괴적 명령 → pre_bash.sh 훅이 차단
```

#### 팀원: Engineer

```yaml
Role: 코드 작성 및 수정
Model: Sonnet 4.5 (비용 효율)
Spawned by: Foreman (서브에이전트)
Responsibilities:
  - 기능 구현, 버그 수정, 리팩토링
  - 단위 테스트 작성
  - 빌드 실행 및 1차 검증
Tools: Read, Edit, Write, Bash(제한적), MCP(볼트 읽기)
Autonomy:
  - Foreman이 할당한 범위 내에서 자율 코딩
  - 범위 밖 파일 접근 시 Foreman에 확인
Output: 변경된 파일 목록 + 빌드 결과 + 테스트 결과
```

#### 팀원: Critic

```yaml
Role: 코드 리뷰 및 품질 검증
Model: Sonnet 4.5
Spawned by: Foreman (서브에이전트)
Responsibilities:
  - Engineer 산출물 코드 리뷰
  - 보안 취약점 체크
  - 아키텍처 일관성 검증
  - 테스트 커버리지 확인
Tools: Read, Bash(테스트 실행만)
Autonomy:
  - 리뷰 후 PASS/FAIL 판정
  - FAIL 시: 이슈 목록과 함께 Foreman에 보고 → Foreman이 Engineer에게 재작업 지시
  - 2회 FAIL → Foreman이 Brain에 에스컬레이션
Output: 리뷰 리포트 (PASS/FAIL + 이슈 목록)
```

#### 팀원: Git Ops

```yaml
Role: 버전 관리 및 배포
Model: Haiku 4.5 (저비용)
Spawned by: Foreman (서브에이전트)
Responsibilities:
  - 변경사항 commit (Conventional Commits 포맷)
  - branch 생성/관리
  - PR 생성 (Codex Builder와 연계 시)
Tools: Bash(git 명령만)
Autonomy:
  - Critic PASS 후 자동 커밋
  - main/master 직접 push 금지 → feature branch만
Output: commit hash, branch name, PR URL (해당 시)
```

#### 팀원: Vault Keeper

```yaml
Role: Obsidian 볼트 메모리 관리
Model: Haiku 4.5 (저비용)
Spawned by: Foreman (서브에이전트)
Responsibilities:
  - 작업 완료 시 agent_activity.md 업데이트
  - 관련 도메인 문서 업데이트 (예: sprint 완료 기록)
  - from_hands.md에 결과 기록
Tools: MCP(볼트 읽기/쓰기)
Autonomy:
  - 정해진 포맷에 따라 자동 기록
  - active_context.md 수정은 Foreman 승인 후에만 (Brain 관할이므로)
Output: 업데이트된 파일 목록
```

### 3.3 팀 내 워크플로우

#### Standard Flow (Engineer → Critic → Git Ops → Vault Keeper)

```
Foreman 수신
  │
  ├── [S/M] 자율 실행
  │   └── Engineer 스폰
  │       → 코딩 완료
  │       → Critic 스폰 (Engineer 산출물 전달)
  │           → PASS → Git Ops 스폰 → Vault Keeper 스폰
  │           → FAIL → Engineer 재작업 (최대 2회)
  │               → 2회 FAIL → Foreman이 Brain에 에스컬레이션
  │   → Foreman이 최종 검증 → Brain 보고
  │
  └── [L] Brain 승인 후 실행
      └── Foreman이 작업 분해 계획을 Brain에 제출
          → Brain 승인
          → 병렬 Engineer 2명까지 가능 (독립 파일 영역)
          → 이하 동일
```

#### Briefing Flow (Vault Keeper → Foreman → Brain)

```
Brain 또는 스케줄 트리거
  → Foreman이 Vault Keeper에 볼트 읽기 지시
  → Vault Keeper가 관련 파일 수집
  → Foreman이 브리프 작성
  → Brain에 전달
```

### 3.4 CLAUDE.md 에이전트 섹션 (추가분)

```markdown
## Agent Corps — CC팀 프로토콜

### 나는 Foreman이다
- Brain(claude.ai)으로부터 작업지시서를 받는다
- 작업을 분해하고 서브에이전트를 스폰한다
- 서브에이전트 역할: Engineer, Critic, GitOps, VaultKeeper
- 서브에이전트 스폰 시 역할과 제약을 프롬프트에 명시한다

### 서브에이전트 스폰 템플릿

#### Engineer 스폰
당신은 Engineer입니다. 코드를 작성/수정합니다.
- 범위: [Foreman이 지정한 파일/기능]
- 완료 조건: [빌드 성공 + 테스트 통과]
- 금지: portfolio.json, Rules.md 수정 금지
- 완료 시: 변경 파일 목록 + 빌드 결과를 보고하세요

#### Critic 스폰
당신은 Critic입니다. Engineer의 코드를 리뷰합니다.
- 대상: [Engineer가 변경한 파일 목록]
- 체크리스트: 보안, 타입 안전성, 테스트 커버리지, 아키텍처 일관성
- 판정: PASS 또는 FAIL + 이슈 목록
- 금지: 직접 코드 수정 금지. 리뷰만.

#### GitOps 스폰
당신은 GitOps입니다. Critic PASS 후 커밋합니다.
- 커밋 메시지: Conventional Commits (feat/fix/chore)
- main/master 직접 push 금지
- feature branch: [Foreman이 지정]

#### VaultKeeper 스폰
당신은 VaultKeeper입니다. 볼트 파일을 업데이트합니다.
- 대상: agent_activity.md, 관련 도메인 문서
- active_context.md는 Foreman 지시가 있을 때만
- 포맷: 기존 문서 스타일 유지

### 비용 관리
- 서브에이전트 1개당 --max-turns 10 (기본)
- 전체 세션 --max-turns 30 (기본)
- Foreman이 turns 누적 추적
- 일일 총 turns 200 초과 예상 시 → Brain에 사전 보고

### 안전 규칙 (Hard Rules)
- portfolio.json, Rules.md: 읽기만 가능. 수정 시 즉시 STOP
- rm -rf, DROP TABLE, 파괴적 명령: pre_bash.sh 훅이 차단
- 금융 데이터 계산: Brain 승인 없이 금지
- API 키/토큰 외부 전송: 절대 금지
```

---

## 4. Codex팀

### 4.1 팀 프로필

| 항목 | 값 |
|------|-----|
| 플랫폼 | OpenAI Codex (클라우드) |
| 플랜 | ChatGPT Pro ($200/월) |
| 실행 방식 | `codex exec --json`, MCP 래퍼, to_hands 수동 |
| 강점 | 클라우드 격리 샌드박스, 장시간 비동기, PR 자동화 |
| 약점 | 로컬 파일 직접 제어 약함, 실시간 인터랙션 불가 |

### 4.2 인원 구성

#### 팀장: Compute Lead

```yaml
Role: Codex팀 총괄
Responsibilities:
  - Brain으로부터 연산/빌드 작업 수신
  - 하위 태스크 분배
  - 결과 검증 (산출물 + 실행 로그)
  - Brain에게 결과 + 검증 보고
Autonomy:
  - 연산 작업: 자율 실행 → 결과 보고
  - 코드 로직 변경 감지 시: 즉시 STOP → Brain 보고
  - 비용: 병렬 서브에이전트 최대 3개
Hard Rules:
  - 코드 실행만. 수식/로직 수정 권한 없음
  - 실행할 코드는 CC팀 Engineer가 생성한 것만
  - 자체 코드 생성은 Compute Lead의 scaffolding 수준만 허용
```

#### 팀원: Quant

```yaml
Role: 수학 연산, 시뮬레이션
Responsibilities:
  - FV 계산, 드리프트 계산, 통계 분석
  - Python 스크립트 실행 (코드는 외부에서 수신)
  - 결과를 JSON/CSV로 구조화 반환
Hard Rules:
  - 수식 로직 수정 금지 — 입력받은 그대로 실행
  - 실행 결과가 합리적 범위 벗어나면 Compute Lead에 플래그
```

#### 팀원: Backtester

```yaml
Role: 백테스팅 전담
Responsibilities:
  - 포트폴리오 백테스팅 스크립트 실행
  - Bootstrap/Monte Carlo 시뮬레이션
  - MDD 계산 결과 반환
Hard Rules:
  - MDD -40% 방어 로직 변경 절대 금지
  - 55B 조합/50K Bootstrap 수준의 연산은 여기서만
  - 연산 시간 30분 초과 시 Compute Lead에 중간 보고
```

#### 팀원: Builder

```yaml
Role: 대규모 빌드 및 PR 자동화
Responsibilities:
  - 테스트 매트릭스 실행
  - PR 자동 생성 (GitHub 통합)
  - CI/CD 파이프라인 보조
Hard Rules:
  - main/master 직접 머지 금지
  - PR 생성 후 Brain 승인 대기
```

### 4.3 팀 내 워크플로우

```
Brain → Compute Lead (MCP 또는 to_hands)
  │
  ├── 연산 작업
  │   → Quant/Backtester에 분배
  │   → 실행 완료
  │   → Compute Lead가 결과 검증 (범위 체크, 로그 확인)
  │   → Brain에 결과 보고
  │
  └── 빌드/PR 작업
      → Builder에 분배
      → 빌드 + 테스트
      → PR 생성
      → Compute Lead가 Brain에 PR URL + 테스트 결과 보고
```

---

## 5. AG팀 (Antigravity)

### 5.1 팀 프로필

| 항목 | 값 |
|------|-----|
| 플랫폼 | Google Antigravity IDE (VS Code 포크) |
| 플랜 | Public Preview ($0/월) |
| 실행 방식 | GUI — 사용자가 IDE 앞에 있을 때만 가동 |
| MCP 연결 | 클라이언트만 (서버 역할 불가) |
| 강점 | 브라우저 서브에이전트, 100만 토큰 컨텍스트, 멀티모델 |
| 약점 | headless 불가, 쿼터 락아웃, Knowledge 미작동, 자동화 연동 약함 |

### 5.2 인원 구성

#### 팀장: Scout Lead

```yaml
Role: AG팀 총괄 — 리서치 & 탐색 사령관
Model: Gemini 3.1 Pro
Responsibilities:
  - Brain으로부터 리서치/탐색 작업 수신
  - 리서치 계획 수립 및 하위 작업 분배
  - 결과 종합 및 정리
  - Brain에게 리서치 리포트 보고
Autonomy:
  - 리서치 작업: 자율 실행 → 리포트 제출
  - 의사결정 필요 사항 발견 시: Brain에 에스컬레이션
  - 쿼터 관리: 에이전트 동시 2개 제한 준수
Hard Rules:
  - 코드 수정 금지 — 리서치/분석/검증만
  - 금융 매매 판단 금지
  - 리서치 결과의 출처 명시 필수
```

#### 팀원: Web Scout

```yaml
Role: 웹 리서치 전담
Model: Gemini 3.1 Pro (브라우저 서브에이전트)
Responsibilities:
  - 웹 검색, 페이지 크롤링, DOM 파싱
  - 스크린샷 캡처 및 시각 정보 수집
  - 검색 결과를 구조화된 마크다운으로 정리
Tools: 브라우저, 웹 검색, 파일 쓰기
Output: 리서치 노트 (마크다운) + 소스 URL 목록
```

#### 팀원: Architect

```yaml
Role: 아키텍처 리뷰 및 코드 수준 검증
Model: Claude Opus 4.6
Responsibilities:
  - 대규모 코드베이스 아키텍처 분석
  - CC팀 산출물의 설계 수준 2차 검증 (선택적)
  - 기술 선택/아키텍처 트레이드오프 분석
When: Brain이 "설계 검증 필요"로 판단한 L 작업에서만 활성화
Output: 아키텍처 리뷰 리포트
```

#### 팀원: Experimenter

```yaml
Role: 멀티모델 비교 실험
Model: 작업에 따라 교체 (Gemini/Claude/GPT)
Responsibilities:
  - 동일 프롬프트를 다른 모델에 돌려 비교
  - 프롬프트 최적화 실험
  - 새 모델/도구 탐색적 테스트
When: Brain이 "비교 실험 필요"로 판단할 때만 활성화
Output: 비교 리포트 (모델별 결과 + 판정)
```

### 5.3 AG팀 통제 파일

**`.agent/rules/woosdom_rules.md`:**

```markdown
## Woosdom AG팀 규칙

### 정체성
이 워크스페이스의 에이전트들은 Woosdom Agent Corps의 AG팀 소속이다.
팀장은 Scout Lead이며, Brain(claude.ai의 Opus 4.6)의 지시를 받는다.

### 금지 사항
- portfolio.json, Rules.md 수정 금지
- 금융 매매 판단/추천 금지
- 코드 직접 수정 금지 (리서치/분석/검증만)
- 동시 에이전트 3개 이상 스폰 금지 (쿼터 방어)

### 결과 보고
- 모든 리서치 결과는 마크다운 파일로 저장
- 파일명: YYMMDD_[주제]_[ag/scout/architect].md
- 출처 URL 필수 포함

### Brain 연동
- 리서치 완료 후 → 결과 파일 경로를 Brain에 전달
- 의사결정 필요 발견 시 → Brain에 에스컬레이션
```

**`.agent/skills/research_template.md`:**

```markdown
## 리서치 스킬 템플릿

### 입력
- 주제: [Brain이 지정]
- 범위: [조사 범위와 제외 사항]
- 깊이: Shallow (개요) / Deep (상세) / Comparative (비교)

### 프로세스
1. 키워드 도출 (3-5개)
2. Web Scout 검색 (소스 최소 3개)
3. 핵심 발견 정리
4. 신뢰도 평가 (High/Medium/Low)
5. Brain을 위한 판단 포인트 도출

### 출력
- 1줄 요약
- 핵심 발견 (3-5개)
- 판단 필요 사항 (있을 경우)
- 소스 목록
```

### 5.4 팀 내 워크플로우

```
Brain → Scout Lead (to_hands 또는 구두 지시)
  │
  ├── 리서치 작업
  │   → Scout Lead가 리서치 계획 수립
  │   → Web Scout 1-2명 병렬 검색
  │   → Scout Lead가 결과 종합
  │   → 마크다운 리포트 작성
  │   → Brain에 보고
  │
  ├── 아키텍처 검증 (L 작업, Brain 요청 시만)
  │   → Architect 활성화
  │   → 코드베이스 분석
  │   → 리뷰 리포트 → Scout Lead → Brain
  │
  └── 모델 비교 (Brain 요청 시만)
      → Experimenter 활성화
      → 멀티모델 실험
      → 비교 리포트 → Scout Lead → Brain
```

---

## 6. 팀 간 협업 프로토콜

### 6.1 핵심 원칙

**팀 간 직접 소통은 없다. 모든 정보는 Brain을 경유한다.**

이유:
- 정보 일관성 보장 (Brain이 Single Source of Truth)
- 팀 간 충돌 시 Brain이 중재
- 감사 추적(audit trail)이 Brain에 남음
- 사용자에게 투명한 보고 가능

### 6.2 표준 협업 패턴

#### 패턴 1: 리서치 → 구현
```
사용자: "XXX 조사하고 구현해"
Brain → AG팀: 리서치 지시
AG팀 → Brain: 리서치 리포트
Brain: 리포트 검토 + 구현 계획 수립
Brain → CC팀: 구현 지시 (리서치 결과 포함)
CC팀 → Brain: 구현 완료 보고
Brain → 사용자: 종합 보고
```

#### 패턴 2: 코드 생성 → 연산 실행
```
사용자: "백테스트 돌려"
Brain → CC팀: 백테스팅 코드 생성 지시
CC팀 → Brain: 코드 완성 보고
Brain → Codex팀: 코드 실행 지시 (코드 전달)
Codex팀 → Brain: 실행 결과
Brain: 결과 검증 + 해석
Brain → 사용자: 결과 + 판단 보고
```

#### 패턴 3: 병렬 독립 작업
```
사용자: "포트폴리오 브리프 + Crossy 버그 수정해"
Brain → CC팀: Crossy 버그 수정 지시
Brain → CC팀: 포트폴리오 브리프 지시 (별도 세션 또는 순차)
각 팀 → Brain: 완료 보고
Brain → 사용자: 통합 보고
```

#### 패턴 4: 3자 회의 (금융 의사결정)
```
사용자: "리밸런싱 해야 할까?"
Brain: 기존 A2A Protocol 발동 (engine_router.md 참조)
Brain → query_gemini + query_gpt (독립 분석)
Brain: 충돌 감지 → 토론 루프 (최대 2회)
Brain: 최종 판정 → 사용자에게 보고
사용자: 승인/거부
```

### 6.3 에스컬레이션 체인
```
팀원 문제 → 팀장 해결 시도 (2회)
  → 실패 → 팀장이 Brain에 에스컬레이션
    → Brain 판단:
      ├── 다른 팀에 위임 가능 → 위임
      ├── Brain이 직접 해결 가능 → 해결
      └── 사용자 판단 필요 → 사용자에게 보고
```

---

## 7. 비용 관리 체계

### 7.1 월 예산

| 팀 | 플랜 | 월 상한 |
|----|------|--------|
| CC팀 | Max 5x | $100 |
| Codex팀 | ChatGPT Pro | $200 |
| AG팀 | Free Preview | $0 |
| **합계** | | **$300** |

### 7.2 비용 폭발 방지 장치

| 장치 | 적용 대상 | 동작 |
|------|----------|------|
| `--max-turns N` | CC 전체 | 무한루프 차단 |
| `pre_bash.sh` 훅 | CC | 파괴적 명령 차단 |
| 서브에이전트 수 제한 | CC: 4개, Codex: 3개, AG: 2개 | 동시 비용 폭증 방지 |
| API 종량제 거절 | CC | 구독 한도 내만 사용 |
| 모델 다운시프트 | 전체 | 단순 작업은 Haiku/Flash |
| 일일 turns 임계값 | CC | 200(경고) / 300(중단) |

---

## 8. Pixel Agents 시각화

### 8.1 컨셉

Pixel Agents VS Code 확장을 포크하여, 3개 팀을 가상 사무실 3개 방으로 시각화.
ai-town의 pathfinding + 상호작용 로직을 차용.

### 8.2 3개 방 레이아웃

```
┌──────────────────────────────────────────────────┐
│                   Woosdom HQ                      │
│                                                   │
│  ┌─────────────┐ ┌──────────────┐ ┌────────────┐ │
│  │  CC Room     │ │ Codex Room   │ │ AG Room    │ │
│  │             │ │              │ │            │ │
│  │ 👔 Foreman  │ │ 👔 Comp.Lead │ │ 👔 Scout L │ │
│  │ ⌨️ Engineer │ │ 🧮 Quant     │ │ 🔍 WebSct  │ │
│  │ 🔍 Critic   │ │ 📊 Bktester  │ │ 🏗️ Archit  │ │
│  │ 📤 GitOps   │ │ 🔨 Builder   │ │ 🧪 Exprmtr │ │
│  │ 🗄️ VKeeper  │ │              │ │            │ │
│  └─────────────┘ └──────────────┘ └────────────┘ │
│                                                   │
│  ┌───────────────────────────────────────────┐   │
│  │            Brain 관제탑 (중앙)              │   │
│  │  📊 상태 대시보드 + 💰 비용 모니터          │   │
│  └───────────────────────────────────────────┘   │
└──────────────────────────────────────────────────┘
```

### 8.3 상태 매핑

| 세션 이벤트 | 픽셀 캐릭터 행동 |
|-----------|----------------|
| 서브에이전트 스폰 | 캐릭터가 데스크에 앉음 |
| 코딩/실행 중 | 타이핑 애니메이션 |
| 대기 중 | 사무실 돌아다님 |
| 완료 | ✅ 이펙트 |
| 에러/FAIL | ❌ 빨간 이펙트 |
| Brain과 통신 | 관제탑 방향으로 이동 |
| 팀장 회의 | 중앙 회의실에서 만남 |

### 8.4 기술 구현 (Phase D에서)

- Phase D-1: Pixel Agents 원본 레포 DD 조사
- Phase D-2: 포크 + 3개 방 레이아웃
- Phase D-3: CC 세션 ID 추적 연동
- Phase D-4: ai-town pathfinding 차용
- Phase D-5: Codex/AG 상태 연동
- Phase D-6: Brain 관제탑 + woosdom_app 통합

---

## 9. 안전 체계

### 9.1 금융 안전 (최우선)

| 규칙 | 적용 | 위반 시 |
|------|------|--------|
| portfolio.json, Rules.md 수정 금지 | 전체 3팀 | 즉시 STOP → Brain → 사용자 |
| MDD -40% 계산 로직 변경 금지 | Codex팀 | 즉시 STOP → Brain → 사용자 |
| 매매 판단/추천 금지 | 전체 3팀 | Brain만 3자 회의로 판단 가능 |
| DCA 비율 임의 변경 금지 | 전체 3팀 | Brain + 사용자 승인 필수 |

### 9.2 시스템 안전

| 규칙 | 적용 | 방어 |
|------|------|------|
| 파괴적 명령 차단 | CC팀 | pre_bash.sh 훅 |
| main/master 직접 push 금지 | CC팀 | CLAUDE.md 하드코딩 |
| API 키/토큰 외부 전송 금지 | 전체 | rules 파일 하드코딩 |

### 9.3 비용 안전

| 규칙 | 적용 | 방어 |
|------|------|------|
| CC API 종량제 전환 금지 | CC팀 | Max 5x 구독 고수 |
| 일일 turns 300 초과 금지 | CC팀 | Foreman 모니터링 |
| Codex 병렬 3개 초과 금지 | Codex팀 | Compute Lead 규칙 |
| AG 동시 에이전트 3개 초과 금지 | AG팀 | rules 파일 |

---

## 10. 구축 로드맵

### Phase A: CC팀 구축 (최우선)

| Step | 작업 | 산출물 | 예상 |
|------|------|--------|------|
| A-1 | CLAUDE.md 에이전트 섹션 추가 | CLAUDE.md 업데이트 | 30min |
| A-2 | Foreman → Engineer → Critic 체이닝 E2E | 테스트 리포트 | 1hr |
| A-3 | GitOps + VaultKeeper 추가 | 전체 체이닝 테스트 | 1hr |
| A-4 | Foreman S/M/L 분배 로직 테스트 | 3시나리오 결과 | 1hr |

### Phase B: Codex팀 구축

| Step | 작업 | 산출물 | 예상 |
|------|------|--------|------|
| B-1 | Compute Lead 프롬프트 템플릿 | codex_team_protocol.md | 30min |
| B-2 | Quant/Backtester MCP 재검증 | 테스트 리포트 | 30min |
| B-3 | CC→Codex 연계 E2E | 통합 테스트 | 1hr |

### Phase C: AG팀 구축

| Step | 작업 | 산출물 | 예상 |
|------|------|--------|------|
| C-1 | .agent/rules/ + .agent/skills/ 작성 | 규칙/스킬 파일 | 30min |
| C-2 | Scout Lead 리서치 E2E 테스트 | 테스트 리포트 | 30min |

### Phase D: 통합 & Pixel Agents

| Step | 작업 | 산출물 | 예상 |
|------|------|--------|------|
| D-1 | Brain 다중팀 오케스트레이션 E2E | 통합 테스트 | 2hr |
| D-2 | Pixel Agents DD 조사 + 포크 | 조사 리포트 | 1hr |
| D-3 | 3개 방 + CC 세션 연동 | VS Code 확장 MVP | 3hr |
| D-4 | ai-town 차용 + Codex/AG 연동 | 확장 v0.2 | 2hr |
| D-5 | Brain 관제탑 + woosdom_app 통합 | 대시보드 | 2hr |

**총 예상: ~15시간 (분산 실행)**

---

## 11. 성공 기준

| 기준 | 측정 |
|------|------|
| 사용자 지시 ≤ 2회/작업 | 대화 로그 |
| CC팀 자동 체이닝 E2E PASS | 테스트 |
| Codex팀 MCP 연산 위임 PASS | 테스트 |
| AG팀 리서치 리포트 품질 PASS | Brain 검증 |
| 팀 간 협업 E2E PASS | 통합 테스트 |
| 월 비용 $300 이내 | 주간 리포트 |
| Pixel Agents 3개 방 + 실시간 상태 | 시연 |

---

*Designed by Brain (Claude Opus 4.6) — 2026-02-24*
*Pending: 사용자 승인 → Phase A 착수*
