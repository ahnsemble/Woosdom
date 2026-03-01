# GPT Deep Research 2차 결과
*Engine: GPT Deep Research*
*Date: 2026-02-25*
*Input: ARCHITECTURE.md v1.2 + CLAUDE.md*
*Status: ⏳ 대기 중 — GPT Deep Research에 프롬프트 전달 후 결과를 여기에 붙여넣기*

---

# GPT Deep Research 2차 검증 보고서 — ARCHITECTURE.md v1.2 + CLAUDE.md

본 보고서는 **ARCHITECTURE.md v1.2**와 **CLAUDE.md v1.0**를 근거로, 1차 Peer Review의 6개 지적사항이 **실제로 해결되었는지**와 그 해결 방식이 **실행 가능한지**(특히 1인 개발 + AI 코딩 에이전트 위임 환경)를 5개 관점에서 재검증한 결과입니다. fileciteturn1file0 fileciteturn1file1

## 1차 지적사항 해결 검증

### 판정
⚠️ 조건부 합격

### 근거
6개 지적사항은 **사실상 모두 “방향성은 올바르게 반영”**되었습니다. 다만, **해결 방식의 구현 세부가 일부 문서/코드 스케치에서 부정확하거나(특히 `window.state`), 자동 디스커버리의 엣지케이스를 막는 “규칙”이 아직 불충분**해서 Phase 0~1에서 흔들릴 가능성이 남아있습니다. fileciteturn1file0

- 지적사항 1: 렌더링 전략 충돌(빌드타임 vs 런타임 fetch)  
  - 해결: “fetch/polling 전면 폐기, 빌드타임 + 앱은 `window.state`”로 책임을 단일화했습니다. fileciteturn1file0  
  - 적절성: 적정. PyWebView 6.0의 shared state는 JS↔Python 상태 동기화를 제공하며, HTTP/fetch 기반보다 **CORS/경로/네트워크 부담을 구조적으로 제거**합니다. citeturn0search4turn0search9  
  - 새 리스크: v1.2 문서의 Python 예시는 `window.state = {...}` 형태인데, pywebview 공식 예시는 **`window.state.<key> = value`**처럼 state 객체의 프로퍼티를 설정합니다. 잘못된 사용은 “상태가 전파되지 않는/이벤트가 안 뜨는” 형태의 치명적 가짜 성공(false confidence)을 만들 수 있습니다. citeturn2view0turn2view2  

- 지적사항 2: 레지스트리 ↔ 파일 수동 동기화 실패 리스크  
  - 해결: 수동 registry를 폐기하고, `src/templates/partials/`를 스캔해 패널을 자동 발견하며, orphan 감지/중복 order 경고까지 포함했습니다. fileciteturn1file0  
  - 적절성: 적정~과잉 사이(하지만 이 프로젝트 맥락에서는 적정 쪽). “AI 에이전트가 registry 동기화를 놓친다”는 1차 지적에 직접 대응합니다. fileciteturn1file0  
  - 새 리스크: `os.walk`는 기본적으로 **숨김 파일/하위 디렉토리까지 순회**하며, 순회 순서가 파일시스템에 따라 달라질 수 있습니다. 따라서 `.DS_Store`, `~` 백업, `partials/` 하위 폴더가 생겼을 때 의도치 않은 패널 발견/비결정적 패널 순서가 Golden Master diff 노이즈를 만들 수 있습니다. citeturn1search14turn1search18  

- 지적사항 3: PyWebView file:// CORS 제약 미반영  
  - 해결: `desktop.py`에서 `http_server=True` 강제 및 file:// 금지를 문서의 “필수 제약”으로 승격했습니다. fileciteturn1file0  
  - 적절성: 적정. PyWebView는 로컬 파일 제공을 위해 내장 HTTP 서버를 제공하며, 브릿지/상태 공유 역시 이 전제에서 더 안정적으로 동작합니다. citeturn0search5turn2view2  
  - 새 리스크: “http_server=True만 켜면 다 된다”가 아니라, **패키징(특히 py2app)에서 리소스 경로가 흔들릴 때** 문제가 재발합니다. 실제로 “py2app로 패키징한 앱이 Applications 폴더에서 실패”한 이슈가 보고된 바 있습니다. citeturn3search5  

