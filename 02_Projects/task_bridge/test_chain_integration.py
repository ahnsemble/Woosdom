"""Sprint 8 E2E-B: 체인 코드 경로 통합 테스트.

실제 task_bridge.py 함수를 import하여 실제 파일 I/O와 함께 검증.
pytest 단위 테스트(test_agent_chaining.py)와 달리, 실제 에이전트 스펙 파일을
읽고 실제 디렉토리에 파일을 쓰는 통합 테스트.

테스트 시나리오:
  1. parse_delegation_block() — 위임 블록 파싱 (delegate_to, task, reason)
  2. validate_delegation() — Foreman→Engineer 위임 승인 (실제 스펙 파일)
  3. validate_delegation() — Foreman→fin-quant 위임 거부 (무권한)
  4. validate_delegation() — 순환 감지 (visited에 포함된 agent)
  5. chain_dispatch() — to_claude_code.md에 체인 메타데이터 + 지시서 작성
  6. chain_execution.log 생성 확인
  7. 코드블록 내 위임 블록 오탐 방지
"""
import os
import sys
import json
import tempfile
import shutil

# task_bridge.py가 있는 디렉토리를 path에 추가
BRIDGE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BRIDGE_DIR)

# task_bridge import 전에 의존 모듈 stub 처리
# (redis, runner, brain_callback, cost_monitor는 통합 테스트 범위 밖)
import types

for mod_name in ("redis_schema", "hands3_runner", "codex_runner",
                 "gemini_runner", "brain_callback", "cost_monitor"):
    if mod_name not in sys.modules:
        sys.modules[mod_name] = types.ModuleType(mod_name)

# stub 함수들 — import 시 AttributeError 방지
sys.modules["redis_schema"].get_redis = lambda: None
sys.modules["redis_schema"].add_task = lambda *a, **k: "stub"
sys.modules["redis_schema"].complete_task = lambda *a, **k: None
sys.modules["redis_schema"].get_latest_pending = lambda *a, **k: None
sys.modules["hands3_runner"].run_claude_code = lambda *a, **k: {"success": True, "elapsed_seconds": 0, "output": ""}
sys.modules["codex_runner"].run_codex = lambda *a, **k: {"success": True, "elapsed_seconds": 0, "output": ""}
sys.modules["gemini_runner"].run_gemini = lambda *a, **k: {"success": True, "elapsed_seconds": 0, "output": ""}
sys.modules["brain_callback"].run_brain_callback = lambda *a, **k: {"decision": "DONE", "summary": ""}
sys.modules["brain_callback"]._check_brain_daily_limit = lambda: True
sys.modules["cost_monitor"].record_engine_run = lambda *a, **k: None
sys.modules["cost_monitor"].record_brain_callback = lambda *a, **k: None
sys.modules["cost_monitor"].record_dangerous_block = lambda *a, **k: None
sys.modules["cost_monitor"].get_daily_summary = lambda: ""

import task_bridge as tb

# ── 설정 ──────────────────────────────────────────────────────────────────────
VAULT_ROOT = "/Users/woosung/Desktop/Dev/Woosdom_Brain"
RESULTS = []
tg_log = []  # _send_telegram 호출 기록


def _fake_send_telegram(text: str):
    """TG 발송 차단 — 로그만 기록."""
    tg_log.append(text)
    print(f"  [TG stub] {text[:80]}...")


def log_result(name: str, passed: bool, detail: str = ""):
    status = "PASS" if passed else "FAIL"
    RESULTS.append((name, status, detail))
    icon = "✅" if passed else "❌"
    print(f"  {icon} {name}: {status}" + (f" — {detail}" if detail else ""))


# ── 환경 준비 ─────────────────────────────────────────────────────────────────
def setup_integration_env():
    """통합 테스트용 임시 환경 구성.

    실제 에이전트 스펙 파일은 원본을 읽되,
    to_/from_ 파일과 로그는 임시 디렉토리에 작성.
    """
    tmp_dir = tempfile.mkdtemp(prefix="chain_integ_")

    # 임시 디렉토리에 필요한 구조 생성
    templates_dir = os.path.join(tmp_dir, "00_System", "Templates")
    logs_dir = os.path.join(tmp_dir, "00_System", "Logs")
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

    # 빈 to_claude_code.md 생성
    to_cc_path = os.path.join(templates_dir, "to_claude_code.md")
    with open(to_cc_path, "w", encoding="utf-8") as f:
        f.write("")

    # 실제 스펙 파일 경로 유지를 위해 스펙 디렉토리를 tmp에 심볼릭 링크
    real_specs = os.path.join(VAULT_ROOT, "00_System", "Specs")
    tmp_specs = os.path.join(tmp_dir, "00_System", "Specs")
    os.symlink(real_specs, tmp_specs)

    return tmp_dir, templates_dir, logs_dir, to_cc_path


