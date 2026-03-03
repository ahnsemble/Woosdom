"""Sprint 8 Phase 1 — Agent Chaining 테스트.

테스트 시나리오:
1. 정상 체인: 위임 블록 파싱 + Delegation Map 검증 통과
2. 깊이 초과: depth=3에서 위임 시도 → 거부
3. 순환 감지: visited에 있는 agent → 거부
4. 무권한 위임: Delegation Map에 없는 agent → 거부
5. 오탐 방지: 코드블록 내 위임 블록 → 무시
6. 실패 중단: YAML 파싱 실패 → fail closed
7. 로그 검증: chain_execution.log 기록 확인
"""
import os
import sys
import json
import pytest

sys.path.insert(0, os.path.dirname(__file__))

import task_bridge as tb


# ── 공통 픽스처 ────────────────────────────────────────────────────────────────

FOREMAN_SPEC = """\
# Agent Spec: Foreman
---
id: eng-foreman
tier: T1
---

## 1. Identity

Foreman identity.

## 7. Delegation Map

```yaml
delegates_to:
  - agent: "eng-engineer"
    when: "코드 작성/수정 실행"
    via: "claude_code"
  - agent: "eng-critic"
    when: "코드 리뷰 필요"
    via: "claude_code"
escalates_to:
  - agent: "brain"
    when: "금융 파일 접근"
```

## 8. Rules

### Hard Rules
- 금융 파일 수정 금지
"""

ENGINEER_SPEC = """\
# Agent Spec: Engineer
---
id: eng-engineer
tier: T2
---

## 1. Identity

Engineer identity.
"""


@pytest.fixture
def chain_env(tmp_path, monkeypatch):
    """체인 테스트용 환경 설정."""
    agents_dir = tmp_path / "00_System" / "Specs" / "agents"
    agents_dir.mkdir(parents=True)
    logs_dir = tmp_path / "00_System" / "Logs"
    logs_dir.mkdir(parents=True)
    templates_dir = tmp_path / "00_System" / "Templates"
    templates_dir.mkdir(parents=True)

    # 스펙 파일 생성
    (agents_dir / "eng-foreman.md").write_text(FOREMAN_SPEC, encoding="utf-8")
    (agents_dir / "eng-engineer.md").write_text(ENGINEER_SPEC, encoding="utf-8")

    # to_claude_code.md 빈 파일 생성
    (templates_dir / "to_claude_code.md").write_text("", encoding="utf-8")

    # 모듈 전역 변수 패치
    monkeypatch.setattr(tb, "VAULT_ROOT", str(tmp_path))
    monkeypatch.setattr(tb, "CHAIN_LOG_PATH",
                        str(logs_dir / "chain_execution.log"))
    monkeypatch.setattr(tb, "SPEC_LOG_PATH",
                        str(logs_dir / "spec_injection.log"))
    # WATCH_FILES 패치 — to_claude_code.md 경로 맞추기
    watch_to = dict(tb.WATCH_FILES["to"])
    watch_to["claude_code"] = str(templates_dir / "to_claude_code.md")
    monkeypatch.setattr(tb, "WATCH_FILES", {
        "to": watch_to,
        "from": tb.WATCH_FILES["from"],
    })
    # TG 발송 차단 (호출 기록용)
    tg_calls = []
    monkeypatch.setattr(tb, "_send_telegram", lambda text: tg_calls.append(text))

    return {"tmp_path": tmp_path, "tg_calls": tg_calls, "logs_dir": logs_dir}


# ── 테스트 1: 정상 체인 (위임 블록 파싱 + 검증 통과) ──────────────────────────────

def test_1_normal_chain(chain_env):
    """Foreman → Engineer 위임 블록 파싱 + Delegation Map 검증 통과."""
    from_content = """\
## 작업 결과
코드 분석 완료. Engineer에게 실제 구현을 위임합니다.

---woosdom-delegation---
delegate_to: eng-engineer
task: "task_bridge.py에 에러 핸들링 추가"
reason: "코드 수정 작업이므로 Engineer에게 위임"
---end-delegation---
"""
    # parse_delegation_block
    block = tb.parse_delegation_block(from_content)
    assert block is not None
    assert block["delegate_to"] == "eng-engineer"
    assert "에러 핸들링" in block["task"]

    # validate_delegation
    valid, reason = tb.validate_delegation(
        source_agent="eng-foreman",
        target_agent="eng-engineer",
        chain_visited=["eng-foreman"],
        chain_depth=1,
    )
    assert valid is True
    assert reason == "OK"


