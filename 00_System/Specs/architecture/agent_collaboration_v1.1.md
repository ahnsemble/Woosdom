# Woosdom Multi-Agent Collaboration Architecture v1.1

> v1.0 → v1.1 변경사항 (3자회의 반영)
> 1. 오류 복구/재시도 전략 추가 (§3.4)
> 2. 모니터링 구체화 (§5.3)
> 3. "병렬" 의미 명확화 (§3.5)
> 4. 워크플로우 복잡성 제한 규칙 (§3.6)
> 5. 단일 Writer 원칙 명시 (§4.3)

---

## 🏗️ 설계 원칙

**"You think. Agents execute. Obsidian remembers."**

| 원칙 | 설명 |
|------|------|
| **Full Autonomy** | 에이전트끼리 알아서 협업, Brain에게는 결과만 보고 |
| **Vault-Native** | 모든 통신은 Obsidian 파일 기반 (MessageBus/) |
| **Zero Trust Execution** | 각 에이전트는 자기 영역만 실행, 타 영역 접근 시 반드시 위임 |
| **Observable** | 모든 태스크의 생명주기가 Vault에 기록됨 |
| **Sequential Execution** | CC가 inbox를 순차 처리. 진짜 병목은 LLM API 호출이지 파일 I/O가 아님 |

---

## 1. 시스템 전체 구조도

```
┌─────────────────────────────────────────────────────────────────┐
│                        🧠 BRAIN (You)                           │
│              결과 보고 수신 / 긴급 에스컬레이션 처리              │
│                    전략적 의사결정만 담당                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │ 📋 결과 보고 / 🔴 긴급 에스컬레이션
                           │
┌──────────────────────────┴──────────────────────────────────────┐
│                   📡 MESSAGE BUS (Vault)                         │
│                                                                  │
│  /00_System/MessageBus/                                          │
│  ├── inbox/          ← 에이전트별 수신함                         │
│  ├── outbox/         ← 처리 완료 메시지 아카이브                 │
│  ├── workflows/      ← 활성 워크플로우 상태 추적                 │
│  │   ├── active/                                                 │
│  │   ├── completed/                                              │
│  │   └── templates/                                              │
│  ├── deadletter/     ← 실패/타임아웃 메시지                      │
│  └── brain_report/   ← Brain 보고 전용 (결과 요약)               │
└─────────────────────────────────────────────────────────────────┘
                           │
    ┌──────────────────────┼──────────────────────┐
    │                      │                      │
┌───┴──────┐  ┌────────────┴──────────┐  ┌───────┴──────┐
│ COMMAND  │  │       DOMAIN          │  │   SUPPORT    │
│ DIVISION │  │      DIVISIONS        │  │  DIVISIONS   │
│          │  │                       │  │              │
│ Dispatch │  │  Finance  Research    │  │  Compute     │
│ Audit    │  │  Engineer Creative    │  │  Operations  │
│ Memory   │  │  Life     Career     │  │              │
└──────────┘  └───────────────────────┘  └──────────────┘
```

---

## 2. 메시지 프로토콜

### 2.1 메시지 포맷 (YAML Front-matter)

```yaml
---
msg_id: "WF-20260304-001-T03"
workflow_id: "WF-20260304-001"
type: task_request
from: fin-market-scout
to: fin-quant
priority: normal                    # critical / high / normal / low
created: "2026-03-04T14:30:00+09:00"
ttl: 60                             # 분 단위 타임아웃
status: pending                     # pending → active → done / failed / escalated
depends_on: ["WF-20260304-001-T02"]
retry_count: 0                      # 🆕 v1.1: 현재 재시도 횟수
---

## Task
시장 데이터 기반 모멘텀 팩터 계산 요청

## Input
- 데이터: SP500 3개월 일봉

## Expected Output
- 모멘텀 스코어 상위 20 종목
- 팩터 가중치 테이블

## Context
[[01_Domains/Finance/market_data/sp500_daily.csv]]
```

### 2.2 메시지 유형 (type)

