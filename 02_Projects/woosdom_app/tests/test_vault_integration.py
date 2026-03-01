"""Phase A-4: Vault Integration Tests (M 작업)"""
import os

VAULT_ROOT = "/Users/woosung/Desktop/Dev/Woosdom_Brain"


def test_active_context_exists():
    """active_context.md 존재 확인"""
    path = os.path.join(VAULT_ROOT, "00_System", "Prompts", "Ontology", "active_context.md")
    assert os.path.isfile(path), f"active_context.md not found at {path}"


def test_brain_directive_exists():
    """brain_directive.md 존재 확인"""
    path = os.path.join(VAULT_ROOT, "00_System", "Prompts", "Ontology", "brain_directive.md")
    assert os.path.isfile(path), f"brain_directive.md not found at {path}"


def test_agent_activity_exists():
    """agent_activity.md 존재 확인"""
    path = os.path.join(VAULT_ROOT, "00_System", "Logs", "agent_activity.md")
    assert os.path.isfile(path), f"agent_activity.md not found at {path}"


def test_portfolio_json_exists():
    """portfolio.json 존재 확인 (읽기만)"""
    path = os.path.join(VAULT_ROOT, "01_Domains", "Finance", "portfolio.json")
    assert os.path.isfile(path), f"portfolio.json not found at {path}"


def test_rules_md_exists():
    """Rules.md 존재 확인 (읽기만)"""
    path = os.path.join(VAULT_ROOT, "01_Domains", "Finance", "Rules.md")
    assert os.path.isfile(path), f"Rules.md not found at {path}"
