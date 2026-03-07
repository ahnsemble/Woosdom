"""
parsers/activity.py — Activity feed parser for Monitor v2 P3 (activity-feed panel).

Parses bridge.log (primary) with fallback to /tmp/woosdom-taskbridge.log for
recent engine execution events. bridge.log contains timestamped entries from
log_bridge() in task_bridge.py.
"""

import re
from datetime import datetime
from pathlib import Path

from parsers import get_vault_root

# Primary: bridge.log (timestamped), Fallback: legacy taskbridge log
BRIDGE_LOG_PATH = get_vault_root() / "00_System" / "Logs" / "bridge.log"
LEGACY_LOG_PATH = Path("/tmp/woosdom-taskbridge.log")
MAX_EVENTS = 50
TAIL_LINES = 100

# bridge.log format: [2026-03-03 23:48:00] [bridge:INFO] message
BRIDGE_LOG_RE = re.compile(
    r'^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[bridge:(\w+)\] (.+)$'
)


def _read_log_tail() -> list[str]:
    """Read last TAIL_LINES lines from bridge.log (primary) or legacy log (fallback)."""
    for path in (BRIDGE_LOG_PATH, LEGACY_LOG_PATH):
        try:
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()
            if lines:
                return lines[-TAIL_LINES:]
        except (FileNotFoundError, OSError):
            continue
    return []


def _classify_engine(tag: str) -> str:
    """Map log tag to engine short name."""
    tag = tag.lower()
    if tag == "cc":
        return "CC"
    elif tag == "bridge":
        return "Bridge"
    elif tag == "brain_cb":
        return "Brain"
    elif tag == "codex":
        return "Codex"
    elif tag == "ag" or tag == "antigravity":
        return "AG"
    return tag.upper()


def _classify_status_from_message(message: str) -> str:
    """Determine event status from message content."""
    if "완료" in message or "DONE" in message or "PASS" in message:
        return "success"
    elif "위험 명령" in message or "BLOCKED" in message or "차단" in message:
        return "warning"
    elif "실패" in message or "FAIL" in message or "Error" in message or "에러" in message:
        return "error"
    return "info"


def _extract_duration(message: str) -> int | None:
    """Extract duration in seconds from message (e.g. '154초', '45s')."""
    dur_m = re.search(r'(\d+)\s*초', message)
    if dur_m:
        return int(dur_m.group(1))
    dur_m = re.search(r'(\d+)s\b', message)
    if dur_m:
        return int(dur_m.group(1))
    return None


def _parse_line(line: str) -> dict | None:
    """Parse a single log line into an event dict. Returns None if not parseable.

    Supports two formats:
      1. bridge.log: [2026-03-03 23:48:00] [bridge:INFO] message
      2. legacy:     [TAG] message text
    """
    line = line.strip()
    if not line:
        return None

    # ── 1. bridge.log format (timestamped) ──
    m = BRIDGE_LOG_RE.match(line)
    if m:
        timestamp_str = m.group(1)
        level = m.group(2).upper()
        message = m.group(3)

        # Format time as MM-DD HH:MM
        try:
            dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            time_str = dt.strftime("%m-%d %H:%M")
        except ValueError:
            time_str = ""

        # Map level to status
        if level == "WARN":
            status = "warning"
        elif level == "ERROR":
            status = "error"
        else:
            status = _classify_status_from_message(message)

        duration = _extract_duration(message)

        # Clean up message
        clean_msg = message
        clean_msg = re.sub(r'\s*—\s*exit=\d+,\s*\d+초\s*$', '', clean_msg)
        clean_msg = re.sub(r'\*\*(.+?)\*\*', r'\1', clean_msg)

        return {
            "time": time_str,
            "engine": "Bridge",
            "status": status,
            "message": clean_msg.strip(),
            "detail": "",
            "duration": duration,
        }

    # ── 2. Legacy format: [TAG] message text ──
    m = re.match(r'^\[(\w+)\]\s+(.+)$', line)
    if not m:
        return None

    tag = m.group(1)
    message = m.group(2)
    engine = _classify_engine(tag)

    status = _classify_status_from_message(message)

    # Extract exit code
    exit_m = re.search(r'exit=(\d+)', message)
    if exit_m:
        code = int(exit_m.group(1))
        status = "success" if code == 0 else "error"

    duration = _extract_duration(message)

    # Clean up message
    clean_msg = message
    clean_msg = re.sub(r'\s*—\s*exit=\d+,\s*\d+초\s*$', '', clean_msg)
    clean_msg = re.sub(r'\*\*(.+?)\*\*', r'\1', clean_msg)

    return {
        "time": "",  # Legacy format has no timestamp
        "engine": engine,
        "status": status,
        "message": clean_msg.strip(),
        "detail": "",
        "duration": duration,
    }


def parse_activity() -> dict:
    """Return activity feed data from bridge log."""
    lines = _read_log_tail()

    events = []
    for line in lines:
        evt = _parse_line(line)
        if evt is not None:
            events.append(evt)

    # Keep only the most recent MAX_EVENTS, newest first
    events = events[-MAX_EVENTS:]
    events.reverse()

    # Try to extract time context
    now = datetime.now()
    last_event_time = now.isoformat(timespec="seconds") if events else None

    return {
        "activity": {
            "events": events,
            "total_events": len(events),
            "last_event_time": last_event_time,
        }
    }


if __name__ == "__main__":
    import json as _json
    r = parse_activity()
    print(f"events: {len(r['activity']['events'])}")
    if r["activity"]["events"]:
        print(_json.dumps(r["activity"]["events"][-3:], indent=2, ensure_ascii=False))
