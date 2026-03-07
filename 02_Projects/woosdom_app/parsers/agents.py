"""
parsers/agents.py — Agent grid parser for Monitor v2 P2 (agent-grid panel).

Combines:
  - Agent spec frontmatter (id, name, department, tier, status) from 00_System/Specs/agents/*.md
  - Activity log from 00_System/Logs/agent_activity.md
"""

import re
from datetime import datetime, timedelta
from pathlib import Path

from parsers import get_vault_root

VAULT_ROOT = get_vault_root()
AGENTS_DIR = VAULT_ROOT / "00_System" / "Specs" / "agents"
ACTIVITY_LOG = VAULT_ROOT / "00_System" / "Logs" / "agent_activity.md"

# Freshness thresholds
FRESH_HOURS = 24
AGING_HOURS = 72


def _parse_frontmatter(filepath: Path) -> dict | None:
    """Extract YAML frontmatter between --- delimiters."""
    try:
        text = filepath.read_text(encoding="utf-8")
    except OSError:
        return None

    # Find frontmatter block (second --- pair; first may be after title line)
    parts = text.split("---")
    if len(parts) < 3:
        return None

    # Try each --- block for valid YAML-like key: value pairs
    for block in parts[1:]:
        lines = block.strip().splitlines()
        data = {}
        for line in lines:
            m = re.match(r'^(\w[\w-]*)\s*:\s*"?(.+?)"?\s*$', line)
            if m:
                data[m.group(1)] = m.group(2)
        if "id" in data and "name" in data:
            # Also parse engine binding from body
            eb = _parse_engine_binding(text)
            data.update(eb)
            return data
    return None


def _parse_engine_binding(text: str) -> dict:
    """Parse '## 4. Engine Binding' yaml block for primary_engine/model."""
    result = {}
    m = re.search(r'## 4\.\s*Engine Binding.*?```(?:yaml)?\s*\n(.*?)```', text, re.DOTALL)
    if not m:
        return result
    block = m.group(1)
    for line in block.strip().splitlines():
        kv = re.match(r'^(\w[\w_]*)\s*:\s*"?(.+?)"?\s*$', line)
        if kv:
            key, val = kv.group(1), kv.group(2)
            if key == "primary_engine":
                result["engine"] = val
            elif key == "primary_model":
                result["model"] = val
    return result


def _parse_activity_log() -> list[dict]:
    """Parse agent_activity.md tables into a list of activity entries."""
    try:
        text = ACTIVITY_LOG.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return []

    entries = []
    current_year = datetime.now().year

    # Match markdown table rows: | col1 | col2 | ... |
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|--") or line.startswith("| 시각") or line.startswith("| 완료"):
            continue

        cols = [c.strip() for c in line.split("|")]
        cols = [c for c in cols if c]  # remove empty from leading/trailing |
        if len(cols) < 4:
            continue

        time_str = cols[0]
        agent_name = cols[1]
        # Try to parse the time
        dt = _parse_time(time_str, current_year)

        entries.append({
            "time": dt,
            "agent_name": agent_name,
            "task": cols[3] if len(cols) > 3 else "",
        })

    return entries


def _parse_time(time_str: str, year: int) -> datetime | None:
    """Best-effort parse of various time formats from activity log."""
    time_str = time_str.strip()

    # Full date: 2026-02-24
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', time_str)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None

    # Short date: 02-24
    m = re.match(r'^(\d{2})-(\d{2})$', time_str)
    if m:
        try:
            return datetime(year, int(m.group(1)), int(m.group(2)))
        except ValueError:
            return None

    # Time only: 03:30, 21:45
    m = re.match(r'^(\d{1,2}):(\d{2})$', time_str)
    if m:
        try:
            now = datetime.now()
            return now.replace(hour=int(m.group(1)), minute=int(m.group(2)), second=0, microsecond=0)
        except ValueError:
            return None

    return None


def _fuzzy_match(agent_name_from_log: str, spec_name: str, spec_id: str) -> bool:
    """Fuzzy match activity log agent name to spec name/id."""
    log_lower = agent_name_from_log.lower()
    name_lower = spec_name.lower()
    id_lower = spec_id.lower()

    # Direct name match
    if name_lower in log_lower:
        return True
    # ID match (e.g. "eng-foreman" in log)
    if id_lower in log_lower:
        return True
    # Partial: "CC팀" matches Engineering Division agents loosely
    # "Hands-4" → Foreman, "Hands-1" → Engineer (legacy naming)
    if "hands-4" in log_lower and name_lower == "foreman":
        return True
    if "hands-1" in log_lower and name_lower == "engineer":
        return True
    if "hands-3" in log_lower and name_lower == "debugger":
        return True
    # Brain → not an agent in specs, skip
    return False


def _compute_freshness(last_seen: datetime | None) -> str:
    """Compute freshness category from last_seen timestamp."""
    if last_seen is None:
        return "never"
    delta = datetime.now() - last_seen
    hours = delta.total_seconds() / 3600
    if hours <= FRESH_HOURS:
        return "fresh"
    elif hours <= AGING_HOURS:
        return "aging"
    else:
        return "stale"


def parse_agents() -> dict:
    """Return agent grid data grouped by department with freshness info."""
    # 1. Load all agent specs
    specs = []
    for md_file in sorted(AGENTS_DIR.glob("*.md")):
        if md_file.name.startswith("_") or md_file.name.endswith("_progress.md"):
            continue
        fm = _parse_frontmatter(md_file)
        if fm and "id" in fm:
            specs.append(fm)

    # 2. Parse activity log
    activities = _parse_activity_log()

    # 3. Match: for each spec, find latest activity
    agent_results = []
    for spec in specs:
        last_seen = None
        last_task = ""
        for act in activities:
            if _fuzzy_match(act["agent_name"], spec.get("name", ""), spec.get("id", "")):
                if act["time"] is not None:
                    if last_seen is None or act["time"] > last_seen:
                        last_seen = act["time"]
                        last_task = act["task"]

        freshness = _compute_freshness(last_seen)
        agent_results.append({
            "id": spec.get("id", ""),
            "name": spec.get("name", ""),
            "department": spec.get("department", "Unknown"),
            "tier": spec.get("tier", "T3"),
            "engine": spec.get("engine", ""),
            "model": spec.get("model", ""),
            "last_seen": last_seen.isoformat(timespec="seconds") if last_seen else None,
            "freshness": freshness,
            "last_task": last_task,
        })

    # 4. Build summary
    summary = {"total": len(agent_results), "fresh": 0, "aging": 0, "stale": 0, "never": 0}
    for a in agent_results:
        summary[a["freshness"]] += 1

    # 5. Group by department
    departments: dict[str, list] = {}
    for a in agent_results:
        dept = a["department"]
        departments.setdefault(dept, []).append(a)

    return {
        "agents": {
            "summary": summary,
            "departments": departments,
        }
    }


if __name__ == "__main__":
    import json as _json
    result = parse_agents()
    print(_json.dumps(result["agents"]["summary"], indent=2, ensure_ascii=False))
