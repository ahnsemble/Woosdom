"""
tests/test_parsers.py — Unit tests for Monitor v2 parsers.

Run: python3 tests/test_parsers.py
Expected: All parser tests PASS
"""

import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from parsers.system import parse_system
from parsers.agents import parse_agents
from parsers.activity import parse_activity


def test_parse_system_basic():
    """T5-1: system parser key structure + failure_threshold==3."""
    result = parse_system()
    assert "system" in result, "Missing top-level 'system' key"
    sys_data = result["system"]

    # Required keys
    for key in ("brain", "engines", "task_bridge", "last_updated"):
        assert key in sys_data, f"Missing system.{key}"

    # Brain structure
    brain = sys_data["brain"]
    for key in ("status", "consecutive_failures", "failure_threshold",
                "daily_callbacks", "daily_callback_limit", "sub_brain"):
        assert key in brain, f"Missing system.brain.{key}"

    assert brain["failure_threshold"] == 3, \
        f"failure_threshold should be 3, got {brain['failure_threshold']}"

    # Engines structure
    for eng in ("claude_code", "codex", "antigravity"):
        assert eng in sys_data["engines"], f"Missing engine: {eng}"

    print("  [PASS] test_parse_system_basic")


def test_parse_agents_summary():
    """T5-2: total > 0, total == fresh+aging+stale+never."""
    result = parse_agents()
    assert "agents" in result, "Missing top-level 'agents' key"
    summary = result["agents"]["summary"]

    assert summary["total"] > 0, "total should be > 0"

    computed_total = summary["fresh"] + summary["aging"] + summary["stale"] + summary["never"]
    assert summary["total"] == computed_total, \
        f"total ({summary['total']}) != fresh+aging+stale+never ({computed_total})"

    print("  [PASS] test_parse_agents_summary")


def test_parse_agents_departments():
    """T5-3: Engineering Division exists in departments."""
    result = parse_agents()
    departments = result["agents"]["departments"]

    assert "Engineering Division" in departments, \
        f"Engineering Division not found. Departments: {list(departments.keys())}"

    eng_agents = departments["Engineering Division"]
    assert len(eng_agents) > 0, "Engineering Division should have agents"

    # Verify agent entry structure
    agent = eng_agents[0]
    for key in ("id", "name", "department", "tier", "freshness"):
        assert key in agent, f"Missing agent field: {key}"

    print("  [PASS] test_parse_agents_departments")


def test_parse_activity_basic():
    """T5-4: events is a list."""
    result = parse_activity()
    assert "activity" in result, "Missing top-level 'activity' key"
    activity = result["activity"]

    assert isinstance(activity["events"], list), \
        f"events should be list, got {type(activity['events'])}"

    assert "total_events" in activity, "Missing total_events"
    assert activity["total_events"] == len(activity["events"]), \
        "total_events should match len(events)"

    print("  [PASS] test_parse_activity_basic")


if __name__ == "__main__":
    tests = [
        test_parse_system_basic,
        test_parse_agents_summary,
        test_parse_agents_departments,
        test_parse_activity_basic,
    ]

    passed = 0
    failed = 0

    print("Running parser tests...\n")
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  [FAIL] {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  [FAIL] {test.__name__}: {type(e).__name__}: {e}")
            failed += 1

    print()
    if failed == 0:
        print(f"All parser tests PASS ({passed}/{passed})")
    else:
        print(f"FAILED: {failed}/{passed + failed} tests failed")
        sys.exit(1)
