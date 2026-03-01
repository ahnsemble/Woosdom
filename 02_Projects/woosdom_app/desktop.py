#!/usr/bin/env python3
"""
desktop.py — Woosdom Mission Control 독립 데스크톱 앱

PyWebView 기반 네이티브 윈도우로 대시보드를 렌더링합니다.
브라우저/서버 불필요, 더블클릭으로 실행.
"""

import webview
import threading
import time
import os
import sys
import subprocess
import webbrowser
import shutil
import re
from datetime import datetime

# 모듈 경로 보장 — PyInstaller frozen 환경과 개발 환경 모두 대응
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # PyInstaller macOS bundle: data files are in sys._MEIPASS (= Contents/Resources)
    SCRIPT_DIR = sys._MEIPASS
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import base64

from parser import (
    parse_active_context,
    generate_briefing,
    parse_engines,
    parse_training,
    parse_roadmap,
    parse_agent_activity,
    parse_agent_logs,
    parse_litellm_status,
    parse_sprint_progress,
    VAULT_ROOT,
    INPUT_FILE,
    DIRECTIVE,
    TRAINING_FILE,
    ROADMAP_FILE,
    ACTIVITY_FILE,
    TO_HANDS_FILE,
    FROM_HANDS_FILE,
)
from build_dashboard import build as _build_dashboard
from build_dashboard_legacy import _compute_pixel_agent_state

# ─── 앱 아이콘 추출 ────────────────────────────────
APP_ICON_MAP = {
    "claude":       "/Applications/Claude.app",
    "gpt":          "/Applications/ChatGPT.app",
    "gemini":       None,  # 웹앱 — favicon URL 사용
    "antigravity":  "/Applications/Antigravity.app",
    "codex":        "/Applications/Codex.app",
    "obsidian":     "/Applications/Obsidian.app",
}

GEMINI_FAVICON = "https://www.gstatic.com/lamda/images/gemini_favicon_f069958c85030456e93de685481c559f160ea06b.png"


def _find_icns(app_path: str) -> str | None:
    """Info.plist의 CFBundleIconFile → .icns 경로 반환. 없으면 툴리스톱 탐색."""
    try:
        plist_path = os.path.join(app_path, "Contents", "Info.plist")
        if os.path.exists(plist_path):
            import plistlib
            with open(plist_path, "rb") as f:
                plist = plistlib.load(f)
            icon_name = plist.get("CFBundleIconFile", "")
            if icon_name:
                if not icon_name.endswith(".icns"):
                    icon_name += ".icns"
                icns_path = os.path.join(app_path, "Contents", "Resources", icon_name)
                if os.path.exists(icns_path):
                    return icns_path
    except Exception:
        pass
    # 툴리스톱: Resources 내 .icns 파일 탐색
    resources = os.path.join(app_path, "Contents", "Resources")
    if os.path.isdir(resources):
        icns_files = [f for f in os.listdir(resources) if f.endswith(".icns")]
        if icns_files:
            preferred = [f for f in icns_files if "appicon" in f.lower() or "icon" in f.lower()]
            name = preferred[0] if preferred else icns_files[0]
            return os.path.join(resources, name)
    return None


