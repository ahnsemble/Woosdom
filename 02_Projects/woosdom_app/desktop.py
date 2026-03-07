#!/usr/bin/env python3
"""
desktop.py — Woosdom Command Center v2 데스크톱 앱

PyWebView + Jinja2 6패널 대시보드.
파일 변경 감지 → HTML 재빌드 → 자동 리로드.
"""

import webview
import threading
import time
import os
import sys
import subprocess
import webbrowser
import re
from pathlib import Path

# 모듈 경로 보장 — PyInstaller frozen 환경과 개발 환경 모두 대응
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    SCRIPT_DIR = sys._MEIPASS
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from build_dashboard_v2 import build as build_v2

# ─── 경로 설정 ───────────────────────────────────
if getattr(sys, 'frozen', False):
    # Frozen (.app): vault 경로를 환경변수 또는 기본값으로
    VAULT_ROOT = Path(os.environ.get(
        "WOOSDOM_VAULT",
        os.path.expanduser("~/Desktop/Dev/Woosdom_Brain"),
    ))
else:
    # 개발 환경: woosdom_app → 02_Projects → Woosdom_Brain
    VAULT_ROOT = Path(SCRIPT_DIR).resolve().parent.parent

WATCH_FILES = [
    str(VAULT_ROOT / "00_System" / "Prompts" / "Ontology" / "active_context.md"),
    str(VAULT_ROOT / "00_System" / "Logs" / "agent_activity.md"),
    str(VAULT_ROOT / "00_System" / "Logs" / "bridge.log"),
    str(VAULT_ROOT / "00_System" / "Logs" / "watcher.log"),
    str(VAULT_ROOT / "02_Projects" / "task_bridge" / ".cost_stats.json"),
    str(VAULT_ROOT / "01_Domains" / "Finance" / "portfolio.json"),
    "/tmp/woosdom-taskbridge.log",
]
# agents 스펙 디렉토리 (mtime 변경 감지)
AGENTS_SPEC_DIR = str(VAULT_ROOT / "00_System" / "Specs" / "agents")

POLL_INTERVAL = 5  # 초 (Jinja2 rebuild 비용 감안)

WINDOW_TITLE = "Woosdom"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 860
if getattr(sys, 'frozen', False):
    INDEX_FILE = "/tmp/woosdom/index_v2.html"
else:
    INDEX_FILE = os.path.join(SCRIPT_DIR, "index_v2.html")


# ─── 빌드 함수 ──────────────────────────────────

def build_and_get_url() -> str:
    """build_v2() 실행 → index_v2.html 생성 후 file:// URL 반환."""
    build_v2()
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
    # agents 스펙 디렉토리 mtime
    try:
        mt = os.path.getmtime(AGENTS_SPEC_DIR)
        if AGENTS_SPEC_DIR not in _file_mtimes or _file_mtimes[AGENTS_SPEC_DIR] != mt:
            _file_mtimes[AGENTS_SPEC_DIR] = mt
            changed = True
    except OSError:
        pass
    return changed


def watcher_loop(window):
    """백그라운드 스레드: 파일 변경 감지 → HTML 재빌드 → 페이지 리로드."""
    check_files_changed()  # 초기 mtime 기록
    while not _shutdown.is_set():
        _shutdown.wait(POLL_INTERVAL)
        if _shutdown.is_set():
            break
        try:
            if check_files_changed():
                build_v2()
                window.evaluate_js('location.reload()')
                print(f"[MC] Rebuilt + reloaded at {time.strftime('%H:%M:%S')}")
        except Exception as e:
            if _shutdown.is_set():
                break
            print(f"[MC] Watcher error: {e}")


# ─── 퀵런처 API ──────────────────────────────────

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
    file_url = build_and_get_url()

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

    webview.start(
        func=watcher_loop,
        args=(window,),
        debug=False,
        http_server=True,
    )


if __name__ == "__main__":
    main()
