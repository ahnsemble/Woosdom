# Gemini Deep Research — 2차 검증 프롬프트
*Target: ARCHITECTURE.md v1.2 + CLAUDE.md*
*Date: 2026-02-25*
*Purpose: 1차 리뷰 반영 검증 + 실전 기술 검증 (웹 리서치 기반)*

---

## 배경

아래에 첨부된 문서 2개는 **PyWebView 기반 데스크톱 대시보드**의 아키텍처 설계서(v1.2)와 AI 코딩 에이전트 작업 규칙(CLAUDE.md)입니다.

이 설계서는 1차 Peer Review(GPT + Gemini)를 거쳐 다음 6개 핵심 보완사항을 반영한 v1.2입니다:

1. 렌더링 전략 단일화: fetch/polling 폐기 → PyWebView `window.state` 채택
2. 레지스트리 자동생성: 수동 JSON → `os.walk` 기반 디렉토리 스캔
3. PyWebView `http_server=True` 강제 + pyinstaller 대안 병행
4. Phase 0 추가 (Golden Master + PoC)
5. CLAUDE.md 배포 (AI 에이전트 작업 규칙)
6. Panel Scaffold 자동 생성 (`--new-panel` 명령어)

이번 리서치의 목적은 **v1.2의 기술적 결정들을 실전 사례/문서/이슈 기반으로 검증**하는 것입니다.

---

## 리서치 관점 (5개)

### 관점 1: PyWebView `window.state` 실전 검증

v1.2의 가장 큰 기술적 결정은 fetch/polling을 폐기하고 PyWebView 6.0의 `window.state`를 실시간 통신 수단으로 채택한 것입니다.

웹에서 다음을 리서치하세요:
- PyWebView 6.0의 `window.state` 기능이 실제로 안정적인가? GitHub Issues, 릴리스 노트, 사용자 보고 기반.
- `window.state`의 알려진 제한사항은? (중첩 객체 감지 실패 외에 추가적인 것이 있는가?)
- `window.state` vs `evaluate_js()` vs JS API bridge(`window.pywebview.api`)의 실전 비교. 어떤 상황에서 어떤 방식이 우월한가?
- `window.state` 채택 시 macOS WKWebView에서의 특이 동작이나 버그가 보고된 적 있는가?
- 실제 프로젝트에서 `window.state`를 사용한 오픈소스 사례가 있는가?

### 관점 2: `http_server=True` + pyinstaller 배포 파이프라인 실전 검증

v1.2는 `http_server=True`를 강제하고, py2app 대신 pyinstaller를 대안으로 병행 테스트합니다.

웹에서 다음을 리서치하세요:
- PyWebView의 `http_server=True` 모드에서 알려진 문제점은? (포트 충돌, 좀비 프로세스, 방화벽 팝업 등)
- pyinstaller로 PyWebView 앱을 패키징한 실전 사례와 알려진 함정은?
- pyinstaller `--onefile` vs `--onedir` 모드에서 PyWebView 에셋 로딩 차이는?
- macOS에서 pyinstaller로 만든 앱의 코드 사이닝(Code Signing)/노터라이제이션(Notarization) 이슈는?
- py2app의 Applications 폴더 버그가 실제로 존재하는가? 최신 PyWebView에서도 여전한가?

### 관점 3: AI 에이전트 프로젝트 규칙 파일 (CLAUDE.md) 효용성

v1.2에서 CLAUDE.md를 도입하여 AI 코딩 에이전트의 행동을 통제합니다.

웹에서 다음을 리서치하세요:
- Claude Code의 CLAUDE.md 공식 가이드라인과 권장 구조는? 현재 CLAUDE.md가 이 가이드라인에 부합하는가?
- Cursor의 `.cursorrules` 파일과 CLAUDE.md의 효용성 비교. 실제 사용자 경험/사례는?
- AI 코딩 에이전트가 프로젝트 규칙 파일을 "무시"하는 알려진 패턴은? (컨텍스트 길이 초과, 규칙 간 충돌, 모호한 표현 등)
- "한 번에 한 파일만 수정" 같은 규칙이 실제로 AI 에이전트의 작업 품질을 높였다는 사례/연구가 있는가?
- 효과적인 AI 프로젝트 규칙의 공통 패턴은? (Do/Don't 형식, 예시 포함, 우선순위 명시 등)

### 관점 4: Jinja2 정적 빌드 + 자동 디스커버리 패턴 실전 검증

v1.2는 `os.walk`로 패널 디렉토리를 스캔하여 레지스트리를 자동 생성합니다.

웹에서 다음을 리서치하세요:
- Python 프로젝트에서 플러그인/모듈 자동 디스커버리 패턴의 모범 사례는? (setuptools entry_points, importlib, stevedore, 직접 디렉토리 스캔 등)
- `os.walk` 기반 디스커버리의 알려진 엣지케이스나 함정은? (.DS_Store, __pycache__, 심볼릭 링크, 파일명 규칙 위반 등)
- Jinja2 + `StrictUndefined` 조합을 실전에서 사용한 프로젝트 사례와 장단점은?
- 정적 사이트 생성기(Hugo, Pelican, Nikola 등)에서 "컨텐츠 자동 발견" 패턴이 어떻게 구현되어 있는가? 본 설계와 비교.

### 관점 5: v1.2 종합 평가 + 잔여 리스크

위 4개 관점의 리서치 결과를 종합하여:
- v1.2가 1차 리뷰의 지적사항을 실질적으로 해결했는가?
- 새롭게 발견된 기술적 리스크는?
- Phase 0 → Phase 1 전환 시 가장 큰 병목은?
- 1인 개발 + AI 에이전트 위임 환경에서 이 아키텍처가 실제로 작동할 확률은?

---

## 출력 형식

각 관점별로:
1. **리서치 결과 요약** (핵심 발견 3~5개, 출처 포함)
2. **v1.2 설계에 대한 영향** (긍정 / 부정 / 중립)
3. **잔여 리스크** (있다면)
4. **구체적 개선 제안** (있다면)

마지막에 종합:
- **전체 점수** (10점 만점, 1차 리뷰 8.5점 대비 변화)
- **"Phase 0 착수해도 되는가?"** 에 대한 명확한 답변
- **Phase 0 착수 전 반드시 확인해야 할 기술적 전제조건** (있다면, 최대 3개)

---

## 첨부 문서

아래에 ARCHITECTURE.md v1.2 전문과 CLAUDE.md 전문을 붙여넣으세요.

### 문서 1: ARCHITECTURE.md v1.2

(여기에 ARCHITECTURE.md 전문 붙여넣기)

### 문서 2: CLAUDE.md

(여기에 CLAUDE.md 전문 붙여넣기)

### 참고: 1차 Gemini 리뷰 결과

(여기에 result_gemini_deep_research.md 전문 붙여넣기)
