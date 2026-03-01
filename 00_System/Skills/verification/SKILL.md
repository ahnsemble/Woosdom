---
name: verification-before-completion
description: >
  완료, done, 끝, 마무리, 최종, final, 검증, verify, 확인, 체크,
  PR, 커밋, commit, 배포, deploy, 릴리스, merge, 제출 관련 시 트리거.
  Hands가 "다 했습니다" 선언 전 반드시 거치는 검증 체크리스트.
---

# Verification Before Completion

## 핵심 원칙

1. **"Done" 선언은 검증 후에만.** 코드 작성 ≠ 완료. 작동 확인 = 완료.
2. **자기 작업을 자기가 검증.** Brain에 넘기기 전에 Hands가 먼저 확인.
3. **체크리스트 기반.** 기억에 의존하지 않음.

## 완료 전 필수 체크리스트

### Level 1: 기본 (모든 태스크)
```
□ 빌드 성공 (exit code 0)
□ 린트/포매팅 에러 없음
□ to_hands.md의 모든 서브태스크 검증 명령어 통과
□ 의도하지 않은 파일 변경 없음 (git diff --stat 확인)
□ console.log / print 디버그 코드 제거
```

### Level 2: 코드 변경 시
```
□ 기존 테스트 스위트 전체 pass (회귀 없음)
□ 새 기능에 대한 테스트 추가 (해당 시)
□ 에지 케이스 최소 1개 수동 테스트
□ 타입 에러 없음 (TypeScript 프로젝트)
□ import 경로 정확 (상대/절대 혼용 없음)
```

### Level 3: 아키텍처 변경 시
```
□ 영향받는 모듈 전체 동작 확인
□ 설정 파일 변경 시 → 전체 서버/앱 재시작 후 테스트
□ 마이그레이션 필요 시 → 마이그레이션 스크립트 실행 확인
□ README / CLAUDE.md 업데이트 (해당 시)
□ breaking change → from_hands.md에 명시
```

## from_hands.md 완료 보고 포맷

```markdown
# from_hands — [작업 제목]
*Completed: YYYY-MM-DD HH:MM*
*Engine: [CC/Codex/AG]*

## 결과
[1~2줄 요약]

## 서브태스크 결과
- T1: ✅ [검증 결과]
- T2: ✅ [검증 결과]
- T3: ✅ [검증 결과]

## 검증 체크리스트
- [x] 빌드 성공
- [x] 린트 에러 없음
- [x] 의도하지 않은 파일 변경 없음
- [x] 디버그 코드 제거

## 특이사항
[예상과 다른 점, Brain이 알아야 할 것]
```

## 주의 사항

| 상황 | 행동 |
|------|------|
| 서브태스크 1개라도 검증 실패 | ❌ Done 선언 금지. 수정 후 재검증 |
| "거의 다 됐는데 한 가지만..." | ❌ Done 선언 금지. 완전히 끝나야 Done |
| 테스트가 없는 프로젝트 | 수동 테스트라도 수행 + 결과 기록 |
| 검증 중 새 버그 발견 | from_hands.md에 기록 + Brain에 에스컬레이션 |

## CLAUDE.md 연동 (TDD 강제)

CC/Codex의 CLAUDE.md에 추가 권장:

```markdown
## 작업 규칙
- 새 기능: RED → GREEN → REFACTOR (TDD)
- "Done" 선언 전: verification SKILL 체크리스트 필수 통과
- from_hands.md 없이 "끝" 선언 금지
```

> ⚠️ 이 스킬은 Hands 엔진이 직접 참조하는 것이 아니라,
> Brain이 to_hands.md 작성 시 검증 기준으로 포함하고,
> from_hands.md 수신 시 체크리스트 대조에 사용합니다.
