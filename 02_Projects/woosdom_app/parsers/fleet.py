"""
parsers/fleet.py — Fleet Health, Engine Badges, Event Feed, System Health parser.

Provides:
  - fleet_health: success rate from watcher.log + bridge.log (last 20 actions)
  - engine_badges: IDLE/WORKING/ERROR from to_*.md status fields
  - event_feed: last 10 bridge.log lines for real-time polling
  - system_health: watcher heartbeat status from heartbeat.json
"""

import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

from parsers import get_vault_root

VAULT = get_vault_root()
WATCHER_LOG = VAULT / "00_System" / "Logs" / "watcher.log"
BRIDGE_LOG = VAULT / "00_System" / "Logs" / "bridge.log"
HEARTBEAT_FILE = VAULT / "00_System" / "Logs" / "heartbeat.json"
TEMPLATES_DIR = VAULT / "00_System" / "Templates"

# Heartbeat staleness thresholds (seconds)
HEARTBEAT_ALIVE_THRESHOLD = 120   # < 2min = alive
HEARTBEAT_STALE_THRESHOLD = 300   # < 5min = stale, >= 5min = dead

ENGINE_FILES = {
    "claude_code": TEMPLATES_DIR / "to_claude_code.md",
    "codex": TEMPLATES_DIR / "to_codex.md",
    "antigravity": TEMPLATES_DIR / "to_antigravity.md",
}

# watcher.log: [2026-03-05 06:03:53] DONE claude_code — task (exit: 1)
WATCHER_DONE_RE = re.compile(
    r'^\[[\d\- :]+\]\s+DONE\s+\w+\s+.+?\(exit:\s*(\d+)\)'
)

# bridge.log: [2026-03-04 19:24:33] [bridge:INFO] CC 완료: ..., 163초, exit=성공
BRIDGE_DONE_RE = re.compile(
    r'^\[[\d\- :]+\]\s+\[bridge:\w+\]\s+.*(완료|DONE|실패|FAIL|ERROR)'
)

# bridge.log timestamp + level + message
BRIDGE_LINE_RE = re.compile(
    r'^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]\s+\[bridge:(\w+)\]\s+(.+)$'
)

# watcher.log: [timestamp] TYPE engine — message
WATCHER_LINE_RE = re.compile(
    r'^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]\s+(START|DONE|SKIP|ERROR)\s+(\w+)\s*[—\-]?\s*(.*)'
)


def _read_tail(path: Path, n: int = 200) -> list[str]:
    """Read last n lines from a file."""
    try:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        return lines[-n:] if len(lines) > n else lines
    except (FileNotFoundError, OSError):
        return []


def _count_watcher_results(lines: list[str]) -> list[bool]:
    """Extract success/fail from DONE lines in watcher.log. True=success."""
    results = []
    for line in lines:
        m = WATCHER_DONE_RE.match(line)
        if m:
            results.append(int(m.group(1)) == 0)
    return results


def _count_bridge_results(lines: list[str]) -> list[bool]:
    """Extract success/fail from bridge.log completion lines. True=success."""
    results = []
    for line in lines:
        m = BRIDGE_DONE_RE.match(line)
        if m:
            keyword = m.group(1)
            if keyword in ("실패", "FAIL", "ERROR"):
                results.append(False)
            else:
                # Check for exit=성공 vs exit=실패
                if "exit=실패" in line or "exit=1" in line:
                    results.append(False)
                else:
                    results.append(True)
    return results


def parse_fleet_health() -> dict:
    """Calculate fleet health from last 20 action results."""
    watcher_lines = _read_tail(WATCHER_LOG)
    bridge_lines = _read_tail(BRIDGE_LOG)

    results = _count_watcher_results(watcher_lines) + _count_bridge_results(bridge_lines)
    # Take last 20
    results = results[-20:] if len(results) > 20 else results

    total = len(results)
    success = sum(1 for r in results if r)
    rate = round((success / total) * 100, 1) if total > 0 else 100.0

    return {
        "success_rate": rate,
        "total": total,
        "success": success,
        "fail": total - success,
    }