def patch_globals(tmp_dir, templates_dir, logs_dir):
    """task_bridge 전역 변수를 임시 디렉토리로 패치."""
    originals = {
        "VAULT_ROOT": tb.VAULT_ROOT,
        "CHAIN_LOG_PATH": tb.CHAIN_LOG_PATH,
        "SPEC_LOG_PATH": tb.SPEC_LOG_PATH,
        "WATCH_FILES": tb.WATCH_FILES,
        "_send_telegram": tb._send_telegram,
    }

    tb.VAULT_ROOT = tmp_dir
    tb.CHAIN_LOG_PATH = os.path.join(logs_dir, "chain_execution.log")
    tb.SPEC_LOG_PATH = os.path.join(logs_dir, "spec_injection.log")

    to_cc_path = os.path.join(templates_dir, "to_claude_code.md")
    tb.WATCH_FILES = {
        "to": {
            "antigravity": originals["WATCH_FILES"]["to"]["antigravity"],
            "codex": originals["WATCH_FILES"]["to"]["codex"],
            "claude_code": to_cc_path,
        },
        "from": originals["WATCH_FILES"]["from"],
    }
    tb._send_telegram = _fake_send_telegram

    return originals


def restore_globals(originals):
    """원래 전역 변수 복원."""
    tb.VAULT_ROOT = originals["VAULT_ROOT"]
    tb.CHAIN_LOG_PATH = originals["CHAIN_LOG_PATH"]
    tb.SPEC_LOG_PATH = originals["SPEC_LOG_PATH"]
    tb.WATCH_FILES = originals["WATCH_FILES"]
    tb._send_telegram = originals["_send_telegram"]


# ── 테스트 실행 ───────────────────────────────────────────────────────────────