# ── 테스트 2: 깊이 초과 (depth=3에서 거부) ──────────────────────────────────────

def test_2_depth_exceeded(chain_env):
    """chain_depth >= MAX_CHAIN_DEPTH(3) → 위임 거부."""
    valid, reason = tb.validate_delegation(
        source_agent="eng-foreman",
        target_agent="eng-engineer",
        chain_visited=["eng-foreman", "eng-critic"],
        chain_depth=3,
    )
    assert valid is False
    assert "깊이 초과" in reason


# ── 테스트 3: 순환 감지 (visited에 있는 agent 거부) ──────────────────────────────

def test_3_cycle_detected(chain_env):
    """visited에 이미 포함된 agent로 위임 시도 → 순환 거부."""
    valid, reason = tb.validate_delegation(
        source_agent="eng-foreman",
        target_agent="eng-engineer",
        chain_visited=["eng-foreman", "eng-engineer"],  # 이미 방문
        chain_depth=1,
    )
    assert valid is False
    assert "순환 감지" in reason
    assert "eng-engineer" in reason


# ── 테스트 4: 무권한 위임 (Delegation Map에 없는 agent 거부) ─────────────────────

def test_4_unauthorized_delegation(chain_env):
    """Foreman의 Delegation Map에 없는 agent → 위임 거부."""
    valid, reason = tb.validate_delegation(
        source_agent="eng-foreman",
        target_agent="res-web-scout",  # Foreman Map에 없음
        chain_visited=["eng-foreman"],
        chain_depth=1,
    )
    assert valid is False
    assert "위임 권한 없음" in reason


# ── 테스트 5: 오탐 방지 (코드블록 내 위임 블록 무시) ─────────────────────────────

def test_5_false_positive_code_block(chain_env):
    """코드블록(```) 내부의 위임 블록은 무시되어야 함."""
    from_content = """\
## 구현 가이드

다음은 위임 블록 예시입니다:

```yaml
---woosdom-delegation---
delegate_to: eng-engineer
task: "이건 예시"
reason: "문서용"
---end-delegation---
```

위 예시를 참고하세요.
"""
    block = tb.parse_delegation_block(from_content)
    assert block is None  # 코드블록 내부이므로 무시


# ── 테스트 6: 실패 중단 (YAML 파싱 실패 → fail closed) ──────────────────────────

def test_6_yaml_parse_failure(chain_env):
    """위임 블록의 YAML이 잘못되면 fail closed (None 반환) + TG 경고."""
    from_content = """\
## 결과

---woosdom-delegation---
delegate_to: eng-engineer
task: [invalid yaml: {{{
reason: broken
---end-delegation---
"""
    block = tb.parse_delegation_block(from_content)
    assert block is None  # fail closed

    # TG 경고 발송 확인
    tg_calls = chain_env["tg_calls"]
    assert any("YAML 파싱 실패" in msg for msg in tg_calls)


# ── 테스트 7: 로그 검증 (chain_execution.log 기록 확인) ──────────────────────────

def test_7_chain_log(chain_env):
    """chain_dispatch 성공 시 chain_execution.log에 기록 확인."""
    log_path = str(chain_env["logs_dir"] / "chain_execution.log")

    # 기존 로그 제거
    if os.path.exists(log_path):
        os.remove(log_path)

    # chain_dispatch 실행
    chain_meta = {
        "chain_id": "test-abc123",
        "depth": 0,
        "visited": ["eng-foreman"],
        "origin": "테스트 작업",
    }
    state = {
        "to_claude_code": {
            "hash": "",
            "mtime": 0.0,
        }
    }
    success = tb.chain_dispatch(
        target_agent="eng-engineer",
        task="에러 핸들링 추가",
        prev_result="이전 결과 텍스트",
        chain_meta=chain_meta,
        state=state,
    )
    assert success is True

    # 로그 파일 확인
    assert os.path.exists(log_path)
    log_content = open(log_path, "r", encoding="utf-8").read()
    assert "chain_id=test-abc123" in log_content
    assert "depth=1" in log_content
    assert "agent=eng-engineer" in log_content
    assert "status=DISPATCH" in log_content

    # to_claude_code.md에 내용이 작성되었는지 확인
    to_path = tb.WATCH_FILES["to"]["claude_code"]
    to_content = open(to_path, "r", encoding="utf-8").read()
    assert "eng-engineer" in to_content
    assert "에러 핸들링 추가" in to_content
    assert "이전 결과 텍스트" in to_content
    assert "chain_depth: 1" in to_content


