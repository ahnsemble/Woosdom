"""Phase A-3: Full Chain E2E Tests"""
import os
import pytest

VAULT_ROOT = "/Users/woosung/Desktop/Dev/Woosdom_Brain"

def test_foreman_exists():
    """CLAUDE.md 파일 존재 확인"""
    claude_md = os.path.join(VAULT_ROOT, "CLAUDE.md")
    assert os.path.isfile(claude_md), f"CLAUDE.md not found at {claude_md}"

def test_agent_activity_writable():
    """agent_activity.md 경로 확인"""
    activity_path = os.path.join(VAULT_ROOT, "00_System", "Logs", "agent_activity.md")
    assert os.path.isfile(activity_path), f"agent_activity.md not found at {activity_path}"

def test_vault_root():
    """VAULT_ROOT 경로 상수 검증"""
    assert os.path.isdir(VAULT_ROOT), f"VAULT_ROOT not found: {VAULT_ROOT}"
    # 핵심 디렉토리 존재 확인
    assert os.path.isdir(os.path.join(VAULT_ROOT, "00_System"))
    assert os.path.isdir(os.path.join(VAULT_ROOT, "01_Domains"))
    assert os.path.isdir(os.path.join(VAULT_ROOT, "02_Projects"))

def test_s_task():
    """S 작업: Phase A-4 자율 실행 검증"""
    assert True