def run_tests():
    print("=" * 60)
    print("Sprint 8 E2E-B: 체인 코드 경로 통합 테스트")
    print("=" * 60)

    # 환경 준비
    tmp_dir, templates_dir, logs_dir, to_cc_path = setup_integration_env()
    originals = patch_globals(tmp_dir, templates_dir, logs_dir)
    tg_log.clear()

    try:
        # ── 테스트 1: parse_delegation_block — 위임 블록 파싱 ─────────────
        print("\n[Test 1] parse_delegation_block — 위임 블록 파싱")
        from_content = """\
## 작업 결과
코드 분석 완료. Engineer에게 실제 구현을 위임합니다.

---woosdom-delegation---
delegate_to: eng-engineer
task: "task_bridge.py에 에러 핸들링 추가"
reason: "코드 수정 작업이므로 Engineer에게 위임"
---end-delegation---
"""
        block = tb.parse_delegation_block(from_content)
        try:
            assert block is not None, "파싱 결과가 None"
            assert block["delegate_to"] == "eng-engineer", f"delegate_to={block.get('delegate_to')}"
            assert "에러 핸들링" in block["task"], f"task={block.get('task')}"
            assert "reason" in block, "reason 필드 없음"
            log_result("parse_delegation_block",
                       True,
                       f"delegate_to={block['delegate_to']}, task={block['task'][:30]}...")
        except AssertionError as e:
            log_result("parse_delegation_block", False, str(e))

        # ── 테스트 2: validate_delegation — Foreman→Engineer 승인 ─────────
        print("\n[Test 2] validate_delegation — Foreman→Engineer 위임 승인")
        try:
            valid, reason = tb.validate_delegation(
                source_agent="eng-foreman",
                target_agent="eng-engineer",
                chain_visited=["eng-foreman"],
                chain_depth=1,
            )
            assert valid is True, f"valid={valid}, reason={reason}"
            assert reason == "OK", f"reason={reason}"
            log_result("validate_delegation (Foreman→Engineer)", True, reason)
        except (AssertionError, Exception) as e:
            log_result("validate_delegation (Foreman→Engineer)", False, str(e))

        # ── 테스트 3: validate_delegation — Foreman→fin-quant 거부 ────────
        print("\n[Test 3] validate_delegation — Foreman→fin-quant 거부 (무권한)")
        try:
            valid, reason = tb.validate_delegation(
                source_agent="eng-foreman",
                target_agent="fin-quant",
                chain_visited=["eng-foreman"],
                chain_depth=1,
            )
            assert valid is False, f"expected False, got valid={valid}"
            assert "위임 권한 없음" in reason, f"reason={reason}"
            log_result("validate_delegation (Foreman→fin-quant 거부)",
                       True, reason)
        except (AssertionError, Exception) as e:
            log_result("validate_delegation (Foreman→fin-quant 거부)", False, str(e))

        # ── 테스트 4: validate_delegation — 순환 감지 ─────────────────────
        print("\n[Test 4] validate_delegation — 순환 감지")
        try:
            valid, reason = tb.validate_delegation(
                source_agent="eng-foreman",
                target_agent="eng-engineer",
                chain_visited=["eng-foreman", "eng-engineer"],  # 이미 방문
                chain_depth=1,
            )
            assert valid is False, f"expected False, got valid={valid}"
            assert "순환 감지" in reason, f"reason={reason}"
            log_result("validate_delegation (순환 감지)", True, reason)
        except (AssertionError, Exception) as e:
            log_result("validate_delegation (순환 감지)", False, str(e))

        # ── 테스트 5: chain_dispatch — to_claude_code.md 작성 ─────────────
        print("\n[Test 5] chain_dispatch — to_claude_code.md에 체인 메타데이터 작성")
        chain_log_path = os.path.join(logs_dir, "chain_execution.log")
        if os.path.exists(chain_log_path):
            os.remove(chain_log_path)

        chain_meta = {
            "chain_id": "integ-test-001",
            "depth": 0,
            "visited": ["eng-foreman"],
            "origin": "Sprint 8 E2E-B 통합 테스트",
        }
        state = {
            "to_claude_code": {
                "hash": "",
                "mtime": 0.0,
            }
        }
        try:
            success = tb.chain_dispatch(
                target_agent="eng-engineer",
                task="task_bridge.py에 에러 핸들링 추가",
                prev_result="이전 단계에서 코드 분석을 완료했습니다. 누락된 에러 핸들링 목록: [1] _read_file, [2] _file_mtime",
                chain_meta=chain_meta,
                state=state,
            )
            assert success is True, "chain_dispatch returned False"

            # to_claude_code.md 내용 검증
            with open(to_cc_path, "r", encoding="utf-8") as f:
                to_content = f.read()
            assert 'chain_id: "integ-test-001"' in to_content, "chain_id 없음"
            assert "chain_depth: 1" in to_content, "chain_depth 없음"
            assert "eng-engineer" in to_content, "target agent 없음"
            assert "에러 핸들링" in to_content, "task 내용 없음"
            assert "이전 단계에서 코드 분석" in to_content, "prev_result 없음"
            # visited 확인
            assert "eng-engineer" in to_content, "visited에 eng-engineer 없음"

            log_result("chain_dispatch → to_claude_code.md",
                       True,
                       f"파일 크기={len(to_content)}B, chain_depth=1 확인")
        except (AssertionError, Exception) as e:
            log_result("chain_dispatch → to_claude_code.md", False, str(e))

        # ── 테스트 6: chain_execution.log 생성 확인 ───────────────────────
        print("\n[Test 6] chain_execution.log 생성 확인")
        try:
            assert os.path.exists(chain_log_path), f"로그 파일 없음: {chain_log_path}"
            with open(chain_log_path, "r", encoding="utf-8") as f:
                log_content = f.read()
            assert "chain_id=integ-test-001" in log_content, "chain_id 없음"
            assert "depth=1" in log_content, "depth 없음"
            assert "agent=eng-engineer" in log_content, "agent 없음"
            assert "status=DISPATCH" in log_content, "status 없음"
            log_result("chain_execution.log 생성",
                       True,
                       f"로그 크기={len(log_content)}B")
        except (AssertionError, Exception) as e:
            log_result("chain_execution.log 생성", False, str(e))

        # ── 테스트 7: 코드블록 내 위임 블록 오탐 방지 ─────────────────────
        print("\n[Test 7] 코드블록 내 위임 블록 오탐 방지")
        code_block_content = """\
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
        try:
            block = tb.parse_delegation_block(code_block_content)
            assert block is None, f"코드블록 내 위임 블록을 파싱함: {block}"
            log_result("코드블록 오탐 방지", True, "None 반환 확인")
        except (AssertionError, Exception) as e:
            log_result("코드블록 오탐 방지", False, str(e))

    finally:
        # 원래 전역 변수 복원
        restore_globals(originals)
        # 임시 디렉토리 정리
        shutil.rmtree(tmp_dir, ignore_errors=True)

    # ── 결과 요약 ─────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("결과 요약")
    print("=" * 60)
    total = len(RESULTS)
    passed = sum(1 for _, s, _ in RESULTS if s == "PASS")
    failed = sum(1 for _, s, _ in RESULTS if s == "FAIL")
    for name, status, detail in RESULTS:
        icon = "✅" if status == "PASS" else "❌"
        print(f"  {icon} {name}: {status}" + (f" — {detail}" if detail else ""))
    print(f"\n총 {total}건: PASS {passed} / FAIL {failed}")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
