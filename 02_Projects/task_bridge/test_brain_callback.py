"""test_brain_callback.py — brain_callback 모듈 가드레일 테스트 (T3).

테스트 목록:
  - test_parse_done         : DONE 응답 파싱
  - test_parse_chain        : CHAIN:codex 응답 파싱
  - test_parse_escalate     : ESCALATE 응답 파싱
  - test_daily_limit        : 30회 초과 시 호출 차단
  - test_chain_depth_limit  : depth >= MAX_CHAIN_DEPTH 시 ESCALATE 강제
  - test_duplicate_response : 동일 응답 반복 시 task_bridge 레벨에서 ESCALATE 강제
"""
import hashlib
import pytest
import brain_callback as bc


# ── 파싱 테스트 ────────────────────────────────────────────────────────────────

def test_parse_done():
    response = "DONE\n작업이 성공적으로 완료되었습니다. 파일 3개 생성."
    decision, target, summary, chain = bc._parse_brain_response(response)
    assert decision == "DONE"
    assert target is None
    assert chain is None
    assert "성공" in summary


def test_parse_chain():
    response = "CHAIN:codex\nto_codex.md에 후속 작업을 작성해주세요.\n\n## 후속 태스크\n코드 리뷰 진행."
    decision, target, summary, chain = bc._parse_brain_response(response)
    assert decision == "CHAIN"
    assert target == "codex"
    assert chain is not None
    assert "후속" in chain


def test_parse_escalate():
    response = "ESCALATE\n결과 파일에 오류가 있어 사용자 판단이 필요합니다."
    decision, target, summary, chain = bc._parse_brain_response(response)
    assert decision == "ESCALATE"
    assert target is None
    assert chain is None
    assert "오류" in summary


# ── 일일 한도 테스트 ─────────────────────────────────────────────────────────

def test_daily_limit():
    """30회 초과 시 _check_brain_daily_limit()가 False를 반환해야 함."""
    # 상태 직접 조작
    original_count = bc._brain_call_count
    original_date  = bc._brain_call_date
    try:
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        bc._brain_call_count = bc.MAX_DAILY_BRAIN_CALLS
        bc._brain_call_date  = today

        assert bc._check_brain_daily_limit() is False

        # 29회일 때는 허용
        bc._brain_call_count = bc.MAX_DAILY_BRAIN_CALLS - 1
        assert bc._check_brain_daily_limit() is True
    finally:
        bc._brain_call_count = original_count
        bc._brain_call_date  = original_date


def test_daily_limit_run_brain_callback():
    """run_brain_callback이 한도 초과 시 ESCALATE를 반환해야 함."""
    original_count = bc._brain_call_count
    original_date  = bc._brain_call_date
    try:
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        bc._brain_call_count = bc.MAX_DAILY_BRAIN_CALLS
        bc._brain_call_date  = today

        result = bc.run_brain_callback("claude_code", "테스트 내용", chain_depth=0)
        assert result["decision"] == "ESCALATE"
        assert result["success"] is False
        assert result["error"] == "daily_limit_exceeded"
    finally:
        bc._brain_call_count = original_count
        bc._brain_call_date  = original_date


# ── 체인 깊이 한도 테스트 ─────────────────────────────────────────────────────

def test_chain_depth_limit():
    """depth >= MAX_CHAIN_DEPTH 시 run_brain_callback이 ESCALATE 반환."""
    result = bc.run_brain_callback(
        "claude_code",
        "테스트 from_ 내용",
        chain_depth=bc.MAX_CHAIN_DEPTH,
    )
    assert result["decision"] == "ESCALATE"
    assert result["success"] is True
    assert "깊이" in result["summary"] or "ESCALATE" in result["summary"] or "초과" in result["summary"]


# ── 중복 응답 감지 테스트 ─────────────────────────────────────────────────────

def test_duplicate_response():
    """task_bridge._handle_brain_decision이 동일 summary를 두 번 받으면 ESCALATE로 전환."""
    import task_bridge as tb

    # 상태 초기화
    original_hash = tb._last_cb_summary_hash
    captured_calls = []

    def mock_send_telegram(text):
        captured_calls.append(text)

    original_send = tb._send_telegram
    tb._send_telegram = mock_send_telegram

    try:
        # 첫 번째 DONE 콜백 — 정상 처리
        cb1 = {"decision": "DONE", "target_engine": None, "summary": "동일한 요약", "chain_content": None, "success": True, "error": None}
        tb._handle_brain_decision(cb1, chain_depth=0, state={})
        assert any("DONE" in c for c in captured_calls), "첫 번째 DONE이 TG로 보내져야 함"

        # 두 번째 DONE — 동일 summary, ESCALATE로 강제 전환되어야 함
        captured_calls.clear()
        cb2 = {"decision": "DONE", "target_engine": None, "summary": "동일한 요약", "chain_content": None, "success": True, "error": None}
        tb._handle_brain_decision(cb2, chain_depth=0, state={})
        assert any("ESCALATE" in c for c in captured_calls), "동일 응답 반복 시 ESCALATE로 강제되어야 함"
    finally:
        tb._send_telegram = original_send
        tb._last_cb_summary_hash = original_hash
