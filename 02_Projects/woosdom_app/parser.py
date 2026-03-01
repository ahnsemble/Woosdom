#!/usr/bin/env python3
from __future__ import annotations
"""
parser.py v0.2 — active_context.md → dashboard_data.json

Changes from v0.1:
- Project-level grouping (## header → project card)
- New JSON schema: projects / standalone_tasks / completed / briefing
- Auto-generated briefing section
- Engine table parsed from brain_directive.md
- Bug fixes: strikethrough, domain classification, Phase detection
"""

import json
import re
import os
from datetime import datetime

# ─── Paths ──────────────────────────────────────────────────────────────────
VAULT_ROOT     = "/Users/woosung/Desktop/Dev/Woosdom_Brain"
INPUT_FILE     = os.path.join(VAULT_ROOT, "00_System", "Prompts", "Ontology", "active_context.md")
DIRECTIVE      = os.path.join(VAULT_ROOT, "00_System", "Prompts", "Ontology", "brain_directive.md")
TRAINING_FILE  = os.path.join(VAULT_ROOT, "01_Domains", "Health", "training_protocol.md")
ROADMAP_FILE   = os.path.join(VAULT_ROOT, "01_Domains", "life_roadmap.md")
ACTIVITY_FILE  = os.path.join(VAULT_ROOT, "00_System", "Logs", "agent_activity.md")
TO_HANDS_FILE  = os.path.join(VAULT_ROOT, "00_System", "Templates", "to_hands.md")
FROM_HANDS_FILE= os.path.join(VAULT_ROOT, "00_System", "Templates", "from_hands.md")
SCRIPT_DIR     = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE    = os.path.join(SCRIPT_DIR, "dashboard_data.json")

# ─── Domain classification ───────────────────────────────────────────────────
DOMAIN_KEYWORDS = {
    "finance": ["매수", "포트폴리오", "드리프트", "SPMO", "Swarm", "금융",
                 "DCA", "리밸런싱", "MDD", "SCHD", "QQQM", "SMH", "TLT",
                 "GLDM", "Trinity", "FIRE", "백테스트", "적립식",
                 "Phase 20", "Phase 21", "Phase 22", "Phase 10", "Phase 11",
                 "BF-S1", "배당", "전략"],
    "game":    ["Crossy", "Godot", "Roblox", "보일러플레이트", "테스터",
                "Luau", "게임패스", "Campfire", "Mutator", "ServiceLocator",
                "GoodSignal", "ProfileStore", "Week 1", "재미검증"],
    "system":  ["Engine Watch", "Boot Briefing", "MCP", "로드맵", "n8n",
                "Telegram", "시스템", "cron", "Obsidian", "Codex",
                "Antigravity", "brain_directive", "launchd", "Mission Control",
                "엔진 평가", "Gemini 평가", "scanner", "API", "pipeline",
                "Phase 1", "Phase 2", "Phase 3", "Phase 4"],
    "career":  ["AEC", "SaaS", "MVP", "법령", "Career", "FDE", "건축",
                "Mooyoung", "아키텍", "영앤리치"],
    "health":  ["Hexagon", "커팅", "근력", "복싱", "러닝", "Health",
                "체력", "Big 3", "훈련", "운동"],
}

# Domain priority (earlier = higher priority match)
DOMAIN_ORDER = ["finance", "game", "system", "career", "health"]

# Section header → section key
SECTION_EMOJI_MAP = {
    "🔴": "critical",
    "🟡": "next",
    "🔵": "later",
    "✅": "done",
}

# Keywords for warning extraction
WARNING_KEYWORDS = ["⚠️", "🔴", "초과", "차단", "비상", "차단", "403", "BlockedOnUser",
                    "민감", "긴급", "주의", "위험", "불가"]


# ─── Domain classifier ───────────────────────────────────────────────────────
def classify_domain(text: str, name_hint: str = "") -> str:
    """Classify domain; name_hint (project name) takes highest priority."""
    # Check name hint first — project names are unambiguous
    if name_hint:
        name_lower = name_hint.lower()
        for domain in DOMAIN_ORDER:
            for kw in DOMAIN_KEYWORDS[domain]:
                if kw.lower() in name_lower:
                    return domain

    # Then check full text
    text_lower = text.lower()
    for domain in DOMAIN_ORDER:
        for kw in DOMAIN_KEYWORDS[domain]:
            if kw.lower() in text_lower:
                return domain
    return "other"


# ─── Status detector ─────────────────────────────────────────────────────────
def detect_status(text: str, section: str) -> str:
    if "🔄" in text:
        return "in_progress"
    if "❌" in text:
        return "blocked"
    # ✅ in done section → done; in active section → recently completed sub-item
    if section == "done":
        return "done"
    if "✅" in text and section not in ("critical", "next", "later"):
        return "done"
    return "waiting"


