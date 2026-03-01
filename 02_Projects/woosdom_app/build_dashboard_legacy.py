#!/usr/bin/env python3
"""
build_dashboard.py v0.2 — dashboard_data.json → index.html

Changes from v0.1:
- Briefing hero card at top (collapsible)
- Project card layout with action items, metadata, completed items
- Improved completed section (5 max, expand more)
- Updated summary cards (projects / actions / this week / recent done)
"""

import json
import os
from datetime import datetime, timedelta

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE  = os.path.join(SCRIPT_DIR, "dashboard_data.json")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "index.html")

DOMAIN_LABELS = {
    "finance": ("💰 Finance", "#4ecdc4"),
    "game":    ("🎮 Game",    "#ff6b6b"),
    "system":  ("⚙️ System",  "#a29bfe"),
    "career":  ("💼 Career",  "#ffeaa7"),
    "health":  ("💪 Health",  "#55efc4"),
    "other":   ("📌 Other",   "#b2bec3"),
}

SECTION_LABELS = {
    "critical": ("🔴 최우선", "#e74c3c"),
    "next":     ("🟡 다음",   "#f39c12"),
    "later":    ("🔵 이후",   "#3498db"),
    "done":     ("✅ 완료",   "#2ecc71"),
}

STATUS_LABELS = {
    "in_progress": ("🔄 진행 중", "#fdcb6e"),
    "waiting":     ("⏳ 대기",    "#74b9ff"),
    "done":        ("✅ 완료",    "#00b894"),
    "blocked":     ("❌ 차단",    "#e17055"),
}

WEEKDAY_KO = ["월", "화", "수", "목", "금", "토", "일"]


def load_data(filepath: str) -> dict:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] {e}")
        return {}


