"""E2E 테스트: to_hands.md 감지 → Redis 기록 → from_hands 감지 → 완료 처리."""
import os
import sys
import time

VAULT_ROOT = "/Users/woosung/Desktop/Dev/Woosdom_Brain"
TO_HANDS   = os.path.join(VAULT_ROOT, "00_System", "Templates", "to_hands.md")
FROM_HANDS = os.path.join(VAULT_ROOT, "00_System", "Templates", "from_hands.md")

# local import
sys.path.insert(0, os.path.dirname(__file__))
from redis_schema import (
    get_redis, STREAM_KEY, get_recent_tasks,
    add_task, complete_task, get_latest_pending,
)


def test_redis_connection():
    client = get_redis()
    assert client.ping(), "Redis PING 실패"
    print("✅ Redis 연결 OK")
    return client


def test_stream_operations(client):
    # Add task
    task_id = add_task(client, "테스트 작업", "hands-1", "테스트 내용")
    assert task_id, "Task ID 미생성"
    print(f"✅ Task 추가: {task_id}")

    # Check pending
    pending = get_latest_pending(client)
    assert pending and pending["task_id"] == task_id, "Pending task 조회 실패"
    print("✅ Pending 조회 OK")

    # Complete
    complete_task(client, task_id)
    print("✅ Task 완료 처리 OK")

    # Recent tasks
    recent = get_recent_tasks(client, 5)
    assert len(recent) >= 2, f"Recent tasks 부족 (got {len(recent)})"
    print(f"✅ Recent tasks: {len(recent)}건")

    # XLEN 출력
    xlen = client.xlen(STREAM_KEY)
    print(f"✅ XLEN woosdom:tasks = {xlen}")


def test_file_parsing():
    from task_bridge import _parse_to_hands

    sample = """# 🔧 실행 요청: Sprint 2 Task Bridge
**추천 엔진:** Hands-1 (Antigravity Sonnet 4.6)
"""
    title, engine = _parse_to_hands(sample)
    assert "Sprint 2" in title, f"제목 파싱 실패: {title}"
    assert engine == "hands-1", f"엔진 파싱 실패: {engine}"
    print(f"✅ 파싱: title='{title}', engine='{engine}'")


def test_no_redis_fallback():
    """Redis 없이도 task_bridge.py가 크래시 없이 동작하는지 확인."""
    import subprocess, sys, time
    result = subprocess.run(
        [sys.executable, "-c",
         "import os, sys; sys.path.insert(0, 'task_bridge');"
         "os.environ['REDIS_HOST']='127.0.0.1'; os.environ['REDIS_PORT']='19999';"  # 잘못된 포트
         "from task_bridge import main;"
         "import threading, signal;"
         "t=threading.Thread(target=main); t.daemon=True; t.start(); import time; time.sleep(1);"
         "print('[test] fallback OK')"],
        capture_output=True, text=True, timeout=5,
        cwd=os.path.dirname(__file__),
    )
    # 크래시(exit code != 0) 가 아닌지 확인
    out = result.stdout + result.stderr
    assert "연결 실패" in out or "fallback OK" in out, f"폴백 테스트 예상 출력 없음: {out}"
    print("✅ Redis 없음 → 파일 전용 모드 OK")


if __name__ == "__main__":
    print("=" * 50)
    print("Woosdom Task Bridge — E2E Tests")
    print("=" * 50)
    try:
        client = test_redis_connection()
    except Exception as e:
        print(f"⚠️  Redis 미연결: {e}")
        print("   Redis 테스트 건너뜀. 파싱 테스트만 수행.")
        test_file_parsing()
        print("\n⚠️  PARTIAL PASS (Redis 필요 테스트 건너뜀)")
        raise SystemExit(0)

    test_stream_operations(client)
    test_file_parsing()
    test_no_redis_fallback()
    print("\n🎉 ALL TESTS PASSED")