# ─── Engine table parser ─────────────────────────────────────────────────────
def parse_engines(directive_path: str) -> dict:
    """Parse execution architecture table from brain_directive.md."""
    default_engines = {
        "Brain":      {"model": "Claude Opus 4.6",  "role": "두뇌 (전략·판단)",   "status": "active"},
        "Hands-1":    {"model": "Antigravity → Sonnet 4.5 / Opus 4.6", "role": "로컬 실행 (코드·구현)", "status": "active"},
        "Hands-2":    {"model": "Antigravity → Gemini 3.1 Pro",        "role": "웹/멀티모달 (리서치)",   "status": "active"},
        "Hands-3":    {"model": "Codex 5.3",         "role": "비동기 코드 생성",    "status": "active"},
        "Hands-4":    {"model": "Claude Code (CLI)",  "role": "인터랙티브 코드 (git·디버그·리팩터)", "status": "active"},
        "Sub-Brain-1":{"model": "GPT-5.2 Thinking",  "role": "서브 브레인-1 (분석)","status": "standby"},
        "Sub-Brain-2":{"model": "Gemini 3.1 Pro",    "role": "서브 브레인-2 (리서치)","status": "standby"},
    }
    try:
        with open(directive_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return default_engines

    engines = {}
    # Find the architecture table (| Role | Engine | ... or | 구성 | 실체 | ...)
    table_match = re.search(
        r"\|\s*(?:Role|구성)\s*\|\s*(?:Engine|실체)\s*\|.*?\n(?:\|[-\s|]+\|\n)?((?:\|.*\|\n?)+)",
        content, re.MULTILINE
    )
    if not table_match:
        return default_engines

    for row in table_match.group(1).strip().split("\n"):
        cells = [c.strip() for c in row.split("|") if c.strip()]
        if len(cells) < 2:
            continue
        # role_cell like "**Brain (전략 두뇌)**"
        role_raw  = cells[0].strip("*").strip()
        model_raw = cells[1].strip() if len(cells) > 1 else ""
        resp_raw  = cells[2].strip() if len(cells) > 2 else ""

        # Derive name from role
        if "Brain" in role_raw and "Sub" not in role_raw and "Hands" not in role_raw:
            name = "Brain"
        elif "Hands-1" in role_raw:
            name = "Hands-1"
        elif "Hands-2" in role_raw:
            name = "Hands-2"
        elif "Hands-3" in role_raw:
            name = "Hands-3"
        elif "Hands-4" in role_raw:
            name = "Hands-4"
        elif "Memory" in role_raw:
            name = "Memory"
        else:
            continue

        # Clean model name: remove markdown
        model_clean = re.sub(r"\*\*|`", "", model_raw).strip()
        # shorten → remove ` / Opus 4.6` etc. for display
        model_display = model_clean[:60]

        engines[name] = {
            "model":  model_display,
            "role":   resp_raw[:80],
            "status": "active",
        }

    return engines if engines else default_engines


# ─── Section parser ───────────────────────────────────────────────────────────
def identify_section_from_header(header: str) -> tuple[str, str | None, str | None]:
    """
    Returns (section_key, project_name, subtitle) from a ## header line.
    e.g. '🟡 다음 — Engine Watch (엔진 모니터링)'
        → ('next', 'Engine Watch', '엔진 모니터링')
    e.g. '🔴 최우선'
        → ('critical', None, None)
    """
    section_key = None
    for emoji, key in SECTION_EMOJI_MAP.items():
        if emoji in header:
            section_key = key
            break

    if section_key is None:
        return (None, None, None)

    # Check for project name after "—"
    dash_match = re.search(r"[—–-]\s*(.+?)(?:\s*\((.+?)\))?\s*$", header)
    if dash_match:
        project_name = dash_match.group(1).strip()
        subtitle     = dash_match.group(2).strip() if dash_match.group(2) else None
        return (section_key, project_name, subtitle)

    return (section_key, None, None)


# ─── Body parser: extract structured fields from a project block ──────────────
def parse_project_body(body: str, section: str) -> dict:
    """
    Parse a project body (lines under a '## 🟡 다음 — Name' header).
    Returns metadata dict, action_items list, notes list, completed_items list,
    overall status, and detail text.
    """
    metadata        = {}
    action_items    = []
    notes           = []
    completed_items = []
    status          = detect_status(body, section)

    lines = body.split("\n")
    i = 0
    in_actions = False

    while i < len(lines):
        line     = lines[i]
        stripped = line.strip()

        if not stripped:
            in_actions = False
            i += 1
            continue

        # "- **Key:** Value" → metadata field
        meta_match = re.match(r"^- \*\*(.+?):\*\*\s*(.*)", stripped)
        if meta_match:
            key = meta_match.group(1).strip()
            val = meta_match.group(2).strip()

            # Detect action items block vs. metadata
            action_keys = {"다음 액션", "다음 액션 아이템", "next action"}
            if key.lower() in {k.lower() for k in action_keys}:
                in_actions = True
                # Sometimes value is on this line, sometimes on next lines
                if val:
                    action_items.append(_strip_status_emoji(val))
            else:
                in_actions = False
                # Status embedded in metadata
                if detect_status(val, section) == "in_progress":
                    status = "in_progress"
                metadata[key] = val
            i += 1
            continue

        # Indented numbered action items (continuation of action block)
        num_match = re.match(r"^\d+\.\s+(.+)$", stripped)
        if num_match and (line.startswith("  ") or in_actions):
            action_items.append(_strip_status_emoji(num_match.group(1).strip()))
            i += 1
            continue

        # Indented bullet action items
        if stripped.startswith("- ") and line.startswith("  ") and in_actions:
            action_items.append(_strip_status_emoji(stripped[2:].strip()))
            i += 1
            continue

        # Completed items: lines with ~~strikethrough~~ ✅ or "✅ 완료" style
        if "~~" in stripped or ("✅" in stripped and "완료" in stripped.lower()):
            completed_items.append(stripped.lstrip("- ").strip())
            i += 1
            continue

        # Non-indented bullets → notes
        if stripped.startswith("- ") and not line.startswith("  "):
            note_text = stripped[2:].strip()
            in_actions = False
            # Check if this looks like a warning
            notes.append(_strip_status_emoji(note_text))
            i += 1
            continue

        i += 1

    # Detect overall status from metadata
    for v in metadata.values():
        s = detect_status(v, section)
        if s == "in_progress":
            status = "in_progress"
            break

    return {
        "metadata":       metadata,
        "action_items":   action_items,
        "notes":          notes,
        "completed_items":completed_items,
        "status":         status,
    }


def _strip_status_emoji(text: str) -> str:
    """Remove leading status emojis from text."""
    return re.sub(r"^[🔄✅❌⚠️🔴🟡🔵]\s*", "", text).strip()


# ─── Main parser ─────────────────────────────────────────────────────────────
def parse_active_context(filepath: str) -> dict:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"[WARN] File not found: {filepath}")
        return _empty_data()
    except Exception as e:
        print(f"[WARN] Error reading: {e}")
        return _empty_data()

    data = _empty_data()

    # ─── Meta: updated date ──────────────────────────────────────────────────
    updated_match = re.search(r"\*Updated:\s*(\d{4}-\d{2}-\d{2})", content)
    if updated_match:
        data["meta"]["updated"] = updated_match.group(1)
        # Also try to extract the note in parentheses
        note_match = re.search(r"\*Updated:[^(]*\(([^)]+)\)", content)
        if note_match:
            data["meta"]["updated_note"] = note_match.group(1).strip()
    else:
        data["meta"]["updated"] = datetime.now().strftime("%Y-%m-%d")

    # ─── Meta: ruleset version ───────────────────────────────────────────────
    rs = re.search(r"헌법 요약\s*\(v([\d.]+)\)", content)
    if rs:
        data["meta"]["ruleset"] = f"v{rs.group(1)}"
    else:
        rs2 = re.search(r"\(v(\d+\.\d+)\)", content)
        if rs2:
            data["meta"]["ruleset"] = f"v{rs2.group(1)}"

    # ─── Meta: highest completed Phase ───────────────────────────────────────
    phase_nums = [int(p) for p in re.findall(r"Phase\s+(\d+)\s*(?:전체\s*)?완료", content)]
    if phase_nums:
        data["meta"]["phase"] = f"Phase {max(phase_nums)} 완료"

    # ─── Split content into ## blocks ────────────────────────────────────────
    blocks = re.split(r"^## ", content, flags=re.MULTILINE)

    for block in blocks:
        if not block.strip():
            continue

        first_nl    = block.find("\n")
        header_line = block[:first_nl].strip() if first_nl != -1 else block.strip()
        body        = block[first_nl+1:] if first_nl != -1 else ""

        # ── Special sections ────────────────────────────────────────────────
        if "상시 규칙" in header_line:
            data["standing_rules"] = _parse_standing_rules(body)
            continue
        if "현행 포트폴리오" in header_line:
            data["portfolio"] = _parse_portfolio(body)
            continue
        if "헌법 요약" in header_line:
            data["rules_summary"] = _parse_rules_summary(body)
            continue

        # ── Task sections ────────────────────────────────────────────────────
        (section_key, project_name, subtitle) = identify_section_from_header(header_line)
        if section_key is None:
            continue

        # "completed" (✅ 최근 완료) section → extract individual completed items
        if section_key == "done":
            _parse_completed_section(body, data["completed"])
            continue

        # Project with name after "—"
        if project_name:
            parsed = parse_project_body(body, section_key)
            proj = {
                "name":            project_name,
                "subtitle":        subtitle or "",
                "section":         section_key,
                "domain":          classify_domain(project_name + " " + body[:300], name_hint=project_name),
                "status":          parsed["status"],
                "metadata":        parsed["metadata"],
                "action_items":    parsed["action_items"],
                "notes":           parsed["notes"],
                "completed_items": parsed["completed_items"],
            }
            data["projects"].append(proj)

        else:
            # No project name → each "- **bold**" or "- plain" is a standalone task
            tasks = _parse_standalone_tasks(body, section_key, header_line)
            data["standalone_tasks"].extend(tasks)

    return data


