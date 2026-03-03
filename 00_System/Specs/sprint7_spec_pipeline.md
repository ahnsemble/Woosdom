# Sprint 7: Spec Pipeline — 설계 확정

## 상태: 설계 완료, 구현 대기
## 확정일: 2026-03-02
## 검증: 3자회의 (Brain + GPT + Gemini) 합의

---

## 문제 정의

현재 Brain이 to_claude_code.md에 작업을 쓸 때, 역할/규칙/금지사항/에스컬레이션을 **매번 수동으로** 작성해야 한다. 39개 에이전트 스펙이 `/00_System/Specs/agents/`에 존재하지만 문서로만 존재하고 실행에 활용되지 않음.

## 목표 상태

```
Brain: "@eng-foreman task_bridge에 에러 핸들링 추가해"
  → task_bridge가 eng-foreman.md 스펙 자동 로드
  → CC 시스템 프롬프트에 Foreman의 Identity/Rules/Thinking 주입
  → CC가 Foreman처럼 사고하고, 규칙 준수하고, 실패 시 에스컬레이션
```

---

## Phase 1 — Single Agent MVP (이번 Sprint)

### 동작 흐름

```
1. Brain → to_claude_code.md: "@eng-foreman task_bridge에 에러 핸들링 추가해"
2. task_bridge.py 감지 → @agent-id 파싱
3. /00_System/Specs/agents/eng-foreman.md 읽기
4. 코어 섹션 추출 (티어별 차등)
5. 스펙 + 작업을 합쳐서 to_claude_code.md 덮어쓰기
6. CC 실행 (스펙이 시스템 컨텍스트로 주입된 상태)
7. 결과 → from_claude_code.md → 기존 플로우
```

### 핵심 구현 사항

| 항목 | 결정 |
|------|------|
| 주입 위치 | task_bridge.py에서 파싱 + 프리펜드 |
| 파싱 방법 | `## N.` 헤더 기반 섹션 추출 (정규식 최소화) |
| 주입 범위 — T1 | 풀 스펙 (~300줄) |
| 주입 범위 — T2/T3 | Identity + Rules + Thinking (~100줄) |
| fallback | 스펙 파일 없으면 기존 동작(스펙 없이 실행) + TG 경고 |
| 디버깅 | 주입된 최종 프롬프트 `Logs/spec_injection.log`에 기록 |
| 하위 호환 | @없는 기존 작업 → 변경 없이 기존대로 실행 |
| 작업량 | task_bridge.py ~60줄 추가 + 테스트 |

### 의사코드

```python
import re, os

SPEC_DIR = "00_System/Specs/agents"
T1_AGENTS = {"cmd-orchestrator", "eng-foreman", "res-scout-lead",
             "cmp-compute-lead", "fin-portfolio-analyst",
             "life-integrator", "car-strategist"}

def extract_sections(spec_text, sections):
    """## N. 헤더 기반 섹션 추출"""
    result = []
    for section in sections:
        pattern = rf'(## \d+\. {section}.*?)(?=## \d+\.|$)'
        match = re.search(pattern, spec_text, re.DOTALL)
        if match:
            result.append(match.group(1).strip())
    return "\n\n".join(result)

def inject_agent_spec(task_content):
    match = re.match(r'@([\w-]+)\s+(.*)', task_content, re.DOTALL)
    if not match:
        return task_content  # @없으면 기존 동작

    agent_id = match.group(1)
    task = match.group(2)
    spec_path = os.path.join(SPEC_DIR, f"{agent_id}.md")

    if not os.path.exists(spec_path):
        log_warning(f"스펙 파일 없음: {agent_id}")
        send_tg(f"⚠️ 스펙 파일 없음: {agent_id}. 스펙 없이 실행.")
        return task_content.lstrip('@').split(' ', 1)[1]  # @제거 후 기존 실행

    spec_text = read_file(spec_path)

    if agent_id in T1_AGENTS:
        injected = spec_text  # T1: 풀 스펙
    else:
        injected = extract_sections(spec_text, ["Identity", "Rules", "Thinking Framework"])

    final = f"## Agent Role: {agent_id}\n{injected}\n\n---\n\n## Task\n{task}"
    log_injection(agent_id, final)  # spec_injection.log
    return final
```

### 테스트 시나리오

1. **정상:** `@eng-foreman 작업` → 스펙 주입 확인, CC 실행 정상
2. **오타:** `@eng-forman 작업` → fallback 동작 + TG 경고
3. **@없음:** `그냥 작업` → 기존 동작 유지
4. **T1 vs T2:** `@eng-foreman` vs `@eng-engineer` → 풀 vs 코어 주입 확인
5. **로그:** spec_injection.log에 주입 내용 기록 확인

---

## Phase 2 — Agent Chaining (Sprint 8, 추후)

- Delegation Map 기반 자동 위임 체인
- Foreman → Engineer → Critic 파이프라인
- multi-step task_bridge 지원 필요
- Phase 1 안정화 후 착수

---

## 3자회의 리스크 검토 결과

| # | 리스크 | 심각도 | 대응 |
|---|--------|--------|------|
| 1 | 마크다운 파싱 취약성 | 🔴 | `## N.` 헤더 기반 안정 파싱 |
| 2 | 컨텍스트 윈도우 초과 | 🟡 | 티어별 차등 (T1 풀, T2/T3 코어) |
| 3 | 스펙 파일 누락/오타 | 🟡 | fallback + TG 경고 |
| 4 | 디버깅 복잡도 | 🟡 | spec_injection.log 기록 |
| 5 | 레이스 컨디션 | 🟢 | 무시 (스펙 변경 빈도 극저) |

### 기각된 제안
- **YAML 전환 (Gemini):** 39개 재작성 비용 > 이득. Obsidian 호환성 유지.
- **스펙 캐싱 (GPT):** 39파일 디스크 I/O <1ms. 100+ 시점에 재검토.

---

## CC 위임 시 프롬프트 (복사용)

```
@eng-foreman Sprint 7 Phase 1 구현.

참조: /00_System/Specs/sprint7_spec_pipeline.md

작업:
1. task_bridge.py에 inject_agent_spec() 함수 추가
2. 기존 디스패치 플로우에서 to_[engine].md 쓰기 직전에 inject_agent_spec() 호출
3. T1_AGENTS 리스트: cmd-orchestrator, eng-foreman, res-scout-lead, cmp-compute-lead, fin-portfolio-analyst, life-integrator, car-strategist
4. spec_injection.log 로깅 추가
5. fallback: 스펙 파일 없으면 기존 동작 + TG 경고
6. pytest 테스트 5개 (정상/오타/무@/T1vsT2/로그)

제약:
- 기존 task_bridge.py 동작 깨뜨리지 말 것
- @없는 기존 작업은 100% 하위 호환
```