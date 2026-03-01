# Dashboard Architecture Review — Brain 종합 판단
*Date: 2026-02-25*
*Status: ✅ 완료*

---

## 입력
- GPT Deep Research: `result_gpt_deep_research.md` — 점수 **7.6/10**
- Gemini Deep Research: `result_gemini_deep_research.md` — 점수 **8.5/10**

---

## Brain 종합 판단

### 양쪽 합의된 강점 (설계서에서 유지할 것)

1. **모듈화 방향 자체는 정확하다.** 1,600줄 단일 파일 → 패널별 분리는 AI 에이전트의 컨텍스트 윈도우 한계(위치 편향, 토큰 절단)를 정면 해소한다.
2. **패널 레지스트리 + 파일 기반 모듈화는 업계 검증 패턴이다.** Homer, Grafana, Übersicht 등과 결이 같다.
3. **Jinja2 선택은 타당하다.** Python 단일 커맨드 빌드, 상속/매크로/include, AI 친화적 구문. Mako(로직 결합도↑), Django(무거움), Nunjucks(Node 의존)보다 이 유즈케이스에 적합.
4. **CSS Variables 기반 디자인 토큰은 과잉이 아니라 필수다.** macOS WebKit의 MPC 최적화로 성능 우려 없음.
5. **"절대 건드리면 안 되는 파일" 체크리스트는 AI 에이전트 지시에 매우 강력하다.**

### 양쪽 합의된 약점 (v1.2에 반영 필수)

| # | 약점 | GPT 지적 | Gemini 지적 | 심각도 |
|---|------|---------|------------|--------|
| 1 | **렌더링 책임 충돌** | 빌드타임(Jinja2) vs 런타임(fetch JSON) 방향 미확정 | fetch polling은 안티패턴, window.state 사용해야 | 🔴 Critical |
| 2 | **레지스트리 ↔ 파일 불일치 리스크** | 스키마 미확정, css/js 매핑 규칙 혼재 | 수동 관리는 동기화 실패 필연, 자동생성 필요 | 🔴 Critical |
| 3 | **PyWebView file:// 제약 미반영** | CORS로 런타임 fetch 차단, 내장 HTTP 서버 필요 | http_server=True 강제, py2app Applications 폴더 버그 존재 | 🟠 High |
| 4 | **회귀 검증 전략 부재** | Golden Master 테스트 필요 | (직접 언급 없으나 동의할 수 있는 방향) | 🟠 High |
| 5 | **AI 에이전트 프로젝트 규칙 파일 미비** | CLAUDE.md에 패널 단위 규칙 추가 권고 | AGENTS.md 배치, 단일 책임 원칙 강제 권고 | 🟡 Medium |
| 6 | **Panel Scaffold(생성기) 없음** | --new-panel 명령어로 자동 생성 권고 | os.walk 기반 디스커버리 권고 | 🟡 Medium |

### 엔진 간 불일치 (GPT vs Gemini가 다르게 판단한 부분)

| 주제 | GPT 입장 | Gemini 입장 | Brain 판단 |
|------|---------|------------|-----------|
| **실시간 업데이트 방식** | fetch + polling을 제한적으로 허용, 빌드타임 렌더링 중심 권고 | fetch/polling 전면 폐기, PyWebView 6.0 `window.state` 채택 | **Gemini 채택.** 로컬 앱에서 HTTP polling은 안티패턴. `window.state` 양방향 바인딩이 구조적으로 우월. 단, 브라우저 직접 열기 모드에서는 정적 빌드 유지 (병행) |
| **레지스트리 관리** | 스키마 확정 + 빌드 시 정합성 검증 | 수동 관리 폐기, os.walk로 자동생성 | **Gemini 채택 + GPT 보완.** 자동생성을 기본으로 하되, override 가능한 수동 메타데이터(`_panel.json`)도 지원. 빌드 시 정합성 검증은 GPT 제안대로 추가. |
| **py2app 대응** | Phase 4에서 다루기, 초기 PoC 권고 | py2app Applications 폴더 버그 심각, pyinstaller 대안 검토 | **양쪽 절충.** Phase 1에서 더미 앱 빌드로 경로/로딩 PoC 확인. pyinstaller 대안도 병행 테스트. |
| **점수 차이** | 7.6/10 | 8.5/10 | GPT가 더 보수적이고 엄격하게 평가. Gemini는 PyWebView 기술적 대안(window.state)까지 제시해서 가산. **종합 8.0/10** |