def _parse_standalone_tasks(body: str, section: str, header: str) -> list:
    """Parse a section without a project name into individual task cards."""
    tasks        = []
    current      = None
    detail_lines = []
    sub_items    = []

    def _flush():
        if current:
            current["detail"]    = "\n".join(detail_lines).strip()
            current["sub_items"] = sub_items
            tasks.append(current)

    for line in body.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue

        # Bold: "- **Title** rest"
        bold_match = re.match(r"^- \*\*(.+?)\*\*(.*)$", stripped)
        # Plain non-indented bullet
        plain_match = (re.match(r"^- (.+)$", stripped)
                       if not bold_match and not line.startswith("  ")
                       else None)

        if bold_match or plain_match:
            _flush()
            if bold_match:
                title = bold_match.group(1).strip()
                rest  = bold_match.group(2).strip()
            else:
                title = plain_match.group(1).strip()
                rest  = ""

            full = title + " " + rest
            current = {
                "title":    title,
                "section":  section,
                "domain":   classify_domain(title + " " + header, name_hint=title),
                "status":   detect_status(full, section),
                "detail":   "",
                "sub_items":[],
            }
            detail_lines = [rest] if rest else []
            sub_items    = []
            continue

        # Indented sub-item bullet
        if current and stripped.startswith("- ") and line.startswith("  "):
            sub_items.append(stripped[2:].strip())
            continue

        # Indented numbered sub-item
        num_m = re.match(r"^\d+\.\s+(.+)$", stripped)
        if current and num_m and line.startswith("  "):
            sub_items.append(num_m.group(1).strip())
            continue

        # Detail continuation
        if current and stripped:
            detail_lines.append(stripped)

    _flush()
    return tasks


