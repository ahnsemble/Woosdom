# Sprint 8: Agent Chaining — 설계 확정

## 상태: 설계 완료, 구현 대기
## 확정일: 2026-03-02
## 검증: 3자회의 (Brain + GPT-5.2 + Gemini 2.5 Pro) 합의 → 수정 후 진행

---

## 문제 정의

Sprint 7에서 `@agent-id`로 에이전트 페르소나를 주입하는 기능이 완성됐지만, 에이전트 스펙의 Delegation Map(예: Foreman→Engineer→Critic)이 문서로만 존재하고 실행 메커니즘이 없다. Foreman이 "이건 Engineer 작업"이라고 판단해도 실제 위임할 방법이 없음.

## 목표 상태

```
Brain: "@eng-foreman task_bridge에 에러 핸들링 추가해"
  → CC(Foreman): 판단 후 구조화된 위임 블록 출력
    → task_bridge 감지 → Delegation Map 검증 → Engineer 스펙 주입 → CC 재실행
      → Engineer 완료 → 결과 반환 (또는 추가 위임)
```

---

## Phase 1 — Chaining MVP (이번 Sprint)

### 핵심 설계 결정

| 항목 | 결정 | 이유 |
|------|------|------|
| 위임 신호 | 구조화된 YAML 블록 (`---woosdom-delegation---`) | 3자회의: 텍스트 마커 오탐 방지, 파싱 안정성 |
| 체인 메타데이터 | chain_id, depth, visited[], origin_task | GPT 제안 채택: visited 배열이 동일 에이전트 차단보다 강력 |
| 감지 위치 | Auto-Brain callback에서 from_ 읽을 때 | 기존 플로우 재활용 |
| 체인 깊이 | 최대 3 (기존 MAX_CHAIN_DEPTH) | 이미 brain_callback에 설정됨 |
| 컨텍스트 전달 | 이전 결과 최대 2000자 슬라이스 | Phase 2에서 요약 방식 검토 |
| 권한 검증 | Delegation Map + visited 배열 | 무권한 위임 + 순환 루프 모두 차단 |
| 실패 정책 | fail closed: 파싱/검증 실패 → 체인 중단 + TG 경고 | Gemini/GPT 공통 제안 |

### 구조화된 위임 블록 포맷

에이전트가 위임이 필요하다고 판단하면 from_ 결과에 다음 블록 출력:

```yaml
---woosdom-delegation---
delegate_to: eng-engineer
task: "task_bridge.py에 에러 핸들링 추가. try-except 블록으로 각 함수 래핑."
reason: "코드 수정 작업이므로 Engineer에게 위임"
---end-delegation---
```

