# Woosdom v0.3

## Quick Start

### 데스크톱 앱 (권장)
pip3 install pywebview
cd /Users/woosung/Desktop/Dev/Woosdom_Brain/02_Projects/woosdom_app
python3 desktop.py

### .app 번들 빌드
pip3 install pywebview py2app
python3 setup.py py2app -A    # 개발용 (소스 링크)
python3 setup.py py2app        # 배포용 (독립 실행)
open dist/Woosdom.app

### Flask 서버 (대안)
python3 app.py
# → http://localhost:5001

### 레거시 (정적 빌드) — ⚠️ Deprecated
./refresh.sh
# refresh.sh / refresh.command — desktop.py 도입 전 구버전 워크플로우. 삭제 가능.

## 아키텍처

### 데스크톱 앱 (v0.3+)
active_context.md ──→ parser.py ──→ build_dashboard.py ──→ PyWebView 네이티브 윈도우
       ↑
  파일 변경 감지 (polling 2초) → window.load_html() 자동 리프레시

### Flask 서버 (대안) — n8n 연동 대비 보존
localhost:5001 → SSE 라이브 리로드
app.py는 /api/data, /api/webhook, /api/refresh 엔드포인트를 제공. Phase 3 n8n 고도화 시 활용 예정.

## 의존성
- Python 3.10+
- pywebview >= 5.0 (`pip3 install pywebview`)
- py2app (빌드 시만, `pip3 install py2app`)
- flask >= 3.0 (Flask 모드 사용 시만)
