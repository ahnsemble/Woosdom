# Woosdom 진화 전략 v1.0
*Created: 2026-02-28*
*Source: anthropics/skills (⭐69.3k) + obra/superpowers (⭐40.9k) 분석 기반*
*Status: Brain 초안 → 사용자 승인 대기*

---

## 요약

현재 우즈덤은 brain_directive.md 중심의 **모놀리식 프롬프트 아키텍처**. 
이를 anthropics/skills의 **SKILL.md 포맷** + obra/superpowers의 **워크플로우 스킬** 패턴으로 진화시킨다.

핵심 변화: "하나의 거대한 지시서" → "필요할 때 꺼내 쓰는 스킬 라이브러리"

---

## Phase E-1: 도메인 스킬화 (구조 변환)

**목표:** 기존 Warm/Module 파일을 SKILL.md 표준 포맷으로 변환
**난이도:** 낮음 | **효과:** 즉시 로딩 효율 개선
**실행:** CC

### 변환 대상

| 기존 파일 | → SKILL.md | 트리거 조건 |
|-----------|-----------|------------|
| `modules/finance_protocol.md` + `Rules.md` | `01_Domains/Finance/SKILL.md` | 투자, 포트폴리오, FIRE, DCA, 리밸런싱 |
| `modules/career_life_protocol.md` + `Career/MOC.md` | `01_Domains/Career/SKILL.md` | FDE, 커리어, 영앤리치, 이직 |
| `Health/training_protocol.md` + `Health/MOC.md` | `01_Domains/Health/SKILL.md` | 운동, Big 3, 복싱, 커팅, 수요일 |
| `modules/engine_router.md` | `00_System/Skills/engine-router/SKILL.md` | Hands 위임, 엔진 선택, 3자 회의 |

### SKILL.md 포맷 (anthropics/skills 표준)

```yaml
---
name: finance-advisor
description: >
  투자, 포트폴리오, FIRE, DCA, 리밸런싱, MDD 관련 질문 시 트리거.
  Trinity v5 규칙, 금융 헌법, 드리프트 점검 로직 포함.
  portfolio.json과 함께 로드.
---

# Finance Advisor

[기존 finance_protocol.md + Rules.md 내용 통합]
```

### brain_directive.md 변경

Memory Loading Protocol의 Module 행을 SKILL.md 참조로 교체:
```
| **Skill** | `01_Domains/*/SKILL.md` | description 매칭 시 | ~1,200 tok |
```

Brain은 대화 시작 시 각 SKILL.md의 `description`(YAML frontmatter)만 스캔하고, 매칭되는 스킬만 본문 로드.

---

## Phase E-2: 워크플로우 스킬 도입 (프로세스 강화)

**목표:** superpowers의 개발 워크플로우 스킬을 우즈덤 Hands 위임에 적용
**난이도:** 중간 | **효과:** CC/Codex 작업 품질 향상
**실행:** Brain 설계 → CC 적용

### 도입 대상

| superpowers 스킬 | 우즈덤 적용 | 위치 |
|-----------------|-----------|------|
| `brainstorming` | Brain 전략 분석에 소크라테스식 질문 강화 | brain_directive.md 추가 |
| `writing-plans` | to_hands.md를 2-5분 단위 태스크로 분할하는 포맷 | `00_System/Skills/writing-plans/SKILL.md` |
| `systematic-debugging` | CC/Codex 디버깅 시 4단계 근본원인 프로토콜 | `00_System/Skills/systematic-debugging/SKILL.md` |
| `test-driven-development` | CC CLAUDE.md에 RED→GREEN→REFACTOR 강제 | CLAUDE.md 추가 |
| `verification-before-completion` | "됐다고 선언 전 검증" 체크리스트 | `00_System/Skills/verification/SKILL.md` |
| `subagent-driven-development` | Agent Corps 서브에이전트 디스패치 + 2단계 리뷰 | agent_corps_spec.md 연동 |

### to_hands.md 포맷 개선 (superpowers 플랜 스타일)

현재:
```
task_prompt: "전체 내용을 통째로"
```

개선:
```
tasks:
  - id: 1
    description: "파일 X에서 Y 함수 수정"
    files: [src/x.ts]
    verification: "npm test — 테스트 3개 통과"
    estimated: 3min
  - id: 2
    description: "..."
```

---

## Phase E-3: 메타 스킬 (자기 진화)

**목표:** 우즈덤이 자기 스킬을 생성/개선하는 루프
**난이도:** 높음 | **효과:** 장기적 자율 진화
**실행:** Brain 설계 → CC 구현

### 구성

```
00_System/Skills/
└── meta-skill-writer/
    └── SKILL.md
```

**동작:**
1. 대화에서 반복 패턴 감지 (예: "매번 디버깅할 때 같은 삽질")
2. Brain이 스킬화 제안: "이 패턴을 스킬로 만들까요?"
3. 사용자 승인 → SKILL.md 자동 생성
4. 다음 대화부터 해당 스킬 자동 트리거

### Flowkater 자비스의 "새벽 크론 → 스킬 자동 보강"에 대응
- 우즈덤 버전: 대화 종료 시 Brain이 active_context에 "스킬화 후보" 태그
- 다음 대화 시작 시 후보 리뷰 → 스킬 생성

---

## 실행 순서 & 선행 조건

```
볼트 정리 (지금)
    ↓
Phase E-1: 도메인 스킬화 ← 볼트 깨끗한 상태에서 시작
    ↓
Phase E-2: 워크플로우 스킬 ← E-1 포맷 확립 후
    ↓  
Phase E-3: 메타 스킬 ← E-1 + E-2 안정화 후
```

### 예상 소요

| Phase | 작업량 | 추정 |
|-------|-------|------|
| E-1 | 파일 4개 변환 + brain_directive 수정 | 2-3시간 (CC) |
| E-2 | 스킬 5개 작성 + to_hands 포맷 개선 + CLAUDE.md 수정 | 4-5시간 (CC) |
| E-3 | 메타 스킬 설계 + 구현 + 테스트 | 3-4시간 (Brain + CC) |

**총 ~10-12시간**, Crossy 등 다른 프로젝트 틈새에 분산 가능.

---

## 참조

- [anthropics/skills](https://github.com/anthropics/skills) — SKILL.md 포맷 표준, description 기반 자동 트리거
- [obra/superpowers](https://github.com/obra/superpowers) — 워크플로우 스킬, TDD 강제, systematic-debugging
- Flowkater 자비스 — 크론 기반 자동 스킬 보강 (우즈덤은 대화 기반으로 변형)
