"""
parsers/cost.py — Cost parser for Monitor v2 P6 (cost panel).

Reads task_bridge/.cost_stats.json for daily engine cost stats.
"""

import json
from datetime import date
from pathlib import Path

from parsers import get_vault_root

VAULT_ROOT = get_vault_root()
COST_STATS = VAULT_ROOT / "02_Projects" / "task_bridge" / ".cost_stats.json"

MONTHLY_CAPS = {
    "claude_code": 100,
    "codex": 200,
    "antigravity": 0,
}
MONTHLY_TOTAL_CAP = 300

ENGINE_DISPLAY = {
    "claude_code": "Claude Code",
    "codex": "Codex",
    "antigravity": "Antigravity",
}


def parse_cost() -> dict:
    """Return cost data from .cost_stats.json."""
    try:
        raw = json.loads(COST_STATS.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return {"cost": _empty()}

    stat_date = raw.get("date", date.today().isoformat())
    engines_raw = raw.get("engines", {})

    engines = []
    for key in ["claude_code", "codex", "antigravity"]:
        eng = engines_raw.get(key, {})
        engines.append({
            "name": ENGINE_DISPLAY.get(key, key),
            "tasks": eng.get("tasks", 0),
            "turns_est": eng.get("total_turns_est", 0),
            "seconds": eng.get("total_seconds", 0),
            "monthly_cap": MONTHLY_CAPS.get(key, 0),
        })

    return {
        "cost": {
            "date": stat_date,
            "engines": engines,
            "brain_callbacks": raw.get("brain_callbacks", 0),
            "dangerous_blocked": raw.get("dangerous_blocked", 0),
            "monthly_total_cap": MONTHLY_TOTAL_CAP,
        }
    }


def _empty() -> dict:
    return {
        "date": date.today().isoformat(),
        "engines": [
            {"name": "Claude Code", "tasks": 0, "turns_est": 0, "seconds": 0, "monthly_cap": 100},
            {"name": "Codex", "tasks": 0, "turns_est": 0, "seconds": 0, "monthly_cap": 200},
            {"name": "Antigravity", "tasks": 0, "turns_est": 0, "seconds": 0, "monthly_cap": 0},
        ],
        "brain_callbacks": 0,
        "dangerous_blocked": 0,
        "monthly_total_cap": 300,
    }


if __name__ == "__main__":
    import json as _json
    print(_json.dumps(parse_cost(), indent=2, ensure_ascii=False))
