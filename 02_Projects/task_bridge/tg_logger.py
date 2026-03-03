#!/usr/bin/env python3
"""
tg_logger.py — TG 대화 자동 로깅 스크립트
DB: /Users/woosung/Desktop/Dev/Woosdom_Brain/data/bot.db
출력: /Users/woosung/Desktop/Dev/Woosdom_Brain/00_System/Memory/tg_history/YYYY-MM-DD.md

동작:
1. bot.db messages 테이블을 30초마다 폴링
2. 새 메시지를 tg_history/YYYY-MM-DD.md에 append
3. 5분 침묵 시 conversation_memory.md에 세션 요약 1줄 추가
4. 에러 시 조용히 로깅 (크래시 금지)
"""

import sqlite3
import logging
import time
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── 경로 설정 ──────────────────────────────────────────────────────────────
VAULT_ROOT = Path("/Users/woosung/Desktop/Dev/Woosdom_Brain")
DB_PATH = VAULT_ROOT / "data" / "bot.db"
TG_HISTORY_DIR = VAULT_ROOT / "00_System" / "Memory" / "tg_history"
MEMORY_FILE = VAULT_ROOT / "00_System" / "Memory" / "conversation_memory.md"
STATE_FILE = VAULT_ROOT / "02_Projects" / "task_bridge" / ".tg_logger_state"

POLL_INTERVAL = 30          # 초
SILENCE_THRESHOLD = 5 * 60  # 5분 (초)
RESPONSE_MAX_LEN = 200      # 봇 응답 truncate 길이

# ── 로거 설정 ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [tg_logger] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("tg_logger")


def get_last_processed_id() -> int:
    """마지막으로 처리한 message_id를 state 파일에서 읽기"""
    try:
        if STATE_FILE.exists():
            return int(STATE_FILE.read_text().strip())
    except Exception:
        pass
    return 0


def save_last_processed_id(message_id: int) -> None:
    try:
        STATE_FILE.write_text(str(message_id))
    except Exception as e:
        log.warning(f"State 저장 실패: {e}")


def fetch_new_messages(last_id: int) -> list[dict]:
    """DB에서 last_id 이후 신규 메시지 조회"""
    try:
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, timeout=5)
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT message_id, timestamp, prompt, response "
            "FROM messages WHERE message_id > ? ORDER BY message_id ASC",
            (last_id,),
        )
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        log.warning(f"DB 조회 실패: {e}")
        return []


def parse_ts(ts_str: str) -> datetime:
    """ISO 8601 문자열 → datetime (KST 기준 변환)"""
    try:
        # SQLite에 UTC로 저장됨
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        # KST (UTC+9) 변환
        kst = timezone(timedelta(hours=9))
        return dt.astimezone(kst)
    except Exception:
        return datetime.now(timezone(timedelta(hours=9)))


def get_tg_history_path(dt: datetime) -> Path:
    """날짜별 tg_history 파일 경로"""
    return TG_HISTORY_DIR / f"{dt.strftime('%Y-%m-%d')}.md"


def ensure_tg_history_header(path: Path, date_str: str) -> None:
    """파일이 없으면 헤더 생성"""
    if not path.exists():
        TG_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# TG Log — {date_str}\n\n", encoding="utf-8")
        log.info(f"새 tg_history 파일 생성: {path.name}")


def truncate(text: str, max_len: int = RESPONSE_MAX_LEN) -> str:
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len] + "…"


def append_to_tg_history(msg: dict) -> None:
    """메시지 1건을 tg_history에 append"""
    dt = parse_ts(msg["timestamp"])
    date_str = dt.strftime("%Y-%m-%d")
    time_str = dt.strftime("%H:%M")
    path = get_tg_history_path(dt)

    ensure_tg_history_header(path, date_str)

    prompt = (msg.get("prompt") or "").strip()
    response = truncate(msg.get("response") or "")

    entry = f"\n## {time_str} — 사용자\n> {prompt}\n"
    if response:
        entry += f"\n## {time_str} — Brain\n> {response}\n"

    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(entry)
        log.info(f"[{date_str} {time_str}] 메시지 기록 완료 (id={msg['message_id']})")
    except Exception as e:
        log.warning(f"tg_history append 실패: {e}")


def update_conversation_memory(summary_line: str) -> None:
    """conversation_memory.md에 세션 요약 1줄 append (기존 내용 삭제 금지)"""
    try:
        if not MEMORY_FILE.exists():
            log.warning(f"conversation_memory.md 없음: {MEMORY_FILE}")
            return
        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n{summary_line}\n")
        log.info(f"conversation_memory.md 업데이트: {summary_line}")
    except Exception as e:
        log.warning(f"conversation_memory.md 업데이트 실패: {e}")


def make_session_summary(msgs: list[dict]) -> str:
    """세션 메시지 목록 → 요약 1줄"""
    if not msgs:
        return ""
    dt = parse_ts(msgs[-1]["timestamp"])
    date_str = dt.strftime("%Y-%m-%d")
    count = len(msgs)
    # 마지막 사용자 메시지 발췌
    last_prompt = truncate(msgs[-1].get("prompt") or "", 60)
    return f"### {date_str} #auto — TG Bot ({count}턴): {last_prompt}"


class TgLogger:
    def __init__(self):
        self.last_id = get_last_processed_id()
        self.session_msgs: list[dict] = []
        self.last_msg_time: float = 0.0
        self.silence_notified: bool = False

    def run(self) -> None:
        log.info(f"tg_logger 시작 (last_id={self.last_id}, poll={POLL_INTERVAL}s)")
        while True:
            try:
                self._poll()
                self._check_silence()
            except Exception as e:
                log.error(f"예상치 못한 에러: {e}", exc_info=True)
            time.sleep(POLL_INTERVAL)

    def _poll(self) -> None:
        new_msgs = fetch_new_messages(self.last_id)
        if not new_msgs:
            return

        for msg in new_msgs:
            append_to_tg_history(msg)
            self.session_msgs.append(msg)
            self.last_id = msg["message_id"]
            self.last_msg_time = time.time()
            self.silence_notified = False

        save_last_processed_id(self.last_id)

    def _check_silence(self) -> None:
        """5분 침묵 감지 → conversation_memory.md 업데이트"""
        if not self.session_msgs:
            return
        if self.silence_notified:
            return
        elapsed = time.time() - self.last_msg_time
        if elapsed >= SILENCE_THRESHOLD:
            summary = make_session_summary(self.session_msgs)
            if summary:
                update_conversation_memory(summary)
            self.session_msgs = []
            self.silence_notified = True
            log.info("세션 종료 감지 → memory 업데이트 완료")


if __name__ == "__main__":
    TgLogger().run()