def _parse_frontmatter_status(path: Path) -> dict:
    """Parse YAML frontmatter from to_*.md, return status and title."""
    try:
        text = path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return {"status": "idle", "title": ""}

    # Extract frontmatter between --- markers
    fm_match = re.match(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
    if not fm_match:
        return {"status": "idle", "title": ""}

    fm = fm_match.group(1)
    status = "idle"
    title = ""

    for line in fm.splitlines():
        line = line.strip()
        if line.startswith("status:"):
            val = line.split(":", 1)[1].strip().strip('"').strip("'").lower()
            if val == "pending":
                status = "working"
            elif val in ("done", "completed"):
                status = "idle"
            elif val in ("error", "failed"):
                status = "error"
            else:
                status = "idle"
        elif line.startswith("title:"):
            title = line.split(":", 1)[1].strip().strip('"').strip("'")

    return {"status": status, "title": title}


def parse_engine_badges() -> dict:
    """Parse engine status from to_*.md files."""
    badges = {}
    for engine_key, path in ENGINE_FILES.items():
        badges[engine_key] = _parse_frontmatter_status(path)
    return badges


def parse_event_feed(max_lines: int = 10) -> list[dict]:
    """Parse last N lines of bridge.log for event feed display."""
    lines = _read_tail(BRIDGE_LOG, n=50)

    events = []
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Try bridge.log format first
        m = BRIDGE_LINE_RE.match(line)
        if m:
            timestamp = m.group(1)
            level = m.group(2).upper()
            message = m.group(3)

            # Determine event type/color
            if level == "ERROR":
                evt_type = "ERROR"
            elif "완료" in message or "DONE" in message:
                evt_type = "DONE"
            elif "시작" in message or "START" in message or "새 작업" in message:
                evt_type = "START"
            elif "SKIP" in message:
                evt_type = "SKIP"
            else:
                evt_type = "INFO"

            # Shorten timestamp to HH:MM:SS
            time_short = timestamp[11:] if len(timestamp) >= 19 else timestamp

            events.append({
                "time": time_short,
                "type": evt_type,
                "message": message[:120],
                "raw_level": level,
            })
            continue

        # Try watcher.log format
        wm = WATCHER_LINE_RE.match(line)
        if wm:
            timestamp = wm.group(1)
            evt_type = wm.group(2)
            engine = wm.group(3)
            msg = wm.group(4)

            time_short = timestamp[11:] if len(timestamp) >= 19 else timestamp
            events.append({
                "time": time_short,
                "type": evt_type,
                "message": f"[{engine}] {msg}"[:120],
                "raw_level": "INFO",
            })

    # Return last max_lines events
    return events[-max_lines:]


def parse_system_health() -> dict:
    """Parse heartbeat.json for watcher/system health status."""
    default = {
        "watcher_status": "dead",  # alive / stale / dead
        "watcher_pid": None,
        "last_beat": None,
        "last_beat_ago": None,  # human-readable "2m ago"
        "uptime_seconds": 0,
        "uptime_display": "—",
        "engines": {
            "claude_code": {"status": "idle", "last_task": None},
            "codex": {"status": "idle", "last_task": None},
            "antigravity": {"status": "idle", "last_task": None},
        },
        "pending_files": [],
        "errors_last_hour": 0,
    }

    try:
        raw = HEARTBEAT_FILE.read_text(encoding="utf-8")
        hb = json.loads(raw)
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return default

    # Parse last_beat and determine status
    last_beat_str = hb.get("last_beat", "")
    watcher_status = "dead"
    last_beat_ago = None

    if last_beat_str:
        try:
            # Parse ISO timestamp (strip timezone for simplicity)
            clean = last_beat_str.replace("+09:00", "+0900").replace("+00:00", "+0000")
            dt = datetime.strptime(clean[:19], "%Y-%m-%dT%H:%M:%S")
            now = datetime.now()
            diff = (now - dt).total_seconds()

            if diff < HEARTBEAT_ALIVE_THRESHOLD:
                watcher_status = "alive"
            elif diff < HEARTBEAT_STALE_THRESHOLD:
                watcher_status = "stale"
            else:
                watcher_status = "dead"

            # Human-readable ago
            if diff < 60:
                last_beat_ago = f"{int(diff)}s ago"
            elif diff < 3600:
                last_beat_ago = f"{int(diff // 60)}m ago"
            else:
                last_beat_ago = f"{int(diff // 3600)}h ago"
        except (ValueError, TypeError):
            pass

    # Uptime display
    uptime = hb.get("uptime_seconds", 0)
    if uptime < 60:
        uptime_display = f"{uptime}s"
    elif uptime < 3600:
        uptime_display = f"{uptime // 60}m {uptime % 60}s"
    else:
        h = uptime // 3600
        m = (uptime % 3600) // 60
        uptime_display = f"{h}h {m}m"

    return {
        "watcher_status": watcher_status,
        "watcher_pid": hb.get("watcher_pid"),
        "last_beat": last_beat_str,
        "last_beat_ago": last_beat_ago,
        "uptime_seconds": uptime,
        "uptime_display": uptime_display,
        "engines": hb.get("engines", default["engines"]),
        "pending_files": hb.get("pending_files", []),
        "errors_last_hour": hb.get("errors_last_hour", 0),
    }


def parse_fleet() -> dict:
    """Main entry point — returns all fleet data for the dashboard."""
    return {
        "fleet": {
            "health": parse_fleet_health(),
            "engines": parse_engine_badges(),
            "event_feed": parse_event_feed(),
            "system_health": parse_system_health(),
        }
    }


if __name__ == "__main__":
    import json
    result = parse_fleet()
    print(json.dumps(result, indent=2, ensure_ascii=False))