def _parse_completed_section(body: str, completed_list: list):
    """Parse ✅ 최근 완료 section."""
    current = None
    desc_lines = []

    def _flush():
        if current:
            current["summary"] = " ".join(desc_lines).strip()
            completed_list.append(current)

    for line in body.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue

        # "- **Title** — date ✅" pattern
        bold_match = re.match(r"^- \*\*(.+?)\*\*\s*[—–-]?\s*(.*)$", stripped)
        if bold_match:
            _flush()
            title    = bold_match.group(1).strip()
            rest     = bold_match.group(2).strip()
            # Try to extract date from rest
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", rest)
            date_str   = date_match.group(1) if date_match else ""
            current    = {
                "title":   title,
                "date":    date_str,
                "domain":  classify_domain(title + " " + rest),
                "summary": "",
            }
            desc_lines = [rest] if rest else []
            continue

        # Indented detail
        if current and stripped.startswith("- ") and line.startswith("  "):
            desc_lines.append(stripped[2:].strip())
            continue

        # Plain non-indented bullet (fallback)
        plain_m = re.match(r"^- (.+)$", stripped)
        if plain_m and not line.startswith("  "):
            _flush()
            title = plain_m.group(1).strip()
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", title)
            date_str   = date_match.group(1) if date_match else ""
            current    = {
                "title":   title,
                "date":    date_str,
                "domain":  classify_domain(title),
                "summary": "",
            }
            desc_lines = []
            continue

        if current:
            desc_lines.append(stripped)

    _flush()


def _parse_standing_rules(body: str) -> list:
    rules = []
    current = None
    for line in body.split("\n"):
        s = line.strip()
        if not s:
            continue
        bold_m = re.match(r"^- \*\*(.+?)\*\*(.*)$", s)
        if bold_m:
            if current:
                rules.append(current)
            current = bold_m.group(1).strip()
        elif s.startswith("- ") and not line.startswith("  "):
            if current:
                rules.append(current)
            current = s[2:].strip()
    if current:
        rules.append(current)
    return rules


def _parse_portfolio(body: str) -> dict:
    portfolio = {}
    for ticker, weight in re.findall(r"([A-Z]{2,5})\s+(\d+)%", body):
        portfolio[ticker] = int(weight)
    return portfolio


def _parse_rules_summary(body: str) -> list:
    rules = []
    for line in body.split("\n"):
        s = line.strip()
        if s.startswith("- "):
            rule_text = s[2:].strip()
            # Fix: only add "(폐기)" if not already present
            def replace_strikethrough(m):
                inner = m.group(1)
                suffix = " (폐기)" if "폐기" not in inner and "보류" not in inner else ""
                return f"{inner}{suffix}"
            rule_text = re.sub(r"~~(.+?)~~", replace_strikethrough, rule_text)
            rules.append(rule_text)
    return rules