- 지적사항 4: 회귀 검증 전략 부재  
  - 해결: Phase 0에 Golden Master 스냅샷을 넣고, Phase 1~2에서 Golden Master 비교를 명시했습니다. fileciteturn1file0  
  - 적절성: 적정. Golden Master(= characterization test)는 레거시의 실제 동작을 스냅샷으로 고정해 리팩터링 회귀를 막는 데 널리 쓰이는 접근입니다. citeturn5search40  
  - 새 리스크: “HTML 문자열 diff”는 매우 brittle할 수 있습니다(패널 순서, 공백, 속성 순서, 빌드 타임스탬프 등). 따라서 **정규화/비주얼 회귀**가 없으면 Phase 1~2에서 ‘의미 없는 diff’로 개발 속도가 크게 떨어질 수 있습니다. citeturn5search40  

- 지적사항 5: AI 에이전트 프로젝트 규칙 파일 미비  
  - 해결: CLAUDE.md에 “절대 규칙/작업 흐름/금지 패턴”을 체계적으로 추가했습니다. fileciteturn1file1  
  - 적절성: 대체로 적정. Claude Code는 CLAUDE.md를 매 세션 시작에 읽는 “특수 파일”로 설명하며, 빌드/테스트 명령과 워크플로우 규칙을 넣는 것을 권장합니다. citeturn4search0turn4search7  
  - 새 리스크: 일부 규칙은 선언적이라(예: “한 번에 한 패널만”) 실제 작업 중 깨질 수 있습니다. 이 부분은 도구적 강제가 없으면 에이전트가 흔히 위반하는 영역입니다.

- 지적사항 6: Panel Scaffold 자동 생성 없음  
  - 해결: `python3 build_dashboard.py --new-panel {id}`로 (HTML/CSS/JS) 스캐폴딩을 자동 생성합니다. fileciteturn1file0turn1file1  
  - 적절성: 적정. “정합성 실패(파일명/ID 불일치)”를 가장 저렴하게 줄이는 조치입니다.  
  - 새 리스크: 스캐폴더가 생성하는 템플릿/보일러플레이트가 “표준”이 되는 만큼, 그 표준이 변경될 때 build script 수정이 필요합니다. 그런데 CLAUDE.md는 `build_dashboard.py` 수정을 강하게 제한하고 있어(승인 필요), **표준 진화 속도**가 느려질 수 있습니다. fileciteturn1file1  

#### 핵심 결정 검토

- `window.state` 채택의 우월성/한계(중요)  
  - 우월한 점: PyWebView 6.0은 JS↔Python 간 **공유 상태 관리(shared state)**를 제공하며, 속성 변경이 자동 전파됩니다. 이는 로컬 앱에서 fetch/polling 대비 네트워크/서버/CORS 문제를 원천 제거해 구조적으로 유리합니다. citeturn0search4turn0search2turn2view2  
  - 알려진 한계: 동기화는 “최상위(top-level) 프로퍼티 변경” 중심이며, **중첩 객체 내부 mutation은 감지되지 않는다**는 제약이 공식 문서/블로그에 명시되어 있습니다. citeturn0search4turn2view2turn0search5  
  - 실무적 함정: JS 쪽은 `pywebview.state`의 change/delete 이벤트를 구독해야 “실시간”이라 부를 수 있습니다. 공식 State 예제는 `pywebview.state.addEventListener('change', …)`를 사용합니다. v1.2 문서의 JS 스케치는 “초기 1회 읽기”만 제시되어 있어, Phase 3에 들어가면 추가 보완이 필요합니다. citeturn2view0turn0search5  

- `os.walk` 자동 디스커버리의 안전성/엣지케이스  
  - 안전성이 올라간 점: 수동 레지스트리 동기화 실패를 제거하고 “파일 존재=패널 존재”로 바꿨기 때문에, AI 에이전트가 놓치기 쉬운 동기화 오류를 크게 줄입니다. fileciteturn1file0  
  - 엣지케이스: 숨김 파일/백업 파일/하위 디렉토리의 `.html`이 패널로 오인될 수 있습니다. `os.walk`는 디렉토리 트리를 재귀 순회하며, 탐색 순서도 환경에 따라 달라질 수 있습니다. citeturn1search14turn1search18  
  - 특히 위험한 케이스: `header.html`, `footer.html` 같은 “include용 partial”이 같은 폴더에 있을 경우 자동 발견 대상이 됩니다(문서 예시에는 header/footer include가 등장). 이 경우 “패널이 아닌 조각”이 패널로 렌더링되는 구조적 버그가 생길 수 있습니다. fileciteturn1file0  