**파싱 규칙:**
- `---woosdom-delegation---` ~ `---end-delegation---` 사이만 파싱
- 코드블록(```) 내부의 블록은 무시 (오탐 방지)
- 블록이 없으면 위임 없음 (기존 동작)
- 블록이 2개 이상이면 첫 번째만 사용 + TG 경고

### 체인 메타데이터

```yaml
# to_ 파일 frontmatter에 포함
---
chain_id: "uuid-abc123"
chain_depth: 1
chain_visited: ["eng-foreman"]
chain_origin: "task_bridge에 에러 핸들링 추가해"
---
```

각 체인 단계에서:
- `chain_depth += 1`
- `chain_visited.append(current_agent)`
- `chain_depth >= 3` → 강제 종료 + TG 에스컬레이션
- `delegate_to in chain_visited` → 순환 감지 → 체인 중단 + TG 경고

### 동작 흐름

```
Phase A — 위임 블록 감지:
1. Brain → to_claude_code.md: "@eng-foreman 작업 내용"
2. task_bridge: inject_agent_spec() → Foreman 스펙 주입 → CC 실행
3. CC(Foreman): 판단 후 from_claude_code.md에 결과 + 위임 블록 출력
4. Auto-Brain callback → from_ 읽기

Phase B — 체인 검증:
5. parse_delegation_block(): 구조화된 블록 추출 (코드블록 내 제외)
6. validate_delegation():
   a. Foreman 스펙의 Delegation Map에 target이 있는지
   b. target이 chain_visited에 없는지 (순환 방지)
   c. chain_depth < MAX_CHAIN_DEPTH
7. 검증 실패 → 체인 중단 + TG 경고 + chain_execution.log 기록

Phase C — 체인 실행:
8. chain_dispatch():
   a. 이전 결과 컨텍스트 (최대 2000자)
   b. 체인 메타데이터 업데이트
   c. target 에이전트 스펙 주입 (inject_agent_spec 재활용)
   d. to_claude_code.md 작성
9. 기존 폴링 루프가 감지 → CC 재실행

Phase D — 체인 종료:
10. 위임 블록 없음 → 체인 종료 → 기존 Auto-Brain 플로우 (DONE/ESCALATE)
11. chain_depth >= 3 → 강제 종료 + Brain 에스컬레이션
```

### 실패 정책

| 실패 유형 | 동작 |
|----------|------|
| CC 실행 실패 | 체인 즉시 중단 + TG 보고 (부분 산출물 포함) |
| 위임 블록 파싱 실패 | fail closed (위임 없음으로 처리) + TG 경고 |
| Delegation Map에 없는 target | 위임 거부 + TG 경고 + 기존 결과만 반환 |
| target 스펙 파일 없음 | 체인 중단 + fallback (Sprint 7 패턴) |
| 순환 감지 (visited) | 체인 중단 + TG 경고 |
| 깊이 초과 | 강제 종료 + Brain 에스컬레이션 |

### 핵심 구현 사항

| # | 작업 | 위치 | 규모 |
|---|------|------|------|
| C1 | `parse_delegation_block()` — 구조화 블록 파싱, 코드블록 내 제외 | task_bridge.py | ~35줄 |
| C2 | `validate_delegation()` — Delegation Map YAML 파싱 + visited 검증 | task_bridge.py | ~45줄 |
| C3 | `chain_dispatch()` — 메타데이터 갱신 + 컨텍스트 + 스펙 합성 → to_ 작성 | task_bridge.py | ~40줄 |
| C4 | Auto-Brain callback 연결 — from_ 읽은 후 위임 블록 감지 → 체인 실행 | brain_callback.py | ~25줄 |
| C5 | `chain_execution.log` — chain_id, depth, agent, status 기록 | task_bridge.py | ~15줄 |
| C6 | 에이전트 스펙 위임 출력 안내 — T1 에이전트 7개 스펙에 위임 블록 포맷 추가 | agents/*.md | 스펙 수정 |
| C7 | pytest 7개 | test_chain.py | ~140줄 |

### 의사코드

```python
import re, os, uuid, yaml

DELEGATION_BLOCK_PATTERN = re.compile(
    r'---woosdom-delegation---\s*\n(.*?)\n---end-delegation---',
    re.DOTALL
)
CODE_BLOCK_PATTERN = re.compile(r'```.*?```', re.DOTALL)

def parse_delegation_block(from_content: str) -> dict | None:
    """from_ 결과에서 구조화된 위임 블록 추출. 코드블록 내 제외."""
    # 코드블록 제거 후 파싱
    cleaned = CODE_BLOCK_PATTERN.sub('', from_content)
    matches = DELEGATION_BLOCK_PATTERN.findall(cleaned)
    if not matches:
        return None
    if len(matches) > 1:
        send_tg("⚠️ 위임 블록 2개 이상 감지. 첫 번째만 사용.")
    try:
        block = yaml.safe_load(matches[0])
        if "delegate_to" in block and "task" in block:
            return block
    except yaml.YAMLError:
        log_chain("PARSE_FAIL", "YAML 파싱 실패")
        send_tg("⚠️ 위임 블록 YAML 파싱 실패. 위임 무시.")
    return None

def validate_delegation(source_agent: str, target_agent: str,
                        chain_meta: dict) -> tuple[bool, str]:
    """Delegation Map + visited + depth 검증."""
    # 깊이 검사
    if chain_meta["depth"] >= MAX_CHAIN_DEPTH:
        return False, f"체인 깊이 초과 ({chain_meta['depth']})"
    # 순환 검사
    if target_agent in chain_meta["visited"]:
        return False, f"순환 감지: {target_agent} already in {chain_meta['visited']}"
    # Delegation Map 검사
    spec = read_agent_spec(source_agent)
    delegation_map = parse_delegation_map_yaml(spec)
    allowed = [d["agent"] for d in delegation_map.get("delegates_to", [])]
    if target_agent not in allowed:
        return False, f"{source_agent}→{target_agent} 위임 권한 없음"
    return True, "OK"

def chain_dispatch(target_agent: str, task: str, prev_result: str,
                   chain_meta: dict):
    """체인 다음 단계 디스패치."""
    chain_meta["depth"] += 1
    chain_meta["visited"].append(target_agent)
    context = prev_result[:2000]
    content = (
        f"---\nchain_id: {chain_meta['chain_id']}\n"
        f"chain_depth: {chain_meta['depth']}\n"
        f"chain_visited: {chain_meta['visited']}\n"
        f"chain_origin: {chain_meta['origin']}\n---\n\n"
        f"@{target_agent} [체인 #{chain_meta['depth']}]\n\n"
        f"## 이전 단계 결과\n{context}\n\n## 작업\n{task}"
    )
    # inject_agent_spec() 재활용 → to_claude_code.md 작성
    injected = inject_agent_spec(content)
    write_to_file("claude_code", injected)
    log_chain(chain_meta, "DISPATCH", target_agent)
```

### 에이전트 스펙 수정 (T1 7개)

각 T1 에이전트 스펙의 Rules 섹션에 추가:

```markdown
### 위임 출력 포맷
다른 에이전트에게 위임이 필요하다고 판단하면, 결과 출력 마지막에 다음 블록을 포함:

\```
---woosdom-delegation---
delegate_to: [agent-id]
task: "[위임할 작업 내용]"
reason: "[위임 이유]"
---end-delegation---
\```

위임이 필요 없으면 이 블록을 포함하지 않는다.
```

### 테스트 시나리오

1. **정상 체인:** Foreman → Engineer 위임 블록 → 검증 통과 → Engineer 스펙 주입 확인
2. **깊이 초과:** depth=3에서 위임 시도 → 강제 종료 확인
3. **순환 감지:** visited에 이미 있는 agent로 위임 → 차단 확인
4. **무권한 위임:** Delegation Map에 없는 agent → 거부 확인
5. **오탐 방지:** 코드블록 내 위임 블록 → 무시 확인
6. **실패 중단:** YAML 파싱 실패 → fail closed 확인
7. **로그 검증:** chain_execution.log에 chain_id, depth, agent 기록 확인

---

## Phase 2 — 고도화 (Sprint 9+, 추후)

- 컨텍스트 전달: raw 슬라이스 → 요약+핵심 아티팩트 방식
- 멀티 엔진 체인: CC → Codex → CC (엔진 간 체이닝)
- 조건부 분기: 결과에 따른 동적 위임 경로
- idempotency 키 (중복 실행 방지, 필요 시)

---

## 3자회의 리스크 검토 결과

| # | 리스크 | 심각도 | 대응 | 출처 |
|---|--------|--------|------|------|
| 1 | 텍스트 마커 오탐 | 🔴 | 구조화 블록 + 코드블록 제외 파싱 | GPT+Gemini |
| 2 | 순환 루프 | 🔴 | visited 배열 + depth cap 3 | GPT |
| 3 | YAML 파싱 실패 | 🟡 | fail closed + TG 경고 | GPT+Gemini |
| 4 | 체인 중간 실패 | 🟡 | 즉시 중단 + 부분 산출물 보존 | Gemini |
| 5 | 컨텍스트 손실 | 🟡 | 2000자 cap (Phase 2에서 개선) | GPT |
| 6 | 파일 I/O 성능 | 🟢 | 무시 (최대 3단계) | Gemini |

### 채택/기각 목록

| 제안 | 출처 | 판정 | 이유 |
|------|------|------|------|
| 구조화 출력 블록 | GPT+Gemini | ✅ 채택 | 파싱 안정성 핵심 |
| 체인 메타데이터 (chain_id, visited) | GPT | ✅ 채택 | 순환/추적 강화 |
| 코드블록 내 오탐 방지 | GPT | ✅ 채택 | 방어적 파싱 |
| YAML fail closed | GPT+Gemini | ✅ 채택 | 안전 우선 |
| 중앙 라우터 재설계 | Gemini | ❌ 기각 | task_bridge가 이미 라우터. 과설계 |
| idempotency 키 | GPT | 🟡 보류 | 기존 hash 방지 존재. 문제 시 추가 |
| 요약+아티팩트 컨텍스트 | GPT | 🟡 Phase 2 | 현재 2000자로 충분 |
| 파일 I/O 성능 개선 | Gemini | ❌ 무시 | 최대 3단계, <1ms |

---

## CC 위임 시 프롬프트 (복사용)

```
@eng-foreman Sprint 8 Phase 1 구현: Agent Chaining.

참조: /00_System/Specs/sprint8_agent_chaining.md

작업:
1. task_bridge.py에 parse_delegation_block() 함수 추가
   - ---woosdom-delegation--- ~ ---end-delegation--- 블록 파싱
   - 코드블록(```) 내부 제외
   - YAML safe_load, 실패 시 None 반환 + TG 경고