# ─── Briefing generator ───────────────────────────────────────────────────────
def generate_briefing(data: dict) -> dict:
    """Generate the briefing section from parsed data."""
    now = datetime.now()
    
    # Top priority: first critical standalone task, or first critical project
    top_priority = ""
    critical_tasks = [t for t in data["standalone_tasks"] if t["section"] == "critical"]
    critical_projs = [p for p in data["projects"] if p["section"] == "critical"]
    if critical_tasks:
        top_priority = critical_tasks[0]["title"]
    elif critical_projs:
        top_priority = critical_projs[0]["name"]

    # Today actions: critical items + first action_item of each next project (max 5)
    today_actions = []
    for t in critical_tasks:
        today_actions.append(t["title"])
    for t in (data["standalone_tasks"]):
        if t["section"] == "next" and len(today_actions) < 5:
            today_actions.append(t["title"])
    for p in data["projects"]:
        if p["section"] in ("critical", "next") and p["action_items"] and len(today_actions) < 5:
            today_actions.append(p["action_items"][0])

    today_actions = today_actions[:5]

    # Warnings: scan all text for warning keywords
    warnings = []
    all_text_sources = []
    for p in data["projects"]:
        all_text_sources.extend(p["notes"])
        all_text_sources.extend(p["action_items"])
        for v in p["metadata"].values():
            all_text_sources.append(v)
    for t in data["standalone_tasks"]:
        all_text_sources.append(t.get("detail", ""))
        all_text_sources.extend(t.get("sub_items", []))

    for line in all_text_sources:
        if any(kw in line for kw in WARNING_KEYWORDS) and line not in warnings:
            warnings.append(line.strip()[:200])

    warnings = warnings[:5]

    # This week: all action_items from next projects (max 8)
    this_week = []
    for p in data["projects"]:
        if p["section"] == "next":
            this_week.extend(p["action_items"])
    this_week = this_week[:8]

    return {
        "generated_at": now.strftime("%Y-%m-%d %H:%M"),
        "top_priority": top_priority,
        "today_actions": today_actions,
        "warnings": warnings,
        "this_week": this_week,
    }


# ─── Training protocol parser ────────────────────────────────────────────────
WEEKDAY_SESSIONS = {
    0: {"day": "월", "morning": "하체 근력+파워+택티컬", "evening": "복싱", "load": "HIGH"},
    1: {"day": "화", "morning": "—", "evening": "복싱 (테크니컬)", "load": "MOD-HIGH"},
    2: {"day": "수", "morning": "Zone 2 러닝 5km + 모빌리티", "evening": "—", "load": "LOW"},
    3: {"day": "목", "morning": "상체 근력+파워 (웨이티드 캘리스테닉스)", "evening": "복싱", "load": "HIGH"},
    4: {"day": "금", "morning": "속도 전용 + 능동적 회복", "evening": "—", "load": "LOW-MOD"},
    5: {"day": "토", "morning": "Contrast Training + 전신 파워", "evening": "—", "load": "HIGH"},
    6: {"day": "일", "morning": "완전 휴식", "evening": "—", "load": "ZERO"},
}


def parse_training(filepath: str) -> dict:
    """Parse training_protocol.md for dashboard display."""
    today_weekday = datetime.now().weekday()  # 0=Mon
    today_session = WEEKDAY_SESSIONS.get(today_weekday, {})

    # Weekly schedule
    weekly = []
    for i in range(7):
        s = WEEKDAY_SESSIONS[i]
        weekly.append({
            "day": s["day"],
            "morning": s["morning"],
            "evening": s["evening"],
            "load": s["load"],
            "is_today": i == today_weekday,
        })

    # Parse exercise table for today from the file
    exercises = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        day_names = {0: "월요일", 1: "화요일", 2: "수요일", 3: "목요일", 4: "금요일", 5: "토요일", 6: "일요일"}
        day_name = day_names[today_weekday]

        # Find section: ### 월요일 — ... up to next ###
        pattern = rf"### {day_name}\s*[—–-].*?\n(.*?)(?=\n### |\n---|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            section = match.group(1)
            # Parse markdown table rows (| 순서 | 운동 | 규격 | 휴식 | 목적 |)
            table_rows = re.findall(
                r"\|\s*([A-Z][0-9]?|W/U)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|",
                section
            )
            for row in table_rows:
                exercises.append({
                    "order":   row[0].strip(),
                    "name":    row[1].strip(),
                    "spec":    row[2].strip(),
                    "rest":    row[3].strip(),
                    "purpose": row[4].strip(),
                })
    except Exception:
        pass

    # Progression goals (hardcoded from protocol — stable data)
    progression = [
        {"exercise": "웨이티드 턱걸이", "current": "+15kg×5", "target_12w": "+25kg×5", "long_term": "+40kg×3"},
        {"exercise": "웨이티드 딥스",   "current": "+20kg×8", "target_12w": "+30kg×5", "long_term": "+50kg×3"},
        {"exercise": "피스톨 스쿼트",   "current": "미확인",    "target_12w": "자체중량 5회", "long_term": "+10kg 고블릿 5회"},
    ]

    stats = {
        "weight":   "73kg → 69kg",
        "big3":     "430kg (Elite)",
        "protocol": "Tactical Hexagon v2.3",
        "phase":    "12주 블록 주기화",
    }

    return {
        "today":           today_session,
        "today_exercises": exercises,
        "weekly":          weekly,
        "progression":     progression,
        "stats":           stats,
    }