| type | 설명 |
|------|------|
| `task_request` | 작업 요청 |
| `task_response` | 작업 완료 응답 |
| `info_share` | 정보 공유 (작업 요청 아님) |
| `escalation` | 에스컬레이션 |
| `status_update` | 진행 상황 중간 보고 |
| `workflow_start` | 워크플로우 시작 트리거 |
| `workflow_complete` | 워크플로우 완료 보고 |

---

## 3. 워크플로우 엔진

### 3.1 cmd-dispatcher v2.5 (역할 확장)

기존 역할:
- ✅ Brain 명령 → 에이전트 라우팅
- ✅ 부서별 Lead 식별

확장 역할:
- 🆕 워크플로우 템플릿 인스턴스화
- 🆕 DAG 의존성 해소 (선행 완료 → 후행 트리거)
- 🆕 타임아웃 감지 → deadletter 이동
- 🆕 워크플로우 완료 시 Brain 보고 생성
- 🆕 병렬 태스크 동시 디스패치
- 🆕 v1.1: 실패 태스크 재시도 관리

### 3.2 워크플로우 템플릿 (DAG)

저장 위치: `/00_System/MessageBus/workflows/templates/`

```yaml
# finance_pipeline.yaml
---
workflow_id_prefix: "FIN-PIPE"
name: "금융 분석 파이프라인"
trigger: manual | scheduled | event
max_tasks: 10                       # 🆕 v1.1: 워크플로우당 최대 태스크 수

tasks:
  T01:
    agent: fin-market-scout
    action: "시장 데이터 수집 + 노이즈 필터링"
    depends_on: []
    ttl: 30
    max_retries: 2                  # 🆕 v1.1
    on_failure: retry_then_escalate # 🆕 v1.1
  T02:
    agent: fin-quant
    action: "팩터 계산 + 시그널 생성"
    depends_on: [T01]
    ttl: 60
    max_retries: 1
    on_failure: escalate
  T03:
    agent: fin-backtester
    action: "시그널 기반 백테스트 실행"
    depends_on: [T02]
    ttl: 90
    max_retries: 1
    on_failure: retry_then_escalate
  T04:
    agent: fin-portfolio-analyst
    action: "백테스트 결과 해석 + 리밸런싱 제안"
    depends_on: [T03]
    ttl: 45
    max_retries: 1
    on_failure: escalate
  T05:
    agent: fin-tax-optimizer
    action: "세금 영향 분석"
    depends_on: [T04]
    ttl: 30
    max_retries: 2
    on_failure: skip_with_warning   # 🆕 v1.1: 선택적 태스크는 스킵 가능
    parallel_with: [T06]
  T06:
    agent: fin-fire-planner
    action: "FIRE 타임라인 영향"
    depends_on: [T04]
    ttl: 30
    max_retries: 2
    on_failure: skip_with_warning
    parallel_with: [T05]

report_to: brain
on_workflow_failure: escalate_to_brain
```

### 3.3 실행 흐름

```
Brain: "금융 파이프라인 실행해"
         │
         ▼
  Dispatcher ─① 템플릿 로드 → 인스턴스 생성
         │    ② T01 즉시 디스패치
         ▼
  Market Scout (T01) → 완료
         │
         ▼
  Quant (T02) → 4중 Sanity Check → 완료
         │
         ▼
  Backtester (T03) → 바이어스 4항목 체크 → 완료
         │
         ▼
  Portfolio Analyst (T04) → 리밸런싱 제안 → 완료
         │
    ┌────┴────┐
    ▼         ▼
  Tax Opt   FIRE Plan    ← 독립 디스패치 (§3.5 참조)
  (T05)     (T06)
    └────┬────┘
         ▼
  Dispatcher → brain_report/ → Brain 최종 보고
```

### 3.4 🆕 오류 복구 / 재시도 전략 (v1.1)