- `StrictUndefined + select_autoescape` 조합의 충분성  
  - 장점: StrictUndefined는 정의되지 않은 변수를 조기에 실패시키는 방식으로, 템플릿 오타/스키마 드리프트를 “침묵 실패”로 남기지 않습니다. citeturn1search15turn1search31  
  - 충분성: 빌드 안정성 측면에서는 충분한 편입니다. 다만 “데이터가 없으면 조용히 빈 상태”라는 설계 목표와 병존하려면, 템플릿에서 `is defined` 방어 패턴을 표준화해야 합니다. CLAUDE.md가 이 규칙을 명시한 점은 타당합니다. fileciteturn1file1  

### 잔여 리스크
- `window.state`의 API 사용 방식이 문서 내 예시에서 일부 부정확해 보이며, 이 상태로 Phase 3에 들어가면 **“실시간이 안 된다”** 유형의 이슈가 높습니다. (프로퍼티 설정/이벤트 구독 필요) citeturn2view0turn0search5turn2view2  
- 자동 디스커버리는 “규칙”이 생명인데, 현재 문서는 **패널로 인정할 파일명 패턴, 제외 규칙, 탐색 범위(최상위만? 재귀?)**가 부족합니다. citeturn1search14turn1search18  
- Golden Master 비교가 문자열 diff에 머물면 “diff 노이즈”로 Phase 1~2 속도가 급락할 수 있습니다. citeturn5search40  

### 제안
- `window.state`는 “객체 재할당”이 아니라 “프로퍼티 설정”으로 문서와 예시를 통일: `window.state.dashboard_data = ...` 형태로 명문화하고, JS는 `pywebview.state` change 이벤트를 구독하는 표준 패턴을 설계서에 포함하세요. citeturn2view0turn0search5turn2view2  
- 패널 자동 발견은 `glob('partials/*.html')`처럼 **최상위만 스캔**하거나, os.walk를 쓰되 `.html`은 최상위에서만 인정하는 규칙을 추가하세요(숨김 파일/하위 폴더를 통한 오인 방지). `os.walk`는 `dirs[:]` 조작으로 탐색 가지치기가 가능하므로 이를 문서화하는 것도 방법입니다. citeturn1search14turn1search18  
- Golden Master는 최소한 “패널 목록 정렬(order→id) 고정 + HTML 정규화(공백/주석 제거) 또는 스크린샷 기반 비주얼 비교” 중 하나를 포함해 노이즈를 줄이세요. citeturn5search40  

## CLAUDE.md 실효성 검증

### 판정
⚠️ 조건부 합격

### 근거
CLAUDE.md는 1차 리뷰에서 요구한 핵심 요소(“패널 단위 작업”, “핵심 파일 수정 금지”, “fetch 금지”, “스캐폴드 사용”, “토큰 기반 CSS”, “StrictUndefined 대응”)를 구체적으로 담고 있어 **실효성이 높습니다.** fileciteturn1file1  
또한 Claude Code 공식 문서는 CLAUDE.md를 “매 세션 시작에 읽는 특수 파일”로 설명하고, 빌드/테스트 명령, 코드 스타일, 워크플로우 규칙을 넣는 것을 권장합니다. 이 방향성은 잘 맞습니다. citeturn4search0turn4search7  

다만 “업계 비교(표준화/상호운용)” 관점에서, **Codex 중심 운영까지 고려하면 AGENTS.md 표준을 병행하는 편이 더 안전**합니다. Codex는 AGENTS.md를 작업 전 읽는다고 공식 문서에서 명시합니다. citeturn4search1turn4search2turn1search9  

