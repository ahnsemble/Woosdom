"""Sprint 7 E2E 안정성 검증 — inject_agent_spec 통합 테스트.

단위 테스트(test_spec_injection.py)는 tmp_path에 샘플 스펙을 생성해서 사용.
이 E2E 테스트는 실제 VAULT_ROOT의 에이전트 스펙 파일(00_System/Specs/agents/)을 사용.

E1. @eng-foreman T1 풀 스펙 정상 주입
E2. @없는 하위호환 (입력 == 출력)
E3. @eng-engineer T2 차등 주입 (Identity, Rules, Thinking Framework만)
E4. @eng-forman-typo fallback + TG 경고 캡처
E5. spec_injection.log OK/FALLBACK 기록 검증
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(__file__))

import task_bridge as tb

VAULT_ROOT = "/Users/woosung/Desktop/Dev/Woosdom_Brain"


@pytest.fixture(autouse=True)
def e2e_env(tmp_path, monkeypatch):
    """실제 VAULT_ROOT 스펙 파일 사용, 로그는 tmp로 격리, TG 차단."""
    # 실제 VAULT_ROOT 사용 (스펙 파일 읽기)
    monkeypatch.setattr(tb, "VAULT_ROOT", VAULT_ROOT)

    # 로그 파일은 tmp_path로 격리 (실제 로그 오염 방지)
    log_path = str(tmp_path / "spec_injection.log")
    monkeypatch.setattr(tb, "SPEC_LOG_PATH", log_path)

    # TG 발송 차단 (기본)
    monkeypatch.setattr(tb, "_send_telegram", lambda text: None)

    return {"log_path": log_path}


# ── E1: @eng-foreman T1 풀 스펙 정상 주입 ─────────────────────────────────────

def test_e1_t1_full_spec_injection(e2e_env):
    """실제 eng-foreman.md에서 풀 스펙이 주입되는지 확인."""
    result = tb.inject_agent_spec("@eng-foreman 간단한 테스트 작업")

    # 헤더 확인
    assert "## Agent Role: eng-foreman" in result

    # 실제 스펙 내용 포함 (eng-foreman.md의 실제 텍스트)
    assert "Google SRE" in result                  # Identity 섹션
    assert "## 2. Expertise" in result             # T1이므로 풀 스펙
    assert "## 7. Delegation Map" in result        # T1이므로 풀 스펙
    assert "## 8. Rules" in result                 # Rules 섹션

    # 원본 작업 보존
    assert "간단한 테스트 작업" in result

    # @mention 제거됨
    assert "@eng-foreman" not in result


# ── E2: 하위호환 (@없는 기존 방식) ────────────────────────────────────────────

def test_e2_backward_compat(e2e_env):
    """@없는 기존 작업 → 입력과 출력이 완전히 동일."""
    content = "기존 방식으로 작업합니다"
    result = tb.inject_agent_spec(content)

    assert result == content


# ── E3: @eng-engineer T2 차등 주입 ────────────────────────────────────────────

def test_e3_t2_differential_injection(e2e_env):
    """eng-engineer(T1_AGENTS 미포함) → Identity, Rules, Thinking Framework만 주입."""
    result = tb.inject_agent_spec("@eng-engineer 테스트 작업")

    # 코어 섹션 포함
    assert "## 1. Identity" in result
    assert "Meta" in result                        # eng-engineer Identity 실제 내용
    assert "## 8. Rules" in result
    assert "Thinking Framework" in result

    # 비코어 섹션 제외
    assert "## 2. Expertise" not in result
    assert "## 7. Delegation Map" not in result

    # 원본 작업 보존 + @mention 제거
    assert "테스트 작업" in result
    assert "@eng-engineer" not in result


# ── E4: fallback + TG 경고 ───────────────────────────────────────────────────

def test_e4_fallback_tg_warning(e2e_env, monkeypatch):
    """@eng-forman-typo → 스펙 주입 없이 원본 반환 + TG 경고 캡처."""
    tg_calls = []
    monkeypatch.setattr(tb, "_send_telegram", lambda text: tg_calls.append(text))

    result = tb.inject_agent_spec("@eng-forman-typo 오타 테스트")

    # 스펙 주입 없이 원본만 반환
    assert "오타 테스트" in result
    assert "## Agent Role:" not in result
    assert "@eng-forman-typo" not in result

    # TG 경고 발송 확인 (실제 발송은 아님)
    assert len(tg_calls) == 1
    assert "스펙 파일 없음" in tg_calls[0]
    assert "eng-forman-typo" in tg_calls[0]


# ── E5: spec_injection.log 검증 ──────────────────────────────────────────────

def test_e5_log_verification(e2e_env, monkeypatch):
    """E1~E4 시나리오 실행 후 로그에 OK/FALLBACK 모두 기록되는지 확인."""
    log_path = e2e_env["log_path"]
    monkeypatch.setattr(tb, "_send_telegram", lambda text: None)

    # OK 케이스: T1 정상 주입
    tb.inject_agent_spec("@eng-foreman 로그 테스트 작업")
    # FALLBACK 케이스: 존재하지 않는 에이전트
    tb.inject_agent_spec("@nonexistent-agent-xyz 로그 테스트")

    assert os.path.exists(log_path), "spec_injection.log가 생성되어야 함"

    with open(log_path, "r", encoding="utf-8") as f:
        log_content = f.read()

    # OK 상태 기록
    assert "agent=eng-foreman" in log_content
    assert "status=OK" in log_content
    assert "length=" in log_content
    assert "--- injected content" in log_content

    # FALLBACK 상태 기록
    assert "agent=nonexistent-agent-xyz" in log_content
    assert "status=FALLBACK" in log_content
