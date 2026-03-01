"""Woosdom Task Bridge v4.3 — Auto-Brain Callback 통합.

v4.3 변경 (S-1):
  - brain_callback.run_brain_callback() — 엔진 완료 후 Brain 자동 호출
  - DONE → TG 요약 보고, CHAIN → to_[engine].md 기록 후 자동실행 루프에 위임
  - ESCALATE → TG 이유 포함 보고
  - 일일 30회 한도, 최대 체인 깊이 3, 반복 응답 감지(강제 ESCALATE) 포함

v4.2 변경:
  - to_claude_code.md → hands3_runner.run_claude_code() (기존 유지)
  - to_codex.md → codex_runner.run_codex() 자동 실행
  - to_antigravity.md → gemini_runner.run_gemini() 자동 실행
  - 모든 엔진 stdout 터미널 실시간 스트리밍
  - 결과를 from_[engine].md에 자동 기록

실행 방법: python task_bridge.py (터미널에서 직접 실행, launchd 아님)
"""
import os
import re
import time
import urllib.request
import json
import hashlib
from datetime import datetime
from redis_schema import get_redis, add_task, complete_task, get_latest_pending
from hands3_runner import run_claude_code
from codex_runner import run_codex
from gemini_runner import run_gemini
from brain_callback import run_brain_callback, _check_brain_daily_limit

VAULT_ROOT = "/Users/woosung/Desktop/Dev/Woosdom_Brain"
TEMPLATES_DIR = os.path.join(VAULT_ROOT, "00_System", "Templates")

# 엔진별 감시 대상 (to_ = 새 작업, from_ = 완료)
WATCH_FILES = {
    "to": {
        "antigravity": os.path.join(TEMPLATES_DIR, "to_antigravity.md"),
        "codex":       os.path.join(TEMPLATES_DIR, "to_codex.md"),
        "claude_code": os.path.join(TEMPLATES_DIR, "to_claude_code.md"),
    },
    "from": {
        "antigravity": os.path.join(TEMPLATES_DIR, "from_antigravity.md"),
        "codex":       os.path.join(TEMPLATES_DIR, "from_codex.md"),
        "claude_code": os.path.join(TEMPLATES_DIR, "from_claude_code.md"),
    }
}

ENGINE_DISPLAY = {
    "antigravity": "Antigravity",
    "codex":       "Codex",
    "claude_code": "Claude Code",
}

POLL_INTERVAL   = 2  # seconds
DEBOUNCE_WINDOW = 5  # 같은 파일에 대한 알림 최소 간격 (초)

# Telegram config (기존 n8n 파이프라인과 동일 토큰 사용)
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
TG_CHAT_ID   = os.getenv("TG_CHAT_ID", "")

# ── Auto-Brain Callback 상태 ───────────────────────────────────────────────────
MAX_CHAIN_DEPTH   = 3
_auto_chain_active = False         # 체이닝으로 기록한 to_ 파일임을 표시
_current_chain_depth = 0           # 현재 체인 깊이 (0-base)
_last_cb_summary_hash = ""         # 반복 응답 감지용 직전 콜백 summary 해시


def _file_mtime(path: str) -> float:
    try:
        return os.path.getmtime(path)
    except OSError:
        return 0.0


def _read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def _content_hash(path: str) -> str:
    content = _read_file(path)
    return hashlib.md5(content.encode()).hexdigest()


def _parse_to_hands(content: str) -> tuple[str, str]:
    """to_[engine].md에서 작업 제목과 추천 엔진 추출."""
    title  = "Unknown Task"
    engine = "hands-1"

    m = re.search(r"(?:#.*실행 요청[:\s]*|#\s*to_\w+\s*—\s*|title:\s*[\"']?)(.+?)(?:[\"']?$)", content, re.MULTILINE)
    if m:
        title = m.group(1).strip()

    m = re.search(r"(?:\*\*추천\s*엔진[:\s]*\*\*\s*|engine:\s*[\"']?)(.+?)(?:[\"']?$)",
                  content, re.MULTILINE)
    if m:
        raw = m.group(1).strip().lower()
        if "hands-2" in raw or "gemini" in raw:
            engine = "hands-2"
        elif "hands-3" in raw or "codex" in raw:
            engine = "hands-3"
        elif "hands-4" in raw or "claude code" in raw or "cc" in raw:
            engine = "hands-4"
        elif "hands-1" in raw or "antigravity" in raw or "sonnet" in raw or "opus" in raw:
            engine = "hands-1"

    return title, engine