def esc(s: str) -> str:
    return (str(s)
            .replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def generate_html(data: dict) -> str:
    projects       = data.get("projects",        [])
    standalone     = data.get("standalone_tasks", [])
    completed      = data.get("completed",        [])
    briefing       = data.get("briefing",         {})
    portfolio      = data.get("portfolio",        {})
    rules_summary  = data.get("rules_summary",    [])
    standing_rules = data.get("standing_rules",   [])
    engines        = data.get("engines",          {})
    agent_activity = data.get("agent_activity",   {"current": [], "recent_done": []})
    litellm_data   = data.get("litellm",          {"proxy_up": False, "redis_up": False, "models": []})
    sprint_progress= data.get("sprint_progress",  [])
    meta           = data.get("meta",             {})
    app_icons      = data.get("app_icons",        {})

    # Summary stats
    n_projects    = len([p for p in projects if p.get("section") in ("critical","next")])
    n_actions     = sum(len(p.get("action_items",[])) for p in projects)
    n_actions    += sum(1 for t in standalone if t.get("status") in ("waiting","in_progress"))
    n_this_week   = len(briefing.get("this_week", []))
    n_recent_done = len([c for c in completed if _is_recent(c.get("date",""), 7)])

    # Domains present
    all_items  = list(projects) + list(standalone)
    domains    = sorted(set(x.get("domain","other") for x in all_items))

    now = datetime.now()
    weekday_str = WEEKDAY_KO[now.weekday()]
    date_str = now.strftime(f"%Y-%m-%d ({weekday_str})")

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Woosdom Mission Control</title>
<style>
{_css()}
</style>
</head>
<body>

<!-- ── Header ────────────────────────────────────── -->
<header class="header">
  <div class="header-content">
    <div class="header-left">
      <h1>🧠 Woosdom Mission Control</h1>
      <p class="subtitle">Active Context Dashboard</p>
    </div>
    <div class="header-right">
      <button class="theme-toggle" onclick="toggleTheme()" id="theme-toggle" title="다크/라이트 모드 전환">🌙</button>
      <span class="badge badge-phase">{esc(meta.get('phase','N/A'))}</span>
      <span class="badge badge-ruleset">{esc(meta.get('ruleset','N/A'))}</span>
      <span class="badge badge-date">📅 {esc(meta.get('updated','N/A'))}</span>
    </div>
  </div>
  <!-- ── Quick Launcher ─────────────────────────── -->
  <div class="ql-bar">
    {_ql_btn('open_claude',      'claude',      'Claude',       '🧠', app_icons)}
    {_ql_btn('open_gpt',         'gpt',         'GPT',          '💬', app_icons)}
    {_ql_btn('open_gemini',      'gemini',      'Gemini',       '✨', app_icons)}
    {_ql_btn('open_antigravity', 'antigravity', 'Antigravity',  '🚀', app_icons)}
    {_ql_btn('open_codex',       'codex',       'Codex',        '💻', app_icons)}
    {_ql_btn('open_obsidian',    'obsidian',    'Obsidian',     '📓', app_icons)}
    <button class="ql-btn ql-engine" id="ql-engine-btn" onclick="launchEngineWatch()" title="Engine Watch 스캔">🔍 Engine Watch</button>
    <button class="ql-btn ql-backup" id="ql-backup-btn" onclick="launchBackup()" title="Vault 백업">💾 Backup</button>
  </div>
</header>

<!-- ── Sprint Progress ───────────────────────── -->
{_sprint_progress_html(sprint_progress)}

<!-- ── Summary Cards ──────────────────────────────── -->
<section class="summary-cards">
  <div class="card card-project">
    <div class="card-number">{n_projects}</div>
    <div class="card-label">🚀 진행 프로젝트</div>
  </div>
  <div class="card card-action">
    <div class="card-number">{n_actions}</div>
    <div class="card-label">📋 액션 아이템</div>
  </div>
  <div class="card card-week">
    <div class="card-number">{n_this_week}</div>
    <div class="card-label">📅 이번 주 할 일</div>
  </div>
  <div class="card card-done">
    <div class="card-number">{n_recent_done}</div>
    <div class="card-label">✅ 최근 7일 완료</div>
  </div>
</section>

<!-- ── Briefing Hero ───────────────────────────────── -->
{_briefing_html(briefing, date_str)}

<!-- ✨ Life Roadmap -->
{_roadmap_html(data.get("roadmap", {}))}

<!-- ✨ Today's Training -->
{_training_html(data.get('training', {}), briefing)}

<!-- ── Filter Bar ─────────────────────────────────── -->
<section class="filter-bar">
  <div class="filter-group">
    <span class="filter-label">도메인:</span>
    <button class="filter-btn active" data-domain="all">전체</button>
    {_domain_buttons(domains)}
  </div>
  <div class="filter-group">
    <span class="filter-label">우선순위:</span>
    <button class="filter-btn active" data-section="all">전체</button>
    {_section_buttons()}
  </div>
</section>

<!-- ── Critical Standalone Tasks ─────────────────── -->
{_standalone_html([t for t in standalone if t["section"] == "critical"], "critical")}

<!-- ── Projects Board ─────────────────────────────── -->
<section class="board-section">
  <div class="board-section-title">🗂 프로젝트 보드</div>
  <div class="project-grid" id="project-grid">
    {_projects_html(projects)}
  </div>
</section>

<!-- ── Later Standalone Tasks ────────────────────── -->
{_standalone_html([t for t in standalone if t["section"] != "critical"], "later")}

<!-- ── Standing Rules ──────────────────────────────── -->
{_standing_rules_html(standing_rules)}

<!-- ── Portfolio ───────────────────────────────────── -->
{_portfolio_html(portfolio)}

<!-- ── Agent Panel ──────────────────────── -->
<!-- ── LiteLLM Panel ─────────────────────── -->
{_litellm_panel_html(litellm_data)}

<!-- ── Agent Panel ──────────────────────── -->
{_agent_panel_html(agent_activity, engines)}

<!-- ── Pixel Agents HQ ──────────────────────── -->
{_pixel_agents_canvas_html(agent_activity)}

<!-- ── Rules Summary ───────────────────────────────── -->
{_rules_html(rules_summary)}

<!-- ── Completed ───────────────────────────────────── -->
{_completed_html(completed)}

<!-- ── Footer ──────────────────────────────────────── -->
<footer class="footer">
  <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Woosdom Mission Control v0.2</p>
</footer>

<script>
{_js()}
</script>
</body>
</html>"""


def _is_recent(date_str: str, days: int) -> bool:
    if not date_str:
        return False
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return (datetime.now() - d).days <= days
    except Exception:
        return False


# ─── Briefing Hero ─────────────────────────────────────────────────────────
def _briefing_html(b: dict, date_str: str) -> str:
    if not b:
        return ""
    top    = esc(b.get("top_priority", ""))
    today  = b.get("today_actions", [])
    warns  = b.get("warnings", [])
    week   = b.get("this_week", [])

    today_li = "".join(f'<li>{esc(a)}</li>' for a in today)
    warn_li  = "".join(f'<li class="warning-item">⚠️ {esc(w)}</li>' for w in warns)
    week_li  = "".join(f'<li>{esc(w)}</li>' for w in week)

    warn_block = ""
    if warns:
        warn_block = f'<div class="briefing-row"><span class="briefing-key">⚠️ 주의</span><ul class="briefing-list warning-list">{warn_li}</ul></div>'

    week_block = ""
    if week:
        week_block = f'<div class="briefing-row"><span class="briefing-key">📅 이번 주</span><ul class="briefing-list">{week_li}</ul></div>'

    return f"""<section class="briefing-section">
  <div class="briefing-card" id="briefing-card">
    <div class="briefing-header">
      <div class="briefing-title">☀️ 오늘의 브리핑 — {esc(date_str)}</div>
      <button class="briefing-toggle" onclick="toggleBriefing()" id="briefing-toggle">▲ 접기</button>
    </div>
    <div class="briefing-body" id="briefing-body">
      <div class="briefing-top-priority">
        <span class="priority-label">🎯 최우선</span>
        <span class="priority-text">{top}</span>
      </div>
      <div class="briefing-row">
        <span class="briefing-key">📋 오늘 할 일</span>
        <ol class="briefing-list">{today_li}</ol>
      </div>
      {warn_block}
      {week_block}
    </div>
  </div>
</section>"""


# ─── Quick Launcher button helper ────────────────────────────────
def _ql_btn(method: str, icon_key: str, label: str, fallback_emoji: str, icons: dict) -> str:
    icon_src = icons.get(icon_key)
    if icon_src:
        icon_html = f'<img class="ql-icon" src="{icon_src}" alt="{label}" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'inline\'"><span class="ql-emoji" style="display:none">{fallback_emoji}</span>'
    else:
        icon_html = f'<span class="ql-emoji">{fallback_emoji}</span>'
    return f'<button class="ql-btn" onclick="launchApp(\'{method}\')" title="{label}">{icon_html} {label}</button>'


def _roadmap_html(roadmap: dict) -> str:
    if not roadmap or (not roadmap.get("axes") and not roadmap.get("milestones")):
        return ""

    axes = roadmap.get("axes", [])
    milestones = roadmap.get("milestones", [])

    axis_colors = {"재산": "#4ecdc4", "기술": "#a29bfe", "체력": "#ff6b6b", "가정": "#ffeaa7"}

    axes_html = ""
    for ax in axes:
        color = axis_colors.get(ax["name"], "#b2bec3")
        axis_id = ax["name"]
        axes_html += f"""<div class="axis-card clickable" style="border-top:3px solid {color};" onclick="filterMilestones('{esc(axis_id)}')" title="클릭하여 마일스톤 보기">
  <div class="axis-icon">{esc(ax["icon"])}</div>
  <div class="axis-name" style="color:{color};">{esc(ax["name"])}</div>
  <div class="axis-status">{esc(ax["status"])}</div>
  <div class="axis-metric">{esc(ax["metric"])}</div>
</div>"""

    ms_html = ""
    for ms in milestones:
        status = ms.get("status", "waiting")
        if status == "in_progress":
            dot_cls, line_cls = "ms-dot active", "ms-line active"
        elif status == "done":
            dot_cls, line_cls = "ms-dot done", "ms-line done"
        else:
            dot_cls, line_cls = "ms-dot", "ms-line"

        ms_html += f"""<div class="ms-item" data-axis="{esc(ms['axis'])}">
  <div class="ms-left">
    <div class="{dot_cls}"></div>
    <div class="{line_cls}"></div>
  </div>
  <div class="ms-content">
    <span class="ms-time">{esc(ms["time"])}</span>
    <span class="ms-text">{esc(ms["milestone"])}</span>
    <span class="ms-axis badge-sm" style="background:rgba(255,255,255,.06);">{esc(ms["axis"])}</span>
  </div>
</div>"""

    n_done = sum(1 for ms in milestones if ms.get('status') == 'done')
    n_prog = sum(1 for ms in milestones if ms.get('status') == 'in_progress')
    n_total = len(milestones)
    ms_summary = f"{n_done + n_prog}/{n_total} 진행"

    return f"""<section class="board-section">
  <div class="board-section-title">🏗️ 인생 로드맵 — Hexagonal Life</div>
  <div class="axes-grid">{axes_html}</div>
  <div class="ms-filter-hint">💡 축 카드를 클릭하면 해당 마일스톤만 표시됩니다 <button class="ms-reset-btn" onclick="filterMilestones('all')">전체 보기</button> <span class="toggle-badge">{ms_summary}</span></div>
  <div class="milestone-timeline" id="ms-timeline">{ms_html}</div>
</section>"""


def _training_html(training: dict, briefing: dict = None) -> str:
    if not training:
        return ""
    if briefing is None:
        briefing = {}

    today      = training.get("today", {})
    exercises  = training.get("today_exercises", [])
    weekly     = training.get("weekly", [])
    progression= training.get("progression", [])
    stats      = training.get("stats", {})

    day_name = today.get("day", "?")
    morning  = today.get("morning", "—")
    evening  = today.get("evening", "—")
    load     = today.get("load", "—")

    load_colors = {"HIGH": "#e74c3c", "MOD-HIGH": "#e67e22", "LOW-MOD": "#f39c12", "LOW": "#2ecc71", "ZERO": "#636e72"}
    load_color  = load_colors.get(load, "#b2bec3")

    # Today exercises table
    ex_html = ""
    if load == "ZERO":
        ex_html = '<div class="rest-day">🛌 완전 휴식일</div>'
    elif exercises:
        rows = "".join(
            f'<tr><td class="ex-order">{esc(e["order"])}</td><td class="ex-name">{esc(e["name"])}</td>'
            f'<td class="ex-spec">{esc(e["spec"])}</td><td class="ex-rest">{esc(e["rest"])}</td>'
            f'<td class="ex-purpose">{esc(e["purpose"])}</td></tr>'
            for e in exercises
        )
        ex_html = f"""<div class="training-exercises">
  <table class="ex-table">
    <thead><tr><th></th><th>운동</th><th>규격</th><th>휴식</th><th>목적</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</div>"""

    # Weekly mini schedule
    week_html = ""
    for w in weekly:
        cls  = "week-day today" if w["is_today"] else "week-day"
        wlc  = load_colors.get(w["load"], "#636e72")
        week_html += f"""<div class="{cls}">
  <div class="week-day-name">{esc(w["day"])}</div>
  <div class="week-day-load" style="color:{wlc};">{esc(w["load"])}</div>
  <div class="week-day-am">{esc(w["morning"][:20])}</div>
  <div class="week-day-pm">{esc(w["evening"][:15])}</div>
</div>"""

    # Progression table
    prog_html = ""
    if progression:
        prog_rows = "".join(
            f'<tr><td>{esc(p["exercise"])}</td><td>{esc(p["current"])}</td>'
            f'<td class="prog-target">{esc(p["target_12w"])}</td><td class="prog-long">{esc(p["long_term"])}</td></tr>'
            for p in progression
        )
        prog_html = f"""<div class="prog-section">
  <div class="proj-section-label">📈 프로그레션</div>
  <table class="prog-table">
    <thead><tr><th>운동</th><th>현재</th><th>12주 목표</th><th>장기 목표</th></tr></thead>
    <tbody>{prog_rows}</tbody>
  </table>
</div>"""

    # Stats bar
    stats_html = ""
    if stats:
        stats_html = f"""<div class="training-stats">
  <span class="stat-item">⚖️ {esc(stats.get('weight',''))}</span>
  <span class="stat-item">🏋️ Big 3: {esc(stats.get('big3',''))}</span>
  <span class="stat-item">📋 {esc(stats.get('protocol',''))}</span>
</div>"""

    # Today tasks from briefing
    today_actions = briefing.get("today_actions", [])
    tasks_html = ""
    if today_actions:
        tasks_li = "".join(f'<li>{esc(a)}</li>' for a in today_actions)
        tasks_html = f"""<div class="today-tasks">
  <div class="today-tasks-title">📋 오늘 할 일</div>
  <ul class="today-task-list">{tasks_li}</ul>
</div>"""

    # Collapsible exercises
    ex_collapsible = ""
    if ex_html:
        n_ex = len(exercises)
        ex_collapsible = f"""<button class="collapsible-toggle" onclick="toggleSection('training-exercises')">
    🏋️ 운동 세부 <span class="toggle-badge">{n_ex}개</span> <span id="training-exercises-arrow">▼</span>
  </button>
  <div class="collapsible-body hidden" id="training-exercises">{ex_html}</div>"""

    # Collapsible progression
    prog_collapsible = ""
    if prog_html:
        prog_collapsible = f"""<button class="collapsible-toggle" onclick="toggleSection('training-progression')">
    📈 프로그레션 <span class="toggle-badge">{len(progression)}개</span> <span id="training-progression-arrow">▼</span>
  </button>
  <div class="collapsible-body hidden" id="training-progression">{prog_html}</div>"""

    return f"""<section class="board-section">
  <div class="board-section-title">💪 오늘의 운동 — {esc(day_name)}요일</div>
  <div class="training-hero">
    <div class="training-today-card">
      <div class="training-load" style="color:{load_color};">부하: {esc(load)}</div>
      <div class="training-sessions">
        <div class="session-block">
          <span class="session-label">🌅 새벽 5:30</span>
          <span class="session-name">{esc(morning)}</span>
        </div>
        <div class="session-block">
          <span class="session-label">🌆 저녁 18:00</span>
          <span class="session-name">{esc(evening)}</span>
        </div>
      </div>
    </div>
    {stats_html}
    {tasks_html}
  </div>
  {ex_collapsible}
  <div class="week-schedule-title">📅 주간 스케줄</div>
  <div class="week-schedule">{week_html}</div>
  {prog_collapsible}
</section>"""


# ─── Domain / Section filter buttons ───────────────────────────────────────
def _domain_buttons(domains: list) -> str:
    parts = []
    for d in domains:
        label, color = DOMAIN_LABELS.get(d, (d, "#b2bec3"))
        parts.append(f'<button class="filter-btn" data-domain="{d}">{label}</button>')
    return "\n    ".join(parts)


def _section_buttons() -> str:
    parts = []
    for key, (label, _) in SECTION_LABELS.items():
        parts.append(f'<button class="filter-btn" data-section="{key}">{label}</button>')
    return "\n    ".join(parts)


# ─── Standalone task cards ──────────────────────────────────────────────────
def _standalone_html(tasks: list, label_section: str) -> str:
    if not tasks:
        return ""
    label, color = SECTION_LABELS.get(label_section, ("", "#b2bec3"))
    cards = "".join(_standalone_card(t) for t in tasks)
    return f"""<section class="board-section">
  <div class="board-section-title" style="color:{color};">{label}</div>
  <div class="standalone-grid">{cards}</div>
</section>"""


def _standalone_card(t: dict) -> str:
    domain   = t.get("domain",  "other")
    section  = t.get("section", "")
    status   = t.get("status",  "waiting")
    title    = esc(t.get("title",  ""))
    detail   = esc(t.get("detail", "")[:250])
    subs     = t.get("sub_items", [])
    d_label, d_color = DOMAIN_LABELS.get(domain,  ("Other", "#b2bec3"))
    s_label, s_color = STATUS_LABELS.get(status, ("?", "#b2bec3"))
    sec_col  = SECTION_LABELS.get(section, ("", "#b2bec3"))[1]

    sub_html = ""
    if subs:
        items = "".join(f"<li>{esc(s)}</li>" for s in subs[:8])
        sub_html = f'<ul class="task-sub">{items}</ul>'

    return f"""<div class="task-card" data-domain="{domain}" data-section="{section}"
     style="border-left-color:{sec_col};">
  <div class="task-header">
    <div class="task-title">{title}</div>
    <div class="task-badges">
      <span class="badge-sm" style="background:{d_color}22;color:{d_color};border:1px solid {d_color}44;">{d_label}</span>
      <span class="badge-sm" style="background:{s_color}22;color:{s_color};border:1px solid {s_color}44;">{s_label}</span>
    </div>
  </div>
  {f'<div class="task-detail">{detail}</div>' if detail else ''}
  {sub_html}
</div>"""


# ─── Project Cards ───────────────────────────────────────────────────────────
def _projects_html(projects: list) -> str:
    if not projects:
        return '<p class="empty-msg">프로젝트가 없습니다.</p>'
    return "".join(_project_card(p) for p in projects)


def _project_card(p: dict) -> str:
    domain   = p.get("domain",   "other")
    section  = p.get("section",  "next")
    status   = p.get("status",   "waiting")
    name     = esc(p.get("name",     ""))
    subtitle = esc(p.get("subtitle", ""))
    actions  = p.get("action_items",    [])
    notes    = p.get("notes",           [])
    compl    = p.get("completed_items", [])
    meta     = p.get("metadata",        {})

    d_label, d_color = DOMAIN_LABELS.get(domain,  ("Other", "#b2bec3"))
    s_label, s_color = STATUS_LABELS.get(status, ("?", "#b2bec3"))
    sec_label, sec_color = SECTION_LABELS.get(section, ("", "#b2bec3"))

    # "현재 단계" prominently shown
    current_stage = esc(meta.get("현재 단계", meta.get("현재단계", "")))

    # Action items
    action_html = ""
    if actions:
        items = "".join(f'<li class="action-item"><span class="check-box">□</span> {esc(a)}</li>' for a in actions)
        action_html = f'<div class="proj-section"><div class="proj-section-label">📋 다음 액션</div><ul class="action-list">{items}</ul></div>'

    # Notes (non-warning, non-completed)
    notes_html = ""
    if notes:
        items = "".join(f'<li>{esc(n)}</li>' for n in notes[:4])
        notes_html = f'<div class="proj-section"><ul class="notes-list">{items}</ul></div>'

    # Completed items (collapsible)
    compl_html = ""
    card_id = f"compl-{abs(hash(name)) % 10000}"
    if compl:
        items = "".join(f'<li>{esc(c)}</li>' for c in compl[:8])
        compl_html = f"""<div class="proj-section">
  <button class="compl-toggle" onclick="toggleCompl('{card_id}')">✅ 완료 항목 보기 ({len(compl)})</button>
  <ul class="compl-list hidden" id="{card_id}">{items}</ul>
</div>"""

    # Metadata footer (folder, tech stack)
    meta_footer_items = []
    for key in ["프로젝트 폴더", "기술 스택", "구현"]:
        if key in meta:
            meta_footer_items.append(f'<span class="meta-tag"><strong>{esc(key)}</strong>: {esc(meta[key][:80])}</span>')
    meta_footer = ""
    if meta_footer_items:
        meta_footer = f'<div class="proj-meta-footer">{"".join(meta_footer_items)}</div>'

    # Week timeline mini-map (for Crossy etc.)
    weeks_html = ""
    weeks = meta.get("weeks", [])
    if weeks:
        chips = []
        for w in weeks:
            wnum = esc(w.get("week", ""))
            wlbl = esc(w.get("label", ""))
            wst  = w.get("status", "waiting")
            if wst == "done":
                wc = "#00b89433"; wb = "#00b894"
            elif wst in ("next", "in_progress"):
                wc = "#0984e322"; wb = "#0984e3"
            else:
                wc = "transparent"; wb = "var(--border)"
            chips.append(f'<span class="week-chip week-{wst}" title="{wlbl}" style="background:{wc};border:1px solid {wb};">W{wnum}</span>')
        weeks_html = f'<div class="week-timeline">{"".join(chips)}</div>'

    return f"""<div class="project-card" data-domain="{domain}" data-section="{section}">
  <div class="proj-header">
    <div class="proj-title-row">
      <span class="proj-domain-icon">{d_label.split()[0]}</span>
      <div class="proj-name-block">
        <div class="proj-name">{name}</div>
        {f'<div class="proj-subtitle">{subtitle}</div>' if subtitle else ''}
      </div>
    </div>
    <div class="proj-badges">
      <span class="badge-sm" style="background:{sec_color}22;color:{sec_color};border:1px solid {sec_color}44;">{sec_label}</span>
      <span class="badge-sm" style="background:{s_color}22;color:{s_color};border:1px solid {s_color}44;">{s_label}</span>
    </div>
  </div>
  {f'<div class="proj-stage">{current_stage}</div>' if current_stage else ''}
  {weeks_html}
  {action_html}
  {notes_html}
  {compl_html}
  {meta_footer}
</div>"""


# ─── Standing Rules ──────────────────────────────────────────────────────────
def _standing_rules_html(rules: list) -> str:
    if not rules:
        return ""
    items = "".join(f'<div class="rule-item">⚠️ {esc(r)}</div>' for r in rules)
    return f"""<section class="board-section">
  <div class="board-section-title">❗ 상시 규칙</div>
  <div class="rules-grid">{items}</div>
</section>"""


# ─── Portfolio ───────────────────────────────────────────────────────────────
def _portfolio_html(portfolio: dict) -> str:
    if not portfolio:
        return ""
    max_w = max(portfolio.values()) if portfolio else 1
    items = []
    for ticker, weight in sorted(portfolio.items(), key=lambda x: -x[1]):
        pct = (weight / max_w) * 100
        items.append(f"""<div class="portfolio-item">
  <div class="portfolio-ticker">{esc(ticker)}</div>
  <div class="portfolio-weight">{weight}%</div>
  <div class="portfolio-bar"><div class="portfolio-bar-fill" style="width:{pct}%;"></div></div>
</div>""")
    return f"""<section class="board-section">
  <div class="board-section-title">📊 포트폴리오 — Trinity v5</div>
  <div class="portfolio-grid">{"".join(items)}</div>
</section>"""


# ─── Sprint Progress Bar ─────────────────────────────────────────────────────
_SPRINT_STATUS_COLOR = {
    "done":        ("#00b894", "✅"),
    "in_progress": ("#6c5ce7", "🔄"),
    "next":        ("#0984e3", "🔵"),
    "waiting":     ("",        "⏳"),
}

def _sprint_progress_html(sprints: list) -> str:
    if not sprints:
        return ""
    total      = len(sprints)
    done_count = sum(1 for s in sprints if s.get("status") == "done")
    pct        = int(done_count / total * 100) if total else 0

    chips = []
    bar_segments = []
    for s in sprints:
        name   = esc(s.get("name",   ""))
        label  = esc(s.get("label",  ""))
        status = s.get("status", "waiting")
        color, emoji = _SPRINT_STATUS_COLOR.get(status, ("", "⏳"))

        if status == "done":
            bg = "#00b89433"; border = "#00b894"
        elif status in ("next", "in_progress"):
            bg = "#0984e322"; border = "#0984e3"
        else:
            bg = "transparent"; border = "var(--border)"

        chips.append(f"""<div class="sprint-chip sprint-{status}" style="border:1px solid {border};background:{bg};">
  <div class="sprint-chip-name">{emoji} {name}</div>
  <div class="sprint-chip-label">{label}</div>
</div>""")

        seg_color = color if color else "var(--border)"
        anim      = "animation:pulse 1.5s infinite;" if status == "next" else ""
        bar_segments.append(
            f'<div class="sprint-seg" style="background:{seg_color};{anim}" title="{name}: {label}"></div>'
        )

    return f"""
<section class="sprint-bar-section">
  <div class="sprint-bar-header">
    <span class="board-section-title" style="margin:0;font-size:.9rem;">📐 Phase 4 Sprint 진행</span>
    <span class="sprint-pct">{pct}% ({done_count}/{total})</span>
  </div>
  <div class="sprint-track">{"".join(bar_segments)}</div>
  <div class="sprint-chips">{"".join(chips)}</div>
</section>"""


# ─── LiteLLM Panel ───────────────────────────────────────────────────────────
def _litellm_panel_html(ll: dict) -> str:
    proxy_up = ll.get("proxy_up", False)
    redis_up = ll.get("redis_up", False)
    models   = ll.get("models",   [])
    error    = ll.get("error",    None)

    def _sb(up: bool, label: str) -> str:
        color = "#00b894" if up else "#e74c3c"
        icon  = "🟢" if up else "🔴"
        text  = "Online" if up else "Offline"
        return (f'<div class="ll-card"><div class="ll-card-label">{label}</div>'
                f'<div class="ll-card-status" style="color:{color};">{icon} {text}</div></div>')

    badges = "".join(
        f'<span class="ll-model-badge ll-{m["status"]}">{esc(m["name"])}</span>'
        for m in models
    ) if models else '<span style="color:var(--muted);font-size:.78rem;">모델 없음</span>'

    err_block = ""
    if error and not proxy_up:
        err_block = f'<div class="ll-error">⚠️ {esc(error[:80])}</div>'

    return f"""
<section class="board-section ll-section">
  <div class="board-section-title">⚡ LiteLLM Proxy 상태</div>
  <div class="ll-grid">
    {_sb(proxy_up, "Proxy")}
    {_sb(redis_up, "Redis")}
    <div class="ll-card">
      <div class="ll-card-label">모델</div>
      <div class="ll-models">{badges}</div>
    </div>
  </div>
  {err_block}
</section>"""


# ─── Agent Panel ────────────────────────────────────────────────────────
AGENT_ICONS = {
    "Brain":   "🧠",
    "Hands-1": "🔧",
    "Hands-2": "🌐",
    "Hands-3": "💻",
    "Hands-4": "⌨️",
    "Memory":  "📓",
}

STATUS_DOT_COLOR = {
    "active":   ("#00b894", True),
    "waiting":  ("#fdcb6e", False),
    "idle":     ("#636e72", False),
    "conflict": ("#e74c3c", True),
    "failed":   ("#e74c3c", False),
    "done":     ("#00b894", False),
}

STATUS_LABEL = {
    "active": "🟢 Active", "waiting": "⏳ Wait",
    "idle": "🔵 Idle",   "conflict": "⚡ Conflict",
    "failed": "❌ Failed", "done": "✅ Done",
}


def _agent_panel_html(activity: dict, engines: dict) -> str:
    current    = activity.get("current",     [])
    recent     = activity.get("recent_done", [])

    # 에이전트 카드 순서: active/conflict 먼저, 나머지 알파벳순
    PRIORITY = {"active": 0, "conflict": 1, "waiting": 2, "idle": 3, "failed": 4, "done": 5}
    sorted_agents = sorted(current, key=lambda a: PRIORITY.get(a["status"], 9))

    cards_html = []
    for ag in sorted_agents:
        name   = ag["agent"]
        status = ag.get("status", "idle")
        task_t = esc(ag.get("task", ""))
        domain = esc(ag.get("domain", ""))
        note   = esc(ag.get("note", ""))
        icon   = AGENT_ICONS.get(name, "🤖")
        color, pulse = STATUS_DOT_COLOR.get(status, ("#636e72", False))
        anim   = "animation:pulse 1.5s infinite;" if pulse else ""
        status_label = STATUS_LABEL.get(status, status.upper())
        card_cls = "agent-card active" if status == "active" else ("agent-card conflict" if status == "conflict" else "agent-card")

        task_block = ""
        if task_t and status not in ("idle", "done"):
            domain_badge = f'<span class="badge-sm" style="background:#6c5ce722;color:#6c5ce7;border:1px solid #6c5ce744;">{domain}</span>' if domain else ""
            task_block = f'<div class="agent-task">{task_t} {domain_badge}</div>'

        cards_html.append(f"""
<div class="{card_cls}">
  <div class="agent-icon">{icon}</div>
  <div class="agent-name">{esc(name)}</div>
  <div class="agent-model">{note}</div>
  <div style="margin-top:8px;">
    <span class="agent-status-dot {status}" style="background:{color};{anim}"></span>
    <span style="font-size:.72rem;color:{color};">{status_label}</span>
  </div>
  {task_block}
</div>""")

    # 에이전트가 없으면 빈 스테이트
    if not cards_html:
        cards_html = ['<div style="color:var(--muted);font-size:.85rem;padding:16px;">🔵 활동 중인 에이전트 없음</div>']

    # 에이전트 그리드
    grid = f'<div class="agent-grid">{chr(10).join(cards_html)}</div>'

    # 최근 작업 목록 (collapsible)
    history_rows = []
    for r in recent[:10]:
        t    = esc(r.get("time", ""))
        ag   = esc(r.get("agent", ""))
        task = esc(r.get("task", ""))
        dur  = esc(r.get("duration", ""))
        smry = esc(r.get("summary", "")[:60])
        history_rows.append(f"""
<div class="agent-history-item">
  <span class="ah-time">{t}</span>
  <span class="ah-agent">{ag}</span>
  <span class="ah-task">{task} <span style="color:var(--muted);font-size:.7rem;">{smry}</span></span>
  <span class="ah-duration">{dur}</span>
</div>""")

    history_block = ""
    if history_rows:
        history_id = "agent-hist"
        # f-string 안 walrus 회제
        history_block = f"""
<div class="card" style="margin-top:12px;">
  <div class="card-header" onclick="this.parentElement.classList.toggle('collapsed')" style="cursor:pointer;display:flex;justify-content:space-between;align-items:center;padding:10px 14px;">
    <span style="font-size:.82rem;font-weight:600;">📋 최근 에이전트 작업 ({len(recent[:10])}건)</span>
    <span class="toggle-icon">▼</span>
  </div>
  <div class="card-body">
    {''.join(history_rows)}
  </div>
</div>"""

    return f"""
<section class="board-section">
  <div class="board-section-title">🤖 에이전트 현황</div>
  {grid}
  {history_block}
</section>"""


# ─── Rules Summary ──────────────────────────────────────────────────────────
def _rules_html(rules: list) -> str:
    if not rules:
        return ""
    items = []
    for r in rules:
        cls = "rule-deprecated" if ("폐기" in r or "보류" in r) else "rule-active"
        items.append(f'<li class="{cls}">{esc(r)}</li>')
    return f"""<section class="board-section">
  <div class="board-section-title">📋 헌법 요약</div>
  <ul class="rules-list">{"".join(items)}</ul>
</section>"""


# ─── Completed ───────────────────────────────────────────────────────────────
def _completed_html(completed: list) -> str:
    if not completed:
        return ""
    # Sort by date desc
    sorted_c = sorted(completed, key=lambda x: x.get("date",""), reverse=True)
    visible  = sorted_c[:5]
    hidden   = sorted_c[5:]

    def _item(c, hidden=False):
        title   = esc(c.get("title",   ""))
        date    = esc(c.get("date",    ""))
        summary = esc(c.get("summary", "")[:120])
        domain  = c.get("domain", "other")
        d_label, d_color = DOMAIN_LABELS.get(domain, ("Other", "#b2bec3"))
        cls = "completed-item hidden-item" if hidden else "completed-item"
        return f"""<div class="{cls}">
  <div class="compl-row">
    <span class="compl-title">{title}</span>
    <span class="badge-sm" style="background:{d_color}22;color:{d_color};border:1px solid {d_color}44;">{d_label}</span>
    {f'<span class="compl-date">{date}</span>' if date else ''}
  </div>
  {f'<div class="compl-summary">{summary}</div>' if summary else ''}
</div>"""

    vis_html  = "".join(_item(c) for c in visible)
    hide_html = "".join(_item(c, True) for c in hidden)
    more_btn  = ""
    if hidden:
        more_btn = f'<button class="more-btn" onclick="toggleMore()" id="more-btn">▼ {len(hidden)}개 더 보기</button>'

    return f"""<section class="board-section">
  <div class="board-section-title">✅ 최근 완료</div>
  {vis_html}
  <div id="hidden-completed">{hide_html}</div>
  {more_btn}
</section>"""


# ─── Pixel Agents HQ — Canvas + Sprite renderer ──────────────────────────────
def _compute_pixel_agent_state(current: list) -> dict:
    """Map agent activity data → team statuses for the Canvas renderer."""
    TEAM_MAP = {
        "Brain":   "brain",
        "Hands-4": "cc",
        "Hands-3": "codex",
        "Hands-1": "ag",
        "Hands-2": "ag",
        "CC팀":    "cc",
    }
    TEAM_REAL = {"cc": "Hands-4", "codex": "Hands-3", "ag": "Hands-1", "brain": "Brain"}

    team_status = {"brain": "idle", "cc": "idle", "codex": "idle", "ag": "idle"}
    agent_tasks: dict = {}

    for entry in current:
        agent = entry.get("agent", "")
        status_raw = str(entry.get("status", "idle"))
        status = status_raw.strip().lower()
        task = entry.get("task", "")

        team = None
        for key, value in TEAM_MAP.items():
            if key in agent:
                team = value
                break
        if team is None:
            continue

        is_active = "active" in status
        is_done = ("done" in status) or ("✅" in status_raw) or (status == "완료")
        is_communicating = "communicating" in status or "📡" in status_raw or "통신" in status
        is_meeting = "meeting" in status or "🤝" in status_raw or "회의" in status

        if is_active:
            team_status[team] = "active"
        elif is_communicating:
            team_status[team] = "communicating"
        elif is_meeting:
            team_status[team] = "meeting"
        elif is_done and team_status[team] == "idle":
            team_status[team] = "done"

        if task and (is_active or is_done):
            agent_tasks[TEAM_REAL.get(team, agent)] = task[:50]

    return {"teamStatus": team_status, "agentTasks": agent_tasks}


def _pixel_agents_canvas_html(agent_activity: dict) -> str:
    """Return the Pixel Agents HQ section (Canvas + tileset tiles + popup) for the dashboard."""
    import json as _json
    current = agent_activity.get("current", [])
    logs    = agent_activity.get("logs", [])
    state   = _compute_pixel_agent_state(current)
    ts      = _json.dumps(state["teamStatus"], ensure_ascii=True)
    ta      = _json.dumps(state["agentTasks"],  ensure_ascii=True)
    al      = _json.dumps(logs,                 ensure_ascii=True)
    js      = _pixel_agents_js()
    css = (
        ".pa-section{margin:16px 0;padding:0 16px 16px;}"
        ".pa-header{display:flex;align-items:baseline;gap:12px;margin-bottom:10px;}"
        ".pa-header h3{font-size:.95rem;font-weight:700;color:var(--text);margin:0;}"
        ".pa-credit{font-size:.7rem;color:var(--muted);}"
        ".pa-credit a{color:#74b9ff;text-decoration:none;}"
        ".pa-wrap{position:relative;background:#06060e;border:1px solid var(--border);"
        "border-radius:12px;overflow:hidden;padding:8px;}"
        "#agentCanvas{display:block;width:100%;max-width:760px;height:auto;"
        "margin:0 auto;image-rendering:pixelated;image-rendering:crisp-edges;cursor:default;}"
        "#pa-popup-overlay{display:none;position:absolute;top:0;left:0;right:0;bottom:0;"
        "background:rgba(0,0,0,0.72);z-index:50;border-radius:12px;}"
        "#pa-popup{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);"
        "width:340px;max-height:85%;overflow-y:auto;background:#0d0d20;"
        "border:1px solid #334;border-radius:10px;padding:14px 16px;"
        "font-family:monospace;font-size:12px;color:#e2e2f0;"
        "box-shadow:0 0 32px rgba(0,0,0,.9);}"
        "#pa-popup-header{display:flex;justify-content:space-between;align-items:center;"
        "margin-bottom:10px;border-bottom:1px solid #334;padding-bottom:8px;}"
        "#pa-popup-title{font-size:14px;font-weight:bold;}"
        "#pa-popup-close{background:none;border:none;color:#888;cursor:pointer;"
        "font-size:18px;line-height:1;padding:0 4px;}"
        "#pa-popup-close:hover{color:#fff;}"
        ".pa-popup-agent{display:flex;align-items:flex-start;gap:8px;padding:6px 0;"
        "border-bottom:1px solid #1a1a2e;}"
        ".pa-popup-emoji{font-size:14px;width:18px;text-align:center;padding-top:1px;}"
        ".pa-popup-name{font-weight:bold;}"
        ".pa-popup-status{padding:1px 6px;border-radius:3px;font-size:10px;"
        "white-space:nowrap;margin-left:auto;}"
        ".pa-popup-task{font-size:10px;color:#8888aa;margin-top:2px;"
        "word-break:break-all;}"
        ".pa-popup-log-header{margin-top:10px;border-top:1px solid #334;padding-top:8px;"
        "font-size:10px;color:#7888aa;font-weight:bold;margin-bottom:4px;}"
        ".pa-popup-log{font-size:10px;color:#555;font-style:italic;padding:4px 0;}"
        ".pa-popup-log-wrap{max-height:120px;overflow-y:auto;}"
        ".pa-log-entry{padding:3px 0;border-bottom:1px solid #1a1a2e;}"
        ".pa-log-arrow{font-size:9px;color:#7888aa;display:block;}"
        ".pa-log-msg{font-size:10px;color:#c8c8e0;display:block;word-break:break-all;}"
    )
    return (
        f"<!-- Pixel Agents HQ — Canvas + ai-town sprites/tiles (MIT) -->\n"
        f"<style>{css}</style>\n"
        f"<section class=\"pa-section\">\n"
        f"  <div class=\"pa-header\">\n"
        f"    <h3>🏢 Pixel Agents HQ</h3>\n"
        f"    <span class=\"pa-credit\">Sprites &amp; tiles: "
        f"<a href=\"https://github.com/a16z-infra/ai-town\" target=\"_blank\">ai-town</a>"
        f" (MIT) &mdash; 방 제목 클릭 시 팀 상세 보기</span>\n"
        f"  </div>\n"
        f"  <div class=\"pa-wrap\">\n"
        f"    <canvas id=\"agentCanvas\" width=\"760\" height=\"420\"\n"
        f"      data-team-status='{ts}'\n"
        f"      data-agent-tasks='{ta}'\n"
        f"      data-agent-logs='{al}'\n"
        f"      title=\"방 제목 클릭 → 팀 상세\"></canvas>\n"
        f"    <div id=\"pa-popup-overlay\" onclick=\"closePaPopup()\">\n"
        f"      <div id=\"pa-popup\" onclick=\"event.stopPropagation()\">\n"
        f"        <div id=\"pa-popup-header\">\n"
        f"          <span id=\"pa-popup-title\">팀 정보</span>\n"
        f"          <button id=\"pa-popup-close\" onclick=\"closePaPopup()\">✕</button>\n"
        f"        </div>\n"
        f"        <div id=\"pa-popup-content\"></div>\n"
        f"      </div>\n"
        f"    </div>\n"
        f"  </div>\n"
        f"</section>\n"
        f"<script>\n{js}\n</script>"
    )


def _pixel_agents_js() -> str:
    """Return the Canvas JS renderer for Pixel Agents HQ.

    Sprite sheet : assets/32x32folk.png  (384x256 — 12 cols x 8 rows, 32px/tile)
    Tileset      : assets/gentle-obj.png (1440x1024 — 45 cols x 32 rows, 32px/tile)
    Credits      : a16z-infra/ai-town (MIT License)

    Tileset rendering:
      - Rooms are pre-rendered to offscreen canvases using actual tileset tiles.
      - A 2x2 checkerboard pattern of adjacent tiles fills the floor.
      - A single wall-strip tile fills the top 20px of each room.
      - A per-room colour tint (low opacity) differentiates team zones.
    """
    return """
(function initPixelAgentsHQ() {
  'use strict';
  var canvas = document.getElementById('agentCanvas');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var W = 760, H = 420;

  // ── Data from canvas attributes ──────────────────────────────────────────────
  var TEAM_STATUS = {brain:'idle', cc:'idle', codex:'idle', ag:'idle'};
  var AGENT_TASKS = {};
  var AGENT_LOGS  = [];
  try {
    TEAM_STATUS = JSON.parse(canvas.dataset.teamStatus || '{}');
    AGENT_TASKS = JSON.parse(canvas.dataset.agentTasks  || '{}');
    AGENT_LOGS  = JSON.parse(canvas.dataset.agentLogs   || '[]');
  } catch(e) {}

  // ── Sprite sheet: assets/32x32folk.png (384x256, 12 cols x 8 rows, 32px/tile)
  // charIdx 0-3 → rows 0-3; charIdx 4-7 → rows 4-7
  // Per char: cols = (charIdx%4)*3 .. +2; rows: down=+0, left=+1, right=+2, up=+3
  var SS = {img:null, ok:false};
  var ssImg = new Image();
  ssImg.onload  = function() { SS.img = ssImg; SS.ok = true; };
  ssImg.onerror = function() { SS.ok = false; };
  ssImg.src = 'assets/32x32folk.png';

  // ── Tileset: assets/gentle-obj.png (1440x1024, 45 cols x 32 rows, 32px/tile)
  // Tile ID = row * 45 + col;  srcX = (id%45)*32;  srcY = floor(id/45)*32
  // Tile 271 (row6,col1 → x=32,y=192) is the primary background tile in ai-town.
  var TS = {img:null, ok:false};
  var tsImg = new Image();
  tsImg.onload  = function() { TS.img = tsImg; TS.ok = true; };
  tsImg.onerror = function() { TS.ok = false; };
  tsImg.src = 'assets/gentle-obj.png';
  var TS_COLS = 45, TS_SZ = 32;

  // ── Room definitions ──────────────────────────────────────────────────────────
  // tiles: 4 IDs for 2x2 checkerboard floor pattern [col0row0, col1row0, col0row1, col1row1]
  // wallTile: single tile ID for the 20px header strip
  // tint: colour overlay that gives each room its identity at low opacity
  var ROOMS = {
    cc:    {name:'CC Room',    x:10,  y:10,  w:235, h:235,
            bg:'#0d1b2e', border:'#4a9eff',
            tiles:[271,272,316,317], wallTile:90,
            tint:'rgba(26,60,110,0.30)'},
    codex: {name:'Codex Room', x:255, y:10,  w:240, h:235,
            bg:'#0a2a1a', border:'#00b894',
            tiles:[315,316,360,361], wallTile:135,
            tint:'rgba(10,80,50,0.30)'},
    ag:    {name:'AG Room',    x:505, y:10,  w:245, h:235,
            bg:'#2a1006', border:'#e17055',
            tiles:[360,361,405,406], wallTile:180,
            tint:'rgba(90,40,10,0.30)'},
    brain: {name:'Brain HQ',   x:10,  y:255, w:740, h:155,
            bg:'#16082e', border:'#a29bfe',
            tiles:[405,406,450,451], wallTile:225,
            tint:'rgba(55,20,100,0.30)'},
  };

  // ── Pre-rendered room backgrounds (offscreen canvas per room) ─────────────────
  // Computed once when tileset loads; then blit every frame via drawImage (fast).
  var ROOM_BG = {};
  var bgRendered = false;

  function prerenderRooms() {
    if (bgRendered || !TS.ok || !TS.img) return;
    Object.keys(ROOMS).forEach(function(key) {
      var room = ROOMS[key];
      var oc = document.createElement('canvas');
      oc.width = room.w; oc.height = room.h;
      var oc2 = oc.getContext('2d');
      oc2.imageSmoothingEnabled = false;

      // Solid colour base (shows through transparent tile regions)
      oc2.fillStyle = room.bg;
      oc2.fillRect(0, 0, room.w, room.h);

      // Floor tiles — 2x2 checkerboard starting below header strip (y=20)
      var WALL_H = 20;
      for (var ty = WALL_H; ty < room.h + TS_SZ; ty += TS_SZ) {
        for (var tx = 0; tx < room.w + TS_SZ; tx += TS_SZ) {
          var col = Math.floor(tx / TS_SZ) % 2;
          var row = Math.floor((ty - WALL_H) / TS_SZ) % 2;
          var tid = room.tiles[col + row * 2];
          var sx  = (tid % TS_COLS) * TS_SZ;
          var sy  = Math.floor(tid / TS_COLS) * TS_SZ;
          oc2.drawImage(TS.img, sx, sy, TS_SZ, TS_SZ, tx, ty, TS_SZ, TS_SZ);
        }
      }

      // Wall strip tiles along top 20px
      var wtid = room.wallTile;
      var wsx = (wtid % TS_COLS) * TS_SZ, wsy = Math.floor(wtid / TS_COLS) * TS_SZ;
      for (var wx = 0; wx < room.w + TS_SZ; wx += TS_SZ) {
        oc2.drawImage(TS.img, wsx, wsy, TS_SZ, TS_SZ, wx, 0, TS_SZ, WALL_H);
      }
      // Darken wall strip for depth
      oc2.fillStyle = 'rgba(0,0,0,0.40)';
      oc2.fillRect(0, 0, room.w, WALL_H);

      // Colour identity tint over the whole room
      oc2.fillStyle = room.tint;
      oc2.fillRect(0, 0, room.w, room.h);

      ROOM_BG[key] = oc;
    });
    bgRendered = true;
  }

  // ── Desk positions (absolute canvas coords) ───────────────────────────────────
  var DESKS = {
    cc:    [[60,90],[127,90],[192,90],[60,175],[127,175]],
    codex: [[300,90],[380,90],[300,175],[380,175]],
    ag:    [[545,90],[620,90],[545,175],[620,175]],
    brain: [[385,330]],
  };

  // ── Agent definitions ─────────────────────────────────────────────────────────
  var AGENT_DEFS = [
    {id:'Foreman',      emoji:'👔', team:'cc',    charIdx:0, roomId:'cc',    di:0, leader:true, color:'#4a9eff'},
    {id:'Engineer',     emoji:'\u2328',       team:'cc',    charIdx:1, roomId:'cc',    di:1,              color:'#74b9ff'},
    {id:'Critic',       emoji:'🔍', team:'cc',    charIdx:2, roomId:'cc',    di:2,              color:'#74b9ff'},
    {id:'GitOps',       emoji:'📤', team:'cc',    charIdx:3, roomId:'cc',    di:3,              color:'#74b9ff'},
    {id:'VaultKeeper',  emoji:'🗄', team:'cc',    charIdx:4, roomId:'cc',    di:4,              color:'#74b9ff'},
    {id:'Compute Lead', emoji:'👔', team:'codex', charIdx:5, roomId:'codex', di:0, leader:true, color:'#00b894'},
    {id:'Quant',        emoji:'🧮', team:'codex', charIdx:6, roomId:'codex', di:1,              color:'#55efc4'},
    {id:'Backtester',   emoji:'📊', team:'codex', charIdx:7, roomId:'codex', di:2,              color:'#55efc4'},
    {id:'Builder',      emoji:'🔨', team:'codex', charIdx:0, roomId:'codex', di:3,              color:'#55efc4'},
    {id:'Scout Lead',   emoji:'👔', team:'ag',    charIdx:1, roomId:'ag',    di:0, leader:true, color:'#e17055'},
    {id:'Web Scout',    emoji:'🔍', team:'ag',    charIdx:2, roomId:'ag',    di:1,              color:'#fab1a0'},
    {id:'Architect',    emoji:'🏗', team:'ag',    charIdx:3, roomId:'ag',    di:2,              color:'#fab1a0'},
    {id:'Experimenter', emoji:'🧪', team:'ag',    charIdx:4, roomId:'ag',    di:3,              color:'#fab1a0'},
    {id:'Brain',        emoji:'🧠', team:'brain', charIdx:5, roomId:'brain', di:0, leader:true, color:'#a29bfe'},
  ];

  // Map fictional team → real dashboard agent key for task text
  var TEAM_REAL = {cc:'Hands-4', codex:'Hands-3', ag:'Hands-1', brain:'Brain'};

  // Room key → engine aliases used in parsed logs
  var ROOM_ENGINES = {
    cc: ['claude_code', 'Hands-4', 'CC팀'],
    codex: ['codex', 'Codex', 'Hands-3'],
    ag: ['antigravity', 'Antigravity', 'Hands-1', 'Hands-2'],
    brain: ['Brain']
  };

  // ── Sprite / animation constants ──────────────────────────────────────────────
  var DIR_ROW   = {down:0, left:1, right:2, up:3};
  var SPRITE_SZ = 28;
  var SPEED     = 0.33;  // idle wander speed (50% of original 0.65)
  var ANIM_RATE = 8;
  var tick      = 0;

  // ── Per-agent runtime state ───────────────────────────────────────────────────
  var STATE = {};
  AGENT_DEFS.forEach(function(def) {
    var desks = DESKS[def.roomId] || [];
    var desk  = desks[def.di]     || [385, 330];
    var room  = ROOMS[def.roomId];
    var ix = room.x + 24 + Math.random() * (room.w - 48);
    var iy = room.y + 32 + Math.random() * (room.h - 56);
    STATE[def.id] = {
      x:ix, y:iy, tx:ix, ty:iy,
      deskX:desk[0], deskY:desk[1],
      dir:'down', frame:0, fTimer:0,
      status:TEAM_STATUS[def.team] || 'idle',
      wanderCd:Math.floor(Math.random() * 160),
      effectT:0, moving:false,
    };
  });
  AGENT_DEFS.forEach(function(def) {
    if (STATE[def.id].status === 'done') STATE[def.id].effectT = 110;
  });

  // ── Update ────────────────────────────────────────────────────────────────────
  function update() {
    AGENT_DEFS.forEach(function(def) {
      var s    = STATE[def.id];
      var room = ROOMS[def.roomId];
      if (s.status === 'active' || s.status === 'done') {
        // Snap to desk immediately for active/done agents
        s.x = s.deskX; s.y = s.deskY;
        s.tx = s.deskX; s.ty = s.deskY;
        s.moving = false; s.dir = 'down'; s.frame = 1;
        if (s.effectT > 0) s.effectT--;
        return; // skip movement code
      } else {
        s.wanderCd--;
        if (s.wanderCd <= 0) {
          if (Math.random() < 0.35) {
            // Random pause in place
            s.tx = s.x; s.ty = s.y;
            s.wanderCd = 60 + Math.floor(Math.random() * 100);
          } else {
            var m = 28;
            s.tx = room.x + m + Math.random() * (room.w - m * 2);
            s.ty = room.y + m + 22 + Math.random() * (room.h - m * 2 - 20);
            s.wanderCd = 80 + Math.floor(Math.random() * 150);
          }
        }
      }
      var dx = s.tx - s.x, dy = s.ty - s.y;
      var dist = Math.sqrt(dx * dx + dy * dy);
      if (dist > 1.5) {
        s.x += (dx / dist) * SPEED;
        s.y += (dy / dist) * SPEED;
        s.moving = true;
        s.dir = (Math.abs(dx) > Math.abs(dy)) ? (dx > 0 ? 'right' : 'left') : (dy > 0 ? 'down' : 'up');
        s.fTimer++;
        if (s.fTimer >= ANIM_RATE) { s.fTimer = 0; s.frame = (s.frame + 1) % 3; }
      } else {
        s.moving = false; s.frame = 1;
      }
      var mg = 16;
      s.x = Math.max(room.x + mg, Math.min(room.x + room.w - mg, s.x));
      s.y = Math.max(room.y + mg + 22, Math.min(room.y + room.h - mg, s.y));
      if (s.effectT > 0) s.effectT--;
    });
  }

  // ── Render ────────────────────────────────────────────────────────────────────
  function render() {
    prerenderRooms(); // no-op after first successful render

    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = '#06060e';
    ctx.fillRect(0, 0, W, H);

    // Draw room backgrounds (tileset-based once loaded, solid-colour fallback)
    Object.keys(ROOMS).forEach(function(k) { drawRoom(ROOMS[k], k); });

    // Draw desks
    Object.keys(DESKS).forEach(function(rid) {
      var border = ROOMS[rid] ? ROOMS[rid].border : '#ffffff';
      DESKS[rid].forEach(function(d) { drawDesk(d[0], d[1], border); });
    });

    // Active-leader room glow
    AGENT_DEFS.filter(function(d) { return d.leader; }).forEach(function(def) {
      var s = STATE[def.id];
      if (s.status === 'active') {
        var r = ROOMS[def.roomId];
        ctx.save();
        ctx.globalAlpha = 0.12 + 0.06 * Math.sin(tick * 0.06);
        ctx.fillStyle = def.color;
        ctx.fillRect(r.x + 2, r.y + 2, r.w - 4, r.h - 4);
        ctx.restore();
      }
    });

    // Draw agents sorted by Y (painter's algorithm)
    var sorted = AGENT_DEFS.slice().sort(function(a, b) {
      return STATE[a.id].y - STATE[b.id].y;
    });
    sorted.forEach(drawAgent);
    tick++;
  }

  // ── drawRoom ─────────────────────────────────────────────────────────────────
  function drawRoom(room, key) {
    if (ROOM_BG[key]) {
      // Fast blit of pre-rendered tileset background
      ctx.drawImage(ROOM_BG[key], room.x, room.y);
    } else {
      // Fallback: solid colour + subtle grid (used before tileset loads)
      ctx.fillStyle = room.bg;
      ctx.fillRect(room.x, room.y, room.w, room.h);
      ctx.strokeStyle = 'rgba(255,255,255,0.025)';
      ctx.lineWidth = 1;
      for (var gx = room.x; gx <= room.x + room.w; gx += 16) {
        ctx.beginPath(); ctx.moveTo(gx+.5, room.y); ctx.lineTo(gx+.5, room.y+room.h); ctx.stroke();
      }
      for (var gy = room.y; gy <= room.y + room.h; gy += 16) {
        ctx.beginPath(); ctx.moveTo(room.x, gy+.5); ctx.lineTo(room.x+room.w, gy+.5); ctx.stroke();
      }
    }
    // Coloured border
    ctx.strokeStyle = room.border;
    ctx.lineWidth = 2;
    ctx.strokeRect(room.x + 1, room.y + 1, room.w - 2, room.h - 2);
    // Clickable room label (pill background + text)
    ctx.font = 'bold 10px monospace';
    var lw = ctx.measureText(room.name).width;
    ctx.fillStyle = 'rgba(0,0,0,0.80)';
    ctx.fillRect(room.x + 4, room.y + 3, lw + 10, 14);
    ctx.fillStyle = room.border;
    ctx.textAlign = 'left';
    ctx.fillText(room.name, room.x + 9, room.y + 13);
  }

  // ── drawDesk ─────────────────────────────────────────────────────────────────
  function drawDesk(dx, dy, color) {
    ctx.fillStyle = 'rgba(255,255,255,0.07)';
    ctx.fillRect(dx - 13, dy - 7, 26, 14);
    ctx.strokeStyle = color; ctx.lineWidth = 1;
    ctx.strokeRect(dx - 13, dy - 7, 26, 14);
    // Monitor
    ctx.fillStyle = '#020208';
    ctx.fillRect(dx - 7, dy - 20, 14, 12);
    ctx.strokeStyle = color; ctx.lineWidth = 1;
    ctx.strokeRect(dx - 7, dy - 20, 14, 12);
    // Screen glow
    ctx.save();
    ctx.globalAlpha = 0.22 + 0.12 * Math.sin(tick * 0.04 + dx * 0.08);
    ctx.fillStyle = color;
    ctx.fillRect(dx - 6, dy - 19, 12, 10);
    ctx.restore();
  }

  // ── drawAgent ─────────────────────────────────────────────────────────────────
  function drawAgent(def) {
    var s = STATE[def.id];
    var x = s.x, y = s.y;

    // Sprite or fallback circle
    ctx.save();
    if (SS.ok && SS.img) {
      var cIdx      = def.charIdx;
      var baseCol   = (cIdx % 4) * 3;
      var baseRow   = Math.floor(cIdx / 4) * 4;
      var spriteCol = baseCol + s.frame;
      var spriteRow = baseRow + (DIR_ROW[s.dir] || 0);
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(SS.img,
        spriteCol * 32, spriteRow * 32, 32, 32,
        Math.round(x - SPRITE_SZ / 2), Math.round(y - SPRITE_SZ), SPRITE_SZ, SPRITE_SZ);
    } else {
      ctx.beginPath();
      ctx.arc(x, y - 10, 11, 0, Math.PI * 2);
      ctx.fillStyle = def.color + '22'; ctx.fill();
      ctx.strokeStyle = def.color; ctx.lineWidth = 1.5; ctx.stroke();
      ctx.font = '13px serif'; ctx.textAlign = 'center';
      ctx.fillText(def.emoji, x, y - 4);
    }
    ctx.restore();

    // Name tag
    var label = def.id.length > 10 ? def.id.slice(0, 10) : def.id;
    ctx.save();
    ctx.font = 'bold 7px monospace'; ctx.textAlign = 'center';
    var tw = ctx.measureText(label).width;
    ctx.fillStyle = 'rgba(0,0,0,0.82)';
    ctx.fillRect(Math.round(x - tw / 2 - 2), Math.round(y + 2), tw + 4, 9);
    ctx.fillStyle = def.color;
    ctx.fillText(label, x, Math.round(y) + 10);
    ctx.restore();

    // Status / speech-bubble overlay
    ctx.save(); ctx.textAlign = 'center';
    if (s.effectT > 0 && s.status === 'done') {
      ctx.globalAlpha = s.effectT / 110;
      ctx.font = '11px serif';
      ctx.fillText('\u2705', x, y - SPRITE_SZ - 5);
    } else if (s.status === 'error') {
      ctx.globalAlpha = 0.5 + 0.5 * Math.sin(tick * 0.25);
      ctx.font = '11px serif';
      ctx.fillText('\u274C', x, y - SPRITE_SZ - 5);
    } else if (s.status === 'active') {
      if (!s.moving && def.leader) {
        // Speech bubble showing current real task for the team leader
        var rk = TEAM_REAL[def.team];
        var taskTxt = AGENT_TASKS[rk] ? AGENT_TASKS[rk].substring(0, 28) : '\uC791\uC5C5 \uC911...';
        drawTaskBubble(x, y - SPRITE_SZ - 4, taskTxt, def.color);
      } else if (!s.moving) {
        // Typing dots for non-leader active agents
        var dots = '.'.repeat(((tick >> 4) % 3) + 1);
        ctx.globalAlpha = 0.9; ctx.fillStyle = def.color;
        ctx.font = '8px monospace';
        ctx.fillText(dots, x, y - SPRITE_SZ - 5);
      }
    }
    ctx.restore();
  }

  // ── drawTaskBubble ────────────────────────────────────────────────────────────
  function drawTaskBubble(x, y, text, color) {
    ctx.save();
    ctx.font = '7px monospace';
    var tw = ctx.measureText(text).width;
    var bw = tw + 8, bh = 12;
    var bx = x - bw / 2, by = y - bh;

    ctx.fillStyle = 'rgba(0,0,0,0.88)';
    ctx.fillRect(bx, by, bw, bh);
    ctx.strokeStyle = color; ctx.lineWidth = 1;
    ctx.strokeRect(bx, by, bw, bh);

    // Downward arrow
    ctx.beginPath();
    ctx.moveTo(x - 4, by + bh);
    ctx.lineTo(x + 4, by + bh);
    ctx.lineTo(x, by + bh + 5);
    ctx.closePath();
    ctx.fillStyle = 'rgba(0,0,0,0.88)'; ctx.fill();
    ctx.strokeStyle = color; ctx.stroke();

    ctx.fillStyle = color;
    ctx.textAlign = 'center';
    ctx.fillText(text, x, by + bh - 3);
    ctx.restore();
  }

  // ── Popup ─────────────────────────────────────────────────────────────────────
  function showPaPopup(roomKey) {
    var room   = ROOMS[roomKey];
    var agents = AGENT_DEFS.filter(function(d) { return d.roomId === roomKey; });
    var rk     = TEAM_REAL[roomKey];

    var titleEl = document.getElementById('pa-popup-title');
    if (titleEl) { titleEl.textContent = room.name; titleEl.style.color = room.border; }

    var stLabels = {active:'🔄 Active', idle:'💤 Idle', done:'✅ Done', error:'❌ Error'};
    var stColors = {active:'#fdcb6e', idle:'#636e72', done:'#00b894', error:'#e17055'};

    var html = '';
    agents.forEach(function(def) {
      var st      = (STATE[def.id] && STATE[def.id].status) || 'idle';
      var stLabel = stLabels[st] || st;
      var stColor = stColors[st] || '#aaa';
      var taskTxt = '';
      if (def.leader && AGENT_TASKS[rk]) {
        taskTxt = AGENT_TASKS[rk].substring(0, 60) + (AGENT_TASKS[rk].length > 60 ? '...' : '');
      }
      html += '<div class="pa-popup-agent">';
      html += '<span class="pa-popup-emoji">' + def.emoji + '</span>';
      html += '<div style="flex:1;min-width:0">';
      html += '<div class="pa-popup-name" style="color:' + def.color + '">' +
              def.id + (def.leader ? ' 👑' : '') + '</div>';
      if (taskTxt) {
        html += '<div class="pa-popup-task">' + taskTxt + '</div>';
      }
      html += '</div>';
      html += '<span class="pa-popup-status" style="color:' + stColor + '">' + stLabel + '</span>';
      html += '</div>';
    });
    var roomEngines = ROOM_ENGINES[roomKey] || [];
    var filteredLogs = AGENT_LOGS.filter(function(entry) {
      return roomEngines.some(function(eng) {
        var fromVal = entry.from || '';
        var toVal = entry.to || '';
        return fromVal.indexOf(eng) >= 0 || toVal.indexOf(eng) >= 0;
      });
    });
    var displayLogs = filteredLogs.length > 0 ? filteredLogs : AGENT_LOGS;

    html += '<div class="pa-popup-log-header">💬 대화 로그</div>';
    if (displayLogs.length === 0) {
      html += '<div class="pa-popup-log">로그 없음</div>';
    } else {
      html += '<div class="pa-popup-log-wrap">';
      displayLogs.forEach(function(entry) {
        var fromVal = entry.from || '';
        var toVal = entry.to || '';
        var fromLabel = fromVal === 'Brain' ? '🧠 Brain' : ('⌨️ ' + fromVal);
        var toLabel   = toVal   === 'Brain' ? '🧠 Brain' : toVal;
        var timeStr   = entry.time ? '[' + entry.time + '] ' : '';
        html += '<div class="pa-log-entry">';
        html += '<span class="pa-log-arrow">' + timeStr + fromLabel + ' → ' + toLabel + '</span>';
        html += '<span class="pa-log-msg">' + (entry.msg || '') + '</span>';
        html += '</div>';
      });
      html += '</div>';
    }

    var contentEl = document.getElementById('pa-popup-content');
    if (contentEl) contentEl.innerHTML = html;

    var overlayEl = document.getElementById('pa-popup-overlay');
    if (overlayEl) overlayEl.style.display = 'block';
  }

  function closePaPopup() {
    var el = document.getElementById('pa-popup-overlay');
    if (el) el.style.display = 'none';
  }
  window.closePaPopup = closePaPopup;

  // ── Click / hover handlers ────────────────────────────────────────────────────
  canvas.addEventListener('click', function(e) {
    var rect = canvas.getBoundingClientRect();
    var scX = W / rect.width, scY = H / rect.height;
    var cx = (e.clientX - rect.left) * scX;
    var cy = (e.clientY - rect.top)  * scY;
    var clicked = null;
    Object.keys(ROOMS).forEach(function(k) {
      var r = ROOMS[k];
      if (cx >= r.x && cx <= r.x + r.w && cy >= r.y && cy <= r.y + 18) clicked = k;
    });
    if (clicked) showPaPopup(clicked);
  });

  canvas.addEventListener('mousemove', function(e) {
    var rect = canvas.getBoundingClientRect();
    var scX = W / rect.width, scY = H / rect.height;
    var cx = (e.clientX - rect.left) * scX;
    var cy = (e.clientY - rect.top)  * scY;
    var over = false;
    Object.keys(ROOMS).forEach(function(k) {
      var r = ROOMS[k];
      if (cx >= r.x && cx <= r.x + r.w && cy >= r.y && cy <= r.y + 18) over = true;
    });
    canvas.style.cursor = over ? 'pointer' : 'default';
  });

  // ── Main loop ─────────────────────────────────────────────────────────────────
  function loop() { update(); render(); requestAnimationFrame(loop); }
  loop();

})();
"""


# ─── CSS ─────────────────────────────────────────────────────────────────────
def _css() -> str:
    return """
:root {
  --bg:      #0d0d1a;
  --bg2:     #13132b;
  --card:    #181830;
  --hover:   #1e1e40;
  --text:    #e2e2f0;
  --muted:   #7a7a9a;
  --dim:     #50506a;
  --accent:  #4ecdc4;
  --border:  #252545;
  --radius:  14px;
  --shadow:  0 6px 30px rgba(0,0,0,.4);
}

/* Light mode */
body.light {
  --bg:      #f5f5f8;
  --bg2:     #eeeef2;
  --card:    #ffffff;
  --hover:   #f0f0f5;
  --text:    #1a1a2e;
  --muted:   #6b6b8a;
  --dim:     #9090a8;
  --accent:  #2da89e;
  --border:  #d8d8e8;
  --shadow:  0 4px 20px rgba(0,0,0,.08);
}
body.light .header {
  background: linear-gradient(135deg, #e8e8f0, #dddde8, #d0d0e0);
}
body.light .header h1 {
  background: linear-gradient(135deg, #2da89e, #7a6bfe);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
body.light .briefing-card {
  background: linear-gradient(135deg, rgba(45,168,158,.06), rgba(122,107,254,.06));
  border-color: rgba(45,168,158,.3);
}
body.light .training-hero {
  background: linear-gradient(135deg, rgba(255,107,107,.04), rgba(122,107,254,.04));
  border-color: rgba(255,107,107,.15);
}
body.light .project-card::before {
  background: linear-gradient(90deg, #2da89e, #7a6bfe);
}
body.light .portfolio-bar-fill {
  background: linear-gradient(90deg, #2da89e, #7a6bfe);
}
body.light .ql-toast {
  background: #ffffff;
  box-shadow: 0 4px 20px rgba(0,0,0,.12);
}

/* Theme toggle button */
.theme-toggle {
  background: rgba(255,255,255,.1);
  border: 1px solid var(--border);
  color: var(--text);
  width: 38px; height: 38px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.1rem;
  display: flex; align-items: center; justify-content: center;
  transition: all .2s;
}
.theme-toggle:hover {
  background: rgba(78,205,196,.2);
  border-color: var(--accent);
  transform: rotate(30deg);
}
body.light .theme-toggle {
  background: rgba(0,0,0,.05);
}

* { margin:0; padding:0; box-sizing:border-box; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg); color: var(--text);
  line-height: 1.6; min-height: 100vh;
}

/* Header */
.header {
  background: linear-gradient(135deg,#13132b,#181842,#0e2060);
  border-bottom: 1px solid var(--border);
  padding: 22px 36px;
}
.header-content {
  max-width: 1440px; margin: 0 auto;
  display: flex; justify-content: space-between;
  align-items: center; flex-wrap: wrap; gap: 14px;
}
.header h1 {
  font-size: 1.75rem; font-weight: 800;
  background: linear-gradient(135deg,#4ecdc4,#a29bfe);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.subtitle { color: var(--muted); font-size: .85rem; margin-top:3px; }
.header-right { display:flex; gap:8px; flex-wrap:wrap; }
.badge { display:inline-block; padding:5px 13px; border-radius:20px; font-size:.78rem; font-weight:600; }
.badge-phase   { background:rgba(78,205,196,.12); color:#4ecdc4; border:1px solid rgba(78,205,196,.3); }
.badge-ruleset { background:rgba(162,155,254,.12); color:#a29bfe; border:1px solid rgba(162,155,254,.3); }
.badge-date    { background:rgba(255,255,255,.07); color:var(--muted); border:1px solid var(--border); }

/* Summary cards */
.summary-cards {
  max-width:1440px; margin:22px auto; padding:0 36px;
  display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:14px;
}
.card {
  background:var(--card); border:1px solid var(--border);
  border-radius:var(--radius); padding:18px; text-align:center;
  transition:transform .2s,box-shadow .2s;
}
.card:hover { transform:translateY(-3px); box-shadow:var(--shadow); }
.card-number { font-size:2.2rem; font-weight:800; }
.card-label  { font-size:.78rem; color:var(--muted); margin-top:4px; }
.card-project .card-number { color: #a29bfe; }
.card-action  .card-number { color: #fdcb6e; }
.card-week    .card-number { color: #74b9ff; }
.card-done    .card-number { color: #00b894; }

/* Briefing hero */
.briefing-section {
  max-width:1440px; margin:0 auto 24px; padding:0 36px;
}
.briefing-card {
  background: linear-gradient(135deg, rgba(78,205,196,.06), rgba(162,155,254,.06));
  border: 1px solid rgba(78,205,196,.3);
  border-left: 4px solid var(--accent);
  border-radius:var(--radius); padding:22px 26px;
}
.briefing-header {
  display:flex; justify-content:space-between; align-items:center;
  margin-bottom:18px;
}
.briefing-title { font-size:1.05rem; font-weight:700; color:var(--accent); }
.briefing-toggle {
  background:rgba(78,205,196,.12); border:1px solid rgba(78,205,196,.3);
  color:var(--accent); padding:5px 14px; border-radius:12px;
  cursor:pointer; font-size:.78rem; transition:all .2s;
}
.briefing-toggle:hover { background:rgba(78,205,196,.22); }
.briefing-top-priority {
  display:flex; align-items:flex-start; gap:10px;
  background:rgba(255,255,255,.04); border-radius:10px; padding:12px 16px;
  margin-bottom:14px;
}
.priority-label { font-size:.85rem; font-weight:700; color:var(--accent); white-space:nowrap; }
.priority-text  { font-size:.95rem; font-weight:600; }
.briefing-row { margin-bottom:12px; }
.briefing-key { font-size:.82rem; font-weight:700; color:var(--muted); display:block; margin-bottom:6px; }
.briefing-list { list-style:none; padding:0; }
.briefing-list li {
  padding:4px 0 4px 16px; font-size:.85rem; color:var(--text);
  position:relative;
}
.briefing-list li::before { content:"›"; position:absolute; left:4px; color:var(--accent); }
.briefing-list.warning-list li::before { content:"•"; }
.warning-item { color:#fdcb6e !important; }

/* Filter bar */
.filter-bar {
  max-width:1440px; margin:0 auto 22px; padding:0 36px;
  display:flex; flex-wrap:wrap; gap:14px;
}
.filter-group { display:flex; align-items:center; gap:7px; flex-wrap:wrap; }
.filter-label { font-size:.78rem; font-weight:600; color:var(--muted); }
.filter-btn {
  background:var(--card); border:1px solid var(--border); color:var(--muted);
  padding:5px 13px; border-radius:20px; cursor:pointer; font-size:.78rem;
  transition:all .2s;
}
.filter-btn:hover { border-color:var(--accent); color:var(--text); }
.filter-btn.active { background:rgba(78,205,196,.14); border-color:var(--accent); color:var(--accent); }

/* Board sections */
.board-section {
  max-width:1440px; margin:0 auto 28px; padding:0 36px;
}
.board-section-title {
  font-size:1.1rem; font-weight:700; margin-bottom:14px;
  padding-bottom:8px; border-bottom:1px solid var(--border);
}

/* Standalone task cards */
.standalone-grid { display:flex; flex-direction:column; gap:10px; }
.task-card {
  background:var(--card); border:1px solid var(--border);
  border-left:4px solid var(--accent); border-radius:var(--radius);
  padding:16px 18px; transition:all .2s;
}
.task-card:hover { background:var(--hover); box-shadow:var(--shadow); }
.task-header { display:flex; justify-content:space-between; align-items:flex-start; gap:10px; flex-wrap:wrap; }
.task-title  { font-size:.95rem; font-weight:600; flex:1; }
.task-badges { display:flex; gap:6px; flex-wrap:wrap; }
.task-detail { margin-top:8px; font-size:.82rem; color:var(--muted); }
.task-sub    { margin-top:8px; padding-left:16px; list-style:none; }
.task-sub li { font-size:.78rem; color:var(--dim); margin-bottom:3px; }
.task-sub li::before { content:"›  "; color:var(--muted); }

/* Project cards */
.project-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(360px,1fr)); gap:16px; }
.project-card {
  background:var(--card); border:1px solid var(--border);
  border-radius:var(--radius); padding:20px; transition:all .2s;
  position:relative; overflow:hidden; display:flex; flex-direction:column; gap:12px;
}
.project-card::before {
  content:''; position:absolute; top:0; left:0; right:0; height:3px;
  background:linear-gradient(90deg,#4ecdc4,#a29bfe);
}
.project-card:hover { background:var(--hover); box-shadow:var(--shadow); }
.proj-header { display:flex; justify-content:space-between; align-items:flex-start; gap:10px; }
.proj-title-row { display:flex; align-items:flex-start; gap:10px; flex:1; }
.proj-domain-icon { font-size:1.3rem; margin-top:2px; }
.proj-name  { font-size:1rem; font-weight:700; }
.proj-subtitle { font-size:.75rem; color:var(--muted); margin-top:2px; }
.proj-badges { display:flex; gap:5px; flex-wrap:wrap; }
.proj-stage {
  font-size:.82rem; color:var(--muted);
  background:rgba(255,255,255,.04); border-radius:8px; padding:8px 12px;
}
.proj-section { margin-top:0; }
.proj-section-label { font-size:.75rem; font-weight:700; color:var(--muted); margin-bottom:6px; }
.action-list { list-style:none; padding:0; }
.action-item {
  display:flex; align-items:flex-start; gap:8px; font-size:.82rem;
  padding:5px 0; border-bottom:1px solid rgba(255,255,255,.04);
}
.action-item:last-child { border-bottom:none; }
.check-box { color:var(--muted); font-size:.9rem; margin-top:1px; }
.notes-list { list-style:none; padding:0; }
.notes-list li { font-size:.78rem; color:var(--muted); padding:3px 0; }
.notes-list li::before { content:"•  "; color:var(--dim); }
.compl-toggle {
  background:rgba(0,184,148,.1); border:1px solid rgba(0,184,148,.25);
  color:#00b894; padding:5px 12px; border-radius:10px;
  cursor:pointer; font-size:.75rem; transition:all .2s;
}
.compl-toggle:hover { background:rgba(0,184,148,.2); }
.compl-list { list-style:none; padding:0; margin-top:8px; }
.compl-list li { font-size:.75rem; color:var(--dim); padding:3px 0; }
.compl-list li::before { content:"✓  "; color:#00b894; }
.proj-meta-footer {
  display:flex; flex-direction:column; gap:4px;
  border-top:1px solid var(--border); padding-top:10px;
}
.meta-tag { font-size:.72rem; color:var(--dim); }

/* Rules grid */
.rules-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:10px; }
.rule-item {
  background:var(--card); border:1px solid var(--border);
  border-left:3px solid #e17055; border-radius:var(--radius);
  padding:12px 16px; font-size:.85rem; color:var(--muted);
}

/* Portfolio */
.portfolio-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:10px; }
.portfolio-item {
  background:var(--card); border:1px solid var(--border);
  border-radius:var(--radius); padding:14px 16px;
}
.portfolio-ticker { font-size:1rem; font-weight:700; color:var(--accent); }
.portfolio-weight { font-size:.8rem; color:var(--muted); margin-top:3px; }
.portfolio-bar { height:5px; background:var(--border); border-radius:3px; margin-top:8px; }
.portfolio-bar-fill {
  height:100%; border-radius:3px;
  background:linear-gradient(90deg,#4ecdc4,#a29bfe);
}

/* Sprint Progress Bar */
.sprint-bar-section {
  background:var(--section-bg);
  border-radius:var(--radius); padding:14px 18px;
  margin:0 0 16px;
}
.sprint-bar-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; }
.sprint-pct { font-size:.78rem; color:var(--accent); font-weight:600; }
.sprint-track {
  display:grid; grid-template-columns:repeat(4,1fr);
  gap:4px; height:10px; border-radius:6px; overflow:hidden; margin-bottom:12px;
}
.sprint-seg { border-radius:inherit; transition:width .4s; }
.sprint-chips { display:grid; grid-template-columns:repeat(auto-fill,minmax(140px,1fr)); gap:8px; }
.sprint-chip { border-radius:8px; padding:8px 10px; }
.sprint-chip-name { font-size:.78rem; font-weight:700; }
.sprint-chip-label { font-size:.7rem; color:var(--muted); margin-top:3px; }

/* LiteLLM Panel */
.ll-section { margin-bottom:16px; }
.ll-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(160px,1fr)); gap:10px; }
.ll-card { background:var(--card); border:1px solid var(--border); border-radius:var(--radius); padding:14px; }
.ll-card-label { font-size:.72rem; color:var(--muted); margin-bottom:6px; }
.ll-card-status { font-size:.85rem; font-weight:700; }
.ll-models { display:flex; flex-wrap:wrap; gap:6px; }
.ll-model-badge {
  font-size:.7rem; padding:3px 8px; border-radius:999px;
  background:rgba(0,184,148,.15); color:#00b894; border:1px solid rgba(0,184,148,.3);
}
.ll-unhealthy { background:rgba(231,76,60,.15); color:#e74c3c; border-color:rgba(231,76,60,.3); }
.ll-error { font-size:.75rem; color:#e74c3c; margin-top:8px; padding:6px 10px; background:rgba(231,76,60,.1); border-radius:6px; }

/* Week Timeline */
.week-timeline { display:flex; gap:6px; flex-wrap:wrap; margin:8px 0; }
.week-chip {
  font-size:.68rem; font-weight:700; padding:4px 8px;
  border-radius:6px; cursor:default;
  transition:transform .15s;
}
.week-chip:hover { transform:scale(1.1); }

/* Agent Panel */
.agent-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(160px,1fr)); gap:10px; }
.agent-card {
  background:var(--card); border:1px solid var(--border);
  border-radius:var(--radius); padding:16px; text-align:center;
  transition:all .2s; position:relative;
}
.agent-card.active { border-color:#00b894; box-shadow:0 0 12px rgba(0,184,148,.2); }
.agent-card.conflict { border-color:#e74c3c; box-shadow:0 0 12px rgba(231,76,60,.2); }
.agent-icon { font-size:1.6rem; margin-bottom:6px; }
.agent-name { font-size:.88rem; font-weight:700; }
.agent-model { font-size:.7rem; color:var(--accent); margin-top:3px; }
.agent-status-dot {
  display:inline-block; width:8px; height:8px;
  border-radius:50%; margin-right:4px; vertical-align:middle;
}
.agent-task {
  font-size:.72rem; color:var(--text); margin-top:8px;
  padding-top:8px; border-top:1px solid rgba(255,255,255,.06);
}
.agent-history-item {
  display:grid; grid-template-columns:56px 72px 1fr 48px;
  gap:8px; align-items:center; padding:6px 0;
  border-bottom:1px solid rgba(255,255,255,.04); font-size:.78rem;
}
.agent-history-item .ah-time { color:var(--muted); }
.agent-history-item .ah-agent { font-weight:600; }
.agent-history-item .ah-task { color:var(--text); }
.agent-history-item .ah-duration { color:var(--dim); text-align:right; }

/* Engines */
.engine-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:10px; }
.engine-card {
  background:var(--card); border:1px solid var(--border);
  border-radius:var(--radius); padding:14px 16px;
  border-top:2px solid var(--accent);
}
.engine-name  { font-size:.9rem; font-weight:700; }
.engine-model { font-size:.72rem; color:var(--accent); margin-top:3px; }
.engine-role  { font-size:.72rem; color:var(--muted); margin-top:2px; }
.engine-status { display:inline-block; margin-top:8px; font-size:.7rem; font-weight:600; }

/* Rules summary */
.rules-list { list-style:none; }
.rules-list li {
  background:var(--card); border:1px solid var(--border);
  border-radius:8px; padding:9px 14px;
  margin-bottom:6px; font-size:.83rem; color:var(--muted);
}
.rule-active     { border-left:3px solid #00b894; }
.rule-deprecated { border-left:3px solid #636e72; opacity:.6; }

/* Completed */
.completed-item {
  background:var(--card); border:1px solid var(--border);
  border-radius:var(--radius); padding:12px 16px; margin-bottom:8px;
}
.compl-row { display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
.compl-title { font-size:.88rem; font-weight:600; flex:1; }
.compl-date  { font-size:.75rem; color:var(--dim); }
.compl-summary { font-size:.78rem; color:var(--muted); margin-top:6px; }
.hidden-item { display:none; }
.more-btn {
  background:rgba(255,255,255,.06); border:1px solid var(--border);
  color:var(--muted); padding:8px 18px; border-radius:20px;
  cursor:pointer; font-size:.8rem; display:block;
  margin: 8px auto 0; transition:all .2s;
}
.more-btn:hover { border-color:var(--accent); color:var(--accent); }

/* Misc */
.badge-sm {
  font-size:.7rem; padding:3px 9px; border-radius:10px; font-weight:600;
  white-space:nowrap;
}
.hidden { display:none !important; }
.empty-msg { color:var(--muted); text-align:center; }
.footer {
  text-align:center; padding:22px; color:var(--dim);
  font-size:.75rem; border-top:1px solid var(--border); margin-top:40px;
}

/* Quick Launcher */
.ql-bar {
  max-width:1440px; margin:12px auto 0;
  display:flex; gap:8px; flex-wrap:wrap;
}
.ql-btn {
  background:rgba(255,255,255,.07); border:1px solid var(--border);
  color:var(--text); padding:6px 14px; border-radius:20px;
  cursor:pointer; font-size:.78rem; font-weight:600;
  transition:all .18s; letter-spacing:.01em;
}
.ql-btn:hover {
  background:rgba(78,205,196,.16); border-color:var(--accent);
  color:var(--accent); transform:translateY(-1px);
}
.ql-btn:active { transform:translateY(0); }
.ql-icon {
  width:20px; height:20px; vertical-align:middle;
  border-radius:4px; margin-right:3px;
  object-fit:contain;
}
.ql-emoji { vertical-align:middle; }
.ql-engine {
  background:rgba(162,155,254,.1); border-color:rgba(162,155,254,.35);
  color:#a29bfe;
}
.ql-engine:hover {
  background:rgba(162,155,254,.22); border-color:#a29bfe;
  color:#a29bfe; transform:translateY(-1px);
}
.ql-backup {
  background:rgba(253,203,110,.1); border-color:rgba(253,203,110,.35);
  color:#fdcb6e;
}
.ql-backup:hover {
  background:rgba(253,203,110,.22); border-color:#fdcb6e;
  color:#fdcb6e; transform:translateY(-1px);
}

/* Toast */
.ql-toast {
  position:fixed; top:20px; right:20px;
  background:var(--card); border:1px solid #00b894;
  border-left:4px solid #00b894;
  color:var(--text); padding:14px 20px; border-radius:10px;
  font-size:.85rem; font-weight:600; z-index:9999;
  box-shadow:0 6px 30px rgba(0,0,0,.4);
  animation:fadeInOut 4s ease forwards;
}
.ql-toast.error {
  border-color:#e17055; border-left-color:#e17055;
}
@keyframes fadeInOut {
  0%   { opacity:0; transform:translateY(-10px); }
  10%  { opacity:1; transform:translateY(0); }
  80%  { opacity:1; }
  100% { opacity:0; }
}

/* Responsive */
@media (max-width:768px) {
  .header { padding:14px 16px; }
  .header h1 { font-size:1.3rem; }
  .summary-cards,.briefing-section,.filter-bar,.board-section { padding:0 14px; }
  .project-grid { grid-template-columns:1fr; }
  .ql-bar { gap:6px; }
  .ql-btn { font-size:.72rem; padding:5px 10px; }
}

/* ─── Life Roadmap ───────────────────────────────────────────────────── */
.axes-grid {
  display:grid; grid-template-columns:repeat(4,1fr); gap:12px;
  margin-bottom:20px;
}
.axis-card {
  background:var(--card); border:1px solid var(--border);
  border-radius:var(--radius); padding:16px; text-align:center;
  transition:transform .2s;
}
.axis-card:hover { transform:translateY(-3px); box-shadow:var(--shadow); }
.axis-icon { font-size:1.8rem; margin-bottom:6px; }
.axis-name { font-size:.9rem; font-weight:700; margin-bottom:4px; }
.axis-status { font-size:.78rem; color:var(--muted); margin-bottom:2px; }
.axis-metric { font-size:.72rem; color:var(--dim); }
.milestone-title { font-size:.9rem; font-weight:700; color:var(--muted); margin-bottom:12px; }
.milestone-timeline { display:flex; flex-direction:column; gap:0; padding-left:8px; }
.ms-item { display:flex; align-items:flex-start; gap:14px; min-height:44px; }
.ms-left { display:flex; flex-direction:column; align-items:center; width:16px; flex-shrink:0; }
.ms-dot {
  width:12px; height:12px; border-radius:50%;
  background:var(--border); border:2px solid var(--dim);
  flex-shrink:0; margin-top:4px;
}
.ms-dot.active { background:var(--accent); border-color:var(--accent); box-shadow:0 0 8px rgba(78,205,196,.5); }
.ms-dot.done   { background:#00b894; border-color:#00b894; }
.ms-line { width:2px; flex:1; background:var(--border); min-height:20px; }
.ms-line.active { background:var(--accent); }
.ms-line.done   { background:#00b894; }
.ms-content { display:flex; align-items:center; gap:10px; flex-wrap:wrap; padding:4px 0 10px; }
.ms-time  { font-size:.78rem; font-weight:700; color:var(--accent); min-width:70px; }
.ms-text  { font-size:.82rem; color:var(--text); }
.ms-axis  { font-size:.68rem; color:var(--muted); }

/* ─── Training ─────────────────────────────────────────────────────────── */
.training-hero {
  background:linear-gradient(135deg,rgba(255,107,107,.06),rgba(162,155,254,.06));
  border:1px solid rgba(255,107,107,.2);
  border-radius:var(--radius); padding:18px; margin-bottom:16px;
}
.rest-day { font-size:1.2rem; padding:20px; text-align:center; color:var(--muted); }
.training-today-card { margin-bottom:12px; }
.training-load { font-size:1rem; font-weight:800; margin-bottom:10px; }
.training-sessions { display:flex; gap:20px; flex-wrap:wrap; }
.session-block { display:flex; align-items:center; gap:8px; }
.session-label { font-size:.75rem; color:var(--muted); font-weight:600; }
.session-name  { font-size:.88rem; font-weight:600; }
.training-stats {
  display:flex; gap:16px; flex-wrap:wrap;
  padding-top:10px; border-top:1px solid rgba(255,255,255,.06);
}
.stat-item { font-size:.78rem; color:var(--muted); }
.training-exercises { margin-bottom:16px; overflow-x:auto; }
.ex-table { width:100%; border-collapse:collapse; font-size:.78rem; }
.ex-table th { text-align:left; padding:8px 10px; color:var(--muted); border-bottom:1px solid var(--border); font-weight:600; }
.ex-table td { padding:7px 10px; border-bottom:1px solid rgba(255,255,255,.04); }
.ex-order   { color:var(--accent); font-weight:700; width:40px; }
.ex-name    { font-weight:600; }
.ex-spec    { color:var(--muted); }
.ex-rest    { color:var(--dim); }
.ex-purpose { color:var(--muted); font-style:italic; }
.week-schedule-title { font-size:.85rem; font-weight:700; color:var(--muted); margin-bottom:10px; }
.week-schedule {
  display:grid; grid-template-columns:repeat(7,1fr); gap:6px;
  margin-bottom:16px;
}
.week-day {
  background:var(--card); border:1px solid var(--border);
  border-radius:10px; padding:10px 8px; text-align:center;
  font-size:.72rem; transition:all .2s;
}
.week-day.today {
  border-color:var(--accent); background:rgba(78,205,196,.08);
  box-shadow:0 0 12px rgba(78,205,196,.15);
}
.week-day-name { font-weight:800; font-size:.85rem; margin-bottom:4px; }
.week-day-load { font-weight:700; font-size:.7rem; margin-bottom:4px; }
.week-day-am   { color:var(--muted); font-size:.65rem; margin-bottom:2px; }
.week-day-pm   { color:var(--dim); font-size:.65rem; }
.prog-section { margin-top:4px; }
.prog-table { width:100%; border-collapse:collapse; font-size:.78rem; }
.prog-table th { text-align:left; padding:8px 10px; color:var(--muted); border-bottom:1px solid var(--border); font-weight:600; }
.prog-table td { padding:7px 10px; border-bottom:1px solid rgba(255,255,255,.04); }
.prog-target { color:#fdcb6e; font-weight:600; }
.prog-long   { color:#ff6b6b; font-weight:600; }

/* Collapsible toggle */
.collapsible-toggle {
  display:flex; align-items:center; gap:8px;
  width:100%; background:rgba(255,255,255,.04); border:1px solid var(--border);
  color:var(--muted); padding:10px 16px; border-radius:10px;
  cursor:pointer; font-size:.85rem; font-weight:700;
  transition:all .2s; margin-bottom:4px; text-align:left;
}
.collapsible-toggle:hover { background:rgba(78,205,196,.08); border-color:var(--accent); color:var(--text); }
.toggle-badge {
  font-size:.72rem; font-weight:600; color:var(--accent);
  background:rgba(78,205,196,.1); padding:2px 8px; border-radius:8px;
  margin-left:4px;
}
.collapsible-body { margin-top:8px; }

/* Today tasks in training */
.today-tasks { margin-top:14px; }
.today-tasks-title { font-size:.85rem; font-weight:700; color:var(--accent); margin-bottom:8px; }
.today-task-list { list-style:none; padding:0; }
.today-task-list li {
  padding:6px 0 6px 18px; font-size:.82rem; color:var(--text);
  position:relative; border-bottom:1px solid rgba(255,255,255,.04);
}
.today-task-list li:last-child { border-bottom:none; }
.today-task-list li::before { content:"›"; position:absolute; left:2px; color:var(--accent); font-size:.85rem; top:4px; }

@media (max-width:768px) {
  .axes-grid    { grid-template-columns:repeat(2,1fr); }
  .week-schedule{ grid-template-columns:repeat(4,1fr); }
}

/* Clickable axis cards */
.axis-card.clickable { cursor:pointer; }
.axis-card.clickable:hover {
  transform:translateY(-3px);
  box-shadow:0 0 16px rgba(78,205,196,.25);
}
.axis-card.active {
  border-color:var(--accent) !important;
  box-shadow:0 0 16px rgba(78,205,196,.3);
}

/* Milestone filter hint */
.ms-filter-hint {
  font-size:.78rem; color:var(--muted); margin-bottom:12px;
  display:flex; align-items:center; gap:10px;
}
.ms-reset-btn {
  background:rgba(78,205,196,.12); border:1px solid rgba(78,205,196,.3);
  color:var(--accent); padding:3px 10px; border-radius:10px;
  cursor:pointer; font-size:.72rem; transition:all .2s;
}
.ms-reset-btn:hover { background:rgba(78,205,196,.22); }

/* Milestone item filtered out */
.ms-item.filtered-out { display:none; }
"""


# ─── JS ───────────────────────────────────────────────────────────────────────
def _js() -> str:
    return """
// ─── Collapsible section toggle ───────────────────────
function toggleSection(id) {
  const el = document.getElementById(id);
  const arrow = document.getElementById(id + '-arrow');
  if (!el) return;
  const isHidden = el.classList.contains('hidden');
  el.classList.toggle('hidden');
  if (arrow) arrow.textContent = isHidden ? '▲' : '▼';
}

// ─── Briefing toggle ───────────────────────────────────
function toggleBriefing() {
  const body = document.getElementById('briefing-body');
  const btn  = document.getElementById('briefing-toggle');
  if (body.style.display === 'none') {
    body.style.display = '';
    btn.textContent = '▲ 접기';
  } else {
    body.style.display = 'none';
    btn.textContent = '▼ 브리핑 보기';
  }
}

// ─── Completed items toggle ───────────────────────────
function toggleCompl(id) {
  const el  = document.getElementById(id);
  const btn = el.previousElementSibling;
  const isHidden = el.classList.contains('hidden');
  el.classList.toggle('hidden');
  btn.textContent = isHidden
    ? '▲ 접기'
    : `✅ 완료 항목 보기 (${el.querySelectorAll('li').length})`;
}

// ─── More completed toggle ───────────────────────────
function toggleMore() {
  const container = document.getElementById('hidden-completed');
  const btn = document.getElementById('more-btn');
  const items = container.querySelectorAll('.hidden-item');
  const showing = btn.dataset.showing === 'true';
  items.forEach(el => { el.style.display = showing ? 'none' : ''; });
  btn.dataset.showing = showing ? 'false' : 'true';
  const count = items.length;
  btn.textContent = showing ? `▼ ${count}개 더 보기` : '▲ 접기';
}

// ─── Quick Launcher ───────────────────────────────────
async function launchApp(method) {
  if (typeof window.pywebview === 'undefined' || !window.pywebview.api) {
    showToast('⚠️ PyWebView API 없음 (브라우저 미지원)', false);
    return;
  }
  try {
    const result = await window.pywebview.api[method]();
    showToast(result, false);
  } catch(e) {
    showToast('❌ 오류: ' + e, true);
  }
}

async function launchEngineWatch() {
  const btn = document.getElementById('ql-engine-btn');
  if (btn) { btn.textContent = '⏳ 스캔 중...'; btn.disabled = true; }
  if (typeof window.pywebview === 'undefined' || !window.pywebview.api) {
    showToast('⚠️ PyWebView API 없음', false);
    if (btn) { btn.textContent = '🔍 Engine Watch'; btn.disabled = false; }
    return;
  }
  try {
    const result = await window.pywebview.api.run_engine_watch();
    showToast(result, result.startsWith('❌'));
  } catch(e) {
    showToast('❌ Engine Watch 오류: ' + e, true);
  } finally {
    if (btn) { btn.textContent = '🔍 Engine Watch'; btn.disabled = false; }
  }
}

async function launchBackup() {
  const btn = document.getElementById('ql-backup-btn');
  if (btn) { btn.textContent = '⏳ 백업 중...'; btn.disabled = true; }
  if (typeof window.pywebview === 'undefined' || !window.pywebview.api) {
    showToast('⚠️ PyWebView API 없음', false);
    if (btn) { btn.textContent = '💾 Backup'; btn.disabled = false; }
    return;
  }
  try {
    const result = await window.pywebview.api.run_backup();
    showToast(result, false);
  } catch(e) {
    showToast('❌ 백업 실패: ' + e, true);
  } finally {
    if (btn) { btn.textContent = '💾 Backup'; btn.disabled = false; }
  }
}

function showToast(msg, isError) {
  const existing = document.querySelector('.ql-toast');
  if (existing) existing.remove();
  const toast = document.createElement('div');
  toast.className = 'ql-toast' + (isError ? ' error' : '');
  toast.textContent = msg;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 4200);
}

// ─── Domain / Section filter ──────────────────────────
document.addEventListener('DOMContentLoaded', function() {
  let activeDomain  = 'all';
  let activeSection = 'all';

  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const domain  = this.dataset.domain;
      const section = this.dataset.section;
      if (domain !== undefined) {
        activeDomain = domain;
        document.querySelectorAll('[data-domain].filter-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
      }
      if (section !== undefined) {
        activeSection = section;
        document.querySelectorAll('[data-section].filter-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
      }
      applyFilters();
    });
  });

  function applyFilters() {
    // Filter project cards
    document.querySelectorAll('.project-card').forEach(card => {
      const dm = activeDomain  === 'all' || card.dataset.domain  === activeDomain;
      const sm = activeSection === 'all' || card.dataset.section === activeSection;
      card.style.display = (dm && sm) ? '' : 'none';
    });
    // Filter standalone task cards
    document.querySelectorAll('.task-card').forEach(card => {
      const dm = activeDomain  === 'all' || card.dataset.domain  === activeDomain;
      const sm = activeSection === 'all' || card.dataset.section === activeSection;
      card.style.display = (dm && sm) ? '' : 'none';
    });
  }
});

// ─── Milestone axis filter ────────────────────────
function filterMilestones(axis) {
  document.querySelectorAll('.axis-card').forEach(c => c.classList.remove('active'));
  const items = document.querySelectorAll('.ms-item');
  if (axis === 'all') {
    items.forEach(el => el.classList.remove('filtered-out'));
    return;
  }
  document.querySelectorAll('.axis-card').forEach(c => {
    const nameEl = c.querySelector('.axis-name');
    if (nameEl && nameEl.textContent.trim() === axis) c.classList.add('active');
  });
  items.forEach(el => {
    if (el.dataset.axis === axis) {
      el.classList.remove('filtered-out');
    } else {
      el.classList.add('filtered-out');
    }
  });
}

// ─── Theme toggle ─────────────────────────────────
function toggleTheme() {
  const body = document.body;
  const btn = document.getElementById('theme-toggle');
  const isLight = body.classList.toggle('light');
  btn.textContent = isLight ? '☀️' : '🌙';
}
"""


# ─── Entry point ─────────────────────────────────────────────────────────────
def main():
    print(f"[INFO] Loading: {INPUT_FILE}")
    data = load_data(INPUT_FILE)
    if not data:
        print("[ERROR] No data. Run parser.py first.")
        return
    html = generate_html(data)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK]   Dashboard: {OUTPUT_FILE}")
    print(f"       Projects: {len(data.get('projects',[]))} | Completed: {len(data.get('completed',[]))}")


if __name__ == "__main__":
    main()
