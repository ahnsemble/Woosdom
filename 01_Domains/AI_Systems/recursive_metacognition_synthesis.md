# 재귀적 메타인지 검증 — 통합 분석서 (Synthesis)

*작성: 2026-02-15*
*소스: GPT Deep Research + Gemini Deep Research 교차 검증*
*목적: Premise Audit Protocol v1.0 개선 → v2.0 설계 근거*

---

## 1. 핵심 발견 요약

### 이 문제를 뭐라고 부르는가?

단일 정식 용어는 없다. 두 리서치를 종합하면 **4개의 어휘권**이 교차한다:

| 어휘권 | 용어 | 출처 |
|--------|------|------|
| 인지 편향 | Anchoring Bias, Plan Continuation Bias, Epistemic Inertia | 인지심리학, 항공 CRM |
| 조직 안전 | Normalization of Deviance, Drift into Failure | Diane Vaughan (Challenger), Sidney Dekker |
| ML 운영 | Model/Data/Concept Drift, Underspecification | Google (D'Amour et al., 2022) |
| 검증/인증 | Assumption Ossification, Premise Drift, Context-of-Use 관리 실패 | NASA-STD-7009, DARPA Assured Autonomy |

**우리 시스템에 가장 실용적인 프레이밍:**
> **Assumption Ossification(전제 고착) + Premise Drift(전제-환경 불일치) + Audit Trigger 부재**의 조합.
> — GPT 리서치 결론

> **Epistemic Inertia(인식론적 관성)** — 에이전트가 자신의 이전 출력을 '참'인 문맥으로 간주하는 자기 강화적(Self-Reinforcing) 속성.
> — Gemini 리서치 결론

---

## 2. 실제 사고 사례 (GPT 리서치 발굴)

| 사례 | 전제 고착 유형 | 교훈 |
|------|-------------|------|
| **Ariane 5 Flight 501** (1996) | 이전 시스템(Ariane 4)의 변수 범위 가정을 재검증 없이 재사용 → 백업도 동일 가정 공유 → 동시 실패 | **독립성(Independence) 없는 백업은 백업이 아니다** |
| **Mars Climate Orbiter** (1999) | 단위 체계(미터법 vs 영국단위) 가정 불일치가 프로젝트 전체에서 미검증 | **인터페이스 전제는 반드시 양쪽에서 교차 검증** |
| **Knight Capital** (2012) | 배포/설정 전제 깨짐 → 자동화가 오류를 증폭 → 사전 이메일 경고 있었으나 감사 트리거로 미배선 | **경고 신호가 존재 ≠ 재검토가 발생. 경고→감사를 명시적으로 배선해야** |
| **Uber 자율주행 충돌** (2018) | "사람이 최후 안전장치" 전제 → 감독 피로/주의 저하로 무너짐 | **인간 개입은 "매번 감시"가 아니라 "정해진 게이트에서의 의사결정"으로 설계** |

---

## 3. 학계·산업계 해결 방법론 비교

### 3.1 턴 내(Single-turn) vs 턴 간(Cross-turn) 검증

| 기법 | 주요 기관 | 턴 내 | 턴 간 | 핵심 메커니즘 |
|------|----------|:-----:|:-----:|-------------|
| Self-Consistency | Stanford NLP | ✅ | ❌ | 다중 추론 경로 샘플링 후 다수결 |
| Reflexion | Stanford/Northeastern | ✅ | ⚠️ 제한적 | 실패 후 언어적 반성 → 일화적 기억 저장 → 다음 시도에 주입 |
| Constitutional AI | Anthropic | ✅ | ❌ | 헌법 기반 자기비판/수정 + RLAIF |
| ReCAP | Stanford | ✅ | ✅ | 하위 작업에 상위 계획 + 전역 문맥 강제 재주입 |
| Process Reward Model | OpenAI | ✅ | ⚠️ | 중간 사고 단계 하나하나를 평가 (결과가 아닌 과정) |
| Deliberative Alignment | OpenAI | ✅ | ❌ | 규정 텍스트를 읽고 추론하여 정책 준수 |
| Multi-Agent Debate | OpenAI/DeepMind | ✅ | ✅ | 역할 분리형 상호 주장·반박 |
| AutoGen | Microsoft Research | ✅ | ✅ | 다중 에이전트 대화로 상호검증 |
| Simplex/Safety Kernel | CMU/NASA | ✅ | ✅ | 학습된 모델을 검증된 안전 커널로 감싸고 조건부 전환 |
| Continual Assurance | DARPA | — | ✅ | 운용 중 보증사례(Assurance Case) 지속 갱신 |
| PCCP | FDA | — | ✅ | 변경 범위/방법/영향평가를 사전 합의 |

**핵심 통찰:** 대부분의 AI 기법은 턴 내 검증에 강하다. **턴 간 검증은 별도의 운영 프로토콜(기록 구조 + 트리거 + 감사 절차)이 없으면 자동으로 발생하지 않는다.**

### 3.2 Gemini가 발굴한 핵심 아키텍처

| 아키텍처 | 기관 | 핵심 메커니즘 | 우리 시스템 적용 |
|----------|------|-------------|----------------|
| **ReCAP** | Stanford | 재귀적 문맥 주입 — 하위 작업 수행 시 상위 목표 강제 주입 | Swarm 에이전트에게 작업 위임 시 Trinity 헌법 + Phase 목표를 시스템 프롬프트 최상단에 항상 포함 |
| **RLM** | MIT CSAIL | 자기 자신을 함수처럼 재귀 호출 + 분할 정복 | 장기 백테스트 결과를 청크로 나눠 각각 전제 기반 평가 후 통합 |
| **TEA** | CMU | SAT 솔버로 안전 영역 이탈 수학적 증명 | MDD -25% 같은 수치적 제약을 형식적 불변식으로 선언, 위반 시 자동 차단 |
| **Meta-Judge** | Meta FAIR | 행위자→판사→메타판사 3중 역할 순환 | Brain→Critic Swarm→사용자(메타판사) 구조로 이미 부분 구현 |
| **WebAnchor** | ResearchGate | 실행 전 계획 모드 강제 진입 + 계획 루브릭 평가 | Phase 시작 시 "계획 작성 → 루브릭 평가 → 통과 시만 실행" 게이트 추가 |

### 3.3 GPT가 발굴한 핵심 제도

| 제도/프레임워크 | 기관 | 핵심 원칙 | 우리 시스템 적용 |
|---------------|------|----------|----------------|
| **NASA-STD-7009** | NASA | 모델/시뮬레이션의 Context-of-Use + 신뢰성 기준 강제 | 전제마다 "어떤 조건에서만 유효한가" 명시 |
| **DoD DT&E 가이드북** | DoD | 반복적 평가 + 위험/환경 복잡성 고려한 단계적 수행 | 리스크 기반 감사 빈도 결정 근거 |
| **Continual Assurance** | DARPA | "한 번 인증하고 끝"을 구조적으로 부정 | Phase 전환 시 전제 원장 강제 업데이트 |
| **PCCP** | FDA | 변경 허용하되 범위/방법/영향평가 사전 정의 | 전제 변경 시 영향 받는 결론 목록 + 재실행 여부 사전 합의 |
| **Assurance Case** | Boeing/Airbus | Claim–Evidence–Argument 구조 | 전제를 Claim-Evidence-Argument 트리플로 분리 |

---

## 4. Premise Audit Protocol v1.0 → v2.0 개선 제안

### 개선 1: Premise Ledger 구조 도입
전제마다 7개 필드 강제: `ID` / `Type` / `Context-of-Use` / `Evidence` / `Risk` / `Expiry` / `Owner` / `Status`
**근거:** NASA-STD-7009 + DARPA Assurance Case

### 개선 2: 리스크 기반 감사 빈도
- **Tier 0 (Catastrophic):** 매 Phase 게이트 + 인간 승인 (예: MDD 한도)
- **Tier 1 (High):** 2~3 Phase마다 + 변경/모순 시 즉시 (예: 데이터 소스)
- **Tier 2 (Medium):** 5 Phase마다 + 샘플링 (예: 리밸런싱 주기)
- **Tier 3 (Low):** 기록만, 모순 시 승격 (예: 출력 형식)
**근거:** DoD DT&E 가이드북

### 개선 3: 독립성(Independence) 원칙
고위험 전제(Tier 0~1)는 **전제를 만든 에이전트와 다른 에이전트**가 검증. 3자 회의 범위를 "결론의 편향"에서 **"전제의 편향"**까지 확장.
**근거:** Ariane 5 사례

### 개선 4: Assurance Case 형태 (Claim–Evidence–Argument)
**근거:** DARPA Continual Assurance + DO-178C

### 개선 5: 경고 신호 → 감사 트리거 명시적 배선
PRM 점수 미만/엔진 불일치/사용자 "왜?"/외부 데이터 변경 → 각각 구체적 감사 행동으로 연결.
**근거:** Knight Capital 사례

### 개선 6: 인식론적 가비지 컬렉션
deprecated 전제가 참조하는 하위 결론들을 추적 → 영향 받는 결론 자동 식별 → 재검증 큐 삽입.
**근거:** Gemini RPA + MemGPT

### 개선 7: Self-AAR 단계 추가
"왜 이 전제가 고착됐는가?" 원인 분류 → 프로토콜 자체 개선에 반영 (Meta-AAR).
**근거:** 미군 AAR + 의료 M&M Conference

---

## 5. 즉시 도입 가능한 Top 3

| 순위 | 방법론 | 난이도 | 기대 효과 | 양쪽 합의 |
|:----:|--------|:-----:|----------|:---------:|
| **1** | Premise Ledger + Risk-based Audit Trigger | 중 | 전제 재검토 자동화 | ✅ + ✅ |
| **2** | 역할 분리형 Multi-Agent 검증 | 중 | 관성 반복 구조적 차단 | ✅ + ✅ |
| **3** | Phase Gate Process Supervision 체크포인트 | 중~상 | 전제 노후 조기 탐지 | ✅ + ✅ |

---

## 6. GPT vs Gemini 리서치 품질 비교

| 평가 항목 | GPT | Gemini |
|----------|:---:|:------:|
| 기관별 커버리지 (21개) | ✅ 전체 비교표 | ⚠️ 핵심 선별 |
| 실제 사고 사례 | ✅ 4개 상세 | ⚠️ 간접 언급 |
| 참고문헌 | ✅ 32개 | ⚠️ 적음 |
| 프로토콜 설계 | ⚠️ 운영적 6단계 | ✅ 수학적 4단계 (PRM 수식) |
| 아키텍처 분석 | ⚠️ 나열 | ✅ ReCAP/RLM/TEA 심층 |
| 메커니즘 원인 | ⚠️ 용어 정리 | ✅ 3축 분석 |

**결론:** GPT = 실증·제도·참고문헌의 폭, Gemini = 이론·아키텍처의 깊이. **둘을 합쳐야 완전하다.**

---

## 7. 다음 단계

1. **즉시:** Premise Audit Protocol v2.0 작성 (개선 1~7 반영)
2. **이번 주:** Premise Ledger 템플릿 생성
3. **Phase 12 시작 전:** 인덱스 백필 전제에 v2.0 첫 적용 (파일럿)
4. **Swarm Phase 1:** Critic 에이전트에게 "전제 공격자" 역할 부여

---

*원본 리서치: `recursive_metacognition_research_gpt.md` + `recursive_metacognition_research_gemini.md`*
*3파일 세트로 관리*