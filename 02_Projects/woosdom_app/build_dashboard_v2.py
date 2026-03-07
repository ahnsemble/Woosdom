#!/usr/bin/env python3
"""
build_dashboard_v2.py — Woosdom Command Center v2 Builder

Jinja2-based build script that:
1. Runs parsers (system, agents, activity) to collect data
2. Discovers panel CSS files automatically
3. Renders base_v2.html with data → index_v2.html
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Ensure project root is importable
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
except ImportError:
    print("[BUILD] ERROR: jinja2 not installed. Run: pip3 install jinja2")
    sys.exit(1)

from parsers.system import parse_system
from parsers.agents import parse_agents
from parsers.activity import parse_activity
from parsers.sprint import parse_sprint
from parsers.portfolio import parse_portfolio
from parsers.cost import parse_cost
from parsers.fleet import parse_fleet

if getattr(sys, 'frozen', False):
    _output_dir = Path("/tmp/woosdom")
    _output_dir.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE = _output_dir / "index_v2.html"
else:
    OUTPUT_FILE = PROJECT_ROOT / "index_v2.html"
TEMPLATES_DIR = PROJECT_ROOT / "src" / "templates"
PANELS_CSS_DIR = PROJECT_ROOT / "src" / "css" / "panels"


def read_all_css() -> str:
    """모든 CSS 파일을 읽어서 하나의 문자열로 합침."""
    css_parts = []
    # base + layout 먼저
    for name in ["base_v2.css", "layout_v2.css"]:
        p = PROJECT_ROOT / "src" / "css" / name
        if p.exists():
            css_parts.append(p.read_text(encoding="utf-8"))
    # panel CSS
    if PANELS_CSS_DIR.exists():
        for f in sorted(PANELS_CSS_DIR.glob("*.css")):
            css_parts.append(f.read_text(encoding="utf-8"))
    return "\n".join(css_parts)


def read_all_js() -> str:
    """JS 파일 읽기."""
    js_path = PROJECT_ROOT / "src" / "js" / "core_v2.js"
    if js_path.exists():
        return js_path.read_text(encoding="utf-8")
    return ""


def collect_data() -> dict:
    """Run all parsers and merge results into a single data dict."""
    data = {}
    parsers = [
        ("system", parse_system),
        ("agents", parse_agents),
        ("activity", parse_activity),
        ("sprint", parse_sprint),
        ("portfolio", parse_portfolio),
        ("cost", parse_cost),
        ("fleet", parse_fleet),
    ]

    for name, parse_fn in parsers:
        try:
            result = parse_fn()
            data.update(result)
            key_count = len(result)
            print(f"[PARSE] \u2705 {name} ({key_count} keys)")
        except Exception as e:
            print(f"[PARSE] \u274c {name}: {e}")
            # Provide empty defaults so templates don't break
            if name == "system":
                data["system"] = {
                    "brain": {"status": "offline", "consecutive_failures": 0,
                              "failure_threshold": 3, "daily_callbacks": 0,
                              "daily_callback_limit": 30, "sub_brain": "standby"},
                    "engines": {
                        "claude_code": {"status": "idle", "today_tasks": 0, "today_turns_est": 0, "today_seconds": 0},
                        "codex": {"status": "idle", "today_tasks": 0, "today_turns_est": 0, "today_seconds": 0},
                        "antigravity": {"status": "idle", "today_tasks": 0, "today_turns_est": 0, "today_seconds": 0},
                    },
                    "task_bridge": {"alive": False, "pid": None},
                    "last_updated": datetime.now().isoformat(timespec="seconds"),
                }
            elif name == "agents":
                data["agents"] = {
                    "summary": {"total": 0, "fresh": 0, "aging": 0, "stale": 0, "never": 0},
                    "departments": {},
                }
            elif name == "activity":
                data["activity"] = {"events": [], "total_events": 0, "last_event_time": None}
            elif name == "sprint":
                data["sprint"] = {"name": "No Sprint", "done": 0, "in_progress": 0,
                                  "pending": 0, "progress_pct": 0, "recent_done": []}
            elif name == "portfolio":
                data["portfolio"] = {"name": "Unknown", "holdings": [],
                                     "next_check": "", "days_until_check": 0, "drift_threshold": 10.0}
            elif name == "cost":
                data["cost"] = {"date": "", "engines": [], "brain_callbacks": 0,
                                "dangerous_blocked": 0, "monthly_total_cap": 300}
            elif name == "fleet":
                data["fleet"] = {
                    "health": {"success_rate": 100.0, "total": 0, "success": 0, "fail": 0},
                    "engines": {
                        "claude_code": {"status": "idle", "title": ""},
                        "codex": {"status": "idle", "title": ""},
                        "antigravity": {"status": "idle", "title": ""},
                    },
                    "event_feed": [],
                    "system_health": {
                        "watcher_status": "dead", "watcher_pid": None,
                        "last_beat": None, "last_beat_ago": None,
                        "uptime_seconds": 0, "uptime_display": "—",
                        "engines": {
                            "claude_code": {"status": "idle", "last_task": None},
                            "codex": {"status": "idle", "last_task": None},
                            "antigravity": {"status": "idle", "last_task": None},
                        },
                        "pending_files": [], "errors_last_hour": 0,
                    },
                }

    return data


def discover_panel_css() -> list[str]:
    """Auto-discover panel CSS files (relative paths for HTML)."""
    css_files = []
    if PANELS_CSS_DIR.exists():
        for f in sorted(PANELS_CSS_DIR.glob("*.css")):
            # Relative path from project root
            rel = f.relative_to(PROJECT_ROOT)
            css_files.append(str(rel))
    print(f"[BUILD] Panel CSS discovered: {len(css_files)} files")
    for c in css_files:
        print(f"        - {c}")
    return css_files


MODEL_SHORT_MAP = {
    "sonnet-4.5": "Sonnet 4.5",
    "sonnet-4.6": "Sonnet 4.6",
    "opus-4.6": "Opus 4.6",
    "haiku-4.5": "Haiku 4.5",
    "gemini-3.1-pro": "Gemini 3.1",
    "gemini-2.5-pro": "Gemini 2.5",
    "gpt-5.3": "GPT 5.3",
    "gpt-5.2": "GPT 5.2",
}

ENGINE_SHORT_MAP = {
    "claude_code": "CC",
    "antigravity": "AG",
    "codex": "Codex",
    "brain_direct": "Brain",
}


def _model_short(value: str) -> str:
    if not value:
        return ""
    return MODEL_SHORT_MAP.get(value, value.replace("-", " ").title())


def _engine_short(value: str) -> str:
    if not value:
        return ""
    return ENGINE_SHORT_MAP.get(value, value)


def build():
    """Main build pipeline."""
    print(f"[BUILD] Woosdom Command Center v2 — {datetime.now().isoformat(timespec='seconds')}")
    print(f"[BUILD] Project: {PROJECT_ROOT}")
    print()

    # 1. Collect data
    data = collect_data()
    print()

    # 2. Discover panel CSS
    panel_css = discover_panel_css()
    print()

    # 3. Setup Jinja2
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "htm"]),
        undefined=StrictUndefined,
    )
    env.filters["model_short"] = _model_short
    env.filters["engine_short"] = _engine_short

    # 4. Render
    template = env.get_template("base_v2.html")
    html = template.render(
        data=data,
        panel_css=panel_css,
        inline_css=read_all_css(),
        inline_js=read_all_js(),
        build_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    # 5. Write output
    OUTPUT_FILE.write_text(html, encoding="utf-8")
    size = OUTPUT_FILE.stat().st_size
    print(f"[BUILD] \u2705 {OUTPUT_FILE.name} generated ({size:,} bytes)")
    print(f"[BUILD] Open: file://{OUTPUT_FILE}")

    return 0


if __name__ == "__main__":
    sys.exit(build())
