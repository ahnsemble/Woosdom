"""
parsers/system.py — System status parser for Monitor v2 P1 (system-status panel).

Collects:
  - Engine stats from .cost_stats.json (task_bridge dir)
  - Brain callback / dangerous_blocked counts
  - task_bridge process alive status
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

from parsers import get_vault_root

COST_STATS_PATH = get_vault_root() / "02_Projects" / "task_bridge" / ".cost_stats.json"

BRAIN_DEFAULTS = {
    "status": "online",
    "consecutive_failures": 0,
    "failure_threshold": 3,
    "daily_callbacks": 0,
    "daily_callback_limit": 30,
    "sub_brain": "standby",
}

ENGINE_DEFAULTS = {
    "tasks": 0,
    "total_turns_est": 0,
    "total_seconds": 0,
}


def _read_cost_stats() -> dict:
    """Read .cost_stats.json, return empty dict on any failure."""
    try:
        with open(COST_STATS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def _check_task_bridge() -> dict:
    """Check if task_bridge process is alive via pgrep."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "task_bridge"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            pid = int(result.stdout.strip().splitlines()[0])
            return {"alive": True, "pid": pid}
    except (subprocess.TimeoutExpired, ValueError, OSError):
        pass
    return {"alive": False, "pid": None}


def _engine_entry(raw: dict, key: str) -> dict:
    """Build a single engine entry from cost_stats engines section."""
    eng = raw.get("engines", {}).get(key, {})
    return {
        "status": "online" if eng.get("tasks", 0) > 0 else "idle",
        "today_tasks": eng.get("tasks", ENGINE_DEFAULTS["tasks"]),
        "today_turns_est": eng.get("total_turns_est", ENGINE_DEFAULTS["total_turns_est"]),
        "today_seconds": eng.get("total_seconds", ENGINE_DEFAULTS["total_seconds"]),
    }


def parse_system() -> dict:
    """Return system status dict for the system-status panel."""
    raw = _read_cost_stats()

    brain_callbacks = raw.get("brain_callbacks", 0)
    dangerous_blocked = raw.get("dangerous_blocked", 0)

    brain = dict(BRAIN_DEFAULTS)
    brain["daily_callbacks"] = brain_callbacks
    # consecutive_failures not in cost_stats → stays 0 (default)

    engines = {
        "claude_code": _engine_entry(raw, "claude_code"),
        "codex": _engine_entry(raw, "codex"),
        "antigravity": _engine_entry(raw, "antigravity"),
    }

    task_bridge = _check_task_bridge()

    return {
        "system": {
            "brain": brain,
            "engines": engines,
            "task_bridge": task_bridge,
            "last_updated": datetime.now().isoformat(timespec="seconds"),
        }
    }


if __name__ == "__main__":
    import pprint
    pprint.pprint(parse_system())
