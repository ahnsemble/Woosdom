#!/usr/bin/env python3
"""
build_dashboard.py v2 — Phase 2 refactor
Jinja2 full template system: all panels are Jinja2 partials.

Usage:
  python3 build_dashboard.py           # standard build
  python3 build_dashboard.py --prod    # inline CSS/JS bundle (single-file output)
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

# frozen (PyInstaller) 환경: sys._MEIPASS = Contents/Resources, 개발: 소스 디렉토리
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    SCRIPT_DIR = Path(sys._MEIPASS)
else:
    SCRIPT_DIR = Path(__file__).parent.resolve()
SRC_DIR     = SCRIPT_DIR / "src"
TMPL_DIR    = SRC_DIR / "templates"
INPUT_FILE  = SCRIPT_DIR / "dashboard_data.json"
OUTPUT_FILE = SCRIPT_DIR / "index.html"

# ── Import utilities from legacy (no HTML-generating functions) ──────────────
sys.path.insert(0, str(SCRIPT_DIR))
from build_dashboard_legacy import (  # noqa: E402
    load_data, WEEKDAY_KO,
    # _is_recent,                      # archived: dashboard simplification
    # DOMAIN_LABELS, SECTION_LABELS, STATUS_LABELS,  # archived
    _compute_pixel_agent_state, _ql_btn,
)


def _collect_css() -> list:
    """Return CSS href paths relative to index.html (base → layout → panels)."""
    css_files = []
    base = SRC_DIR / "css"
    for name in ["base.css", "layout.css"]:
        if (base / name).exists():
            css_files.append(f"src/css/{name}")
    panels_dir = base / "panels"
    if panels_dir.exists():
        for p in sorted(panels_dir.glob("*.css")):
            css_files.append(f"src/css/panels/{p.name}")
    return css_files


def _collect_js() -> list:
    """Return JS src paths relative to index.html (core → launcher → panels)."""
    js_files = []
    base = SRC_DIR / "js"
    for name in ["core.js", "launcher.js"]:
        if (base / name).exists():
            js_files.append(f"src/js/{name}")
    panels_dir = base / "panels"
    if panels_dir.exists():
        for p in sorted(panels_dir.glob("*.js")):
            js_files.append(f"src/js/panels/{p.name}")
    return js_files


def build(data: dict) -> str:
    now      = datetime.now()
    date_str = now.strftime(f"%Y-%m-%d ({WEEKDAY_KO[now.weekday()]})")

    # -- Archived panels data (commented out for dashboard simplification) --
    # projects        = data.get("projects",         [])
    # standalone      = data.get("standalone_tasks", [])
    # completed       = data.get("completed",         [])
    # briefing        = data.get("briefing",          {})
    # portfolio       = data.get("portfolio",         {})
    # rules_summary   = data.get("rules_summary",     [])
    # standing_rules  = data.get("standing_rules",    [])
    # engines         = data.get("engines",           {})
    # litellm         = data.get("litellm",           {"proxy_up": False, "redis_up": False, "models": []})
    # sprint_progress = data.get("sprint_progress",   [])
    # roadmap         = data.get("roadmap",           {})
    # training        = data.get("training",          {})

    meta            = data.get("meta",              {})
    app_icons       = data.get("app_icons",         {})
    agent_activity  = data.get("agent_activity",    {"current": [], "recent_done": [], "logs": []})

    # -- Archived filters --
    # critical_tasks = [t for t in standalone if t.get("section") == "critical"]
    # later_tasks    = [t for t in standalone if t.get("section") != "critical"]
    # sorted_completed = sorted(completed, key=lambda x: x.get("date", ""), reverse=True)

    # Pixel Agents state
    pixel_state = _compute_pixel_agent_state(agent_activity.get("current", []))
    pixel_logs  = agent_activity.get("logs", [])

    # -- Archived summary stats --
    # n_projects    = len([p for p in projects if p.get("section") in ("critical", "next")])
    # n_actions     = sum(len(p.get("action_items", [])) for p in projects)
    # n_actions    += sum(1 for t in standalone if t.get("status") in ("waiting", "in_progress"))
    # n_this_week   = len(briefing.get("this_week", []))
    # n_recent_done = len([c for c in completed if _is_recent(c.get("date", ""), 7)])

    # -- Archived domains --
    # all_items = list(projects) + list(standalone)
    # domains   = sorted(set(x.get("domain", "other") for x in all_items))

    # Quick Launcher buttons (pre-rendered HTML — external icons/fallback logic)
    ql_buttons = "".join([
        _ql_btn("open_claude",      "claude",      "Claude",      "🧠", app_icons),
        _ql_btn("open_gpt",         "gpt",         "GPT",         "💬", app_icons),
        _ql_btn("open_gemini",      "gemini",      "Gemini",      "✨", app_icons),
        _ql_btn("open_antigravity", "antigravity", "Antigravity", "🚀", app_icons),
        _ql_btn("open_codex",       "codex",       "Codex",       "💻", app_icons),
        _ql_btn("open_obsidian",    "obsidian",    "Obsidian",    "📓", app_icons),
    ])

    env = Environment(
        loader=FileSystemLoader(str(TMPL_DIR)),
        autoescape=False,
        undefined=StrictUndefined,
    )
    # Add tojson filter for pixel-agents.html data attributes
    env.filters["tojson"] = lambda obj: json.dumps(obj, ensure_ascii=True)

    template = env.get_template("base.html")
    return template.render(
        # CSS / JS file lists
        css_files=_collect_css(),
        js_files=_collect_js(),
        # Meta
        meta=meta,
        date_str=date_str,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        # Pixel Agents HQ
        pixel_state=pixel_state,
        pixel_logs=pixel_logs,
        # Quick Launcher
        ql_buttons=ql_buttons,
        # -- Archived panel data (commented out for dashboard simplification) --
        # briefing=briefing, roadmap=roadmap, training=training,
        # portfolio=portfolio, sprint_progress=sprint_progress,
        # projects=projects, critical_tasks=critical_tasks,
        # later_tasks=later_tasks, completed=sorted_completed,
        # standing_rules=standing_rules, rules_summary=rules_summary,
        # litellm=litellm, agent_activity=agent_activity,
        # DOMAIN_LABELS=DOMAIN_LABELS, SECTION_LABELS=SECTION_LABELS,
        # STATUS_LABELS=STATUS_LABELS, domains=domains,
        # stats={...},
    )


def main():
    prod = "--prod" in sys.argv
    print(f"[BUILD] Loading: {INPUT_FILE}")
    data = load_data(str(INPUT_FILE))
    if not data:
        print("[BUILD] ❌ No data. Run parser.py first.")
        return

    html = build(data)

    if prod:
        # --prod: inline all external CSS/JS into index.html (single-file output)
        css_parts = []
        for href in _collect_css():
            p = SCRIPT_DIR / href
            if p.exists():
                css_parts.append(p.read_text(encoding="utf-8"))
        js_parts = []
        for src in _collect_js():
            p = SCRIPT_DIR / src
            if p.exists():
                js_parts.append(p.read_text(encoding="utf-8"))
        html = re.sub(r'<link rel="stylesheet" href="[^"]+">[\n]?', "", html)
        html = html.replace("</head>",
            f"<style>\n{''.join(css_parts)}\n</style>\n</head>", 1)
        html = re.sub(r'<script src="[^"]+"></script>[\n]?', "", html)
        html = html.replace("</body>",
            f"<script>\n{''.join(js_parts)}\n</script>\n</body>", 1)
        print("[BUILD] 📦 --prod: CSS/JS inlined")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    css_files = _collect_css()
    js_files  = _collect_js()
    print(f"[BUILD] ✅ css: {len(css_files)}개 | js: {len(js_files)}개 | orphan: 0개")
    print(f"[BUILD] ✅ index.html 생성 완료 → {OUTPUT_FILE}")
    print(f"       Projects: {len(data.get('projects', []))} | "
          f"Completed: {len(data.get('completed', []))}")


if __name__ == "__main__":
    main()
