"""Woosdom Task Bridge v4.7 — Agent Chaining (Sprint 8 Phase 1).

v4.7 변경 (S-8):
  - parse_delegation_block(): from_ 결과에서 구조화된 위임 블록 파싱
  - validate_delegation(): Delegation Map + visited + depth 검증
  - chain_dispatch(): 체인 메타데이터 갱신 + 컨텍스트 합성 → to_ 작성
  - chain_execution.log: 체인 실행 추적 로그
  - brain_callback.py 연동: from_ 읽은 후 위임 블록 감지 → 자동 체인

v4.6 변경 (S-7):
  - inject_agent_spec(): @agent-id 파싱 → 에이전트 스펙 자동 주입
  - T1 에이전트(7명): 풀 스펙 주입 / T2·T3: Identity+Rules+Thinking만
  - fallback: 스펙 파일 없으면 기존 동작 + TG 경고
  - spec_injection.log 디버깅 로그

v4.5 변경 (S-5):
  - T1: _send_telegram() 3회 재시도 + 지수 백오프 (2s, 4s, 8s)
  - T3: DANGEROUS_PATTERNS 위험 명령 감지/차단
  - T4b: cost_monitor 통합 (엔진 실행/콜백/차단 기록)

v4.4 변경 (S-3):
  - to_ 파일 content 읽은 직후 status:done/complete 감지 시 스킵
  - 동일 to_ 파일이 완료 상태로 재감지되어 엔진 재실행되는 버그 수정

v4.3 변경 (S-1):
  - brain_callback.run_brain_callback() — 엔진 완료 후 Brain 자동 호출
  - DONE → TG 요약 보고, CHAIN → to_[engine].md 기록 후 자동실행 루프에 위임
  - ESCALATE → TG 이유 포함 보고
  - 일일 30회 한도, 최대 체인 깊이 3, 반복 응답 감지(강제 ESCALATE) 포함

v4.2 변경:
  - to_claude_code.md → hands3_runner.run_claude_code() (기존 유지)
  - to_codex.md → codex_runner.run_codex() 자동 실행
  - to_antigravity.md → gemini_runner.run_gemini() 자동 실행
  - 모든 엔진 stdout 터미널 실시간 스트리밍
  - 결과를 from_[engine].md에 자동 기록

실행 방법: python task_bridge.py (터미널에서 직접 실행, launchd 아님)
"""
import os
import re
import time
import uuid
import urllib.request
import json
import hashlib
from datetime import datetime

import yaml
from redis_schema import get_redis, add_task, complete_task, get_latest_pending
from hands3_runner import run_claude_code
from codex_runner import run_codex
from gemini_runner import run_gemini
from brain_callback import run_brain_callback, _check_brain_daily_limit, get_daily_brain_stats
from cost_monitor import record_engine_run, record_brain_callback, record_dangerous_block, get_daily_summary, get_morning_brief

START_TIME = time.time()


def get_version() -> str:
    """현재 Task Bridge 버전 문자열 반환."""
    return "v4.8"


def health_check() -> dict:
    """Bridge 상태 점검. 버전, PID, 업타임, Redis 가용성 반환."""
    redis_available = False
    try:
        get_redis().ping()
        redis_available = True
    except Exception:
        pass
    return {
        "bridge_version": get_version(),
        "pid": os.getpid(),
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "redis_available": redis_available,
    }


def get_status_summary() -> dict:
    """Bridge 상태 + 일일 Brain 호출 수 + 감시 파일 수를 포함한 종합 요약."""
    summary = health_check()
    summary["daily_brain_calls"] = get_daily_brain_stats()["calls_made"]
    summary["watched_files"] = len(WATCH_FILES["to"]) + len(WATCH_FILES["from"])
    return summary


VAULT_ROOT = "/Users/woosung/Desktop/Dev/Woosdom_Brain"
TEMPLATES_DIR = os.path.join(VAULT_ROOT, "00_System", "Templates")

# 엔진별 감시 대상 (to_ = 새 작업, from_ = 완료)
WATCH_FILES = {
    "to": {
        "antigravity": os.path.join(TEMPLATES_DIR, "to_antigravity.md"),
        "codex":       os.path.join(TEMPLATES_DIR, "to_codex.md"),
        "claude_code": os.path.join(TEMPLATES_DIR, "to_claude_code.md"),
    },
    "from": {
        "antigravity": os.path.join(TEMPLATES_DIR, "from_antigravity.md"),
        "codex":       os.path.join(TEMPLATES_DIR, "from_codex.md"),
        "claude_code": os.path.join(TEMPLATES_DIR, "from_claude_code.md"),
    }
}

ENGINE_DISPLAY = {
    "antigravity": "Antigravity",
    "codex":       "Codex",
    "claude_code": "Claude Code",
}


def get_engine_display(engine_key: str) -> str:
    """Return human-readable engine name, falling back to the raw key."""
    return ENGINE_DISPLAY.get(engine_key, engine_key)


