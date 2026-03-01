"""Redis Stream schema + CRUD for Woosdom Task Bridge."""
import os
import uuid
import hashlib
from datetime import datetime, timezone
from redis import Redis

STREAM_KEY = "woosdom:tasks"


def get_redis() -> Redis:
    return Redis(
        host=os.getenv("REDIS_HOST", "127.0.0.1"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=0,
        decode_responses=True,
    )


def add_task(client: Redis, title: str, engine: str, content: str) -> str:
    """to_hands.md 감지 시 호출. Redis Stream에 task 추가."""
    task_id = str(uuid.uuid4())[:8]
    entry = {
        "task_id":      task_id,
        "title":        title,
        "engine":       engine,
        "status":       "pending",
        "content_hash": hashlib.md5(content.encode()).hexdigest()[:12],
        "created_at":   datetime.now(timezone.utc).isoformat(),
        "completed_at": "",
    }
    client.xadd(STREAM_KEY, entry)
    return task_id


def complete_task(client: Redis, task_id: str) -> bool:
    """from_hands.md 감지 시 호출. Redis Streams는 entry 수정 불가 → 새 entry로 상태 변경 기록."""
    entry = {
        "task_id":      task_id,
        "status":       "done",
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    client.xadd(STREAM_KEY, entry)
    return True


def get_recent_tasks(client: Redis, count: int = 20) -> list:
    """최근 task 목록 조회 (대시보드용)."""
    entries = client.xrevrange(STREAM_KEY, count=count)
    return [{"id": eid, **data} for eid, data in entries]


def get_latest_pending(client: Redis) -> dict | None:
    """가장 최근 pending task 조회."""
    entries = client.xrevrange(STREAM_KEY, count=50)
    for eid, data in entries:
        if data.get("status") == "pending":
            return {"id": eid, **data}
    return None
