"""Sprint 7 Phase 1 — inject_agent_spec() 테스트.

테스트 시나리오:
1. 정상: @eng-foreman 작업 → T1 풀 스펙 주입 확인
2. 오타: @eng-forman 작업 → fallback 동작 + TG 경고
3. @없음: 그냥 작업 → 기존 동작 유지 (하위 호환)
4. T1 vs T2: @eng-foreman(T1 풀) vs @eng-engineer(T2 코어) 주입 확인
5. 로그: spec_injection.log에 주입 내용 기록 확인
"""
import os
import sys
import pytest

# task_bridge 모듈 경로 추가
sys.path.insert(0, os.path.dirname(__file__))

import task_bridge as tb


# ── 공통 픽스처 ────────────────────────────────────────────────────────────────

SAMPLE_SPEC_FULL = """\
# Agent Spec: Foreman
---
id: eng-foreman
tier: T1
---

## 1. Identity

Foreman identity section content here.

## 2. Expertise

Foreman expertise section content here.

## 3. Rules

Foreman rules section content here.

## 4. Thinking Framework

Foreman thinking framework content here.

## 5. Delegation Map

Foreman delegation map content here.
"""

SAMPLE_SPEC_T2 = """\
# Agent Spec: Engineer
---
id: eng-engineer
tier: T1
---

## 1. Identity

Engineer identity section content here.

## 2. Expertise

Engineer expertise section content here.

## 3. Rules

Engineer rules section content here.

## 4. Thinking Framework

Engineer thinking framework content here.

## 5. Delegation Map

Engineer delegation map content here.
"""


@pytest.fixture
def spec_env(tmp_path, monkeypatch):
    """에이전트 스펙 디렉토리를 tmp_path에 설정."""
    agents_dir = tmp_path / "00_System" / "Specs" / "agents"
    agents_dir.mkdir(parents=True)
    logs_dir = tmp_path / "00_System" / "Logs"
    logs_dir.mkdir(parents=True)

    # eng-foreman.md 생성 (T1)
    (agents_dir / "eng-foreman.md").write_text(SAMPLE_SPEC_FULL, encoding="utf-8")
    # eng-engineer.md 생성 (T1 tier이지만 T1_AGENTS 세트에는 미포함 → 코어만 주입)
    (agents_dir / "eng-engineer.md").write_text(SAMPLE_SPEC_T2, encoding="utf-8")

    # 모듈 전역 변수 패치
    monkeypatch.setattr(tb, "VAULT_ROOT", str(tmp_path))
    monkeypatch.setattr(tb, "SPEC_LOG_PATH",
                        str(logs_dir / "spec_injection.log"))
    # TG 발송 차단
    monkeypatch.setattr(tb, "_send_telegram", lambda text: None)

    return tmp_path


# ── 테스트 1: 정상 주입 (T1 풀 스펙) ────────────────────────────────────────────

def test_1_normal_t1_injection(spec_env):
    """@eng-foreman 작업 → T1 에이전트이므로 풀 스펙 주입 확인."""
    content = "@eng-foreman task_bridge에 에러 핸들링 추가해"
    result = tb.inject_agent_spec(content)

    # 풀 스펙이 주입되어야 함
    assert "## Agent Role: eng-foreman" in result
    assert "Foreman identity section content here." in result
    assert "Foreman expertise section content here." in result
    assert "Foreman delegation map content here." in result
    # 원본 작업이 포함되어야 함
    assert "task_bridge에 에러 핸들링 추가해" in result
    # @mention이 제거되어야 함
    assert "@eng-foreman" not in result


# ── 테스트 2: 오타 → fallback + TG 경고 ─────────────────────────────────────────

def test_2_typo_fallback(spec_env, monkeypatch):
    """@eng-forman (오타) → 스펙 파일 없으므로 fallback + TG 경고."""
    tg_calls = []
    monkeypatch.setattr(tb, "_send_telegram", lambda text: tg_calls.append(text))

    content = "@eng-forman task_bridge 수정해"
    result = tb.inject_agent_spec(content)

    # @제거 후 원본 작업만 반환
    assert "task_bridge 수정해" in result
    assert "@eng-forman" not in result
    # 스펙 주입 없어야 함
    assert "## Agent Role:" not in result
    # TG 경고 발송
    assert len(tg_calls) == 1
    assert "스펙 파일 없음" in tg_calls[0]
    assert "eng-forman" in tg_calls[0]


# ── 테스트 3: @없음 → 기존 동작 유지 (하위 호환) ─────────────────────────────────

def test_3_no_mention_passthrough(spec_env):
    """@없는 기존 작업 → content 그대로 반환 (100% 하위 호환)."""
    content = "그냥 task_bridge에 에러 핸들링 추가해"
    result = tb.inject_agent_spec(content)

    assert result == content  # 완전히 동일


# ── 테스트 4: T1 vs T2 (풀 vs 코어 주입) ─────────────────────────────────────────

def test_4_t1_vs_t2_injection(spec_env):
    """T1(@eng-foreman)은 풀 스펙, T2(@eng-engineer)는 코어만 주입."""
    # T1: eng-foreman — 풀 스펙
    t1_result = tb.inject_agent_spec("@eng-foreman 작업 실행")
    assert "Foreman delegation map content here." in t1_result  # 풀 스펙의 섹션 5
    assert "Foreman expertise section content here." in t1_result  # 풀 스펙의 섹션 2

    # T2: eng-engineer — T1_AGENTS에 없으므로 코어만 (Identity, Rules, Thinking)
    t2_result = tb.inject_agent_spec("@eng-engineer 작업 실행")
    assert "Engineer identity section content here." in t2_result     # Identity ✓
    assert "Engineer rules section content here." in t2_result         # Rules ✓
    assert "Engineer thinking framework content here." in t2_result    # Thinking ✓
    assert "Engineer expertise section content here." not in t2_result  # Expertise ✗ (코어 아님)
    assert "Engineer delegation map content here." not in t2_result     # Delegation ✗ (코어 아님)


# ── 테스트 5: spec_injection.log 기록 확인 ────────────────────────────────────────

def test_5_log_written(spec_env):
    """inject_agent_spec() 호출 시 spec_injection.log에 기록 확인."""
    log_path = str(spec_env / "00_System" / "Logs" / "spec_injection.log")

    # 기존 로그 제거
    if os.path.exists(log_path):
        os.remove(log_path)

    # 정상 주입 → OK 로그
    tb.inject_agent_spec("@eng-foreman 작업 실행")
    assert os.path.exists(log_path), "로그 파일이 생성되어야 함"

    log_content = open(log_path, "r", encoding="utf-8").read()
    assert "agent=eng-foreman" in log_content
    assert "status=OK" in log_content
    assert "length=" in log_content
    assert "--- injected content" in log_content

    # fallback → FALLBACK 로그
    tb.inject_agent_spec("@nonexistent-agent 작업 실행")
    log_content = open(log_path, "r", encoding="utf-8").read()
    assert "agent=nonexistent-agent" in log_content
    assert "status=FALLBACK" in log_content
