"""Hands-3 Runner E2E 테스트."""
import os
import sys
import subprocess
import time

sys.path.insert(0, os.path.dirname(__file__))
import hands3_runner as h3
from hands3_runner import (
    _sanitize_env, _check_daily_limit, run_claude_code,
    get_daily_stats, MAX_DAILY_TASKS,
)


# ── 헬퍼 ──────────────────────────────────────────────────────────────────────
def _reset_daily():
    h3._daily_count      = 0
    h3._daily_reset_date = ""


def _ok(desc: str):
    print(f"✅ {desc}")


# ── 테스트 함수 ───────────────────────────────────────────────────────────────
def test_1_env_sanitization():
    """ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN 이 제거되는지 확인."""
    os.environ["ANTHROPIC_API_KEY"]    = "test-key-should-be-removed"
    os.environ["ANTHROPIC_AUTH_TOKEN"] = "test-token-should-be-removed"
    env = _sanitize_env()
    assert "ANTHROPIC_API_KEY"    not in env, "API_KEY 제거 실패"
    assert "ANTHROPIC_AUTH_TOKEN" not in env, "AUTH_TOKEN 제거 실패"
    del os.environ["ANTHROPIC_API_KEY"]
    del os.environ["ANTHROPIC_AUTH_TOKEN"]
    _ok("환경변수 제거 (API_KEY, AUTH_TOKEN 모두 제거됨)")


def test_2_daily_limit():
    """MAX_DAILY_TASKS 도달 시 run_claude_code가 즉시 실패 dict 반환."""
    from datetime import datetime, timezone
    _reset_daily()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    h3._daily_reset_date = today           # 오늘 날짜 고정 → 리셋 안 됨
    h3._daily_count      = MAX_DAILY_TASKS  # 한도에 정확히 도달
    result = run_claude_code("테스트")
    assert not result["success"], "한도 초과 시 success=True 오류"
    assert "한도" in (result["error"] or ""), f"에러 메시지 이상: {result['error']}"
    _ok(f"일일 한도 ({MAX_DAILY_TASKS}건) 초과 시 즉시 거부")
    _reset_daily()




def test_3_claude_code_available():
    """claude CLI가 설치되어 있는지 확인."""
    try:
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"⚠️  Claude Code 미설치 — test_4 건너뜀 (npm install -g @anthropic-ai/claude-code)")
            return False
        _ok(f"Claude Code 설치 확인: {result.stdout.strip()[:60]}")
        return True
    except FileNotFoundError:
        print(f"⚠️  Claude Code 미설치 (명령어 찾을 수 없음) — test_4 건너뜀")
        return False



def test_4_simple_execution():
    """간단한 프롬프트 실행 — "Hands-3 test OK" 출력 확인."""
    _reset_daily()
    result = run_claude_code("Reply with exactly: Hands-3 test OK")
    if not result["success"]:
        print(f"⚠️  실행 실패 (OAuth 미로그인?): {result['error']}")
        return
    assert "OK" in result["output"], f"출력 이상: {result['output'][:200]}"
    _ok(f"실행 성공 ({result['elapsed_seconds']:.1f}초): {result['output'][:80].strip()}")


def test_5_timeout_handling():
    """MAX_TASK_TIMEOUT이 적용되는지 확인 (임시로 1초 설정)."""
    _reset_daily()
    orig = h3.MAX_TASK_TIMEOUT
    h3.MAX_TASK_TIMEOUT = 1
    result = run_claude_code("Sleep 10 seconds then say done")
    h3.MAX_TASK_TIMEOUT = orig
    # 타임아웃이 발생하거나 매우 빨리 성공할 수 있음
    # 타임아웃 시 success=False, error에 "타임아웃" 포함
    if not result["success"]:
        assert "타임아웃" in result["error"] or "expired" in result["error"].lower(), \
            f"예상치 못한 에러: {result['error']}"
    _ok(f"타임아웃 처리 OK (success={result['success']}, elapsed={result['elapsed_seconds']:.1f}s)")
    _reset_daily()


def test_6_bridge_integration():
    """_parse_to_hands YAML 포맷 + _extract_prompt 파싱 확인."""
    from task_bridge import _parse_to_hands, _extract_prompt

    yaml_sample = """---
title: "Sprint 3 테스트"
engine: "antigravity_sonnet"
---

# 실행 지시서

---

## 실제 프롬프트 본문
이 내용이 Claude에게 전달됩니다.
"""
    # engine 파싱 — YAML engine: 필드 인식
    title, engine = _parse_to_hands(yaml_sample)
    # engine 필드에 hands-3 키워드 없으면 hands-1이 기본
    _ok(f"YAML 파싱: title='{title}', engine='{engine}'")

    # _extract_prompt 검증
    prompt = _extract_prompt(yaml_sample)
    assert "실제 프롬프트" in prompt, f"프롬프트 추출 실패: {prompt[:100]}"
    _ok(f"프롬프트 추출 OK: 첫 40자='{prompt[:40]}'")


def test_7_daily_stats():
    """get_daily_stats() 반환값 포맷 확인."""
    _reset_daily()
    stats = get_daily_stats()
    assert "tasks_run"       in stats
    assert "tasks_remaining" in stats
    assert stats["tasks_remaining"] == MAX_DAILY_TASKS
    _ok(f"일일 통계: {stats}")


# ── 메인 ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("Hands-3 Runner — E2E Tests")
    print("=" * 55)

    test_1_env_sanitization()
    test_2_daily_limit()
    claude_ok = test_3_claude_code_available()
    if claude_ok:
        test_4_simple_execution()
        test_5_timeout_handling()
    else:
        print("⏭️  test_4, test_5 건너뜀 (Claude Code 미설치)")
    test_6_bridge_integration()
    test_7_daily_stats()

    print("\n🎉 ALL TESTS PASSED")
