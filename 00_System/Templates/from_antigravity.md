# Antigravity (AG) 에이전트 시스템 가이드

요청하신 대로 **Antigravity (AG) 앱** 환경에서 에이전트가 어떻게 할당되고, 작동하며, 지식(Knowledge)을 활용하는지에 초점을 맞춘 가이드입니다.

---

## 1. AG 기반 에이전트 할당 및 설정 (Setup)

Antigravity(이하 AG)는 GUI 기반의 에이전트 매니저 앱으로, 웹 검색, 멀티모달 처리, 그리고 심층 추론 및 어드바이저리 역할을 수행합니다. 총 40개의 시스템 에이전트 중 **18개**가 AG 엔진에 할당되어 있습니다.

### AG 전담 에이전트 구성 (18개)
AG 앱 내에서는 작업의 성격에 따라 다음 두 가지 "페르소나(모델)" 그룹으로 무장하여 투입됩니다:

1. **AG-Gemini (5개) - 실시간 웹 브라우징 및 리서치 전담**
   - **사용 모델**: `gemini-3.1-pro` 
   - **주요 에이전트**: `res-web-scout` (웹 수집), `res-deep-researcher` (논문/심층 조사), `fin-market-scout` (시세/매크로 수집) 등
   - **특징**: 최고 수준의 OSINT(공개 출처 정보) 수집, 최신 정보 실시간 검색, 구글 검색 품질 평가 수준의 스팸 필터링.
2. **AG-Sonnet/Opus (13개) - 심층 추론 및 멘토링 전담**
   - **사용 모델**: `claude-opus-4-6` (복잡한 전략) 및 `claude-sonnet-4-6` (창작/코칭)
   - **주요 에이전트**: `cmd-orchestrator` (작업 분해), `fin-portfolio-analyst` (투자 전략 분석), `cre-writer` (글쓰기), `life-integrator` (라이프스타일 멘토) 등
   - **특징**: 수치 연산이나 코드 실행보다는 '사람의 고민을 듣고 방향을 잡아주거나, 전략적 체계를 세우는' 가이던스 파트너 역할.

### 할당 시나리오
- 사용자가 Brain에게 "요즘 미국 금리 인하 트렌드를 바탕으로 내 포트폴리오를 점검해줘"라고 요청하면, Brain은 리서치가 필요한 부분은 **AG의 `res-web-scout`**에게, 투자 전략 분석은 **AG의 `fin-portfolio-analyst`**에게 할당하기로 결정합니다.

---

## 2. AG 작동 방식 (Operating Mechanism: Hand-off)

Claude Code(CC)가 보이지 않는 배경(Headless)에서 코드를 자동으로 실행하는 것과 달리, **AG는 사용자가 눈으로 보고 직접 실행(Manual Handoff)하는 통제된 환경**으로 작동합니다. (품질 검증 체계 및 과금 방지 목적)

### 실행 워크플로우 (Multi-engine Dispatch Protocol)
1. **작업 지시서 발급 (`to_antigravity.md`)**:
   - Brain(또는 `cmd-dispatcher`)이 AG에서 실행할 특정 에이전트의 스펙(정체성, Hard Rules, 태스크, 제한사항)을 하나의 파일인 `00_System/Templates/to_antigravity.md`에 작성합니다.
2. **사용자의 AG 앱 수동 실행**:
   - 사용자는 GUI를 가진 Antigravity 앱을 엽니다.
   - Brain이 발급한 `to_antigravity.md`의 내용을 AG 앱에 입력하여, AG가 해당 페르소나(예: Web Scout)로 빙의하도록 트리거합니다.
3. **AG 내부 수행 (웹 브라우징 / 시각화 / 분석)**:
   - AG는 지시받은 역할에 맞춰 수차례 웹 검색을 하거나, 도표를 파싱하거나, 복합적인 답변을 추론해 냅니다.
4. **결과 회수 (`from_antigravity.md`)**:
   - AG 앱에서 출력된 최종 리포트나 데이터를 사용자가 복사하여 (또는 자동화 플러그인을 통해) `00_System/Templates/from_antigravity.md`에 저장합니다.
   - 메인 Brain은 이 `from_` 파일을 읽어들여 자신의 기억으로 통합한 뒤, 다음 단계를 진행합니다.

---

## 3. Knowledge (AG의 지식 주입 및 볼트 연동)

AG는 로컬 파일 시스템을 직접 자유롭게 헤집고 다니는 CC와 달리, 외부 GUI 앱 환경이므로 별도의 **지식 주입(Knowledge Injection)** 메커니즘이 필요합니다.

### 지식 전달 방식
1. **Context RAG 주입**:
   - AG 에이전트가 Vault 안의 방대한 정보(도메인 데이터 등)를 알아야 할 때, `to_antigravity.md` 파일이 생성되는 시점에 **Brain이 필요한 부분만 발췌하여 문서 안에 함께 적어줍니다.**
   - 즉, AG 앱 자체가 전체 폴더를 스캔하는 작업이 아닌, "현재 내 자산 상태 json의 사본"이나 "최근 대화 기록(active_context) 요약본"을 지시서에 동봉해서 보냅니다.
2. **Hard Rules 동봉**:
   - 각 에이전트 스펙(`00_System/Specs/agents/*.md`)에 적힌 금지 사항(예: "출처 없는 정보 전달 금지", "금융 파일 접근 금지" 등)이 지시서 상단에 강제 규칙으로 명시되어, AG 모델이 엉뚱한 창작(환각)을 하지 않도록 통제합니다.
3. **독자적 웹 수집 지식 (`res-` 에이전트의 경우)**:
   - AG 내부의 웹 브라우징 에이전트들(Gemini)은 외부 인터넷을 뒤져 스스로 새로운 지식을 수집합니다. 이때 원본 소스(Primary Source)를 반드시 추적하고 "URL, 신뢰도 기준, 작성일" 3가지 태그를 달아서만 `from_` 파일로 넘기기 때문에, 불분명한 외부 정보가 내부 지식(Vault)으로 오염되는 것을 막습니다.