def _format_engine_result(title: str, result: dict, engine: str = "claude_code") -> str:
    """엔진 실행 결과를 from_[engine].md 포맷으로 변환."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    status = "done" if result["success"] else "failed"
    error_section = ""
    if result.get("error"):
        error_section = f"\n## 에러\n{result['error']}\n"

    return f"""---
title: "{title}"
engine: {engine}
status: {status}
completed: "{now}"
elapsed_seconds: {result['elapsed_seconds']:.1f}
---
# from_{engine} — 실행 결과

## 상태
{"✅ 성공" if result["success"] else "❌ 실패"}
소요 시간: {result['elapsed_seconds']:.0f}초
{error_section}
## 출력
{result.get('output', '(출력 없음)')}
"""


def _escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _send_telegram(text: str):
    """Telegram 알림 발송. 미설정 시 콘솔 출력만."""
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        print(f"[bridge] Telegram 미설정 — 콘솔만 출력: {text}")
        return

    url     = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id":    TG_CHAT_ID,
        "text":       text,
        "parse_mode": "HTML",
    }).encode()

    try:
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=5)
        print("[bridge] Telegram 발송 완료")
    except Exception as e:
        print(f"[bridge] Telegram 실패: {e}")


# ── Auto-Brain Callback 핸들러 ────────────────────────────────────────────────

def _handle_brain_decision(cb_result: dict, chain_depth: int, state: dict):
    """Brain의 DONE / CHAIN / ESCALATE 판단에 따라 처리."""
    global _auto_chain_active, _current_chain_depth, _last_cb_summary_hash

    decision      = cb_result.get("decision", "UNKNOWN")
    summary       = cb_result.get("summary", "")
    target_engine = cb_result.get("target_engine")
    chain_content = cb_result.get("chain_content")

    # 반복 응답 감지 — 동일 summary hash면 강제 ESCALATE
    summary_hash = hashlib.md5(summary.encode()).hexdigest()
    if summary_hash == _last_cb_summary_hash and decision != "ESCALATE":
        print("[brain_cb] ⚠️ 반복 응답 감지 — 강제 ESCALATE")
        decision = "ESCALATE"
        summary  = "반복 응답 감지 — 강제 에스컬레이션 (루프 방지)"
    _last_cb_summary_hash = summary_hash

    if decision == "DONE":
        print(f"[brain_cb] ✅ DONE — {summary[:100]}")
        _send_telegram(
            f"✅ <b>Auto-Brain: DONE</b>\n{_escape_html(summary[:500])}"
        )
        _current_chain_depth = 0

    elif decision == "CHAIN":
        if chain_depth >= MAX_CHAIN_DEPTH or not target_engine:
            reason = f"chain_depth={chain_depth}>={MAX_CHAIN_DEPTH}" if chain_depth >= MAX_CHAIN_DEPTH else "target_engine 미지정"
            print(f"[brain_cb] ⚠️ CHAIN 한도 초과/미지정 — ESCALATE. {reason}")
            _send_telegram(
                f"⚠️ <b>Auto-Brain: ESCALATE</b> (체인 한도)\n{_escape_html(reason)}"
            )
            _current_chain_depth = 0
            return

        to_path = WATCH_FILES["to"].get(target_engine)
        if not to_path:
            print(f"[brain_cb] ❌ 알 수 없는 target_engine: {target_engine}")
            _send_telegram(f"❌ <b>Auto-Brain: CHAIN 오류</b>\n알 수 없는 엔진: {target_engine}")
            return

        chain_body = chain_content or summary
        try:
            with open(to_path, "w", encoding="utf-8") as f:
                f.write(chain_body)
            # 상태 해시 갱신 — 새로 쓴 to_ 파일이 자신의 다음 폴링에서 중복 처리되지 않도록
            key = f"to_{target_engine}"
            if key in state:
                state[key]["hash"]  = hashlib.md5(chain_body.encode()).hexdigest()
                state[key]["mtime"] = _file_mtime(to_path)

            _auto_chain_active   = True
            _current_chain_depth = chain_depth + 1
            display = ENGINE_DISPLAY.get(target_engine, target_engine)
            print(f"[brain_cb] 🔗 CHAIN → {display} (depth={_current_chain_depth})")
            _send_telegram(
                f"🔗 <b>Auto-Brain: CHAIN</b>\n→ {display}\n깊이: {_current_chain_depth}/{MAX_CHAIN_DEPTH}\n\n"
                f"{_escape_html(chain_body[:300])}"
            )
        except Exception as e:
            print(f"[brain_cb] ❌ CHAIN 파일 기록 실패: {e}")
            _send_telegram(f"❌ <b>Auto-Brain: CHAIN 실패</b>\n{_escape_html(str(e))}")

    else:  # ESCALATE or UNKNOWN
        label = "ESCALATE" if decision == "ESCALATE" else "UNKNOWN"
        print(f"[brain_cb] 🚨 {label} — {summary[:100]}")
        _send_telegram(
            f"🚨 <b>Auto-Brain: {label}</b>\n{_escape_html(summary[:500])}"
        )
        _current_chain_depth = 0


def _run_auto_brain_callback(engine: str, from_path: str, state: dict):
    """엔진 자동실행 완료 후 Brain 콜백 호출."""
    global _current_chain_depth

    if not _check_brain_daily_limit():
        print("[brain_cb] ⚠️ 일일 Brain 콜백 한도 초과 — 스킵")
        _send_telegram("⚠️ <b>Auto-Brain 한도 초과</b> — 오늘 30회 소진")
        return

    from_content = _read_file(from_path)
    if not from_content.strip():
        print("[brain_cb] from_ 파일이 비어있어 콜백 스킵")
        return

    depth = _current_chain_depth
    print(f"[brain_cb] 🧠 Brain 콜백 시작 (engine={engine}, depth={depth})")
    cb_result = run_brain_callback(engine, from_content, chain_depth=depth)
    _handle_brain_decision(cb_result, chain_depth=depth, state=state)


def main():
    global _auto_chain_active, _current_chain_depth

    print("[bridge] Task Bridge v4.3 시작 (엔진별 6파일 감시, 3엔진 자동 트리거, Auto-Brain Callback)")

    client = None
    try:
        client = get_redis()
        client.ping()
        print("[bridge] Redis 연결 OK")
    except Exception as e:
        print(f"[bridge] Redis 연결 실패: {e} — 파일 전용 모드")

    # 각 파일의 상태 초기화
    state = {}
    for direction in ("to", "from"):
        for engine, filepath in WATCH_FILES[direction].items():
            key = f"{direction}_{engine}"
            state[key] = {
                "path": filepath,
                "mtime": _file_mtime(filepath),
                "hash": _content_hash(filepath),
                "last_alert": 0.0,
                "last_task_id": None,
            }

    while True:
        try:
            for direction in ("to", "from"):
                for engine, filepath in WATCH_FILES[direction].items():
                    key = f"{direction}_{engine}"
                    s = state[key]
                    new_mt = _file_mtime(filepath)

                    if new_mt <= s["mtime"]:
                        continue

                    s["mtime"] = new_mt
                    now = time.time()
                    if now - s["last_alert"] < DEBOUNCE_WINDOW:
                        print(f"[bridge] {key} 디바운스 — 스킵")
                        continue

                    time.sleep(2)  # 쓰기 완료 대기
                    s["mtime"] = _file_mtime(filepath)
                    content = _read_file(filepath)
                    new_hash = hashlib.md5(content.encode()).hexdigest()

                    if new_hash == s["hash"] or not content.strip() or "EMPTY" in content[:50]:
                        continue

                    s["hash"] = new_hash
                    s["last_alert"] = time.time()
                    display = ENGINE_DISPLAY.get(engine, engine)

                    if direction == "to":
                        title, _ = _parse_to_hands(content)
                        print(f"[bridge] 새 작업: {title} → {display}")
                        if client:
                            try:
                                tid = add_task(client, title, engine, content)
                                s["last_task_id"] = tid
                                print(f"[bridge] Redis: task_id={tid}")
                            except Exception as e:
                                print(f"[bridge] Redis 실패: {e}")
                        _send_telegram(
                            f"<b>새 작업</b>\n{_escape_html(title)}\n엔진: {display}\n\n"
                            f"to_{engine}.md → {display}에 전달하세요"
                        )

                        # CC 자동 실행 (claude_code 엔진만)
                        if engine == "claude_code":
                            print(f"[bridge] ⚡ CC 자동 실행 시작: {title}")
                            _send_telegram(f"⚡ <b>CC 자동 실행 시작</b>\n{_escape_html(title)}")

                            cc_result = run_claude_code(
                                prompt=f"다음 작업지시서를 읽고 실행하세요. 결과를 간결하게 보고하세요.\n\n{content}",
                                working_dir="/Users/woosung/Desktop/Dev/Woosdom_Brain"
                            )

                            from_path = WATCH_FILES["from"]["claude_code"]
                            result_md = _format_engine_result(title, cc_result, "claude_code")
                            with open(from_path, "w", encoding="utf-8") as f:
                                f.write(result_md)
                            # from_ 상태 갱신 — 자동실행 내부에서 기록한 from_은 별도 콜백 안 함
                            fkey = "from_claude_code"
                            state[fkey]["hash"]  = hashlib.md5(result_md.encode()).hexdigest()
                            state[fkey]["mtime"] = _file_mtime(from_path)

                            status_emoji = "✅" if cc_result["success"] else "❌"
                            elapsed = cc_result["elapsed_seconds"]
                            _send_telegram(
                                f"{status_emoji} <b>CC 실행 완료</b>\n{_escape_html(title)}\n"
                                f"소요: {elapsed:.0f}초\nfrom_claude_code.md 업데이트됨"
                            )

                            # Auto-Brain Callback (S-1)
                            _run_auto_brain_callback("claude_code", from_path, state)

                        # Codex 자동 실행
                        if engine == "codex":
                            print(f"[bridge] ⚡ Codex 자동 실행 시작: {title}")
                            _send_telegram(f"⚡ <b>Codex 자동 실행 시작</b>\n{_escape_html(title)}")

                            codex_result = run_codex(
                                prompt=f"다음 작업지시서를 읽고 실행하세요. 결과를 간결하게 보고하세요.\n\n{content}",
                                working_dir="/Users/woosung/Desktop/Dev/Woosdom_Brain"
                            )

                            from_path = WATCH_FILES["from"]["codex"]
                            result_md = _format_engine_result(title, codex_result, "codex")
                            with open(from_path, "w", encoding="utf-8") as f:
                                f.write(result_md)
                            fkey = "from_codex"
                            state[fkey]["hash"]  = hashlib.md5(result_md.encode()).hexdigest()
                            state[fkey]["mtime"] = _file_mtime(from_path)

                            status_emoji = "✅" if codex_result["success"] else "❌"
                            elapsed = codex_result["elapsed_seconds"]
                            _send_telegram(
                                f"{status_emoji} <b>Codex 실행 완료</b>\n{_escape_html(title)}\n"
                                f"소요: {elapsed:.0f}초\nfrom_codex.md 업데이트됨"
                            )

                            # Auto-Brain Callback (S-1)
                            _run_auto_brain_callback("codex", from_path, state)

                        # Gemini CLI 자동 실행 (antigravity 엔진)
                        if engine == "antigravity":
                            print(f"[bridge] ⚡ Gemini CLI 자동 실행 시작: {title}")
                            _send_telegram(f"⚡ <b>Gemini CLI 자동 실행 시작</b>\n{_escape_html(title)}")

                            gemini_result = run_gemini(
                                prompt=f"다음 작업지시서를 읽고 실행하세요. 결과를 간결하게 보고하세요.\n\n{content}",
                                working_dir="/Users/woosung/Desktop/Dev/Woosdom_Brain"
                            )

                            from_path = WATCH_FILES["from"]["antigravity"]
                            result_md = _format_engine_result(title, gemini_result, "antigravity")
                            with open(from_path, "w", encoding="utf-8") as f:
                                f.write(result_md)
                            fkey = "from_antigravity"
                            state[fkey]["hash"]  = hashlib.md5(result_md.encode()).hexdigest()
                            state[fkey]["mtime"] = _file_mtime(from_path)

                            status_emoji = "✅" if gemini_result["success"] else "❌"
                            elapsed = gemini_result["elapsed_seconds"]
                            _send_telegram(
                                f"{status_emoji} <b>Gemini CLI 실행 완료</b>\n{_escape_html(title)}\n"
                                f"소요: {elapsed:.0f}초\nfrom_antigravity.md 업데이트됨"
                            )

                            # Auto-Brain Callback (S-1)
                            _run_auto_brain_callback("antigravity", from_path, state)

                    else:  # from — Brain이 직접 기록한 경우 (외부 에이전트 완료)
                        print(f"[bridge] 작업 완료: {display}")
                        to_key = f"to_{engine}"
                        tid = state[to_key]["last_task_id"]
                        if client and tid:
                            try:
                                complete_task(client, tid)
                                print(f"[bridge] Redis 완료: task_id={tid}")
                            except Exception as e:
                                print(f"[bridge] Redis 완료 실패: {e}")
                            state[to_key]["last_task_id"] = None
                        _send_telegram(f"<b>작업 완료</b>\n{display} → from_{engine}.md 업데이트됨")
                        # 참고: task_bridge 자신이 쓴 from_은 위 자동실행 블록에서 hash 갱신하여
                        # 이 else 분기에 도달하지 않음. 여기 도달하는 경우는 외부 에이전트가 기록한 경우.

        except KeyboardInterrupt:
            print("[bridge] 종료")
            break
        except Exception as e:
            print(f"[bridge] 루프 에러: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