---

## ARCHITECTURE.md v1.2 반영 사항

### 반영 항목 (우선순위 순)

**1. 렌더링 전략 확정 (Critical)**
- 빌드타임(Jinja2) = 기본. 데이터까지 포함한 완성 HTML 생성.
- 런타임(앱 모드) = PyWebView `window.state` 기반 부분 갱신.
- 런타임(브라우저 모드) = 정적 HTML 그대로 사용 (새로고침으로 반영).
- ~~fetch('dashboard_data.json')~~ 방식 삭제. file:// CORS 문제 원천 차단.

**2. 레지스트리 자동생성 + 정합성 검증 (Critical)**
- 빌드 시 `src/templates/partials/` 디렉토리를 os.walk로 스캔 → 패널 자동 발견.
- `_panel.json` (선택적 메타데이터): order, size, collapsible 등 오버라이드.
- 빌드 시 정합성 검증: 템플릿 존재, css/js 존재(규칙 기반: id와 동일 이름), order 중복 탐지.
- 수동 `panel_registry.json` → 폐기. 빌드가 자동 생성.

**3. PyWebView 런타임 제약 반영 (High)**
- `desktop.py`: `http_server=True` 강제 (file:// 사용 금지).
- Phase 1에서 더미 앱 빌드 PoC (assets/src 로딩 확인).
- py2app Applications 폴더 버그 인지 → pyinstaller 대안 병행 테스트.

**4. Golden Master 회귀 테스트 (High)**
- Phase 0으로 추가: 리팩토링 시작 전 현재 `index.html` 출력을 스냅샷 저장.
- 동일 `dashboard_data.json` 입력 → 구버전/신버전 출력 비교.
- (선택) 헤드리스 스크린샷 비교.

**5. AI 에이전트 프로젝트 규칙 강화 (Medium)**
- `CLAUDE.md`에 대시보드 작업 규칙 추가:
  - "한 번에 한 패널만 수정"
  - "core.js 수정은 Brain 승인 필요"
  - "CSS 하드코딩 금지 → 토큰 참조만"
  - "3-depth 이상 CSS 중첩 금지"

**6. Panel Scaffold 자동 생성 (Medium)**
- `python3 build_dashboard.py --new-panel {id}` 명령어 추가.
- 자동 생성: `partials/{id}.html` + `css/panels/{id}.css` + `js/panels/{id}.js` + `_panel.json`.

### 보류 항목 (YAGNI)
- WebSocket 실시간 (Step 3) — window.state로 충분
- Layout 드래그/프리셋 — 현재 필요 없음
- 파서 플러그인 고도화(외부 API 연동) — 외부 API 붙이기 전까지 단일 parser.py 유지
- 크로스-패널 이벤트 버스 — 실제 요구가 생길 때 추가

---

## 최종 결정

### **조건부 진행 (Conditional GO)**

양쪽 엔진 모두 "조건부 진행" 판단. Brain도 동의합니다.

**Phase 1 착수 전 필수 선행 조건:**
1. ARCHITECTURE.md를 v1.2로 업데이트 (위 6개 반영 항목)
2. CLAUDE.md에 대시보드 작업 규칙 추가
3. Phase 0(Golden Master 스냅샷) 실행

이 3개 완료 후 CC팀에 Phase 1 리팩토링 위임.

---

## 마이그레이션 Phase 수정

| Phase | 내용 | 변경사항 |
|-------|------|---------|
| **Phase 0 (NEW)** | Golden Master 스냅샷 + 더미 앱 PoC | 신규 추가 |
| **Phase 1** | 골격 구조 + Jinja2 빌드러너 | 레지스트리 자동생성, http_server=True 반영 |
| **Phase 2** | 템플릿 분리 + 디자인 토큰 | macros.html 포함 |
| **Phase 3** | 버그 수정 + window.state 실시간 | fetch 대신 window.state |
| **Phase 4** | 프로덕션 빌드 | py2app + pyinstaller 양쪽 테스트 |