#### 규칙의 명확성
- 강점: “절대 금지(f-string JS/CSS, fetch, panel_registry 수동 수정, core/base 수정 금지)”처럼 모호성이 낮습니다. fileciteturn1file1  
- 모호한 지점(개선 필요):
  - “ES5+ 문법만 사용”이라고 하면서 `let/const/arrow`를 허용합니다. 이는 사실상 ES2015+이므로, 목표 런타임(특히 PyWebView의 엔진 차이)을 감안해 문구를 더 정확히 해야 혼선을 줄입니다. fileciteturn1file1  
  - “한 번에 한 패널만 수정”과 “버그 수정 시 3파일 이내” 규칙은 좋지만, 실제로는 버그가 parser/스키마에 있을 수 있으므로 예외 경로(“데이터 파이프라인 버그면 parser.py 수정 허용”)를 더 명시해야 합니다. fileciteturn1file1  

#### 규칙의 완결성
- 잘 채워진 것: 파일 위치 규칙, 네임스페이스 CSS, IIFE JS, StrictUndefined 대응(if defined), 빌드 커맨드 등이 포함됩니다. fileciteturn1file1  
- 빠진 것(현장에서 에이전트가 자주 실수하는 영역):
  - “생성 산출물 편집 금지”: `index.html`을 직접 수정하지 말 것(생성물).  
  - “Golden Master 업데이트 규칙”: 어떤 경우에 스냅샷을 갱신하는가(의도된 변경 승인 프로세스).  
  - “패널 디스커버리 예외”: header/footer 같은 include용 partial을 어디에 두며, 자동 발견에서 어떻게 제외되는가.  
  - “실행 환경 버전 체크”: pywebview 6.0+/설치 확인(설계서에만 있고, 에이전트 작업 절차에선 빠질 수 있음). citeturn0search10  

#### 규칙 간 충돌
- 큰 모순은 없지만, 아래 2개는 충돌 가능성이 있습니다.
  - “패널만 수정” 원칙 vs “StrictUndefined로 빌드 실패 시 스키마/데이터/템플릿을 함께 고쳐야 하는 상황”  
  - “외부 라이브러리 승인 필요” vs Phase 4에 Chart.js vendoring(외부 라이브러리 도입)  
  → 둘 다 “승인/예외 프로세스”를 CLAUDE.md에 최소한으로라도 명시하면 충돌 비용이 줄어듭니다. fileciteturn1file0turn1file1  

#### 실행 가능성(강제 vs 선언)
- 구조적으로 강제되는 규칙: 자동 디스커버리(레지스트리 수동 편집 제거), StrictUndefined(미정의 변수 차단), `--new-panel` 스캐폴드(정합성 기반) — **구조적 강제력이 있습니다.** fileciteturn1file0turn1file1  
- 선언적으로만 존재하는 규칙: “한 번에 한 패널”, “500줄 이상 금지”, “!important 남용 금지” — 도구/검증이 없으면 어겨질 수 있습니다.

#### 업계 비교
- Cursor는 “Rules”로 에이전트에 시스템 수준 지시를 제공하는 문서를 공식화하고 있습니다. citeturn1search2  
- Codex는 AGENTS.md를 작업 전 읽는다고 명시하며, 전용 가이드까지 제공합니다. citeturn4search1turn4search2  
- 따라서 “다중 에이전트(Claude Code + Codex)” 환경에서는 CLAUDE.md 단독보다는 **AGENTS.md도 병행(또는 CLAUDE.md를 AGENTS.md로 미러링)**하는 편이 업계 흐름과 맞고, 도구 간 규칙 전달의 신뢰성이 높습니다. citeturn1search9turn4search1turn4search0  

### 잔여 리스크
- CLAUDE.md가 “좋은 선언”을 담고 있음에도, 자동 검사(예: 변경 파일 경로 검사, index.html 직접 수정 감지, 패널 디스커버리 제외 규칙 검사)가 없으면 일부 규칙은 쉽게 무너질 수 있습니다.  
- Codex 측 규칙 파일(AGENTS.md)이 없으면, Codex가 CLAUDE.md를 동일하게 읽는다는 보장이 약합니다(도구별 컨벤션이 다름). citeturn4search1turn1search9  