def parse_roadmap(filepath: str) -> dict:
    """Parse life_roadmap.md for dashboard display."""
    result = {"axes": [], "milestones": []}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return result

    # Parse 4축 현황 table
    axes_match = re.findall(r"\|\s*([💰🔧💪🏠])\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|", content)
    for row in axes_match:
        result["axes"].append({
            "icon":   row[0].strip(),
            "name":   row[1].strip(),
            "status": row[2].strip(),
            "metric": row[3].strip(),
        })

    # Parse milestones table
    ms_match = re.findall(r"\|\s*(\d{4}\s*\w+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(\w+)\s*\|", content)
    for row in ms_match:
        result["milestones"].append({
            "time":      row[0].strip(),
            "milestone": row[1].strip(),
            "axis":      row[2].strip(),
            "status":    row[3].strip(),
        })

    return result


# ─── Agent activity parser ──────────────────────────────────────────────────
STATUS_EMOJI_MAP = {
    "🟢": "active", "⏳": "waiting", "🔵": "idle",
    "⚡": "conflict", "✅": "done", "❌": "failed",
    "📡": "communicating", "🤝": "meeting",
}


def parse_agent_activity(filepath: str) -> dict:
    """Parse agent_activity.md → {current: [...], recent_done: [...], logs: [...]}"""
    result: dict = {"current": [], "recent_done": [], "logs": []}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return result

    def _parse_table_rows(block: str) -> list:
        """마크다운 테이블 행 파싱 (헤더·구분선 제외)"""
        rows = []
        for line in block.split("\n"):
            stripped = line.strip()
            if not stripped.startswith("|") or stripped.startswith("| ---") or "-|-" in stripped:
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if all(c in ("---", "----", "") or set(c) <= {'-'} for c in cells):
                continue
            rows.append(cells)
        return rows

    def _normalize_status(status_raw: str, default: str = "") -> str:
        s = (status_raw or "").strip()
        if not s:
            return default
        if s in STATUS_EMOJI_MAP:
            return STATUS_EMOJI_MAP[s]
        lower = s.lower()
        if "active" in lower or "🟢" in s or "진행" in s:
            return "active"
        if "waiting" in lower or "⏳" in s or "대기" in s:
            return "waiting"
        if "idle" in lower or "🔵" in s or "유휴" in s:
            return "idle"
        if "conflict" in lower or "⚡" in s or "충돌" in s:
            return "conflict"
        if "done" in lower or "✅" in s or "완료" in s:
            return "done"
        if "failed" in lower or "❌" in s or "실패" in s:
            return "failed"
        if "communicating" in lower or "📡" in s or "통신" in s:
            return "communicating"
        if "meeting" in lower or "🤝" in s or "회의" in s:
            return "meeting"
        return lower

    def _looks_like_time(value: str) -> bool:
        return bool(re.match(r"^(\d{2}:\d{2}|\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2})?)$", value.strip()))

    # Split by ## 섹션
    blocks = re.split(r"^## ", content, flags=re.MULTILINE)
    for block in blocks:
        if not block.strip():
            continue
        first_nl = block.find("\n")
        header = block[:first_nl].strip() if first_nl != -1 else block.strip()
        body = block[first_nl + 1:] if first_nl != -1 else ""

        if "현재 활동" in header:
            for cells in _parse_table_rows(body):
                if len(cells) < 4:
                    continue
                # | 시각 | 에이전트 | 도메인 | 작업 | 상태 | 비고 |
                status_raw = cells[4] if len(cells) > 4 else ""
                status = _normalize_status(status_raw, "active")
                if cells[1].strip() in ("", "에이전트", "활동 없음"):
                    continue
                result["current"].append({
                    "time": cells[0],
                    "agent": cells[1],
                    "domain": cells[2],
                    "task": cells[3],
                    "status": status,
                    "note": cells[5] if len(cells) > 5 else "",
                })

        elif "최근 완료" in header:
            for cells in _parse_table_rows(body):
                if len(cells) < 4:
                    continue
                # | 완료 시각 | 에이전트 | 도메인 | 작업 | 소요 | 결과 요약 |
                if cells[1].strip() in ("", "에이전트"):
                    continue
                result["recent_done"].append({
                    "time": cells[0],
                    "agent": cells[1],
                    "domain": cells[2],
                    "task": cells[3],
                    "duration": cells[4] if len(cells) > 4 else "",
                    "summary": cells[5] if len(cells) > 5 else "",
                })

        elif "대화 로그" in header:
            for cells in _parse_table_rows(body):
                if len(cells) < 3:
                    continue

                time_str, from_agent, to_agent, msg, status_raw = "", "", "", "", ""
                if len(cells) >= 5:
                    time_str, from_agent, to_agent, msg, status_raw = cells[0], cells[1], cells[2], cells[3], cells[4]
                elif len(cells) == 4:
                    if _looks_like_time(cells[0]):
                        time_str, from_agent, to_agent, msg = cells[0], cells[1], cells[2], cells[3]
                    else:
                        from_agent, to_agent, msg, status_raw = cells[0], cells[1], cells[2], cells[3]
                else:  # len == 3
                    from_agent, to_agent, msg = cells[0], cells[1], cells[2]

                if from_agent.strip().lower() in ("", "from", "발신", "보낸이"):
                    continue
                if to_agent.strip().lower() in ("", "to", "수신", "받는이"):
                    continue
                if msg.strip().lower() in ("", "msg", "message", "내용"):
                    continue

                result["logs"].append({
                    "time": time_str,
                    "from": from_agent,
                    "to": to_agent,
                    "msg": msg,
                    "status": _normalize_status(status_raw, ""),
                })

    return result