```yaml
failure_handling:
  retry_then_escalate:
    # 재시도 후에도 실패 시 에스컬레이션
    1: "retry_count < max_retries → 메시지를 inbox에 재작성 (retry_count +1)"
    2: "retry_count >= max_retries → 에스컬레이션 매트릭스 진입"
    
  escalate:
    # 재시도 없이 즉시 에스컬레이션
    1: "즉시 에스컬레이션 매트릭스 진입"
    
  skip_with_warning:
    # 선택적 태스크 — 실패해도 워크플로우 계속 진행
    1: "retry_count < max_retries → 재시도"
    2: "재시도 실패 → 해당 태스크 status: skipped"
    3: "brain_report에 ⚠️ 경고 포함, 워크플로우는 계속"
    
  on_workflow_failure:
    # 핵심 태스크(T01~T04) 실패 시
    1: "워크플로우 status: paused"
    2: "brain_report/에 즉시 실패 보고"
    3: "Brain 판단 대기 (재시도 / 중단 / 수동 처리)"
```

**실패 메시지 처리 흐름:**
```
태스크 실패 발생
    │
    ├─ retry_count < max_retries?
    │   ├─ YES → inbox에 재작성 (retry_count +1) → 재실행
    │   └─ NO ─┐
    │          │
    ├─ on_failure = skip_with_warning?
    │   ├─ YES → status: skipped, 워크플로우 계속, ⚠️ 보고
    │   └─ NO → 에스컬레이션 매트릭스 진입
    │
    └─ 핵심 태스크 실패 → 워크플로우 paused → Brain 보고
```

### 3.5 🆕 병렬 실행 — CC 서브에이전트 스폰 (v1.1 → v1.1.1 업데이트)

> **v1.1 원안**: parallel = 순차 처리, 의존성 없는 독립 디스패치
> **v1.1.1 변경**: parallel = **CC 서브에이전트를 실제 병렬 스폰**

#### 작동 방식

```
workflow_engine.py가 DAG에서 depends_on이 해소된 태스크를 수집
  → 독립 태스크가 2개 이상이면
  → CC 서브에이전트를 태스크 수만큼 동시 스폰
  → 각 서브에이전트: 에이전트 스펙 로드 → 페르소나로 실행 → inbox에 결과 작성
  → 전체 완료 대기 후 DAG 다음 단계 진행
```

#### 구현 (workflow_engine.py)

```python
import concurrent.futures
import subprocess

def dispatch_parallel(independent_tasks, max_workers=3):
    """depends_on 해소된 독립 태스크들을 CC 서브에이전트로 병렬 실행"""
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for task in independent_tasks:
            cmd = [
                "claude", "code",
                "--agent-prompt", build_agent_prompt(task),
                "--output", f"MessageBus/inbox/{task.target_agent}.md"
            ]
            future = executor.submit(subprocess.run, cmd, capture_output=True)
            futures[future] = task
        
        for future in concurrent.futures.as_completed(futures):
            task = futures[future]
            result = future.result()
            update_workflow_state(task, result)  # workflows/active/{id}.md 갱신
```

#### 파일 충돌 방지 — 왜 안전한가

```
inbox/fin-quant.md        ← fin-quant만 읽음
inbox/fin-tax-optimizer.md ← fin-tax-optimizer만 읽음
inbox/fin-fire-planner.md  ← fin-fire-planner만 읽음
workflows/active/{id}.md   ← workflow_engine.py만 수정 (단일 Writer)
```

- 각 에이전트는 **자기 inbox만** 결과를 씀
- 병렬 에이전트가 같은 파일에 동시 쓰기하는 경우 없음
- workflows/active 상태 파일은 workflow_engine.py만 수정 → 단일 Writer 유지

#### 동시 실행 한도

```yaml
parallel_config:
  max_concurrent_agents: 3     # 초기값. 안정성 확인 후 확장
  reason: "CC는 Anthropic API 호출이므로 로컬 리소스 부담 미미. 병목은 API rate limit."
```

#### 실행 예시 (금융 파이프라인 T05+T06)

```
v1.1 원안:  T05 처리(30분) → T06 처리(30분) = 총 60분
v1.1.1:     T05 + T06 동시 스폰 = 총 ~30분 (2배 단축)
```