### 제안
- CLAUDE.md를 유지하되, 루트에 AGENTS.md를 추가하고 “CLAUDE.md 요약/링크”를 넣는 구성을 권장합니다(동일 규칙을 두 번 관리하지 않기 위해). Codex는 AGENTS.md를 읽는다고 공식 문서에서 명시합니다. citeturn4search1turn4search2turn1search9  
- “생성물(index.html) 직접 수정 금지”, “panel partial 중 자동 발견 제외 디렉토리/접두사 규칙”, “Golden Master 스냅샷 갱신 절차”를 짧게 추가하세요. CLAUDE.md는 “짧고 인간이 읽을 수 있게”가 권장되므로, 디테일은 별도 문서로 보내고 링크하는 방식이 적합합니다. citeturn4search7turn4search0  

## Phase 0 실행 가능성

### 판정
⚠️ 조건부 합격

### 근거
Phase 0는 1차 리뷰에서 요구했던 “리팩터링 안전망”을 명확히 포함합니다(골든 마스터 + PyWebView 로딩 PoC + 패키징 탐색). fileciteturn1file0  
또한 pywebview 6.0의 `window.state`는 공식 문서/블로그에서 핵심 기능으로 소개되어 있고, 상태 변경 이벤트까지 제공하므로, “PoC로 검증할 가치”가 충분합니다. citeturn0search4turn2view0turn0search5turn2view2  

다만 v1.2 Phase 0의 PoC 정의는 “http_server=True 로딩 확인”까지만 강조되어 있어, **정작 가장 큰 리스크인 `window.state` 동기화/이벤트 흐름**을 Phase 0에서 놓칠 수 있습니다. fileciteturn1file0  

#### Golden Master 적합성/한계
- 적합: 레거시(단일 파일) 리팩터링에서 회귀 방지 목적에 매우 적합합니다. citeturn5search40  
- 한계: HTML diff는 취약합니다(순서/공백/주석). 따라서 최소한 “패널 순서 결정의 결정성”이 보장되어야 하고, 가능하면 DOM 정규화나 스크린샷 기반 비교를 같이 고려해야 합니다. citeturn5search40  

#### PyWebView http_server=True PoC의 검증 범위
- 검증하는 것: file:// 제약 회피, 상대 경로 static asset 제공, 앱 모드 렌더링 기반. citeturn0search5turn2view2  
- 놓칠 수 있는 것: 패키징 이후(특히 py2app) **Resources 경로/Applications 폴더에서의 실패**. 실제로 “py2app 패키징 앱이 Applications 폴더에서 실패”가 보고된 이슈가 있으므로, 최소 PoC는 이 케이스를 포함해야 설계 리스크를 줄입니다. citeturn3search5  

#### pyinstaller 대안 테스트의 필요성
- 과잉일 수 있는 이유: 최종 목표가 macOS 중심이고 기본 툴이 py2app라면, Phase 0에서 pyinstaller까지 다 하면 비용이 늘 수 있습니다.  
- 필요한 이유(조건부): pywebview 쪽에서 py2app 리소스/경로 이슈가 실제 보고된 바 있고, 패키징 실패는 “마지막에 터지면 비용이 가장 큰” 리스크입니다. 따라서 “py2app PoC가 실패할 때의 백업 옵션”으로 pyinstaller를 Phase 0에서 가볍게 확인하는 건 합리적일 수 있습니다. citeturn3search5turn3search3turn3search0  

#### Phase 0 완료 기준의 명확성
- 현재 문서의 완료 기준은 “Golden Master 존재 + PoC 로딩 성공 + pyinstaller 동작” 수준인데, **정량/구체화가 더 필요**합니다. 예: (1) assets 이미지 2개 이상 정상 로드, (2) `pywebview.state` change 이벤트 1회 이상 수신, (3) Applications 폴더에서 재실행 시도 등. fileciteturn1file0  

### 잔여 리스크
- Phase 0이 `window.state`의 “전파/이벤트/중첩 객체 제약”까지 검증하지 않으면, Phase 3에서 구조가 흔들릴 수 있습니다. `window.state`는 top-level만 전파되고, mutation은 감지되지 않는다는 제약이 공식적으로 명시되어 있습니다. citeturn0search4turn2view2turn0search5  
- py2app/pyinstaller 포장에서는 index.html/정적 자산 경로 누락이 흔한 이슈이며, “index.html not found” 류 문제가 실제 이슈로 보고됩니다. citeturn3search0turn3search3  

