"""get_version() 반환값 검증 테스트."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from task_bridge import get_version


def test_get_version_returns_v47():
    assert get_version() == "v4.7"