2. task_bridge.py에 validate_delegation() 함수 추가
   - 소스 에이전트 스펙에서 Delegation Map(## 7. Delegation Map) YAML 파싱
   - delegates_to 목록에 target 있는지 확인
   - chain_visited에 target 있으면 순환 거부
   - chain_depth >= 3이면 깊이 초과 거부
3. task_bridge.py에 chain_dispatch() 함수 추가
   - chain_meta 업데이트 (depth+1, visited append)
   - 이전 결과 2000자 컨텍스트 + 새 작업 합성
   - inject_agent_spec() 재활용하여 to_claude_code.md 작성
4. brain_callback.py에서 from_ 읽은 후 parse_delegation_block() 호출
   - 위임 블록 감지 시 validate → chain_dispatch 실행
   - 위임 없으면 기존 DONE/CHAIN/ESCALATE 플로우 유지
5. chain_execution.log 로깅 (chain_id, depth, agent, status)
6. T1 에이전트 스펙 7개(cmd-orchestrator, eng-foreman, res-scout-lead, cmp-compute-lead, fin-portfolio-analyst, life-integrator, car-strategist)의 Rules 섹션에 위임 출력 포맷 안내 추가
7. pytest 7개 (test_agent_chaining.py):
   - 정상 체인 (위임 블록 파싱 + 검증 통과)
   - 깊이 초과 (depth=3에서 거부)
   - 순환 감지 (visited에 있는 agent 거부)
   - 무권한 위임 (Delegation Map에 없는 agent 거부)
   - 오탐 방지 (코드블록 내 위임 블록 무시)
   - 실패 중단 (YAML 파싱 실패 → fail closed)
   - 로그 검증 (chain_execution.log 기록 확인)

제약:
- 기존 task_bridge.py / brain_callback.py 동작 깨뜨리지 말 것
- @없는 기존 작업, @agent 스펙 주입(Sprint 7) 100% 하위 호환
- PyYAML import 추가 (이미 설치되어 있을 것, 없으면 pip install)
```