# ─── to_hands / from_hands log parser ────────────────────────────────────────
def parse_agent_logs() -> list:
    """Parse to_hands.md and from_hands.md → logs list for agent_activity.logs.

    to_hands.md  : Brain → engine  (direction 'to')
    from_hands.md: engine → Brain  (direction 'from')

    Returns list of:
      {"time": "HH:MM", "from": "Brain"|engine, "to": engine|"Brain",
       "msg": str, "status": str}
    """
    logs = []

    def _parse_one(filepath: str, direction: str):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return None
        if not content.strip():
            return None

        # Extract YAML frontmatter (--- ... ---)
        fm_match = re.match(r"^---\n(.*?)\n---\n?(.*)", content, re.DOTALL)
        if not fm_match:
            return None

        fm_text = fm_match.group(1)
        body    = fm_match.group(2).strip()

        # Parse key: "value" or key: value
        fm: dict = {}
        for line in fm_text.split("\n"):
            kv = re.match(r'^(\w+):\s*["\']?(.*?)["\']?\s*$', line)
            if kv:
                fm[kv.group(1).strip()] = kv.group(2).strip()

        engine  = fm.get("engine", "unknown")
        created = fm.get("created", fm.get("completed", ""))
        status  = fm.get("status", "")

        # Extract HH:MM from ISO timestamp or MM-DD from date
        time_str = ""
        ts_match = re.search(r"T(\d{2}:\d{2})", created)
        if ts_match:
            time_str = ts_match.group(1)
        elif re.match(r"\d{4}-\d{2}-\d{2}", created):
            time_str = created[5:10]  # MM-DD

        # Message: frontmatter title first, else first heading in body
        title = fm.get("title", "")
        if not title:
            h_match = re.search(r"^#{1,3}\s+(.+)$", body, re.MULTILINE)
            title = h_match.group(1).strip() if h_match else "(내용 없음)"

        title = re.sub(r"\*+", "", title).strip()
        if len(title) > 60:
            title = title[:60] + "..."

        if direction == "to":
            return {"time": time_str, "from": "Brain", "to": engine,
                    "msg": title, "status": status}
        else:
            return {"time": time_str, "from": engine, "to": "Brain",
                    "msg": title, "status": status}

    to_entry   = _parse_one(TO_HANDS_FILE,   "to")
    from_entry = _parse_one(FROM_HANDS_FILE, "from")

    if to_entry:
        logs.append(to_entry)
    if from_entry:
        logs.append(from_entry)

    return logs


# ─── Empty data ──────────────────────────────────────────────────────────
def _empty_data() -> dict:
    return {
        "projects":        [],
        "standalone_tasks":[],
        "completed":       [],
        "briefing":        {},
        "portfolio":       {},
        "standing_rules":  [],
        "rules_summary":   [],
        "engines":         {},
        "training":        {},
        "roadmap":         {},
        "agent_activity":  {"current": [], "recent_done": [], "logs": []},
        "litellm":         {"proxy_up": False, "redis_up": False, "models": [], "error": None},
        "sprint_progress": [],
        "meta":            {"updated": "", "updated_note": "", "ruleset": "", "phase": ""},
    }


# ─── LiteLLM Status ───────────────────────────────────────────────────────
import urllib.request as _urllib_req
import json as _json_m
import socket as _socket

def parse_litellm_status() -> dict:
    """LiteLLM 프록시(localhost:4000) + Redis(localhost:6379) 상태 조회."""
    result = {
        "proxy_up": False,
        "redis_up": False,
        "models":   [],
        "error":    None,
    }
    # 1) /health 엔드포인트
    try:
        key = os.environ.get("LITELLM_MASTER_KEY", "")
        req = _urllib_req.Request("http://localhost:4000/health", method="GET")
        if key:
            req.add_header("Authorization", "Bearer " + key)
        with _urllib_req.urlopen(req, timeout=3) as resp:
            data = _json_m.loads(resp.read())
            result["proxy_up"] = True
            for ep in data.get("healthy_endpoints", []):
                result["models"].append({"name": ep.get("model", "?"), "status": "healthy"})
            for ep in data.get("unhealthy_endpoints", []):
                result["models"].append({"name": ep.get("model", "?"), "status": "unhealthy"})
    except Exception as e:
        result["error"] = str(e)[:120]
    # 2) Redis PING
    try:
        s = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect(("localhost", 6379))
        s.sendall(b"PING\r\n")
        resp = s.recv(64)
        result["redis_up"] = b"+PONG" in resp or b"PONG" in resp
        s.close()
    except Exception:
        result["redis_up"] = False
    return result