> **3자회의 결론 (2026-03-04)**: GPT 도입OK, Gemini 조건부OK.
> Brain 판단: inbox 파일 분리로 충돌 없음, CC는 API 호출이라 로컬 부담 미미.
> 3개 동시 실행으로 시작, 안정성 확인 후 확장.

### 3.6 🆕 워크플로우 복잡성 제한 (v1.1)

```yaml
complexity_rules:
  max_tasks_per_workflow: 10
    # 10개 초과 시 서브 워크플로우로 분리 필수
    
  max_depth: 5
    # DAG 최대 깊이 5단계 (T01→T02→T03→T04→T05 = 깊이 5)
    
  sub_workflow:
    # 복잡한 작업은 부모-자식 워크플로우로 분리
    # 부모 워크플로우의 한 태스크가 자식 워크플로우 트리거
    example:
      parent: "FIN-PIPE-001"
      task_T03_triggers: "BACKTEST-DETAIL-001"  # 서브 워크플로우
      parent_waits: true  # 서브 완료까지 부모 T03 대기
      
  naming:
    workflow_id: "WF-{YYYYMMDD}-{SEQ}"         # 일반
    sub_workflow_id: "WF-{YYYYMMDD}-{SEQ}-SUB{N}" # 서브
```

---

## 4. 에이전트 행동 규칙 (Collaboration Protocol)

### 4.1 수신 규칙

```yaml
on_message_received:
  1_validate:
    - msg_id 형식 검증
    - from 에이전트가 실존하는지 확인
    - 자기 expertise 범위인지 확인
  2_if_in_scope:
    - status를 "active"로 변경
    - 작업 수행
    - 결과를 task_response로 발신자(또는 dispatcher)에게 전송
  3_if_out_of_scope:
    - 올바른 에이전트를 판단
    - inbox/cmd-dispatcher.md에 "재라우팅 요청" 전송
  4_if_blocked:
    - 30분 경과 시 status_update (진행 상황 보고)
    - TTL 초과 시 escalation to dispatcher
    - 에스컬레이션 조건 충족 시 brain_report/ 에 직접 보고
```

### 4.2 에스컬레이션 매트릭스

```
레벨 0: 에이전트 자체 해결
         │ 실패 (+ 재시도 소진)
         ▼
레벨 1: 부서 내 Lead에 보고
         │ Lead도 해결 불가
         ▼
레벨 2: cmd-dispatcher에 타 부서 지원 요청
         │ 정책 판단 필요
         ▼
레벨 3: 🔴 Brain 직접 보고 (brain_report/)
```

즉시 Brain 보고 트리거 (레벨 3 직행):

| 부서 | 조건 |
|------|------|
| Finance | VIX 40+, 일일 -10%, P5 파산, MDD 로직 변경 |
| Engineering | 프로덕션 배포 실패, 보안 취약점 |
| Research | 3회 검색 후 핵심 정보 미발견 |
| Compute | 리소스 90%+, 60분 초과 연산 |
| Operations | 백업 실패, 인프라 다운 |

### 4.3 🆕 단일 Writer 원칙 (v1.1)

> **상태 불일치 방지를 위한 핵심 규칙:**
> 
> ```
> 규칙: 한 시점에 하나의 에이전트만 하나의 파일을 수정할 수 있다.
> ```
> 
> CC는 순차 실행이므로 이 규칙은 **구조적으로 보장됩니다:**
> 
> - CC가 Agent A의 태스크를 처리하는 동안 → Agent A만 파일 쓰기 가능
> - Agent A 완료 후 → Agent B 처리 시작
> - 동시에 두 에이전트가 같은 파일을 수정하는 상황은 발생하지 않음
> 
> **파일별 소유권 규칙:**
> 
> | 파일 | Writer | Reader |
> |------|--------|--------|
> | inbox/{agent}.md | Dispatcher 또는 다른 에이전트 | 해당 에이전트만 |
> | workflows/active/{id}.md | Dispatcher만 | 모든 에이전트 (읽기 전용) |
> | brain_report/{id}.md | Dispatcher만 | Brain만 |
> | deadletter/{msg_id}.md | Dispatcher만 | Brain (디버깅용) |
> 
> **inbox 파일 라이프사이클:**
> ```
> 1. 발신자가 inbox/{수신자}.md에 메시지 작성 (append)
> 2. 수신 에이전트가 읽고 처리
> 3. 처리 완료 → 해당 메시지를 outbox/로 이동 (inbox에서 제거)
> 4. inbox/{수신자}.md는 항상 "미처리 메시지만" 포함
> ```

