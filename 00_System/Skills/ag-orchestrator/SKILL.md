---
name: ag-orchestrator
description: >
  AG(Antigravity)에서 39개 에이전트를 오케스트레이션하는 마스터 스킬.
  Brain이 to_antigravity.md에 주제+판단기준만 작성하면,
  AG가 적절한 에이전트를 선발 → GPT/Gemini로 페르소나 실행 → 결과 종합 → from_antigravity.md 저장.
  트리거: Brain이 to_antigravity.md를 작성하고 AG에게 실행 요청 시.
---

# AG Master Orchestrator — 39 Agent System

## 역할

Brain의 지시를 받아 39개 에이전트를 적재적소에 배치하고,
GPT / Gemini API를 통해 각 에이전트 페르소나로 작업을 수행한다.
실행이 필요한 작업은 `delegate_to_engine`으로 CC에 위임한다.
모든 결과를 종합해 `from_antigravity.md`에 저장한다.

---

## 에이전트 명부 (39개)

### Command Division (지휘)
| ID | 역할 | 엔진 |
|----|------|------|
| cmd-orchestrator | 복합 작업 분해·DAG·의존성 분석 | Brain직접 |
| cmd-dispatcher | 단일 작업 라우팅·파일 디스패치 | Brain직접 |
| cmd-memory-keeper | 볼트 기억 관리·세션 기록 | Brain직접 |
| cmd-auditor | 시스템 감사·이상 탐지 | Brain직접 |

### Engineering Division (개발)
| ID | 역할 | 엔진 |
|----|------|------|
| eng-foreman | 엔지니어링 팀 리드·작업 분배 | CC |
| eng-engineer | 코드 작성·수정·구현 | CC |
| eng-critic | 코드 리뷰·품질 검증 | CC |
| eng-debugger | 버그 분석·수정 | CC |
| eng-gitops | Git·브랜치·배포 관리 | CC |
| eng-vault-keeper | Obsidian 볼트 구조 관리 | CC |

### Compute Division (연산)
| ID | 역할 | 엔진 |
|----|------|------|
| cmp-compute-lead | 연산 팀 리드·Codex 조율 | Codex |
| cmp-data-wrangler | 데이터 전처리·정제 | Codex |
| cmp-parallel-coordinator | 병렬 연산 조율 | Codex |
| cmp-sandbox-runner | 격리 실행·테스트 | Codex |

### Finance Division (재무)
| ID | 역할 | 엔진 |
|----|------|------|
| fin-portfolio-analyst | 자산배분·드리프트·리밸런싱 분석 | GPT/Gemini |
| fin-quant | 수치 연산·통계·백테스트 설계 | Codex |
| fin-backtester | 백테스트·Monte Carlo 실행 | Codex |
| fin-market-scout | 실시간 시세·매크로·뉴스 수집 | Gemini(search) |
| fin-fire-planner | FIRE 시뮬레이션·인출 전략 | GPT |
| fin-tax-optimizer | 세금 효율·TLH 분석 | GPT |

### Research Division (리서치)
| ID | 역할 | 엔진 |
|----|------|------|
| res-scout-lead | 리서치 팀 리드 | Gemini |
| res-web-scout | 웹 검색·URL 수집 | Gemini(search) |
| res-deep-researcher | 심층 분석·종합 리포트 | GPT/Gemini |
| res-architect | 시스템 설계·아키텍처 분석 | GPT |
| res-experimenter | 가설 설계·A/B 실험 | GPT |

### Creative Division (창작)
| ID | 역할 | 엔진 |
|----|------|------|
| cre-content-strategist | 콘텐츠 전략·기획 | GPT |
| cre-writer | 글쓰기·문서 작성 | GPT |
| cre-designer | 디자인·UX 기획 | Gemini |
| cre-prompt-engineer | 프롬프트 설계·최적화 | GPT |

### Career Division (커리어)
| ID | 역할 | 엔진 |
|----|------|------|
| car-strategist | 커리어 전략·로드맵 | GPT |
| car-skill-tracker | 스킬 갭 분석·학습 계획 | GPT |
| car-network-builder | 네트워크 전략·인맥 관리 | GPT |

### Life Division (라이프)
| ID | 역할 | 엔진 |
|----|------|------|
| life-integrator | 헥사고날 라이프 통합 조율 | GPT |
| life-health-coach | 운동·체력·복싱·다이어트 | GPT |
| life-relationship-advisor | 관계·가정·커뮤니케이션 | GPT |

### Ops Division (운영)
| ID | 역할 | 엔진 |
|----|------|------|
| ops-infra-manager | 인프라·서버·환경 관리 | CC |
| ops-scheduler | 일정·자동화·크론 관리 | CC |
| ops-health-monitor | 시스템 헬스·모니터링 | CC |
| ops-backup-guard | 백업·복구·데이터 보호 | CC |

---

## 오케스트레이션 프로토콜

### Step 1 — 지시서 파싱

