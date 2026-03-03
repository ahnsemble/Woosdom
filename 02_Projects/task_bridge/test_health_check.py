"""health_check() 단위 테스트."""
from unittest.mock import patch, MagicMock

from task_bridge import health_check


@patch("task_bridge.get_redis")
def test_health_check_return_type(mock_get_redis):
    """health_check() 반환값이 dict인지 검증."""
    mock_get_redis.return_value = MagicMock()
    result = health_check()
    assert isinstance(result, dict)


@patch("task_bridge.get_redis")
def test_health_check_required_keys(mock_get_redis):
    """반환 dict에 bridge_version, pid, uptime_seconds, redis_available 키 존재 검증."""
    mock_get_redis.return_value = MagicMock()
    result = health_check()
    required_keys = {"bridge_version", "pid", "uptime_seconds", "redis_available"}
    assert required_keys.issubset(result.keys())
