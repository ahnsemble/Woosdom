"""get_status_summary() 단위 테스트."""

from unittest.mock import patch
from task_bridge import get_status_summary


def test_return_type():
    """get_status_summary() 반환값이 dict인지 검증."""
    with patch("task_bridge.get_redis") as mock_redis:
        mock_redis.return_value.ping.side_effect = Exception("no redis")
        with patch("task_bridge.get_daily_brain_stats", return_value={"calls_made": 0}):
            result = get_status_summary()
    assert isinstance(result, dict)


def test_required_keys():
    """필수 키 6개 존재 검증."""
    required = {
        "bridge_version",
        "pid",
        "uptime_seconds",
        "redis_available",
        "daily_brain_calls",
        "watched_files",
    }
    with patch("task_bridge.get_redis") as mock_redis:
        mock_redis.return_value.ping.side_effect = Exception("no redis")
        with patch("task_bridge.get_daily_brain_stats", return_value={"calls_made": 5}):
            result = get_status_summary()
    assert required.issubset(result.keys()), f"Missing keys: {required - result.keys()}"
