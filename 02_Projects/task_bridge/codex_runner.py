"""Codex Runner — OpenAI Codex CLI non-interactive 실행기 (hands3_runner.py 패턴).

CODEX_API_KEY 환경변수가 있으면 API 키 인증, 없으면 ChatGPT OAuth 폴백.
"""
import os
import subprocess
import time
from datetime import datetime, timezone

# ── 안전장치 상수 ──────────────────────────────────────────────────────────────
MAX_TASK_TIMEOUT  = 1800       # 단일 작업 최대 30분
MAX_DAILY_TASKS   = 20         # 일일 자동실행 최대 20건 (codex 독립 카운터)
MAX_OUTPUT_CHARS  = 50_000     # 출력 최대 50K 문자
COOLDOWN_SECONDS  = 10         # 작업 간 강제 쿨다운
DEFAULT_CWD       = "/Users/woosung/Desktop/Dev/Woosdom_Brain"

# ── 일일 카운터 (프로세스 수명 내, 단순 날짜 기반 리셋) ─────────────────────────
_daily_count      = 0
_daily_reset_date = ""


def _check_daily_limit() -> bool:
    """일일 한도 체크. 날짜 변경 시 카운터 리셋."""
    global _daily_count, _daily_reset_date
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if today != _daily_reset_date:
        _daily_count      = 0
        _daily_reset_date = today
    return _daily_count < MAX_DAILY_TASKS


def run_codex(prompt: str, working_dir: str | None = None) -> dict:
    """Codex CLI를 non-interactive 모드로 실행.
    stdout을 터미널에 실시간 출력하면서 동시에 버퍼에 저장.

    Returns:
        {"success": bool, "output": str, "elapsed_seconds": float, "error": str|None}
    """
    global _daily_count

    if not _check_daily_limit():
        return {
            "success": False, "output": "",
            "elapsed_seconds": 0.0,
            "error": f"일일 한도 초과 ({MAX_DAILY_TASKS}건/일)",
        }

    cmd = [
        "codex", "exec", prompt,
        "--full-auto",
        "--skip-git-repo-check",
    ]
    env = os.environ.copy()
    cwd = working_dir or DEFAULT_CWD

    start = time.time()
    output_lines = []

    try:
        print(f"\n{'='*60}")
        print(f"[Codex] 실행 시작: {prompt[:80]}...")
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
            print(f"[Codex] {line}", end="")
            output_lines.append(line)

        proc.wait(timeout=MAX_TASK_TIMEOUT)
        elapsed = time.time() - start
        output = "".join(output_lines)[:MAX_OUTPUT_CHARS]
        stderr_out = proc.stderr.read()[:500] if proc.stderr else ""
        _daily_count += 1

        print(f"\n{'='*60}")
        print(f"[Codex] 완료 — exit={proc.returncode}, {elapsed:.0f}초")
        print(f"{'='*60}\n")

        if proc.returncode != 0:
            return {
                "success": False, "output": output,
                "elapsed_seconds": elapsed,
                "error": f"exit code {proc.returncode}: {stderr_out}",
            }

        return {
            "success": True, "output": output,
            "elapsed_seconds": elapsed, "error": None,
        }

    except subprocess.TimeoutExpired:
        proc.kill()
        elapsed = time.time() - start
        print(f"\n[Codex] ⚠️ 타임아웃 ({MAX_TASK_TIMEOUT}초)")
        return {
            "success": False, "output": "".join(output_lines),
            "elapsed_seconds": elapsed,
            "error": f"타임아웃 ({MAX_TASK_TIMEOUT}초 초과)",
        }
    except FileNotFoundError:
        print("[Codex] ❌ codex CLI를 찾을 수 없음")
        return {
            "success": False, "output": "",
            "elapsed_seconds": 0.0,
            "error": "codex CLI를 찾을 수 없음. npm install -g @openai/codex 또는 PATH 확인 필요",
        }
    except Exception as e:
        elapsed = time.time() - start
        print(f"[Codex] ❌ 예외: {e}")
        return {
            "success": False, "output": "",
            "elapsed_seconds": elapsed, "error": str(e),
        }


def get_daily_stats() -> dict:
    """대시보드용 일일 통계."""
    _check_daily_limit()
    return {
        "date":            _daily_reset_date,
        "tasks_run":       _daily_count,
        "tasks_remaining": MAX_DAILY_TASKS - _daily_count,
    }


if __name__ == "__main__":
    print("[codex-runner] 직접 실행 테스트")
    result = run_codex("echo 'Hello from Woosdom Codex auto-trigger test'")
    print(f"결과: {result}")
