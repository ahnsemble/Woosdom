# Phase 0 PoC 검증 결과
*Date: 2026-02-25*

## 환경
- Python: 3.14.2
- PyWebView: 6.1 ✅ (6.0+ 필요 — 충족)
- Jinja2: 3.1.6 ✅
- psutil: 설치됨
- OS: macOS Darwin 25.3.0

## PoC A: http_server=True 에셋 로딩
- 파일: `poc/poc_app.py`, `poc_index.html`, `poc_style.css`, `poc_script.js`
- 검증 방법: `python3 poc/poc_app.py` 실행 → GUI 확인
  - CSS 적용됨 (h1 cyan색)?
  - 스프라이트 이미지 보임?
  - JS 실행됨 (title에 " — JS OK" 추가)?
- 상태: **수동 실행 필요** (GUI 앱)

## PoC B: window.state 이벤트
- 파일: `poc/poc_state.py`, `poc_state.html`
- 검증 방법: `python3 poc/poc_state.py` 실행 → GUI 확인
  - 3초 후 counter=1?
  - 5초 후 counter=2?
  - 7초 후 message="Hello from Python"?
- PyWebView 6.1 → window.state 지원 확인됨 (릴리즈 노트 기준)
- 상태: **수동 실행 필요** (GUI 앱)

## PoC C: psutil 좀비 정리
- 파일: `poc/poc_zombie.py`
- 실행 결과: ✅ 성공
  ```
  정리된 프로세스: 없음  (포트 23948 점유 없음 — 정상)
  [PoC C] psutil 좀비 정리 실행 성공
  ```
- macOS 권한 이슈: `psutil.net_connections()` 전체 스캔 → AccessDenied
  → `lsof -ti tcp:{port}` 대안으로 해결
- 상태: ✅ PASS

## PyInstaller PoC
- 버전: 6.19.0
- 명령: `pyinstaller --onedir --windowed --add-data "poc_index.html:." ...`
- 결과: ✅ `poc/dist/PocApp.app` 생성 (41MB)
- 상태: ✅ PASS (빌드 성공)
- 수동 확인 필요: Applications 폴더 이동 후 실행

## 비고
- macOS에서 psutil.net_connections()는 root 권한 필요
- 좀비 정리는 lsof 기반으로 구현 (macOS 기본 제공)
- PyWebView 6.1이 설치되어 window.state 지원 확정 (Phase 3에서 활용)
