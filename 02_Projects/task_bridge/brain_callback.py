"""brain_callback.py — Auto-Brain Callback (task_bridge v4.3 S-1).

엔진 실행 완료 후 `claude -p`로 Brain을 자동 호출하여
DONE / CHAIN:engine_name / ESCALATE 판단을 받는다.
"""
import os
import subprocess
import time
import hashlib
from datetime import datetime, timezone

# ── 안전장치 상수 ──────────────────────────────────────────────────────────────
CALLBACK_TIMEOUT   = 120        # Brain 콜백 최대 대기 시간 (초)
MAX_FROM_PREVIEW   = 3000       # from_ 내용 Brain에 전달할 최대 문자 수
MAX_CHAIN_DEPTH    = 3          # 최대 체이닝 깊이

VALID_ENGINES = {"claude_code", "codex", "antigravity"}

# ── 일일 한도 ─────────────────────────────────────────────────────────────────
MAX_DAILY_BRAIN_CALLS = 30
_brain_call_count     = 0
_brain_call_date      = ""


def _check_brain_daily_limit() -> bool:
    """일일 30회 한도 체크. 날짜 변경 시 카운터 리셋."""
    global _brain_call_count, _brain_call_date
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if today != _brain_call_date:
        _brain_call_count = 0
        _brain_call_date  = today
    return _brain_call_count < MAX_DAILY_BRAIN_CALLS


def _increment_brain_count():
    global _brain_call_count
    _brain_call_count += 1


def _sanitize_env() -> dict:
    """ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN 제거 — 구독 플랜으로만 실행."""
    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY",    None)
    env.pop("ANTHROPIC_AUTH_TOKEN", None)
    return env


def _build_callback_prompt(engine: str, from_content: str, chain_depth: int) -> str:
    """Brain에 전달할 compact callback prompt 구성 (~300 tok)."""
    preview = from_content[:MAX_FROM_PREVIEW]
    return f"""[Woosdom Auto-Brain Callback]
엔진: {engine}
체인 깊이: {chain_depth}/{MAX_CHAIN_DEPTH}

== 엔진 실행 결과 ==
{preview}

판단하세요:
1. DONE — 작업 성공 완료. 한 줄 요약 보고.
2. CHAIN:engine_name — 후속 작업 필요. 반드시 to_[engine].md 형식으로 후속 작업 내용을 출력하세요. engine_name은 claude_code, codex, antigravity 중 하나.
3. ESCALATE — 사용자 판단 필요. 이유를 설명하세요.

첫 줄에 반드시 DONE, CHAIN:xxx, ESCALATE 중 하나만 출력. 그 아래에 설명.
성공 기준: 에러 없이 의도한 산출물이 생성됨. 단순 "실행했습니다"는 검증 불충분.
"""


def _parse_brain_response(response: str) -> tuple[str, str | None, str, str | None]:
    """Brain 응답 첫 줄에서 결정 추출.

    Returns:
        (decision, target_engine, summary, chain_content)
        decision: "DONE" | "CHAIN" | "ESCALATE" | "UNKNOWN"
        target_engine: CHAIN일 때 엔진 이름, 나머지는 None
        summary: 첫 줄 이후 전체 텍스트 (설명/체인 내용 포함)
        chain_content: CHAIN일 때 summary와 동일 (to_[engine].md에 쓸 내용)
    """
    lines = response.strip().splitlines()
    if not lines:
        return "UNKNOWN", None, response, None

    first_line = lines[0].strip().upper()
    rest = "\n".join(lines[1:]).strip()

    if first_line == "DONE":
        return "DONE", None, rest, None

    if first_line.startswith("CHAIN:"):
        raw_engine = lines[0].split(":", 1)[1].strip().lower()
        # 정규화
        target_engine = None
        if raw_engine in VALID_ENGINES:
            target_engine = raw_engine
        elif "claude" in raw_engine or "cc" in raw_engine:
            target_engine = "claude_code"
        elif "codex" in raw_engine:
            target_engine = "codex"
        elif "antigravity" in raw_engine or "gemini" in raw_engine:
            target_engine = "antigravity"
        return "CHAIN", target_engine, rest, rest

    if first_line == "ESCALATE":
        return "ESCALATE", None, rest, None

    # 첫 줄이 규칙에 맞지 않는 경우 — 전체 응답을 summary로
    return "UNKNOWN", None, response, None


