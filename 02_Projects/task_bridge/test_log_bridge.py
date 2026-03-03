"""log_bridge() 레벨별 출력 포맷 검증 테스트."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from task_bridge import log_bridge


def test_log_bridge_info_format():
    line = log_bridge("테스트 메시지", level="INFO")
    assert "[bridge:INFO]" in line
    assert "테스트 메시지" in line


def test_log_bridge_warn_format():
    line = log_bridge("경고 메시지", level="WARN")
    assert "[bridge:WARN]" in line
    assert "경고 메시지" in line


def test_log_bridge_error_format():
    line = log_bridge("에러 메시지", level="ERROR")
    assert "[bridge:ERROR]" in line
    assert "에러 메시지" in line
