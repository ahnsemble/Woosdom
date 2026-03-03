"""get_engine_display() 반환값 검증 테스트."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from task_bridge import get_engine_display


def test_known_key_returns_display_name():
    assert get_engine_display("claude_code") == "Claude Code"
    assert get_engine_display("codex") == "Codex"
    assert get_engine_display("antigravity") == "Antigravity"


def test_unknown_key_returns_raw_key():
    assert get_engine_display("unknown_engine") == "unknown_engine"
