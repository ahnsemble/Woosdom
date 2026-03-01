# Woosdom Task Bridge

`to_hands.md` / `from_hands.md` 파일 변경 감지 → Redis Stream 기록 + Telegram 알림.

기존 파일 기반 워크플로우는 100% 보존. Redis는 **관찰·알림·이력 레이어**로만 동작.

---

## Quick Start

```bash
cd /Users/woosung/Desktop/Dev/Woosdom_Brain/02_Projects/task_bridge

# 1. 의존성 설치
pip3 install -r requirements.txt

# 2. 테스트 실행
python3 test_bridge.py

# 3. 수동 실행
python3 task_bridge.py
```

## launchd 등록 (Mac 자동 시작)

```bash
# TG 토큰을 plist에 먼저 설정한 뒤:
cp com.woosdom.taskbridge.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.woosdom.taskbridge.plist

# 로그 확인
tail -f /tmp/woosdom-taskbridge.log
```

## 환경변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `REDIS_HOST` | `127.0.0.1` | Redis 호스트 |
| `REDIS_PORT` | `6379` | Redis 포트 |
| `TG_BOT_TOKEN` | (비어있음) | Telegram 봇 토큰 (선택) |
| `TG_CHAT_ID` | (비어있음) | Telegram 채팅 ID (선택) |

> Telegram 미설정 시 콘솔 출력만 — 정상 동작.

## Redis Schema

```
STREAM  woosdom:tasks
  fields: task_id, title, engine, status (pending|done),
          content_hash, created_at, completed_at
```

## 동작 흐름

```
to_hands.md 변경
  → parse_to_hands() → xadd(pending)
  → Telegram "🔧 새 작업" 알림

from_hands.md 변경
  → xadd(done for last_task_id)
  → Telegram "✅ 작업 완료" 알림
```

## 의존성

- Python 3.10+
- Redis 6+ (Docker litellm-redis 컨테이너 공유 가능)
- `redis>=5.0` Python 패키지
