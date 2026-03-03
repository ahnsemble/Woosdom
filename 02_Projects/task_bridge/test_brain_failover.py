"""test_brain_failover.py — Sub-Brain failover 테스트.

테스트 목록:
  - test_consecutive_failures_increment : 실패 시 카운터 증가, 성공 시 리셋
  - test_failover_triggers_at_threshold : 3회 연속 실패 시 generate_brain_handoff 호출
  - test_generate_brain_handoff         : 템플릿 치환 + 파일 저장 검증
  - test_get_failover_status            : 상태 dict 정합성 검증
"""
import os
import subprocess
from unittest.mock import patch, MagicMock

import pytest

import brain_callback as bc


@pytest.fixture(autouse=True)
def reset_failure_counter():
    """각 테스트 전후로 카운터 리셋."""
    original = bc._consecutive_failures
    bc._consecutive_failures = 0
    yield
    bc._consecutive_failures = original


# ── 1. 연속 실패 카운터 증가/리셋 ────────────────────────────────────────────

def test_consecutive_failures_increment():
    """returncode != 0 → 카운터 증가, returncode == 0 → 카운터 리셋."""
    failed_proc = MagicMock()
    failed_proc.returncode = 1
    failed_proc.stdout = ""
    failed_proc.stderr = "error"

    success_proc = MagicMock()
    success_proc.returncode = 0
    success_proc.stdout = "DONE\n작업 완료"
    success_proc.stderr = ""

    with patch("subprocess.run") as mock_run, \
         patch.object(bc, "_check_failover_threshold"), \
         patch.object(bc, "_check_brain_daily_limit", return_value=True), \
         patch.object(bc, "_sanitize_env", return_value={}):

        # 2회 연속 실패
        mock_run.return_value = failed_proc
        bc.run_brain_callback("claude_code", "test", chain_depth=0)
        assert bc._consecutive_failures == 1
        bc.run_brain_callback("claude_code", "test", chain_depth=0)
        assert bc._consecutive_failures == 2

        # 1회 성공 → 리셋
        mock_run.return_value = success_proc
        bc.run_brain_callback("claude_code", "test", chain_depth=0)
        assert bc._consecutive_failures == 0


# ── 2. threshold 도달 시 handoff 호출 ────────────────────────────────────────

def test_failover_triggers_at_threshold():
    """3회 연속 실패 시 generate_brain_handoff()가 호출되어야 함."""
    failed_proc = MagicMock()
    failed_proc.returncode = 1
    failed_proc.stdout = ""
    failed_proc.stderr = "error"

    with patch("subprocess.run", return_value=failed_proc), \
         patch.object(bc, "_check_brain_daily_limit", return_value=True), \
         patch.object(bc, "_sanitize_env", return_value={}), \
         patch.object(bc, "generate_brain_handoff", return_value="/tmp/handoff.md") as mock_handoff, \
         patch("task_bridge._send_telegram"):

        for _ in range(bc.FAILOVER_THRESHOLD):
            bc.run_brain_callback("claude_code", "test", chain_depth=0)

        assert mock_handoff.call_count >= 1
        assert bc._consecutive_failures == bc.FAILOVER_THRESHOLD


# ── 3. generate_brain_handoff 템플릿 치환 ────────────────────────────────────

def test_generate_brain_handoff(tmp_path, monkeypatch):
    """템플릿 {{placeholder}} 치환 + brain_handoff.md 저장 검증."""
    # 디렉토리 구조 구성
    templates_dir = tmp_path / "00_System" / "Templates"
    templates_dir.mkdir(parents=True)
    ontology_dir = tmp_path / "00_System" / "Prompts" / "Ontology"
    ontology_dir.mkdir(parents=True)
    memory_dir = tmp_path / "00_System" / "Memory"
    memory_dir.mkdir(parents=True)

    # 템플릿 파일
    (templates_dir / "brain_handoff_template.md").write_text(
        "Generated: {{timestamp}}\nContext: {{active_context}}\nMemory: {{conversation_memory}}",
        encoding="utf-8",
    )
    # 컨텍스트 파일
    (ontology_dir / "active_context.md").write_text("현재 S-3 진행 중", encoding="utf-8")
    (memory_dir / "conversation_memory.md").write_text("대화 기억 내용", encoding="utf-8")

    # VAULT_ROOT를 tmp_path로 교체
    monkeypatch.setattr("brain_callback.VAULT_ROOT", str(tmp_path),
                        raising=False)

    with patch("task_bridge.VAULT_ROOT", str(tmp_path)):
        output_path = bc.generate_brain_handoff()

    assert os.path.exists(output_path)
    content = open(output_path, "r", encoding="utf-8").read()
    assert "{{timestamp}}" not in content
    assert "{{active_context}}" not in content
    assert "{{conversation_memory}}" not in content
    assert "현재 S-3 진행 중" in content
    assert "대화 기억 내용" in content


# ── 4. get_failover_status dict 검증 ─────────────────────────────────────────

def test_get_failover_status():
    """get_failover_status()가 올바른 dict를 반환하는지 검증."""
    # 초기 상태 (리셋됨)
    status = bc.get_failover_status()
    assert status["consecutive_failures"] == 0
    assert status["threshold"] == bc.FAILOVER_THRESHOLD
    assert status["failover_triggered"] is False

    # 카운터 수동 설정
    bc._consecutive_failures = bc.FAILOVER_THRESHOLD
    status = bc.get_failover_status()
    assert status["consecutive_failures"] == bc.FAILOVER_THRESHOLD
    assert status["failover_triggered"] is True