`to_antigravity.md`에서 다음 항목 추출:
```
- 주제 (topic)
- 목적 (objective)
- 필요 에이전트 (agents) — Brain이 지정하거나, 미지정 시 AG가 선발
- 판단 기준 (criteria)
- 출력 형식 (output_format)
- 제약 (constraints)
```

### Step 2 — 에이전트 선발

Brain이 에이전트를 지정하지 않은 경우, 주제 키워드로 선발:

| 키워드 | 투입 에이전트 |
|--------|-------------|
| 투자/포트폴리오/FIRE/리밸런싱 | fin-portfolio-analyst + fin-market-scout |
| 코드/버그/구현/배포 | eng-foreman → CC 위임 |
| 리서치/트렌드/기술동향 | res-deep-researcher + res-web-scout |
| 커리어/FDE/성장 | car-strategist + car-skill-tracker |
| 운동/건강/체중 | life-health-coach |
| 시스템/인프라/서버 | ops-infra-manager → CC 위임 |
| 비교/의사결정/A vs B | res-architect + res-experimenter + (domain별 전문가) |
| 3자 회의 | GPT(찬성) + GPT(반론) + Gemini(비판) → Brain 판정 |

**선발 원칙:**
- 최소 2개, 최대 5개 에이전트 투입 (Brain 지정 없을 때)
- 실행형(CC/Codex 필요) + 두뇌형(GPT/Gemini) 혼합 시 → 두뇌형 먼저 실행 → 결과를 실행형에 전달
- 에이전트 간 의존성 있으면 순차, 없으면 병렬

### Step 3 — 엔진 매핑 및 실행

**두뇌형 에이전트 실행 (GPT/Gemini 직접 호출):**

```
query_gpt 또는 query_gemini 호출 시:
  system_message: "[에이전트 ID] 페르소나로 답변. [에이전트 Identity 요약]"
  prompt: "[작업 내용 + 판단 기준 + 출력 형식]"
  model: 복잡도에 따라 선택
    - 단순 분석 → gpt-4o / gemini-2.5-flash
    - 복잡한 판단 → gpt-4o / gemini-2.5-pro
    - 심층 리서치 → query_gemini_deep_research
```

**실행형 에이전트 위임 (CC/Codex):**

```
delegate_to_engine 호출:
  recommended_engine: "antigravity_sonnet" | "codex" | "claude_code"
  task_title: "[에이전트 ID]: [작업 한 줄 요약]"
  task_prompt: "[에이전트 스펙 + 구체적 작업 지시]"
  reason: "[CC/Codex 선택 이유]"
  brain_followup: "from_[engine] 수신 후 AG가 결과 종합"
```

### Step 4 — 에이전트 간 협력

에이전트 A의 출력을 에이전트 B의 입력으로 전달:

```
예시: 3자 회의
  1. query_gpt(fin-portfolio-analyst 페르소나) → 찬성 분석
  2. query_gpt(res-architect 페르소나, 반론 역할) → 반론
  3. query_gemini(res-experimenter 페르소나) → 비판적 관점
  4. AG: 3개 결과 종합 → 충돌 지점 추출 → from_antigravity.md 저장
  5. Brain: 최종 판정
```

### Step 5 — 결과 종합 및 저장

모든 에이전트 결과 수신 후 `from_antigravity.md`에 저장:

```markdown
---
from: ag-orchestrator
topic: [주제]
agents_used: [투입 에이전트 목록]
completed_at: [ISO timestamp]
status: done
---

## 에이전트별 결과

### [agent-id]: [역할]
[결과 요약]

### [agent-id]: [역할]
[결과 요약]

## 종합 분석
[AG의 통합 분석 — 충돌 지점, 합의 지점, 불확실성]

## Brain에 전달할 핵심
→ [판정에 필요한 핵심 3가지]
→ 불확실성: [High/Medium/Low]
→ 권장 사항: [있으면 기재, 없으면 "Brain 판정 대기"]
```

---

## 제약 및 Hard Rules

- LLM으로 수학 연산 직접 수행 금지 → Codex(fin-quant/cmp-compute-lead) 위임
- 금융 파일(Rules.md, portfolio.json) 직접 수정 금지 → Brain 에스컬레이션
- GPT 호출 최대 4회 / Gemini 호출 최대 4회 (1회 오케스트레이션당)
- 실행 결과는 반드시 `from_antigravity.md`에 저장 후 완료 선언
- Brain이 "확인해" 라고 하기 전까지 from_ 덮어쓰기 금지

---

## Brain → AG 지시서 최소 포맷

Brain은 `to_antigravity.md`에 아래만 작성하면 됨:

```markdown
---
status: pending
priority: normal | high | urgent
---

## 주제
[한 줄]

## 목적
[무엇을 알고 싶은가]

## 에이전트 (선택 — 미입력 시 AG 자율 선발)
- [agent-id]
- [agent-id]

## 판단 기준
- [기준 1]
- [기준 2]

## 출력 형식
[자유 서술 | 3-Layer | 표 | 비교 분석]

## 제약
[시간, 호출 횟수, 특이사항]
```
