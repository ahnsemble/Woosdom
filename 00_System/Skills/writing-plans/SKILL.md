---
name: writing-plans
description: >
  to_claude_code, to_codex, to_antigravity 작성, 태스크 분해, 위임 계획, 서브태스크, 실행 계획,
  플랜, plan, delegate, 작업 분할, 검증 기준 관련 시 트리거.
  Brain이 Hands에 위임할 때 엔진별 전용 파일에 구조화된 계획을 작성하는 스킬.
---

# Writing Plans — 구조화된 Hands 위임 포맷

## 핵심 원칙 (superpowers 기반)

1. **하나의 blob 금지.** 모든 위임은 2~7개 서브태스크로 분해.
2. **각 서브태스크는 독립 검증 가능.** "이것만 하고 확인" 단위.
3. **파일 경로 명시.** Hands가 추측하지 않도록.
4. **예상 시간 명시.** 2~5분 단위. 15분 초과 태스크는 분할.
5. **완료 기준은 실행 가능한 명령어로.** "확인해라" 금지 → "npm test — 3 pass" OK.

## 엔진별 전용 파일 포맷 (v3)

**파일 매핑:**
- CC → `to_claude_code.md` / `from_claude_code.md`
- Codex → `to_codex.md` / `from_codex.md`
- AG → `to_antigravity.md` / `from_antigravity.md`

```markdown
# to_[engine] — [작업 제목]
*Created: YYYY-MM-DD*
*Status: pending*
*Engine: [CC/Codex/AG] (Hands-N)*

## 목표
[1~2줄 — 이 태스크가 완료되면 무엇이 달라지는가]

## 사전 조건
- [ ] [필요한 선행 상태 — 파일 존재, 서버 실행 등]

## 태스크

### T1: [서브태스크 제목]
- **파일:** `path/to/file.ts`
- **작업:** [구체적 수정/생성 내용]
- **검증:** `[실행 가능한 확인 명령어]`
- **예상:** ~3min

### T2: [서브태스크 제목]
- **파일:** `path/to/another.ts`
- **작업:** [구체적 수정/생성 내용]
- **검증:** `[실행 가능한 확인 명령어]`
- **예상:** ~2min

### T3: 최종 통합 검증
- **검증:** `[전체 동작 확인 명령어]`
- **예상:** ~2min

## 완료 시 행동
- [ ] from_[engine].md에 결과 기록 (CC→from_claude_code / Codex→from_codex / AG→from_antigravity)
- [ ] [추가 행동 — git commit, active_context 업데이트 등]

## brain_followup
[Brain이 결과 수신 후 할 판단/행동]
```

## 서브태스크 분해 가이드

| 작업 크기 | 서브태스크 수 | 예시 |
|----------|------------|------|
| 단순 (파일 1개, 수정 1곳) | 2개 (수정 + 검증) | 오타 수정, 설정 변경 |
| 중간 (파일 2~4개) | 3~5개 | 기능 추가, 리팩토링 |
| 대형 (파일 5개+, 아키텍처 변경) | 5~7개 | 모듈 재설계, 마이그레이션 |

> ⚠️ 7개 초과 시 → 2개 to_hands로 분리.
> ⚠️ 15분 초과 서브태스크 → 더 작게 분할.

## 검증 명령어 패턴

| 유형 | 검증 명령어 예시 |
|------|----------------|
| 코드 빌드 | `npm run build — exit 0` |
| 테스트 | `npm test — N tests pass` |
| 파일 존재 | `ls -la path/to/file — exists` |
| 서버 동작 | `curl localhost:PORT/health — 200 OK` |
| 린트 | `npm run lint — 0 errors` |
| 스크립트 실행 | `python script.py — output contains "PASS"` |
| 파일 내용 | `grep "keyword" file — found` |

## delegate_to_engine MCP 연동

Brain이 `delegate_to_engine` MCP 도구 사용 시:
- `task_title`: 한 줄 요약
- `task_prompt`: **이 포맷 전체를 task_prompt에 넣기**
- `recommended_engine`: 엔진 선택 (engine-router SKILL 참조)
- `reason`: 엔진 선택 이유
- `brain_followup`: 결과 수신 후 Brain 행동

> ⚠️ `delegate_to_engine` MCP는 현재 to_hands.md에 저장하는 레거시 코드.
> CC로 엔진별 파일 라우팅 패치 필요 (recommended_engine 값에 따라 to_codex/to_claude_code/to_antigravity 분기).

## Bad vs Good 예시

**❌ Bad (v1 — blob):**
```
SKILL.md로 이전 완료된 구 모듈 파일 3개를 /Dev/trash/로 이동하고
modules/ 폴더에 changelog.md만 남았는지 확인하고 SKILL.md 4개
존재도 확인해주세요.
```

**✅ Good (v2 — 구조화):**
```
### T1: 구 모듈 3개 이동
- **파일:** modules/finance_protocol.md, engine_router.md, career_life_protocol.md
- **작업:** 3개 파일을 /Dev/trash/로 mv
- **검증:** `ls /Dev/trash/{finance_protocol,engine_router,career_life_protocol}.md`
- **예상:** ~1min

### T2: modules/ 폴더 잔여 확인
- **검증:** `ls modules/ — changelog.md만 존재`
- **예상:** ~1min

### T3: SKILL.md 4개 존재 확인
- **검증:** `ls 01_Domains/*/SKILL.md 00_System/Skills/*/SKILL.md — 4개`
- **예상:** ~1min
```