---

## 5. 부서 간 협업 라우팅

### 5.1 라우팅 규칙

```yaml
cross_department_routes:
  - trigger: "res-architect 기술 평가 완료"
    route: "eng-foreman 구현 가능성 검토"
  - trigger: "fin-backtester 대규모 연산 필요"
    route: "cmp-compute-lead 리소스 할당"
  - trigger: "eng-engineer 배포 준비 완료"
    route: "ops-infra-manager 배포 환경 확인"
  - trigger: "res-web-scout 시장 뉴스 발견"
    route: "fin-market-scout 영향도 분석"
  - trigger: "life-integrator 라이프 변경 감지"
    route: "fin-fire-planner FIRE 재계산"
  - trigger: "car-strategist 신기술 학습 필요"
    route: "res-architect 기술 평가"
```

### 5.2 기존 시스템 통합

**to_hands/from_hands 호환:**
```
기존 유지:
  to_hands.md  → Brain ↔ Hands(CC) 직접 통신
  from_hands.md → CC → Brain 보고

확장 추가:
  MessageBus/inbox/  → 에이전트 간 자동 협업
  MessageBus/brain_report/ → 워크플로우 완료 보고
```

**Memory 연동:**
- Hot: active_context.md → Dispatcher 워크플로우 시작 시 참조
- Warm: 도메인 Rules.md → 해당 부서 에이전트 직접 참조
- Cold: completed/ 워크플로우 → 명시적 요청 시만
- conversation_memory: Memory Keeper가 완료 시 핵심 결과 기록

### 5.3 🆕 모니터링 구체화 (v1.1)

```yaml
monitoring:
  dashboard_polling:
    # parser.py가 주기적으로 파싱하는 대상
    sources:
      - "MessageBus/workflows/active/*.md"   # 활성 워크플로우 상태
      - "MessageBus/inbox/*.md"              # 에이전트별 대기 메시지 수
      - "MessageBus/deadletter/*.md"         # 실패 메시지
      
  dashboard_data_fields:
    active_workflows:
      - workflow_id
      - template_name
      - progress: "완료 태스크 / 전체 태스크"
      - current_task: "현재 실행 중인 태스크"
      - elapsed_time
      
    agent_status:
      - agent_id
      - status: "idle | active | blocked"
      - current_task: "처리 중인 msg_id (있으면)"
      - pending_count: "inbox 내 미처리 메시지 수"
      
    recent_completions:
      - "최근 완료된 워크플로우 5건"
      - "각각의 소요 시간, 성공/실패 여부, 플래그"
      
    alerts:
      - "deadletter에 새 메시지 존재 → 🔴 표시"
      - "TTL 80% 도달 태스크 → 🟡 표시"
      - "Brain 보고 대기 중 → 📋 표시"
```

---

## 6. Pre-built 워크플로우 5종

### 6.1 금융 파이프라인
```
Market Scout → Quant → Backtester → Portfolio Analyst
                                         ├→ Tax Optimizer (skip 가능)
                                         └→ FIRE Planner (skip 가능)
```

### 6.2 리서치→엔지니어링
```
Web Scout → Scout Lead → Architect → Foreman
                                       ├→ Engineer → Critic
                                       └→ GitOps → Infra Manager
```

### 6.3 프로젝트 부트스트랩
```
Architect → VaultKeeper → Foreman → Engineer → Critic → GitOps
```

### 6.4 시장 긴급 대응
```
Market Scout (🔴) → Brain Report (즉시)
                  → Portfolio Analyst + FIRE Planner + Quant (독립 디스패치)
                  → 통합 긴급 보고
```