# ── 테스트 8: fallback 파싱 (코드블록으로 감싼 위임 블록) ────────────────────────

def test_8_fallback_codeblock_delegation(chain_env):
    """위임 블록이 코드블록으로 감싸져 있을 때 fallback으로 파싱 성공."""
    from_content = """\
## 작업 결과
분석 완료. Engineer에게 위임합니다.

```
---woosdom-delegation---
delegate_to: eng-engineer
task: "fallback 테스트 작업"
reason: "코드블록 내 위임"
---end-delegation---
```
"""
    block = tb.parse_delegation_block(from_content)
    assert block is not None
    assert block["delegate_to"] == "eng-engineer"
    assert "fallback 테스트" in block["task"]

    # fallback 경고 TG 발송 확인
    tg_calls = chain_env["tg_calls"]
    assert any("fallback 파싱" in msg for msg in tg_calls)


# ── 테스트 9: fallback은 마지막 코드블록만 검사 (중간 코드블록 무시) ──────────────

def test_9_fallback_only_last_codeblock(chain_env):
    """코드 설명 중간의 위임 블록은 무시하고, 마지막 코드블록만 fallback."""
    from_content = """\
## 구현 가이드

예시 코드:

```yaml
---woosdom-delegation---
delegate_to: eng-engineer
task: "이건 설명용 예시"
reason: "문서용"
---end-delegation---
```

실제 코드:

```python
def hello():
    pass
```
"""
    block = tb.parse_delegation_block(from_content)
    assert block is None  # 마지막 코드블록에 위임 블록 없으므로 None


# ── 테스트 10: fallback + 마지막 코드블록에 위임 블록 있는 혼합 케이스 ────────────

def test_10_fallback_mixed_codeblocks(chain_env):
    """여러 코드블록 중 마지막에만 위임 블록이 있을 때 fallback 성공."""
    from_content = """\
## 구현 가이드

```python
def example():
    return 42
```

분석 결과 Engineer에게 위임합니다.

```
---woosdom-delegation---
delegate_to: eng-engineer
task: "혼합 코드블록 테스트"
reason: "마지막 블록에 위임"
---end-delegation---
```
"""
    block = tb.parse_delegation_block(from_content)
    assert block is not None
    assert block["delegate_to"] == "eng-engineer"
    assert "혼합 코드블록" in block["task"]

    tg_calls = chain_env["tg_calls"]
    assert any("fallback 파싱" in msg for msg in tg_calls)


# ── 테스트 11: chain_dispatch 후 state hash/mtime 리셋 검증 ──────────────────

def test_11_chain_dispatch_state_reset(chain_env):
    """chain_dispatch 후 state hash가 빈 문자열, mtime이 0.0으로 리셋되어야 함.

    메인 루프가 hash 불일치로 새 작업을 감지할 수 있도록 보장."""
    chain_meta = {
        "chain_id": "test-reset",
        "depth": 0,
        "visited": ["eng-foreman"],
        "origin": "state 리셋 테스트",
    }
    state = {
        "to_claude_code": {
            "hash": "old_hash_value",
            "mtime": 9999999.0,
        }
    }
    success = tb.chain_dispatch(
        target_agent="eng-engineer",
        task="state 리셋 검증",
        prev_result="이전 결과",
        chain_meta=chain_meta,
        state=state,
    )
    assert success is True
    assert state["to_claude_code"]["hash"] == ""
    assert state["to_claude_code"]["mtime"] == 0.0
