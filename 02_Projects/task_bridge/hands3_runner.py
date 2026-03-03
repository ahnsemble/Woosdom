"""Hands-3 Runner — Claude Code CLI 무인 실행기 (Sprint 5-5, v4.5).

v4.5 변경:
  - estimate_task_size() — 프롬프트 길이 + 키워드로 S/M/L 판별, 동적 max-turns
  - _git_stash_save() / _git_stash_pop() — 실행 전 git stash 안전장치
"""
import os
import re
import subprocess
import time
from datetime import datetime, timezone

# ── 안전장치 상수 ──────────────────────────────────────────────────────────────
MAX_TASK_TIMEOUT  = 1800       # 단일 작업 최대 30분
MAX_DAILY_TASKS   = 20         # 일일 자동실행 최대 20건
MAX_OUTPUT_CHARS  = 50_000     # 출력 최대 50K 문자
COOLDOWN_SECONDS  = 10         # 작업 간 강제 쿨다운
DEFAULT_CWD       = "/Users/woosung/Desktop/Dev/Woosdom_Brain"  # macOS TCC 팝업 방지

# ── 일일 카운터 (프로세스 수명 내, 단순 날짜 기반 리셋) ─────────────────────────
_daily_count      = 0
_daily_reset_date = ""


# ── T2: 동적 턴 한도 ─────────────────────────────────────────────────────────
_SIZE_KEYWORDS_L = re.compile(r"디버그|리팩토링|마이그레이션|debug|refactor|migrat", re.IGNORECASE)

TURN_LIMITS = {"S": 15, "M": 30, "L": 50}


def estimate_task_size(prompt: str) -> str:
    """프롬프트 길이 + 키워드로 작업 크기를 S/M/L로 판별."""
    if _SIZE_KEYWORDS_L.search(prompt):
        return "L"
    length = len(prompt)
    if length <= 500:
        return "S"
    if length <= 2000:
        return "M"
    return "L"


# ── T5: git stash 롤백 ───────────────────────────────────────────────────────