# ─── Sprint Progress ───────────────────────────────────────────────────────
def parse_sprint_progress() -> list:
    """active_context.md 에서 Phase 4 Sprint 상태 파싱. 실패 시 하드코딩 폴백."""
    HARDCODED = [
        {"name": "Sprint 1", "label": "LiteLLM + Redis",   "status": "done"},
        {"name": "Sprint 2", "label": "Redis Pub/Sub",      "status": "next"},
        {"name": "Sprint 3", "label": "Claude Code CLI",    "status": "waiting"},
        {"name": "Sprint 4", "label": "Persona Council",    "status": "waiting"},
    ]
    STATUS_MAP = {"✅": "done", "🔄": "in_progress", "⏳": "waiting", "🟢": "done"}
    try:
        with open(INPUT_FILE, encoding="utf-8") as f:
            content = f.read()
        # Phase 4 스프린트 섹션 찾기
        m = re.search(r"Phase 4[^\n]*\n(.*?)(?=\n#{1,2} |─{3}|$)", content, re.DOTALL)
        if not m:
            return HARDCODED
        block = m.group(1)
        sprints = []
        for line in block.splitlines():
            sm = re.search(r"(Sprint\s*\d+)[^\|\n]*(\|[^\n]+)", line, re.IGNORECASE)
            if sm:
                name = sm.group(1).strip()
                rest = sm.group(2)
                status = "waiting"
                for emoji, st in STATUS_MAP.items():
                    if emoji in line:
                        status = st
                        break
                label_m = re.search(r"\|\s*([^|\n]+)", rest)
                label = label_m.group(1).strip() if label_m else ""
                sprints.append({"name": name, "label": label, "status": status})
        return sprints if sprints else HARDCODED
    except Exception:
        return HARDCODED



# ─── Entry point ─────────────────────────────────────────────────────────────
def main():
    print(f"[INFO] Parsing: {INPUT_FILE}")
    data = parse_active_context(INPUT_FILE)

    print(f"[INFO] Projects: {len(data['projects'])}")
    print(f"[INFO] Standalone tasks: {len(data['standalone_tasks'])}")
    print(f"[INFO] Completed: {len(data['completed'])}")
    print(f"[INFO] Portfolio tickers: {len(data['portfolio'])}")

    # Generate briefing
    data["briefing"] = generate_briefing(data)
    print(f"[INFO] Today actions: {len(data['briefing']['today_actions'])}")
    print(f"[INFO] Warnings: {len(data['briefing']['warnings'])}")

    # Parse engines from brain_directive.md
    data["engines"] = parse_engines(DIRECTIVE)
    print(f"[INFO] Engines: {len(data['engines'])}")

    # Parse training protocol
    data["training"] = parse_training(TRAINING_FILE)
    print(f"[INFO] Today exercises: {len(data['training']['today_exercises'])}")

    # Parse life roadmap
    data["roadmap"] = parse_roadmap(ROADMAP_FILE)
    print(f"[INFO] Milestones: {len(data['roadmap']['milestones'])}")

    # Parse agent activity
    data["agent_activity"] = parse_agent_activity(ACTIVITY_FILE)
    print(f"[INFO] Active agents: {len(data['agent_activity']['current'])}")
    print(f"[INFO] Recent agent tasks: {len(data['agent_activity']['recent_done'])}")

    # Parse to_hands / from_hands communication logs + activity log table merge
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
    print(f"[INFO] Agent logs: {len(data['agent_activity']['logs'])}")

    # Merge idle engines into agent_activity.current
    active_agents = {a["agent"] for a in data["agent_activity"]["current"]}
    for name, info in data["engines"].items():
        if name not in active_agents:
            data["agent_activity"]["current"].append({
                "time":   "",
                "agent":  name,
                "domain": "",
                "task":   "",
                "status": "idle",
                "note":   info.get("model", ""),
            })

    # Parse LiteLLM status
    data["litellm"] = parse_litellm_status()
    ll = data["litellm"]
    print(f"[INFO] LiteLLM proxy: {'UP' if ll['proxy_up'] else 'DOWN'}, Redis: {'UP' if ll['redis_up'] else 'DOWN'}")

    # Parse sprint progress
    data["sprint_progress"] = parse_sprint_progress()
    print(f"[INFO] Sprint items: {len(data['sprint_progress'])}")

    # Inject Crossy weeks into matching project
    CROSSY_WEEKS = [
        {"week": "1-2",   "label": "Godot 1분 런 프로토",   "status": "next"},
        {"week": "2말",  "label": "재미 Y/N 판정",       "status": "waiting"},
        {"week": "3-5",   "label": "Luau 전환",             "status": "waiting"},
        {"week": "6-7",   "label": "클로즈드 베타",         "status": "waiting"},
        {"week": "8-10",  "label": "오픈베타→출시",        "status": "waiting"},
        {"week": "11-12", "label": "Moments+수익화",      "status": "waiting"},
    ]
    for proj in data["projects"]:
        if "Crossy" in proj.get("name", "") or "crossy" in proj.get("name", "").lower():
            if "metadata" not in proj:
                proj["metadata"] = {}
            proj["metadata"]["weeks"] = CROSSY_WEEKS

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK]   Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