def run_brain_callback(engine: str, from_content: str, chain_depth: int = 0) -> dict:
    """Auto-Brain Callback 실행.

    Args:
        engine: 방금 실행한 엔진 이름 ("claude_code" | "codex" | "antigravity")
        from_content: from_[engine].md 전체 내용
        chain_depth: 현재 체이닝 깊이 (0-base)

    Returns:
        {
            "decision": "DONE"|"CHAIN"|"ESCALATE"|"UNKNOWN",
            "target_engine": str|None,
            "summary": str,
            "chain_content": str|None,
            "success": bool,
            "error": str|None,
        }
    """
    # 깊이 초과 → 강제 ESCALATE
    if chain_depth >= MAX_CHAIN_DEPTH:
        return {
            "decision": "ESCALATE",
            "target_engine": None,
            "summary": f"최대 체인 깊이({MAX_CHAIN_DEPTH}) 초과 — 강제 에스컬레이션",
            "chain_content": None,
            "success": True,
            "error": None,
        }

    # 일일 한도 체크
    if not _check_brain_daily_limit():
        return {
            "decision": "ESCALATE",
            "target_engine": None,
            "summary": f"일일 Brain 콜백 한도 초과 ({MAX_DAILY_BRAIN_CALLS}회/일)",
            "chain_content": None,
            "success": False,
            "error": "daily_limit_exceeded",
        }

    prompt = _build_callback_prompt(engine, from_content, chain_depth)
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "text",
        "--max-turns", "10",
        "--dangerously-skip-permissions",
    ]
    env = _sanitize_env()

    start = time.time()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=CALLBACK_TIMEOUT,
            env=env,
        )
        elapsed = time.time() - start
        _increment_brain_count()

        if proc.returncode != 0:
            stderr = proc.stderr[:500] if proc.stderr else ""
            return {
                "decision": "ESCALATE",
                "target_engine": None,
                "summary": f"Brain CLI 오류 (exit={proc.returncode}): {stderr}",
                "chain_content": None,
                "success": False,
                "error": f"exit code {proc.returncode}",
            }

        response = proc.stdout.strip()
        decision, target_engine, summary, chain_content = _parse_brain_response(response)

        return {
            "decision": decision,
            "target_engine": target_engine,
            "summary": summary,
            "chain_content": chain_content,
            "success": True,
            "error": None,
        }

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        return {
            "decision": "ESCALATE",
            "target_engine": None,
            "summary": f"Brain 콜백 타임아웃 ({CALLBACK_TIMEOUT}초)",
            "chain_content": None,
            "success": False,
            "error": f"timeout after {elapsed:.0f}s",
        }
    except FileNotFoundError:
        return {
            "decision": "ESCALATE",
            "target_engine": None,
            "summary": "claude CLI를 찾을 수 없음 — PATH 확인 필요",
            "chain_content": None,
            "success": False,
            "error": "claude CLI not found",
        }
    except Exception as e:
        return {
            "decision": "ESCALATE",
            "target_engine": None,
            "summary": f"Brain 콜백 예외: {e}",
            "chain_content": None,
            "success": False,
            "error": str(e),
        }


def get_daily_brain_stats() -> dict:
    """대시보드용 일일 Brain 콜백 통계."""
    _check_brain_daily_limit()  # 날짜 리셋 체크
    return {
        "date":           _brain_call_date,
        "calls_made":     _brain_call_count,
        "calls_remaining": MAX_DAILY_BRAIN_CALLS - _brain_call_count,
    }