def _git_stash_save(cwd: str) -> str | None:
    """실행 전 git stash. 변경사항 없거나 git repo가 아니면 None."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    msg = f"woosdom-safety-{timestamp}"
    try:
        result = subprocess.run(
            ["git", "stash", "push", "-m", msg],
            capture_output=True, text=True, cwd=cwd, timeout=10,
        )
        if result.returncode != 0:
            return None
        # "No local changes to save" → stash 안 됨
        if "No local changes" in result.stdout:
            return None
        print(f"[CC] git stash 저장: {msg}")
        return msg
    except Exception:
        return None


def _git_stash_pop(cwd: str, stash_ref: str):
    """실패 시 git stash pop으로 복원."""
    try:
        subprocess.run(
            ["git", "stash", "pop"],
            capture_output=True, text=True, cwd=cwd, timeout=10,
        )
        print(f"[CC] git stash pop 완료: {stash_ref}")
    except Exception as e:
        print(f"[CC] git stash pop 실패: {e}")


def _git_stash_drop(cwd: str, stash_ref: str):
    """성공 시 stash 제거."""
    try:
        # stash list에서 해당 ref 찾아서 drop
        result = subprocess.run(
            ["git", "stash", "list"],
            capture_output=True, text=True, cwd=cwd, timeout=10,
        )
        for line in result.stdout.splitlines():
            if stash_ref in line:
                stash_id = line.split(":")[0]  # e.g. "stash@{0}"
                subprocess.run(
                    ["git", "stash", "drop", stash_id],
                    capture_output=True, text=True, cwd=cwd, timeout=10,
                )
                print(f"[CC] git stash drop: {stash_id} ({stash_ref})")
                return
    except Exception as e:
        print(f"[CC] git stash drop 실패: {e}")


def _check_daily_limit() -> bool:
    """일일 한도 체크. 날짜 변경 시 카운터 리셋."""
    global _daily_count, _daily_reset_date
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if today != _daily_reset_date:
        _daily_count      = 0
        _daily_reset_date = today
    return _daily_count < MAX_DAILY_TASKS


def _sanitize_env() -> dict:
    """ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN 제거한 환경변수 반환.

    Claude Code가 이 키들을 발견하면 구독 OAuth 대신 API 종량제로 과금함.
    반드시 제거해야 구독 플랜으로 실행된다.
    """
    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY",    None)
    env.pop("ANTHROPIC_AUTH_TOKEN", None)
    return env


def run_claude_code(prompt: str, working_dir: str | None = None) -> dict:
    """Claude Code CLI를 non-interactive 모드로 실행.
    stdout을 터미널에 실시간 출력하면서 동시에 버퍼에 저장.
    """
    global _daily_count

    if not _check_daily_limit():
        return {
            "success": False, "output": "",
            "elapsed_seconds": 0.0,
            "error": f"일일 한도 초과 ({MAX_DAILY_TASKS}건/일)",
        }

    # T2: 동적 턴 한도
    size = estimate_task_size(prompt)
    max_turns = TURN_LIMITS[size]
    print(f"[CC] 작업 크기: {size} → max-turns {max_turns}")

    cmd = [
        "claude", "-p", prompt,
        "--output-format", "text",
        "--dangerously-skip-permissions",
        "--max-turns", str(max_turns),
    ]
    env = _sanitize_env()
    cwd = working_dir or DEFAULT_CWD

    # T5: git stash 안전장치
    stash_ref = _git_stash_save(cwd)

    start = time.time()
    output_lines = []

    try:
        print(f"\n{'='*60}")
        print(f"[CC] 실행 시작: {prompt[:80]}...")
        print(f"{'='*60}")

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            cwd=cwd,
        )

        # stdout 실시간 스트리밍
        for line in proc.stdout:
            print(f"[CC] {line}", end="")  # 터미널에 실시간 출력
            output_lines.append(line)

        proc.wait(timeout=MAX_TASK_TIMEOUT)
        elapsed = time.time() - start
        output = "".join(output_lines)[:MAX_OUTPUT_CHARS]
        stderr_out = proc.stderr.read()[:500] if proc.stderr else ""
        _daily_count += 1

        print(f"\n{'='*60}")
        print(f"[CC] 완료 — exit={proc.returncode}, {elapsed:.0f}초")
        print(f"{'='*60}\n")

        if proc.returncode != 0:
            # T5: 실패 시 stash pop 복원
            if stash_ref:
                _git_stash_pop(cwd, stash_ref)
                print("[CC] 🔄 롤백 실행됨 (exit code != 0)")
            return {
                "success": False, "output": output,
                "elapsed_seconds": elapsed,
                "error": f"exit code {proc.returncode}: {stderr_out}",
                "max_turns_used": max_turns,
            }

        # T5: 성공 시 stash drop
        if stash_ref:
            _git_stash_drop(cwd, stash_ref)

        return {
            "success": True, "output": output,
            "elapsed_seconds": elapsed, "error": None,
            "max_turns_used": max_turns,
        }

    except subprocess.TimeoutExpired:
        proc.kill()
        elapsed = time.time() - start
        print(f"\n[CC] ⚠️ 타임아웃 ({MAX_TASK_TIMEOUT}초)")
        # T5: 타임아웃 시 stash pop 복원
        if stash_ref:
            _git_stash_pop(cwd, stash_ref)
            print("[CC] 🔄 롤백 실행됨 (타임아웃)")
        return {
            "success": False, "output": "".join(output_lines),
            "elapsed_seconds": elapsed,
            "error": f"타임아웃 ({MAX_TASK_TIMEOUT}초 초과)",
            "max_turns_used": max_turns,
        }
    except FileNotFoundError:
        print("[CC] ❌ claude CLI를 찾을 수 없음")
        if stash_ref:
            _git_stash_pop(cwd, stash_ref)
        return {
            "success": False, "output": "",
            "elapsed_seconds": 0.0,
            "error": "claude CLI를 찾을 수 없음. PATH 확인 필요",
            "max_turns_used": max_turns,
        }
    except Exception as e:
        elapsed = time.time() - start
        print(f"[CC] ❌ 예외: {e}")
        if stash_ref:
            _git_stash_pop(cwd, stash_ref)
            print("[CC] 🔄 롤백 실행됨 (예외)")
        return {
            "success": False, "output": "",
            "elapsed_seconds": elapsed, "error": str(e),
            "max_turns_used": max_turns,
        }


def get_daily_stats() -> dict:
    """대시보드용 일일 통계."""
    _check_daily_limit()          # 날짜 리셋 체크
    return {
        "date":            _daily_reset_date,
        "tasks_run":       _daily_count,
        "tasks_remaining": MAX_DAILY_TASKS - _daily_count,
    }

if __name__ == "__main__":
    print("[hands3-runner] 직접 실행 테스트")
    result = run_claude_code("echo 'Hello from Woosdom auto-trigger test'")
    print(f"결과: {result}")