POLL_INTERVAL   = 2  # seconds
DEBOUNCE_WINDOW = 5  # 같은 파일에 대한 알림 최소 간격 (초)

# ── 범용 Bridge 로깅 ───────────────────────────────────────────────────────────
BRIDGE_LOG_PATH = os.path.join(VAULT_ROOT, "00_System", "Logs", "bridge.log")
_VALID_LEVELS = {"INFO", "WARN", "ERROR"}


def log_bridge(message: str, level: str = "INFO") -> str:
    """범용 Bridge 로그. 콘솔 + bridge.log에 기록.

    Args:
        message: 로그 메시지
        level: INFO, WARN, ERROR (기본 INFO)

    Returns:
        포맷된 로그 라인 (테스트/디버깅용)
    """
    level = level.upper()
    if level not in _VALID_LEVELS:
        level = "INFO"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [bridge:{level}] {message}"
    print(line)
    try:
        os.makedirs(os.path.dirname(BRIDGE_LOG_PATH), exist_ok=True)
        with open(BRIDGE_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"[bridge] 로그 기록 실패: {e}")
    return line

# Telegram config (기존 n8n 파이프라인과 동일 토큰 사용)
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
TG_CHAT_ID   = os.getenv("TG_CHAT_ID", "")

# ── T3: 위험 명령 패턴 ────────────────────────────────────────────────────────
DANGEROUS_PATTERNS = [
    re.compile(r"\bgit\s+push\b"),
    re.compile(r"\brm\s+-rf\b"),
    re.compile(r"\brm\s+-r\s+/"),
    re.compile(r"\blaunchctl\b"),
    re.compile(r"\bsudo\b"),
    re.compile(r"\bchmod\s+777\b"),
    re.compile(r"\bcurl\b.*\|\s*sh"),
    re.compile(r"\bDROP\s+TABLE\b", re.IGNORECASE),
    re.compile(r"\bDELETE\s+FROM\b", re.IGNORECASE),
]


def _check_dangerous(content: str) -> list[str]:
    """content에서 위험 패턴 매치. 매치된 패턴 문자열 리스트 반환."""
    matched = []
    for pat in DANGEROUS_PATTERNS:
        if pat.search(content):
            matched.append(pat.pattern.replace(r"\b", "").replace(r"\s+", " "))
    return matched


# ── S-7: Spec Pipeline ────────────────────────────────────────────────────────
SPEC_DIR = os.path.join("00_System", "Specs", "agents")
T1_AGENTS = {"cmd-orchestrator", "eng-foreman", "res-scout-lead",
             "cmp-compute-lead", "fin-portfolio-analyst",
             "life-integrator", "car-strategist"}
SPEC_LOG_PATH = os.path.join(VAULT_ROOT, "00_System", "Logs", "spec_injection.log")


def _extract_sections(spec_text: str, sections: list[str]) -> str:
    """## N. 헤더 기반 섹션 추출 (T2/T3 에이전트용 코어 섹션만)."""
    result = []
    for section in sections:
        pattern = rf'(## \d+\. {re.escape(section)}.*?)(?=## \d+\.|$)'
        match = re.search(pattern, spec_text, re.DOTALL)
        if match:
            result.append(match.group(1).strip())
    return "\n\n".join(result)