def extract_app_icons() -> dict:
    """설치된 .app에서 아이콘을 추출하여 base64 data URI로 반환."""
    icons = {}
    for key, app_path in APP_ICON_MAP.items():
        if app_path is None:
            continue
        try:
            icns_path = _find_icns(app_path)
            if not icns_path:
                continue
            # sips로 256x256 PNG 변환 (고해상도 원본 → CSS에서 축소)
            tmp_png = f"/tmp/woosdom_icon_{key}.png"
            subprocess.run(
                ["sips", "-s", "format", "png", "-z", "256", "256",
                 icns_path, "--out", tmp_png],
                capture_output=True, timeout=5,
            )
            if os.path.exists(tmp_png) and os.path.getsize(tmp_png) > 0:
                with open(tmp_png, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                icons[key] = f"data:image/png;base64,{b64}"
                os.remove(tmp_png)
        except Exception:
            pass
    # Gemini — 웹 favicon
    icons.setdefault("gemini", GEMINI_FAVICON)
    return icons

# ─── 설정 ───────────────────────────────────────
WATCH_FILES = [
    INPUT_FILE,
    DIRECTIVE,
    TRAINING_FILE,
    ROADMAP_FILE,
    ACTIVITY_FILE,
    TO_HANDS_FILE,
    FROM_HANDS_FILE,
]
POLL_INTERVAL = 2  # 초

WINDOW_TITLE = "Woosdom"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 860
INDEX_FILE = os.path.join(SCRIPT_DIR, "index.html")


# ─── 빌드 함수 ──────────────────────────────────
# 앱 아이콘 캐시 (기동 시 1회 추출, 이후 재사용)
_icon_cache = None


def load_dashboard_data() -> dict:
    """모든 소스 파일을 파싱하여 데이터 딕셔너리 반환 (HTML 빌드 없음).
    watcher_loop에서 window.state 갱신용으로 호출됨."""
    data = parse_active_context(INPUT_FILE)
    data["briefing"] = generate_briefing(data)
    data["engines"] = parse_engines(DIRECTIVE)
    data["training"] = parse_training(TRAINING_FILE)
    data["roadmap"] = parse_roadmap(ROADMAP_FILE)
    data["agent_activity"] = parse_agent_activity(ACTIVITY_FILE)
    merged_logs = []
    seen_logs = set()
    for entry in data["agent_activity"].get("logs", []) + parse_agent_logs():
        key = (
            entry.get("time", ""),
            entry.get("from", ""),
            entry.get("to", ""),
            entry.get("msg", ""),
            entry.get("status", ""),
        )
        if key in seen_logs:
            continue
        seen_logs.add(key)
        merged_logs.append(entry)
    data["agent_activity"]["logs"] = merged_logs
    data["litellm"] = parse_litellm_status()
    data["sprint_progress"] = parse_sprint_progress()

    active_agents = {a["agent"] for a in data["agent_activity"]["current"]}
    for name, info in data["engines"].items():
        if name not in active_agents:
            data["agent_activity"]["current"].append({
                "time": "",
                "agent": name,
                "domain": "",
                "task": "",
                "status": "idle",
                "note": info.get("model", ""),
            })

    # Pixel Agents 상태 (JS Canvas 실시간 갱신용)
    agent_activity = data.get("agent_activity", {})
    pixel_state = _compute_pixel_agent_state(agent_activity.get("current", []))
    data["pixel_state"] = pixel_state
    data["pixel_logs"] = agent_activity.get("logs", [])

    return data


def build_html() -> str:
    """parser + builder를 실행하여 HTML 문자열 반환."""
    global _icon_cache
    if _icon_cache is None:
        _icon_cache = extract_app_icons()

    data = load_dashboard_data()
    data["app_icons"] = _icon_cache
    return _build_dashboard(data)


def build_index_file() -> str:
    """현재 대시보드를 index.html로 저장하고 file:// URL 반환."""
    html = build_html()
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    return "file://" + os.path.abspath(INDEX_FILE)


# ─── 파일 감시 + 자동 리프레시 ──────────────────
_file_mtimes = {}
_shutdown = threading.Event()


def check_files_changed() -> bool:
    global _file_mtimes
    changed = False
    for fp in WATCH_FILES:
        try:
            mt = os.path.getmtime(fp)
            if fp not in _file_mtimes or _file_mtimes[fp] != mt:
                _file_mtimes[fp] = mt
                changed = True
        except OSError:
            pass
    return changed


def watcher_loop(window):
    """백그라운드 스레드: 파일 변경 감지 → window.state로 데이터 푸시.

    Phase 3: window.state.dashboard_data 갱신으로 pixel-agents 캔버스를
    페이지 리로드 없이 실시간 업데이트.
    """
    # 초기 mtime 기록
    check_files_changed()
    while not _shutdown.is_set():
        _shutdown.wait(POLL_INTERVAL)  # sleep 대신 event wait — 즉시 종료 가능
        if _shutdown.is_set():
            break
        try:
            if check_files_changed():
                new_data = load_dashboard_data()
                # 전체 재할당 (중첩 객체 반응성 보장)
                window.state.dashboard_data = new_data
                window.state.last_updated = datetime.now().isoformat()
                print(f"[MC] State updated at {time.strftime('%H:%M:%S')}")
        except Exception as e:
            if _shutdown.is_set():
                break
            print(f"[MC] Watcher error: {e}")


# ─── 퀵런처 API ──────────────────────────────────
# 백업: backup_dev.sh (3중 클라우드 백업) 호출로 전환됨 (v3.1)


class Api:
    def open_claude(self):
        subprocess.Popen(["open", "-a", "Claude"])
        return "Claude 실행됨"

    def open_gpt(self):
        subprocess.Popen(["open", "-a", "ChatGPT"])
        return "GPT 실행됨"

    def open_gemini(self):
        webbrowser.open("https://gemini.google.com")
        return "Gemini 열림"

    def open_antigravity(self):
        subprocess.Popen(["open", "-a", "Antigravity"])
        return "Antigravity 실행됨"

    def open_codex(self):
        subprocess.Popen(["open", "-a", "Codex"])
        return "Codex 실행됨"

    def open_obsidian(self):
        subprocess.Popen(["open", "-a", "Obsidian"])
        return "Obsidian 실행됨"

    def run_backup(self):
        """Dev 3중 백업 (iCloud + Google Drive + Dropbox) 실행."""
        script = "/Users/woosung/Desktop/Dev/backup_dev.sh"
        try:
            result = subprocess.run(
                ["/bin/bash", script],
                capture_output=True, text=True, timeout=300,
                encoding="utf-8",
            )
            # 출력에서 성공/실패 수 추출
            output = result.stdout
            success_m = re.search(r"성공:\s*(\d+)/3", output)
            fail_m = re.search(r"실패:\s*(\d+)/3", output)
            s = success_m.group(1) if success_m else "?"
            f = fail_m.group(1) if fail_m else "?"
            if result.returncode == 0:
                return f"✅ 3중 백업 완료 — 성공 {s}/3, 실패 {f}/3"
            else:
                return f"⚠️ 백업 종료코드 {result.returncode} — {result.stderr[:200]}"
        except subprocess.TimeoutExpired:
            return "⚠️ 백업 타임아웃 (300초)"
        except Exception as e:
            return f"❌ 백업 실패: {e}"

    def run_engine_watch(self):
        script = "/Users/woosung/Desktop/Dev/Projects/engine_watch/run_weekly.sh"
        try:
            result = subprocess.run(
                ["/bin/bash", script],
                capture_output=True, text=True, timeout=120,
            )
            log_path = "/Users/woosung/Desktop/Dev/Projects/engine_watch/logs/engine_watch.log"
            if os.path.exists(log_path):
                with open(log_path, "r") as f:
                    lines = f.readlines()[-5:]
                tail = " | ".join(l.strip() for l in lines if l.strip())
            else:
                tail = "(로그 없음)"
            if result.returncode == 0:
                return f"✅ Engine Watch 스캔 완료 — {tail}"
            else:
                return f"⚠️ Engine Watch 종료코드 {result.returncode} — {result.stderr[:200]}"
        except subprocess.TimeoutExpired:
            return "⚠️ Engine Watch 타임아웃 (120초)"
        except Exception as e:
            return f"❌ Engine Watch 실패: {e}"


# ─── 엔트리포인트 ────────────────────────────────
def main():
    file_url = build_index_file()

    api = Api()
    window = webview.create_window(
        WINDOW_TITLE,
        url=file_url,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        resizable=True,
        text_select=True,
        js_api=api,
    )

    def on_closing():
        _shutdown.set()

    window.events.closing += on_closing

    # 파일 감시 스레드를 webview 시작 후 실행
    webview.start(
        func=watcher_loop,
        args=(window,),
        debug=False,
        http_server=True,
    )


if __name__ == "__main__":
    main()