### 제안
- Phase 0 PoC의 핵심 목표를 2개로 고정하세요.
  - (A) `http_server=True`에서 src/css/src/js/assets가 모두 로드되는지  
  - (B) `window.state.<key>=value` 변경이 JS에서 `pywebview.state` change 이벤트로 수신되는지  
  pywebview 공식 State 예제는 `pywebview.state.addEventListener('change', …)` 구독을 사용합니다. citeturn2view0turn0search5turn2view2  
- 패키징 PoC는 “py2app 최소 앱”을 우선으로 하고(공식 예제도 존재), 실패할 때만 pyinstaller로 백업 타당성을 확인하는 “조건부 분기”가 비용 대비 효율적입니다. citeturn3search3turn3search5  

## 마이그레이션 4 Phase 실현 가능성

### 판정
⚠️ 조건부 합격

### 근거
Phase 0~4는 **의존성 흐름이 명확**하고(안전망 → 골격 → 템플릿/토큰 → 기능/실시간 → 패키징), 각 Phase에 검증 항목을 붙이려는 의도가 강합니다. fileciteturn1file0  
그러나 “자동 디스커버리/Golden Master/`window.state`”라는 세 축이 모두 **결정성(determinism)**과 **정합성(contract)**에 민감하므로, 각 Phase 완료 기준을 조금 더 기술적으로 못 박아야 1인 + 에이전트 위임에서 흔들림이 줄어듭니다.

#### Phase별 현실성/의존성/완료 기준 평가

- Phase 1(골격 + Jinja2 빌드러너 + auto-discovery)  
  - 현실성: 중간 난이도. “CSS/JS 추출 + Jinja 렌더러 ~150줄”은 목표로서 적절하지만, 실제는 디버깅/경로 문제로 늘어날 수 있습니다. fileciteturn1file0  
  - 완료 기준 강화 필요:  
    - auto-discovery 결과가 OS/filesystem에 무관하게 동일(정렬 규칙 고정)  
    - header/footer 등 “include용 partial”이 패널로 오인되지 않음(제외 규칙)  
    - StrictUndefined로 인해 빌드 실패가 생기면, “템플릿 방어 패턴”이 표준화되어야 함 citeturn1search15turn1search31  

- Phase 2(템플릿 분리 + 토큰/매크로)  
  - 현실성: 적정. UI 반복 패턴이 많은 대시보드 성격상 tokens/macros는 비용 대비 효과가 큽니다. fileciteturn1file0  
  - 실패 지점: 매크로 도입은 전역 변경 효과가 크므로 Golden Master diff가 폭발할 수 있습니다(“원치 않는 전역 변경”). 따라서 Phase 2는 “패널별로 하나씩 전환”이 핵심이며, 문서도 이를 언급합니다. fileciteturn1file0  

- Phase 3(버그 수정 + window.state 실시간)  
  - 현실성: 조건부. `window.state`는 실제 기능이므로, Phase 0에서 확실히 검증되지 않으면 Phase 3이 가장 위험해집니다. citeturn0search4turn2view2  
  - 실패 지점:  
    - state 업데이트가 이벤트로 전파되지 않음(잘못된 API 사용)  
    - 대형 `dashboard_data`를 자주 통째로 재할당하면서 성능/렌더링 부담이 커짐(top-level 재할당만 감지되는 제약 때문에 업데이트 방식이 “전체 객체 교체”로 쏠릴 수 있음) citeturn0search4turn0search5turn2view2  

- Phase 4(프로덕션 빌드: 인라인 + 패키징 + Chart.js vendoring)  
  - 현실성: 조건부. 번들링/인라인은 상대경로/리소스 로딩 이슈가 잘 터지는 구간입니다.  
  - 실패 지점: py2app에서 리소스 경로 문제(특히 Applications 폴더에서 실패) 및 “정적 파일 누락”이 반복적으로 보고됩니다. citeturn3search5turn3search3  

#### 롤백 전략
- 문서에는 “구버전 빌더 병행 유지” 같은 롤백 메커니즘이 명시적으로는 약합니다. Golden Master가 있어도, 롤백은 별도 전략이 필요합니다. fileciteturn1file0  

