"""cost_monitor.py — 일일 비용/사용량 모니터링 (Sprint 5-5 T4).

JSON 파일 기반으로 엔진별 실행 횟수, 턴 수, 소요 시간,
Brain 콜백 횟수, 위험 차단 횟수를 일일 단위로 기록한다.
날짜 변경 시 이전 데이터를 .cost_history/에 아카이브한다.
"""
import json
import os
import re
import shutil
from datetime import datetime, timedelta

STATS_DIR = os.path.dirname(os.path.abspath(__file__))
STATS_PATH = os.path.join(STATS_DIR, ".cost_stats.json")
HISTORY_DIR = os.path.join(STATS_DIR, ".cost_history")

_DEFAULT_ENGINES = ("claude_code", "codex", "antigravity")


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _empty_stats(date: str) -> dict:
    return {
        "date": date,
        "engines": {
            eng: {"tasks": 0, "total_turns_est": 0, "total_seconds": 0}
            for eng in _DEFAULT_ENGINES
        },
        "brain_callbacks": 0,
        "dangerous_blocked": 0,
    }


def _load_stats() -> dict:
    """현재 통계 파일 로드. 날짜 변경 시 아카이브 후 리셋."""
    today = _today()

    if not os.path.exists(STATS_PATH):
        return _empty_stats(today)

    try:
        with open(STATS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return _empty_stats(today)

    if data.get("date") != today:
        # 이전 날 데이터 아카이브
        _archive(data)
        return _empty_stats(today)

    return data


def _archive(data: dict):
    """이전 날 통계를 .cost_history/YYYY-MM-DD.json에 저장."""
    old_date = data.get("date", "unknown")
    os.makedirs(HISTORY_DIR, exist_ok=True)
    archive_path = os.path.join(HISTORY_DIR, f"{old_date}.json")
    try:
        with open(archive_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"[cost_monitor] 아카이브 실패: {e}")


def _save_stats(data: dict):
    """통계 파일 저장."""
    try:
        with open(STATS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"[cost_monitor] 저장 실패: {e}")


def record_engine_run(engine: str, elapsed_seconds: float, max_turns_used: int):
    """엔진 실행 1회 기록."""
    data = _load_stats()
    if engine not in data["engines"]:
        data["engines"][engine] = {"tasks": 0, "total_turns_est": 0, "total_seconds": 0}
    eng = data["engines"][engine]
    eng["tasks"] += 1
    eng["total_turns_est"] += max_turns_used
    eng["total_seconds"] += int(elapsed_seconds)
    _save_stats(data)


def record_brain_callback():
    """Brain 콜백 1회 기록."""
    data = _load_stats()
    data["brain_callbacks"] += 1
    _save_stats(data)


def record_dangerous_block():
    """위험 명령 차단 1회 기록."""
    data = _load_stats()
    data["dangerous_blocked"] += 1
    _save_stats(data)


def get_daily_summary() -> str:
    """TG 발송용 일일 요약 텍스트 생성."""
    data = _load_stats()
    lines = [f"📊 일일 리포트 ({data['date']})"]

    total_tasks = 0
    total_turns = 0
    total_secs = 0
    for eng_name, eng in data["engines"].items():
        if eng["tasks"] > 0:
            lines.append(
                f"  • {eng_name}: {eng['tasks']}건, "
                f"~{eng['total_turns_est']}턴, {eng['total_seconds']}초"
            )
        total_tasks += eng["tasks"]
        total_turns += eng["total_turns_est"]
        total_secs += eng["total_seconds"]

    lines.append(f"  합계: {total_tasks}건, ~{total_turns}턴, {total_secs}초")
    lines.append(f"  Brain 콜백: {data['brain_callbacks']}회")
    lines.append(f"  위험 차단: {data['dangerous_blocked']}회")
    return "\n".join(lines)


# ── 한국어 요일 ────────────────────────────────────────────────────────────────
_KR_WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]

_BRAIN_QUOTES = {
    0: "이번 주도 빡세게 가봅시다.",
    1: "어제의 나보다 1% 더.",
    2: "수요일, 고비를 넘기면 내리막입니다.",
    3: "목요일, 마무리 준비 시작.",
    4: "주말이 코앞. 오늘만 버팁시다.",
    5: "토요일, 리프레시 하면서도 한 발짝.",
    6: "일요일, 다음 주를 위한 충전.",
}

VAULT_ROOT_CM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
TEMPLATES_DIR_CM = os.path.join(VAULT_ROOT_CM, "00_System", "Templates")


def _read_yesterday_stats() -> dict | None:
    """어제 날짜의 .cost_history/YYYY-MM-DD.json 읽기."""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    path = os.path.join(HISTORY_DIR, f"{yesterday}.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _read_to_status(filename: str) -> str:
    """to_*.md 파일의 status 필드 읽기."""
    path = os.path.join(TEMPLATES_DIR_CM, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read(500)
        m = re.search(r"status:\s*(\S+)", content)
        if m:
            return m.group(1).strip()
    except OSError:
        pass
    return "없음"


def get_morning_brief() -> str:
    """TG 발송용 모닝 브리프 생성."""
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    weekday = _KR_WEEKDAYS[now.weekday()]

    lines = [f"🌅 Woosdom Morning Brief — {today_str} ({weekday})", ""]

    # ── 어제 실적 ──
    yd = _read_yesterday_stats()
    lines.append("📌 어제 실적")
    if yd:
        eng = yd.get("engines", {})
        cc = eng.get("claude_code", {})
        codex = eng.get("codex", {})
        ag = eng.get("antigravity", {})
        lines.append(
            f"  • CC: {cc.get('tasks', 0)}건, {cc.get('total_turns_est', 0)}턴 / "
            f"Codex: {codex.get('tasks', 0)}건 / "
            f"AG: {ag.get('tasks', 0)}건"
        )
        lines.append(
            f"  • Brain 콜백: {yd.get('brain_callbacks', 0)}회 | "
            f"위험 차단: {yd.get('dangerous_blocked', 0)}회"
        )
    else:
        lines.append("  • 데이터 없음")

    # ── 시스템 상태 ──
    lines.append("")
    lines.append("⚙️ 시스템 상태")
    cc_st = _read_to_status("to_claude_code.md")
    codex_st = _read_to_status("to_codex.md")
    ag_st = _read_to_status("to_antigravity.md")
    lines.append(f"  • Watcher: 감시 중 (CC:{cc_st} / Codex:{codex_st} / AG:{ag_st})")
    lines.append("  • 일일 한도: CC 100턴 / Codex 무제한 / Brain콜백 30회")

    # ── 대기 작업 ──
    lines.append("")
    lines.append("🎯 오늘 대기 중인 작업")
    pending_found = False
    for fname, label in [("to_claude_code.md", "CC"), ("to_codex.md", "Codex"), ("to_antigravity.md", "AG")]:
        st = _read_to_status(fname)
        if st == "pending":
            pending_found = True
            lines.append(f"  • [{label}] {fname} — pending")
    if not pending_found:
        lines.append("  • 대기 작업 없음")

    # ── Brain 한마디 ──
    lines.append("")
    lines.append("💡 Brain 한마디")
    lines.append(f"  • {_BRAIN_QUOTES.get(now.weekday(), '좋은 아침. 시스템 정상 가동 중.')}")

    return "\n".join(lines)
