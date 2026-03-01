# Dashboard Architecture Peer Review — Gemini Deep Research Prompt
*Created: 2026-02-25*
*Purpose: ARCHITECTURE.md v1.1 설계서의 효용성 검증*
*Engine: Gemini Deep Research*

---

## 지시사항

아래에 첨부된 문서는 **Woosdom Dashboard**라는 개인 데스크톱 대시보드 앱의 아키텍처 설계서(v1.1)입니다.

이 설계서의 효용성과 현실성을 **웹 리서치 기반**으로 검증해주세요.

### 배경
- 1인 개발자가 AI 코딩 에이전트(Claude Code, Codex, Antigravity)에게 작업을 위임하는 구조
- 현재: Python f-string 안에 JS 500줄 + CSS 400줄이 갇혀있는 1,600줄 단일 파일 — AI 에이전트가 반복적으로 수정 실패
- 목표: AI 에이전트가 개별 파일을 정밀 수정할 수 있는 모듈형 구조로 리팩토링
- 런타임: PyWebView (macOS 데스크톱 앱) + 브라우저 직접 열기 병행
- 기술 스택: Python + Jinja2 + Vanilla JS + Vanilla CSS (No React, No Webpack)
- 빌드: `python3 build_dashboard.py` 한 줄로 완결

### 리서치 요청 — 아래 영역을 웹 검색 및 사례 조사를 통해 검증해주세요:

**1. PyWebView 실전 사례 및 함정 (Web Research Required)**
- PyWebView로 대시보드를 만든 오픈소스 프로젝트 또는 사례를 찾아주세요
- PyWebView에서 흔히 발생하는 문제(에셋 로딩, 파일 경로, CORS, 보안)가 이 설계에서 방지되어 있는가?
- PyWebView의 `url=` vs `html=` 방식의 장단점과 이 설계의 선택이 올바른가?
- py2app 빌드 시 정적 에셋 번들링 관련 공지된 이슈가 있는가?

**2. Jinja2 기반 정적 대시보드 생성기 사례 (Web Research Required)**
- Jinja2를 사용하여 HTML 대시보드를 생성하는 오픈소스 프로젝트를 찾아주세요 (예: monitoring dashboards, static site generators)
- 이런 프로젝트들이 공통적으로 겪는 한계점은? 이 설계가 그 한계를 피하고 있는가?
- Jinja2 대비 대안 템플릿 엔진(Mako, Chameleon, Nunjucks)의 장단점 비교

**3. AI 에이전트 + 코드베이스 구조 연구 (Web Research Required)**
- AI 코딩 에이전트(Cursor, Copilot, Claude Code, Codex)가 모듈형 코드베이스에서 더 높은 성공률을 보이는가에 대한 연구나 블로그 포스트가 있는가?
- "AI가 수정하기 좋은 코드 구조"에 대한 best practice가 논의된 곳이 있는가?
- 단일 파일 vs 모듈 분리 시 AI 에이전트의 작업 품질 차이에 대한 경험적 보고가 있는가?

**4. CSS Design Token / Design System 실전 (Web Research Required)**
- CSS Variables 기반 디자인 토큰 시스템의 실제 운용 사례와 한계점
- 1인 개발자가 디자인 시스템을 도입할 때의 현실적 조언 (과잉 vs 최소)
- CSS Variables가 PyWebView 내장 WebKit에서 완전히 지원되는가?

**5. Panel Registry / Plugin System 패턴 (Web Research Required)**
- JSON 레지스트리로 패널/플러그인을 관리하는 대시보드 프로젝트 사례
- 이 패턴의 알려진 함정 (registry ↔ 실제 파일 불일치, 순환 의존성 등)
- Grafana, Backstage, Metabase 같은 대시보드의 플러그인 구조와 비교 시 이 설계의 수준은?

**6. 실시간 업데이트 아키텍처 (Web Research Required)**
- PyWebView 앱에서 데이터를 실시간으로 업데이트하는 방법의 best practice
- fetch() polling vs WebSocket vs PyWebView의 evaluate_js() 콜백 — 각각의 장단점
- 유사 프로젝트에서 어떤 방식을 채택했는가?

**7. 종합 아키텍처 평가**
- 위 리서치 결과를 종합하여, 이 설계서의 현실성과 완성도를 평가
- 리서치에서 발견된 구체적 리스크와 개선 제안
- "이대로 진행해도 되는가?" 에 대한 명확한 답변

### 출력 형식

```markdown
## 1. PyWebView 실전 사례 및 함정
### 발견된 사례
- [프로젝트명](URL) — 설명
### 이 설계에 대한 시사점
- ...
### 리스크
- ...

## 2. Jinja2 대시보드 생성기 사례
(동일 형식)

...

## 7. 종합 아키텍처 평가
- 전체 점수 (10점 만점): X/10
- 리서치 기반 핵심 보완 사항 (최대 5개, 우선순위 순)
- "이대로 진행해도 되는가?" 에 대한 명확한 답변

## 참고 자료
- 검색한 URL / 논문 / 블로그 포스트 목록 (링크 포함)
```

---

## 첨부 문서

(아래에 ARCHITECTURE.md v1.1 전문을 붙여넣기)