def _log_spec_injection(agent_id: str, final_content: str | None, status: str = "OK"):
    """spec_injection.log에 주입 기록."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] agent={agent_id} status={status}"
    if final_content:
        entry += f" length={len(final_content)}"
    entry += "\n"
    if status == "OK" and final_content:
        entry += f"--- injected content (first 500 chars) ---\n{final_content[:500]}\n--- end ---\n"
    entry += "\n"
    try:
        os.makedirs(os.path.dirname(SPEC_LOG_PATH), exist_ok=True)
        with open(SPEC_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        print(f"[spec] 로그 기록 실패: {e}")


def inject_agent_spec(task_content: str) -> str:
    """@agent-id 파싱 → 에이전트 스펙 자동 주입.

    - @없으면 원본 반환 (하위 호환)
    - 스펙 파일 없으면 @제거 후 원본 반환 + TG 경고
    - T1 에이전트는 풀 스펙, T2/T3는 코어 섹션(Identity+Rules+Thinking)만 주입
    """
    match = re.search(r'@([\w-]+)\s', task_content)
    if not match:
        return task_content  # @없으면 기존 동작

    agent_id = match.group(1)
    spec_path = os.path.join(VAULT_ROOT, SPEC_DIR, f"{agent_id}.md")

    if not os.path.exists(spec_path):
        _log_spec_injection(agent_id, None, "FALLBACK")
        _send_telegram(f"⚠️ 스펙 파일 없음: {agent_id}. 스펙 없이 실행.")
        # @agent-id 제거 후 기존 실행
        return task_content.replace(f"@{agent_id} ", "", 1)

    spec_text = _read_file(spec_path)

    if agent_id in T1_AGENTS:
        injected = spec_text  # T1: 풀 스펙
    else:
        injected = _extract_sections(spec_text, ["Identity", "Rules", "Thinking Framework"])

    # @agent-id 제거한 원본 작업
    task = task_content.replace(f"@{agent_id} ", "", 1)

    final = f"## Agent Role: {agent_id}\n{injected}\n\n---\n\n## Task\n{task}"
    _log_spec_injection(agent_id, final)
    return final


# ── S-8: Agent Chaining ──────────────────────────────────────────────────────
DELEGATION_BLOCK_RE = re.compile(
    r'---woosdom-delegation---\s*\n(.*?)\n---end-delegation---',
    re.DOTALL,
)
CODE_BLOCK_RE = re.compile(r'```.*?```', re.DOTALL)
CHAIN_LOG_PATH = os.path.join(VAULT_ROOT, "00_System", "Logs", "chain_execution.log")
MAX_CHAIN_CONTEXT = 2000  # 이전 결과 컨텍스트 최대 길이


def _log_chain(chain_id: str, depth: int, agent: str, status: str, detail: str = ""):
    """chain_execution.log에 체인 실행 기록."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] chain_id={chain_id} depth={depth} agent={agent} status={status}"
    if detail:
        entry += f" detail={detail}"
    entry += "\n"
    try:
        os.makedirs(os.path.dirname(CHAIN_LOG_PATH), exist_ok=True)
        with open(CHAIN_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        print(f"[chain] 로그 기록 실패: {e}")


def parse_delegation_block(from_content: str) -> dict | None:
    """from_ 결과에서 구조화된 위임 블록 추출.

    2단계 파싱:
      1차: 코드블록 제거 후 plain text에서 위임 블록 탐색 (오탐 방지)
      2차 (fallback): 1차 실패 시 마지막 코드블록 내부에서 위임 블록 탐색.
           마지막 코드블록만 허용하여 코드 설명 중간의 위임 블록은 무시.

    Returns:
        {"delegate_to": str, "task": str, "reason": str} 또는 None
    """
    # ── 1차: 코드블록 제거 후 파싱 (기존 로직) ──
    cleaned = CODE_BLOCK_RE.sub('', from_content)
    matches = DELEGATION_BLOCK_RE.findall(cleaned)
    if matches:
        if len(matches) > 1:
            _send_telegram("⚠️ 위임 블록 2개 이상 감지. 첫 번째만 사용.")
        try:
            block = yaml.safe_load(matches[0])
            if isinstance(block, dict) and "delegate_to" in block and "task" in block:
                return block
        except yaml.YAMLError:
            _log_chain("N/A", -1, "N/A", "PARSE_FAIL", "YAML 파싱 실패")
            _send_telegram("⚠️ 위임 블록 YAML 파싱 실패. 위임 무시 (fail closed).")
            return None

    # ── 2차 (fallback): 마지막 코드블록 내부에서 위임 블록 탐색 ──
    # 마지막 코드블록이 콘텐츠 끝에 위치할 때만 허용 (설명 중간 코드블록 무시)
    code_block_matches = list(CODE_BLOCK_RE.finditer(from_content))
    if not code_block_matches:
        return None
    last_match = code_block_matches[-1]
    after_last = from_content[last_match.end():].strip()
    if after_last:
        return None  # 마지막 코드블록 뒤에 텍스트가 있으면 설명용으로 판단
    last_block = last_match.group()
    fb_matches = DELEGATION_BLOCK_RE.findall(last_block)
    if not fb_matches:
        return None
    try:
        block = yaml.safe_load(fb_matches[0])
        if isinstance(block, dict) and "delegate_to" in block and "task" in block:
            _send_telegram("⚠️ 위임 블록이 코드블록 내에 있었음 (fallback 파싱)")
            return block
    except yaml.YAMLError:
        _log_chain("N/A", -1, "N/A", "PARSE_FAIL", "YAML 파싱 실패 (fallback)")
        _send_telegram("⚠️ 위임 블록 YAML 파싱 실패. 위임 무시 (fail closed).")
    return None


def _parse_delegation_map(spec_text: str) -> list[str]:
    """에이전트 스펙에서 ## 7. Delegation Map 내 delegates_to 목록 추출.

    Returns:
        허용된 target agent id 리스트
    """
    # ## 7. Delegation Map 섹션 추출
    section_match = re.search(
        r'## 7\. Delegation Map.*?```(?:yaml)?\s*\n(.*?)```',
        spec_text, re.DOTALL,
    )
    if not section_match:
        return []
    try:
        data = yaml.safe_load(section_match.group(1))
        if not isinstance(data, dict):
            return []
        delegates = data.get("delegates_to", [])
        if not isinstance(delegates, list):
            return []
        return [d["agent"] for d in delegates if isinstance(d, dict) and "agent" in d]
    except (yaml.YAMLError, KeyError, TypeError):
        return []


def validate_delegation(source_agent: str, target_agent: str,
                        chain_visited: list[str], chain_depth: int) -> tuple[bool, str]:
    """Delegation Map + visited + depth 검증.

    Returns:
        (valid, reason)
    """
    # 깊이 검사
    if chain_depth >= MAX_CHAIN_DEPTH:
        return False, f"체인 깊이 초과 ({chain_depth}/{MAX_CHAIN_DEPTH})"
    # 순환 검사
    if target_agent in chain_visited:
        return False, f"순환 감지: {target_agent} ∈ {chain_visited}"
    # Delegation Map 검사
    spec_path = os.path.join(VAULT_ROOT, SPEC_DIR, f"{source_agent}.md")
    spec_text = _read_file(spec_path)
    if not spec_text:
        return False, f"소스 에이전트 스펙 없음: {source_agent}"
    allowed = _parse_delegation_map(spec_text)
    if target_agent not in allowed:
        return False, f"{source_agent}→{target_agent} 위임 권한 없음 (allowed={allowed})"
    return True, "OK"


def chain_dispatch(target_agent: str, task: str, prev_result: str,
                   chain_meta: dict, state: dict) -> bool:
    """체인 다음 단계 디스패치. to_claude_code.md에 작업 작성.

    Args:
        target_agent: 위임 대상 에이전트 id
        task: 위임 작업 내용
        prev_result: 이전 단계 from_ 결과
        chain_meta: {"chain_id", "depth", "visited", "origin"}
        state: 메인 루프 상태 dict (hash/mtime 갱신용)

    Returns:
        True if dispatch succeeded, False otherwise
    """
    # 메타데이터 업데이트
    new_depth = chain_meta["depth"] + 1
    new_visited = chain_meta["visited"] + [target_agent]
    context = prev_result[:MAX_CHAIN_CONTEXT]

    # to_ 내용 합성
    content = (
        f"---\n"
        f"chain_id: \"{chain_meta['chain_id']}\"\n"
        f"chain_depth: {new_depth}\n"
        f"chain_visited: {json.dumps(new_visited)}\n"
        f"chain_origin: \"{chain_meta['origin']}\"\n"
        f"---\n\n"
        f"@{target_agent} [체인 #{new_depth}]\n\n"
        f"## 이전 단계 결과\n{context}\n\n"
        f"## 작업\n{task}"
    )

    # inject_agent_spec()으로 타겟 스펙 주입
    injected = inject_agent_spec(content)

    # to_claude_code.md에 작성
    to_path = WATCH_FILES["to"]["claude_code"]
    try:
        with open(to_path, "w", encoding="utf-8") as f:
            f.write(injected)
        # 상태 리셋 — 메인 루프가 hash 불일치로 새 작업 감지하도록
        key = "to_claude_code"
        if key in state:
            state[key]["hash"] = ""
            state[key]["mtime"] = 0.0
        _log_chain(chain_meta["chain_id"], new_depth, target_agent, "DISPATCH")
        _send_telegram(
            f"🔗 <b>Agent Chain</b>\n→ {target_agent}\n"
            f"깊이: {new_depth}/{MAX_CHAIN_DEPTH}\n"
            f"경로: {' → '.join(new_visited)}"
        )
        return True
    except Exception as e:
        _log_chain(chain_meta["chain_id"], new_depth, target_agent, "DISPATCH_FAIL", str(e))
        _send_telegram(f"❌ <b>체인 디스패치 실패</b>\n{_escape_html(str(e))}")
        return False


def _extract_chain_meta(task_content: str) -> dict:
    """to_ 파일 frontmatter에서 체인 메타데이터 추출."""
    meta = {
        "chain_id": str(uuid.uuid4())[:8],
        "depth": 0,
        "visited": [],
        "origin": "",
    }
    fm_match = re.match(r'^---\s*\n(.*?)\n---', task_content, re.DOTALL)
    if not fm_match:
        return meta
    try:
        data = yaml.safe_load(fm_match.group(1))
        if isinstance(data, dict):
            meta["chain_id"] = data.get("chain_id", meta["chain_id"])
            meta["depth"] = int(data.get("chain_depth", 0))
            visited = data.get("chain_visited", [])
            if isinstance(visited, list):
                meta["visited"] = visited
            meta["origin"] = data.get("chain_origin", "")
    except (yaml.YAMLError, ValueError):
        pass
    return meta


def _extract_source_agent(task_content: str) -> str | None:
    """to_ 파일에서 현재 에이전트 id 추출 (## Agent Role: xxx)."""
    m = re.search(r'## Agent Role:\s*([\w-]+)', task_content)
    return m.group(1) if m else None


# ── Auto-Brain Callback 상태 ───────────────────────────────────────────────────
MAX_CHAIN_DEPTH   = 3
_auto_chain_active = False         # 체이닝으로 기록한 to_ 파일임을 표시
_current_chain_depth = 0           # 현재 체인 깊이 (0-base)
_last_cb_summary_hash = ""         # 반복 응답 감지용 직전 콜백 summary 해시


def _file_mtime(path: str) -> float:
    try:
        return os.path.getmtime(path)
    except OSError:
        return 0.0


def _read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def _content_hash(path: str) -> str:
    content = _read_file(path)
    return hashlib.md5(content.encode()).hexdigest()


def _parse_to_hands(content: str) -> tuple[str, str]:
    """to_[engine].md에서 작업 제목과 추천 엔진 추출."""
    title  = "Unknown Task"
    engine = "hands-1"

    m = re.search(r"(?:#.*실행 요청[:\s]*|#\s*to_\w+\s*—\s*|title:\s*[\"']?)(.+?)(?:[\"']?$)", content, re.MULTILINE)
    if m:
        title = m.group(1).strip()

    m = re.search(r"(?:\*\*추천\s*엔진[:\s]*\*\*\s*|engine:\s*[\"']?)(.+?)(?:[\"']?$)",
                  content, re.MULTILINE)
    if m:
        raw = m.group(1).strip().lower()
        if "hands-2" in raw or "gemini" in raw:
            engine = "hands-2"
        elif "hands-3" in raw or "codex" in raw:
            engine = "hands-3"
        elif "hands-4" in raw or "claude code" in raw or "cc" in raw:
            engine = "hands-4"
        elif "hands-1" in raw or "antigravity" in raw or "sonnet" in raw or "opus" in raw:
            engine = "hands-1"

    return title, engine


def _format_engine_result(title: str, result: dict, engine: str = "claude_code") -> str:
    """엔진 실행 결과를 from_[engine].md 포맷으로 변환."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    status = "done" if result["success"] else "failed"
    error_section = ""
    if result.get("error"):
        error_section = f"\n## 에러\n{result['error']}\n"

    return f"""---
title: "{title}"
engine: {engine}
status: {status}
completed: "{now}"
elapsed_seconds: {result['elapsed_seconds']:.1f}
---
# from_{engine} — 실행 결과

## 상태
{"✅ 성공" if result["success"] else "❌ 실패"}
소요 시간: {result['elapsed_seconds']:.0f}초
{error_section}
## 출력
{result.get('output', '(출력 없음)')}
"""


def _escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _send_telegram(text: str):
    """Telegram 알림 발송 (3회 재시도 + 지수 백오프). 미설정 시 콘솔 출력만."""
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        print(f"[bridge] Telegram 미설정 — 콘솔만 출력: {text}")
        return

    url     = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id":    TG_CHAT_ID,
        "text":       text,
        "parse_mode": "HTML",
    }).encode()

    max_retries = 3
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                url, data=payload,
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=5)
            print("[bridge] Telegram 발송 완료")
            log_bridge("Telegram 발송 완료")
            return
        except Exception as e:
            wait = 2 ** (attempt + 1)  # 2s, 4s, 8s
            if attempt < max_retries - 1:
                print(f"[bridge] Telegram 실패 (시도 {attempt+1}/{max_retries}): {e} — {wait}초 후 재시도")
                time.sleep(wait)
            else:
                print(f"[bridge] Telegram 최종 실패 (시도 {max_retries}/{max_retries}): {e}")
                log_bridge(f"Telegram 최종 실패: {e}", "ERROR")


# ── Auto-Brain Callback 핸들러 ────────────────────────────────────────────────

def _handle_brain_decision(cb_result: dict, chain_depth: int, state: dict):
    """Brain의 DONE / CHAIN / ESCALATE 판단에 따라 처리."""
    global _auto_chain_active, _current_chain_depth, _last_cb_summary_hash

    decision      = cb_result.get("decision", "UNKNOWN")
    summary       = cb_result.get("summary", "")
    target_engine = cb_result.get("target_engine")
    chain_content = cb_result.get("chain_content")

    # 반복 응답 감지 — 동일 summary hash면 강제 ESCALATE
    summary_hash = hashlib.md5(summary.encode()).hexdigest()
    if summary_hash == _last_cb_summary_hash and decision != "ESCALATE":
        print("[brain_cb] ⚠️ 반복 응답 감지 — 강제 ESCALATE")
        decision = "ESCALATE"
        summary  = "반복 응답 감지 — 강제 에스컬레이션 (루프 방지)"
    _last_cb_summary_hash = summary_hash

    if decision == "DONE":
        print(f"[brain_cb] ✅ DONE — {summary[:100]}")
        log_bridge(f"Brain 콜백 DONE: {summary[:100]}")
        _send_telegram(
            f"✅ <b>Auto-Brain: DONE</b>\n{_escape_html(summary[:500])}"
        )
        _current_chain_depth = 0

    elif decision == "CHAIN":
        if chain_depth >= MAX_CHAIN_DEPTH or not target_engine:
            reason = f"chain_depth={chain_depth}>={MAX_CHAIN_DEPTH}" if chain_depth >= MAX_CHAIN_DEPTH else "target_engine 미지정"
            print(f"[brain_cb] ⚠️ CHAIN 한도 초과/미지정 — ESCALATE. {reason}")
            _send_telegram(
                f"⚠️ <b>Auto-Brain: ESCALATE</b> (체인 한도)\n{_escape_html(reason)}"
            )
            _current_chain_depth = 0
            return

        to_path = WATCH_FILES["to"].get(target_engine)
        if not to_path:
            print(f"[brain_cb] ❌ 알 수 없는 target_engine: {target_engine}")
            _send_telegram(f"❌ <b>Auto-Brain: CHAIN 오류</b>\n알 수 없는 엔진: {target_engine}")
            return

        chain_body = chain_content or summary
        try:
            with open(to_path, "w", encoding="utf-8") as f:
                f.write(chain_body)
            # 상태 해시 갱신 — 새로 쓴 to_ 파일이 자신의 다음 폴링에서 중복 처리되지 않도록
            key = f"to_{target_engine}"
            if key in state:
                state[key]["hash"]  = hashlib.md5(chain_body.encode()).hexdigest()
                state[key]["mtime"] = _file_mtime(to_path)

            _auto_chain_active   = True
            _current_chain_depth = chain_depth + 1
            display = ENGINE_DISPLAY.get(target_engine, target_engine)
            print(f"[brain_cb] 🔗 CHAIN → {display} (depth={_current_chain_depth})")
            _send_telegram(
                f"🔗 <b>Auto-Brain: CHAIN</b>\n→ {display}\n깊이: {_current_chain_depth}/{MAX_CHAIN_DEPTH}\n\n"
                f"{_escape_html(chain_body[:300])}"
            )
        except Exception as e:
            print(f"[brain_cb] ❌ CHAIN 파일 기록 실패: {e}")
            _send_telegram(f"❌ <b>Auto-Brain: CHAIN 실패</b>\n{_escape_html(str(e))}")

    else:  # ESCALATE or UNKNOWN
        label = "ESCALATE" if decision == "ESCALATE" else "UNKNOWN"
        print(f"[brain_cb] 🚨 {label} — {summary[:100]}")
        log_bridge(f"Brain 콜백 {label}: {summary[:100]}", "WARN")
        _send_telegram(
            f"🚨 <b>Auto-Brain: {label}</b>\n{_escape_html(summary[:500])}"
        )
        _current_chain_depth = 0


def _run_auto_brain_callback(engine: str, from_path: str, state: dict,
                             to_content: str = ""):
    """엔진 자동실행 완료 후 위임 블록 감지 → 체인 또는 Brain 콜백 호출.

    S-8: from_ 읽은 후 parse_delegation_block() 먼저 시도.
         위임 블록 있으면 validate → chain_dispatch (Brain 콜백 스킵).
         위임 블록 없으면 기존 DONE/CHAIN/ESCALATE 플로우.
    """
    global _current_chain_depth

    from_content = _read_file(from_path)
    if not from_content.strip():
        print("[brain_cb] from_ 파일이 비어있어 콜백 스킵")
        return

    # S-8: Agent Chaining — 위임 블록 감지
    delegation = parse_delegation_block(from_content)
    if delegation:
        target_agent = delegation["delegate_to"]
        task = delegation["task"]
        reason = delegation.get("reason", "")
        print(f"[chain] 위임 블록 감지: → {target_agent} (reason: {reason})")

        # 체인 메타데이터 추출 (to_ 파일에서)
        chain_meta = _extract_chain_meta(to_content)
        source_agent = _extract_source_agent(to_content)

        if not source_agent:
            print("[chain] ⚠️ 소스 에이전트 식별 불가 — 위임 무시, Brain 콜백으로 전환")
            _send_telegram("⚠️ 소스 에이전트 식별 불가. 위임 블록 무시.")
        else:
            # 검증
            valid, reason_msg = validate_delegation(
                source_agent, target_agent,
                chain_meta["visited"], chain_meta["depth"],
            )
            if valid:
                success = chain_dispatch(
                    target_agent, task, from_content,
                    chain_meta, state,
                )
                if success:
                    _log_chain(chain_meta["chain_id"], chain_meta["depth"],
                               target_agent, "VALIDATED")
                    _current_chain_depth = chain_meta["depth"] + 1
                    return  # 체인 디스패치 성공 — Brain 콜백 스킵
            else:
                print(f"[chain] ❌ 위임 검증 실패: {reason_msg}")
                _log_chain(chain_meta["chain_id"], chain_meta["depth"],
                           target_agent, "REJECTED", reason_msg)
                _send_telegram(
                    f"⚠️ <b>위임 거부</b>\n{source_agent}→{target_agent}\n"
                    f"사유: {_escape_html(reason_msg)}"
                )
        # 검증 실패 시 → 기존 Brain 콜백 플로우로 폴스루

    # 기존 Brain 콜백 플로우
    if not _check_brain_daily_limit():
        print("[brain_cb] ⚠️ 일일 Brain 콜백 한도 초과 — 스킵")
        _send_telegram("⚠️ <b>Auto-Brain 한도 초과</b> — 오늘 30회 소진")
        return

    depth = _current_chain_depth
    print(f"[brain_cb] 🧠 Brain 콜백 시작 (engine={engine}, depth={depth})")
    log_bridge(f"Brain 콜백 시작: engine={engine}, depth={depth}")
    cb_result = run_brain_callback(engine, from_content, chain_depth=depth)
    record_brain_callback()  # T4b: 비용 기록
    _handle_brain_decision(cb_result, chain_depth=depth, state=state)


def main():
    global _auto_chain_active, _current_chain_depth

    print(f"[bridge] Task Bridge {get_version()} 시작 (Agent Chaining + Spec Pipeline + 안전장치)")

    # 모닝 브리프 발송 (startup)
    _send_telegram(get_morning_brief())

    client = None
    try:
        client = get_redis()
        client.ping()
        print("[bridge] Redis 연결 OK")
    except Exception as e:
        print(f"[bridge] Redis 연결 실패: {e} — 파일 전용 모드")

    # 각 파일의 상태 초기화
    state = {}
    for direction in ("to", "from"):
        for engine, filepath in WATCH_FILES[direction].items():
            key = f"{direction}_{engine}"
            state[key] = {
                "path": filepath,
                "mtime": _file_mtime(filepath),
                "hash": _content_hash(filepath),
                "last_alert": 0.0,
                "last_task_id": None,
            }

    while True:
        try:
            for direction in ("to", "from"):
                for engine, filepath in WATCH_FILES[direction].items():
                    key = f"{direction}_{engine}"
                    s = state[key]
                    new_mt = _file_mtime(filepath)

                    if new_mt <= s["mtime"]:
                        continue

                    s["mtime"] = new_mt
                    now = time.time()
                    if now - s["last_alert"] < DEBOUNCE_WINDOW:
                        print(f"[bridge] {key} 디바운스 — 스킵")
                        continue

                    time.sleep(2)  # 쓰기 완료 대기
                    s["mtime"] = _file_mtime(filepath)
                    content = _read_file(filepath)
                    new_hash = hashlib.md5(content.encode()).hexdigest()

                    if new_hash == s["hash"] or not content.strip() or "EMPTY" in content[:50]:
                        continue

                    # v4.4: status:done 재감지 방지 — content 읽은 직후 체크
                    if direction == "to" and re.search(r"status:\s*(done|complete)", content[:300], re.IGNORECASE):
                        print(f"[bridge] {key} — status:done 감지, 스킵")
                        s["hash"] = new_hash  # 해시 갱신하여 재처리 방지
                        continue

                    s["hash"] = new_hash
                    s["last_alert"] = time.time()
                    display = ENGINE_DISPLAY.get(engine, engine)

                    if direction == "to":
                        title, _ = _parse_to_hands(content)
                        print(f"[bridge] 새 작업: {title} → {display}")
                        log_bridge(f"새 작업: {title} → {display}")
                        if client:
                            try:
                                tid = add_task(client, title, engine, content)
                                s["last_task_id"] = tid
                                print(f"[bridge] Redis: task_id={tid}")
                            except Exception as e:
                                print(f"[bridge] Redis 실패: {e}")
                        _send_telegram(
                            f"<b>새 작업</b>\n{_escape_html(title)}\n엔진: {display}\n\n"
                            f"to_{engine}.md → {display}에 전달하세요"
                        )

                        # T3: 위험 명령 차단 — 엔진 자동실행 직전
                        dangers = _check_dangerous(content)
                        if dangers:
                            print(f"[bridge] ⛔ 위험 명령 차단: {dangers}")
                            log_bridge(f"위험 명령 차단: {dangers}", "WARN")
                            _send_telegram(
                                f"⚠️ 위험 명령 감지: {dangers}. 실행을 건너뜁니다."
                            )
                            record_dangerous_block()
                            continue  # 엔진 실행 스킵

                        # S-7: Spec Pipeline — @agent-id 스펙 주입
                        injected_content = inject_agent_spec(content)

                        # CC 자동 실행 (claude_code 엔진만)
                        if engine == "claude_code":
                            print(f"[bridge] ⚡ CC 자동 실행 시작: {title}")
                            log_bridge(f"CC 자동 실행 시작: {title}")
                            _send_telegram(f"⚡ <b>CC 자동 실행 시작</b>\n{_escape_html(title)}")

                            cc_result = run_claude_code(
                                prompt=f"다음 작업지시서를 읽고 실행하세요. 결과를 간결하게 보고하세요.\n\n{injected_content}",
                                working_dir="/Users/woosung/Desktop/Dev/Woosdom_Brain"
                            )

                            from_path = WATCH_FILES["from"]["claude_code"]
                            result_md = _format_engine_result(title, cc_result, "claude_code")
                            with open(from_path, "w", encoding="utf-8") as f:
                                f.write(result_md)
                            fkey = "from_claude_code"
                            state[fkey]["hash"]  = hashlib.md5(result_md.encode()).hexdigest()
                            state[fkey]["mtime"] = _file_mtime(from_path)

                            status_emoji = "✅" if cc_result["success"] else "❌"
                            elapsed = cc_result["elapsed_seconds"]
                            log_bridge(f"CC 완료: {title}, {elapsed:.0f}초, exit={'성공' if cc_result['success'] else '실패'}")
                            _send_telegram(
                                f"{status_emoji} <b>CC 실행 완료</b>\n{_escape_html(title)}\n"
                                f"소요: {elapsed:.0f}초\nfrom_claude_code.md 업데이트됨"
                            )

                            # T4b: 비용 기록
                            record_engine_run("claude_code", elapsed, cc_result.get("max_turns_used", 50))

                            # Auto-Brain Callback (S-1) + Agent Chaining (S-8)
                            _run_auto_brain_callback("claude_code", from_path, state,
                                                     to_content=injected_content)

                        # Codex 자동 실행
                        if engine == "codex":
                            print(f"[bridge] ⚡ Codex 자동 실행 시작: {title}")
                            log_bridge(f"Codex 자동 실행 시작: {title}")
                            _send_telegram(f"⚡ <b>Codex 자동 실행 시작</b>\n{_escape_html(title)}")

                            codex_result = run_codex(
                                prompt=f"다음 작업지시서를 읽고 실행하세요. 결과를 간결하게 보고하세요.\n\n{injected_content}",
                                working_dir="/Users/woosung/Desktop/Dev/Woosdom_Brain"
                            )

                            from_path = WATCH_FILES["from"]["codex"]
                            result_md = _format_engine_result(title, codex_result, "codex")
                            with open(from_path, "w", encoding="utf-8") as f:
                                f.write(result_md)
                            fkey = "from_codex"
                            state[fkey]["hash"]  = hashlib.md5(result_md.encode()).hexdigest()
                            state[fkey]["mtime"] = _file_mtime(from_path)

                            status_emoji = "✅" if codex_result["success"] else "❌"
                            elapsed = codex_result["elapsed_seconds"]
                            log_bridge(f"Codex 완료: {title}, {elapsed:.0f}초, exit={'성공' if codex_result['success'] else '실패'}")
                            _send_telegram(
                                f"{status_emoji} <b>Codex 실행 완료</b>\n{_escape_html(title)}\n"
                                f"소요: {elapsed:.0f}초\nfrom_codex.md 업데이트됨"
                            )

                            # T4b: 비용 기록
                            record_engine_run("codex", elapsed, codex_result.get("max_turns_used", 10))

                            # Auto-Brain Callback (S-1) + Agent Chaining (S-8)
                            _run_auto_brain_callback("codex", from_path, state,
                                                     to_content=injected_content)

                        # Antigravity — GUI 앱, CLI 자동 실행 불가. 완전 스킵.
                        # (v4.8: Gemini CLI 대체 실행 제거 — Brain 지시)
                        if engine == "antigravity":
                            print(f"[bridge] SKIP antigravity — GUI app, manual execution only: {title}")
                            log_bridge(f"SKIP antigravity — GUI app, manual only: {title}", "INFO")
                            # TG 알림은 위에서 이미 '새 작업 / 수동 전달' 메시지로 발송됨. 추가 실행 없음.

                    else:  # from — Brain이 직접 기록한 경우 (외부 에이전트 완료)
                        print(f"[bridge] 작업 완료: {display}")
                        to_key = f"to_{engine}"
                        tid = state[to_key]["last_task_id"]
                        if client and tid:
                            try:
                                complete_task(client, tid)
                                print(f"[bridge] Redis 완료: task_id={tid}")
                            except Exception as e:
                                print(f"[bridge] Redis 완료 실패: {e}")
                            state[to_key]["last_task_id"] = None
                        _send_telegram(f"<b>작업 완료</b>\n{display} → from_{engine}.md 업데이트됨")
                        # 참고: task_bridge 자신이 쓴 from_은 위 자동실행 블록에서 hash 갱신하여
                        # 이 else 분기에 도달하지 않음. 여기 도달하는 경우는 외부 에이전트가 기록한 경우.

        except KeyboardInterrupt:
            print("[bridge] 종료")
            break
        except Exception as e:
            print(f"[bridge] 루프 에러: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