### 6.5 라이프 통합
```
Life Integrator → FIRE Planner + Career Strategist + Health Coach + Tax Optimizer (독립 디스패치)
               → 종합 영향 보고
```

---

## 7. 구현 Phase

| Phase | 내용 | 담당 |
|-------|------|------|
| **1** | MessageBus 디렉토리 + 39개 inbox 생성 | VaultKeeper → CC |
| **2** | cmd-dispatcher v2.5 스펙 + workflow_engine.py | Brain → CC |
| **3** | 에이전트 스펙에 Collaboration Protocol 섹션 추가 | Brain |
| **4** | parser.py + dashboard 확장 (모니터링 §5.3 반영) | CC |

---

## 8. 설계 결정 요약

| 항목 | 결정 |
|------|------|
| 통신 방식 | Obsidian Vault 파일 기반 (MessageBus/) |
| 자동화 수준 | 풀 자동 (Brain은 결과만 수신) |
| 오케스트레이터 | cmd-dispatcher v2.5 |
| 메시지 포맷 | YAML front-matter + Markdown body |
| 워크플로우 정의 | DAG 기반 YAML 템플릿 (최대 10 태스크, 깊이 5) |
| 에스컬레이션 | 4단계 (자체→Lead→Dispatcher→Brain) |
| 오류 복구 | 🆕 retry_then_escalate / escalate / skip_with_warning |
| 병렬 실행 | 🆕 순차 처리 기반 독립 디스패치 (OS 동시 실행 아님) |
| 파일 무결성 | 🆕 단일 Writer 원칙 (CC 순차 실행으로 구조적 보장) |
| 모니터링 | 🆕 parser.py 폴링 → 대시보드 (활성WF/에이전트상태/알림) |
| 복잡성 제한 | 🆕 10 태스크/WF, 깊이 5, 초과 시 서브 워크플로우 |
| 하위 호환 | to_hands/from_hands 유지 |
| 구현 순서 | 구조→Dispatcher→스펙 보강→대시보드 |

---

## 부록: 3자회의 기록

### GPT-4o 리뷰 (2026-03-04)
- 강점: 모듈화, 워크플로우 자동화, 프로토콜 명확성
- 약점: DAG 복잡성, 에스컬레이션 지연, 파일 I/O 병목
- 누락: 모니터링, 보안, 장애 복구
- 판정: 재설계 필요 (→ Brain 판단: 과잉. 엔터프라이즈 제안 폐기)

### Gemini 2.5 Flash 리뷰 (2026-03-04)
- 강점: 프라이버시/비용, Obsidian 직관성, 구조화된 에스컬레이션
- 약점: 파일 I/O 병목, 확장성, 동시성 충돌
- 누락: 파일 잠금, 실시간 모니터링, 오류 복구
- 판정: 아이디어 OK, MessageBus 보강 필요 (→ Brain 판단: 동시성 우려는 순차 실행으로 해소)

### Brain 최종 판단 (1차)
- GPT 에스컬레이션 과잉 인프라 제안 폐기 (Kafka, Prometheus, TLS, OAuth 불필요)
- Gemini 동시성 우려 해소 (CC 순차 실행 = 구조적 단일 Writer)
- 양쪽 공통 피드백 5건 반영 → v1.1 확정

### 2차 리뷰 (v1.1 대상, 2026-03-04)
- GPT-4o: 5개 항목 전부 "충분", 새 문제 없음, **구현 착수 OK**
- Gemini 2.5 Flash: 6개 항목 전부 "충분", 새 지적 1건 — "순차 실행 보장의 외부 취약성"
- Brain 판단: 외부 간섭은 운영 레벨 문제이지 설계 레벨 문제 아님

### ⚠️ 운영 주의사항
- **워크플로우 실행 중 MessageBus/ 하위 파일을 수동 편집하지 말 것**
- Obsidian에서 inbox/*.md를 열어보는 것은 OK (읽기 전용), 직접 수정은 금지
- 수동 개입이 필요한 경우 brain_report/의 지시를 따를 것

### ✅ v1.1 최종 확정 — 구현 착수 승인 (2026-03-04)