### 잔여 리스크
- auto-discovery의 결정성(정렬, 제외 규칙)이 확정되지 않으면, Phase 1~2에서 Golden Master 비교가 “항상 실패”하는 상태가 될 수 있습니다. citeturn1search14turn5search40  
- `window.state`를 도입한 순간, “브라우저 모드에서 JS 패널이 데이터를 어디서 얻는가?”(초기 데이터 주입)가 설계서에 더 명확해야 합니다. (fetch를 폐기했기 때문에, JS 패널이 데이터를 읽을 수 있는 다른 경로가 반드시 필요) fileciteturn1file0  

### 제안
- Phase 1 완료 기준에 “패널 자동 발견 결정성”을 명문화: `order → id` 정렬 고정, 제외 규칙(예: `_` 접두사, `header/footer` 별도 폴더) 고정. citeturn1search14  
- fetch 폐기 이후, JS 패널용 “초기 데이터 주입” 표준을 설계서에 추가하세요. 예: build-time에 `<script type="application/json" id="dashboard-data">…</script>`로 주입 후 core.js가 파싱해 `Dashboard.init()` 호출. 앱 모드는 `pywebview.state` change 이벤트로 덮어쓰기. (이 구조는 fetch를 복구하지 않으면서도 browser/app 양쪽을 일관되게 만듭니다.) citeturn2view0turn0search5turn2view2  
- 롤백은 “구버전 build_dashboard.py 유지” 또는 “index_old.html/index_new.html 병행 생성”처럼 실행 가능한 형태로 한 줄이라도 문서화하세요. fileciteturn1file0  

## 과잉 엔지니어링 재점검

### 판정
✅ 합격

### 근거
v1.2에서 추가된 구조는 “기반만 깔고 Step 2~3은 보류”라는 형태로 **YAGNI를 비교적 잘 준수**합니다. 특히 아래는 지금 규모에서도 비용 대비 효과가 큰 요소입니다. fileciteturn1file0  

- 디자인 토큰(CSS Variables): 대시보드 UI의 변경 비용을 급격히 낮추는 장치이며, “CSS 하드코딩 금지” 규칙과 결합해 에이전트가 만들기 쉬운 스타일 난잡함을 줄입니다. fileciteturn1file0turn1file1  
- macros.html(매크로 라이브러리): badge/card 같은 반복 패턴이 있는 경우, early 도입이 오히려 중복을 줄여 “과잉”이 아니라 부채 예방입니다. fileciteturn1file0turn1file1  
- 관측성(빌드 로그): 침묵 실패를 줄이는 최소한의 관측성은 Phase 0~2를 빠르게 만듭니다. fileciteturn1file0  

반면, 과잉이 될 수 있는 요소도 문서에서 “나중 단계”로 분리해두었습니다. 예를 들어 Layout의 드래그/프리셋, WebSocket 등은 “지금 만들지 않음”으로 명시되어 있습니다. fileciteturn1file0  

### 잔여 리스크
- 파서 플러그인 구조(parsers/ + registry)는 외부 데이터 소스 확장이 가까운 미래에 없다면 MVP 단계에서는 과잉이 될 수 있습니다. 다만 문서가 “보류(YAGNI)” 가능성을 언급하고 있어 운영으로 흘러갈 위험은 낮습니다. fileciteturn1file0  
- “py2app + pyinstaller 병행”은 유지 비용을 늘립니다. 하지만 py2app 관련 실패 사례가 실제 이슈로 존재하므로, 최소 PoC로 위험을 조기에 드러내는 목적이라면 과잉이라 단정하기 어렵습니다. citeturn3search5turn3search3  

### 제안
- MVP 수준에서는 parsers/ 플러그인 레이어를 “구현하지 않고 인터페이스만” 남기거나, 실제로 새로운 데이터 소스를 추가해야 하는 시점에 Phase로 분리해도 됩니다. fileciteturn1file0  
- 패키징은 Phase 0에서 “하나를 기본으로 확정(예: py2app)”하고, 백업(예: pyinstaller)은 실패 시에만 활성화하도록 문서화하면 복잡도가 줄어듭니다. citeturn3search3turn3search5  