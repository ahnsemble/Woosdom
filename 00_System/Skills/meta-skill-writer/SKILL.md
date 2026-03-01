---
name: meta-skill-writer
description: >
  스킬 생성, 새 스킬, skill 추가, 패턴 반복, 자동화 후보,
  스킬화, skillify, 프로토콜 추가, 워크플로우 정의,
  brain_directive 수정, 스킬 라이브러리 관련 시 트리거.
  Woosdom의 자기 진화 루프 — 반복 패턴을 스킬로 결정화.
---

# Meta-Skill Writer — 자기 진화 프로토콜

## 핵심 원칙

1. **반복은 스킬의 신호.** 3회 이상 같은 패턴이 나타나면 스킬 후보.
2. **사용자 승인 필수.** Brain이 제안 → 사용자가 승인 → 생성.
3. **기존 스킬과 중복 금지.** 생성 전 현재 스킬 목록 대조.
4. **최소 유효 스킬.** 과도하게 크지 않게 — 한 스킬 = 한 역할.

## 스킬 후보 감지 (대화 중)

Brain이 대화 중 아래 패턴을 감지하면 **스킬 후보 태그**:

| 감지 패턴 | 예시 |
|----------|------|
| 같은 워크플로우 3회+ 반복 | "또 같은 방식으로 to_hands 쓰네" |
| 사용자가 매번 같은 규칙 언급 | "저번에도 말했지만 이건..." |
| 도메인 지식이 대화에만 존재 | 파일로 안 남아서 매번 다시 설명 |
| Brain이 매번 같은 판단 로직 적용 | "이건 항상 X 기준으로 판단하는데..." |
| 새 도메인/프로젝트가 규칙 축적 | Project Crossy 규칙이 3개 이상 |

## 대화 중 제안 포맷

```
💡 **스킬 후보 감지**
- 패턴: [반복된 패턴 설명]
- 제안 스킬명: [name]
- 트리거 키워드: [keyword1, keyword2, ...]
- 예상 토큰: ~N tok

스킬로 만들까요?
```

> 사용자가 "ㅇㅇ" / "가" / "만들어" → 즉시 생성.
> 사용자가 "아니" / "나중에" → active_context.md 후보란에 기록.

## 스킬 생성 프로토콜

### Step 1: 기존 스킬 충돌 검사
```
현재 스킬 목록 (brain_directive.md Skill 테이블)과 대조:
- 동일 트리거 키워드 50%+ 중복 → 기존 스킬 확장으로 전환
- 중복 없음 → 신규 생성 진행
```

### Step 2: SKILL.md 생성
```
위치: 도메인 스킬 → /01_Domains/[Domain]/SKILL.md
       워크플로우 스킬 → /00_System/Skills/[name]/SKILL.md
       프로젝트 스킬 → /02_Projects/[project]/SKILL.md

포맷: YAML frontmatter (name + description) + 본문
```

### Step 3: brain_directive.md 등록
```
1. Skill 테이블에 행 추가
2. Skill 경로 목록에 추가
3. active_context.md에 생성 기록
```

### Step 4: 검증
```
□ SKILL.md 파일 존재 확인
□ brain_directive.md 테이블에 등록 확인
□ description 키워드로 트리거 테스트 (해당 키워드 언급 → 스킬 로드 판단)
```

## active_context.md 스킬 후보 섹션

대화 종료 시 감지된 후보가 있으면 active_context.md에 기록:

```markdown
## 🌱 스킬 후보 (미승인)
- **[후보명]** — [패턴 설명] (감지일: YYYY-MM-DD)
```

다음 대화 시작 시 active_context 로드하면서 후보 목록 확인 → 적절한 시점에 재제안.

## 스킬 품질 기준

| 기준 | 최소 요구 |
|------|----------|
| description 키워드 | 5개 이상 (트리거 정확도) |
| 본문 길이 | 200~1500 tok (너무 짧으면 무의미, 너무 길면 로딩 비효율) |
| 검증 가능성 | Brain이 "이 스킬 로드해야 하나" 판단 가능 |
| 독립성 | 다른 스킬 없이도 단독 작동 |
| 실행 가능성 | 추상적 원칙만이 아닌 구체적 행동 지침 포함 |

## 스킬 라이프사이클

```
감지 → 제안 → 승인 → 생성 → 등록 → 사용
                                      ↓
                              3개월 미사용 → 비활성 제안
                                      ↓
                              사용자 승인 → 아카이브 이동
```

## Codex 호환 스킬 생성 (Agent Skills 표준)

meta-skill-writer가 새 스킬을 생성할 때, 아래 표준 구조를 따른다:

### 디렉토리 구조
```
skill-name/
├── SKILL.md          # 필수 — YAML frontmatter + 마크다운 본문
├── agents/           # 권장
│   └── openai.yaml   # display_name, short_description, default_prompt
├── scripts/          # 선택 — 결정론적 실행이 필요한 코드
├── references/       # 선택 — 컨텍스트에 필요시 로드할 문서
└── assets/           # 선택 — 템플릿, 아이콘 등 출력물에 사용할 파일
```

### openai.yaml 자동 생성 규칙
스킬 생성 시 `agents/openai.yaml`을 반드시 함께 생성:
- `display_name`: SKILL.md의 name을 사람이 읽기 좋은 형태로
- `short_description`: description에서 핵심만 추출 (1줄, 80자 이내)
- `default_prompt`: 이 스킬을 트리거하는 대표 프롬프트 예시 (1줄)

### 3-Tier 로딩 인지
1. **Metadata** (name + description) — 항상 컨텍스트에 로드 (~100 words)
2. **SKILL.md 본문** — 트리거 시에만 로드
3. **Bundled resources** — 필요 시에만 Codex가 접근

> description은 트리거 정확도의 핵심이므로 키워드 5개 이상 필수.
> SKILL.md 본문은 500줄 이하 유지 (컨텍스트 효율).

### brain_directive.md 등록 시 추가 행동
기존 Step 3 (brain_directive.md 등록)에 추가:
- agents/openai.yaml 파일 존재 확인
- display_name이 기존 스킬과 중복되지 않는지 확인

## 금지 사항

| 금지 | 이유 |
|------|------|
| 사용자 승인 없이 스킬 생성 | 볼트는 사용자 소유 |
| 기존 스킬과 90%+ 중복 생성 | 스킬 스프롤 방지 |
| 1000 tok 초과 description | YAML frontmatter 비대화 |
| 프로젝트 종료 후 프로젝트 스킬 잔류 | 정기 정리 필요 |
