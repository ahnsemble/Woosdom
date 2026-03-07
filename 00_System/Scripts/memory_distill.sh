#!/bin/bash
# Memory Distillation — conversation_memory.md 자동 증류
# 실행: ./memory_distill.sh
# 조건: memory가 300토큰 초과 시 증류 실행

VAULT="/Users/woosung/Desktop/Dev/Woosdom_Brain"
MEMORY_FILE="$VAULT/00_System/Memory/conversation_memory.md"
SESSIONS_DIR="$VAULT/00_System/Memory/sessions"
LOG_FILE="$VAULT/00_System/Logs/memory_distill.log"

# cron 환경은 PATH가 매우 제한적일 수 있음 (Homebrew 포함)
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

LOCK_FILE="$VAULT/00_System/Scripts/.distill.lock"

mkdir -p "$SESSIONS_DIR" "$(dirname "$LOG_FILE")"

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    echo "$msg" >> "$LOG_FILE"
    echo "$msg" >&2
}

# ── 토큰 추정 (단어 수 × 1.3) ───────────────────────────

estimate_tokens() {
    local word_count
    word_count=$(wc -w < "$MEMORY_FILE" | tr -d ' ')
    echo "$word_count" | awk '{printf "%d", $1 * 1.3}'
}

# ── frontmatter 추출 ────────────────────────────────────

get_frontmatter() {
    awk 'BEGIN{n=0} /^---$/{n++; if(n==2) exit; print; next} n>=1{print}' "$1"
    echo "---"
}

get_body() {
    awk 'BEGIN{n=0} /^---$/{n++; next} n>=2{print}' "$1"
}

# ── 세션 번호 결정 ──────────────────────────────────────

next_session_file() {
    local date_str
    date_str=$(date '+%Y-%m-%d')
    local n=1
    while [ -f "$SESSIONS_DIR/${date_str}_s$(printf '%02d' $n).md" ]; do
        n=$((n + 1))
    done
    echo "$SESSIONS_DIR/${date_str}_s$(printf '%02d' $n).md"
}

# ── 메인 ────────────────────────────────────────────────

# ── 동시성 보호 (lock) ────────────────────────────────────

if [ -f "$LOCK_FILE" ]; then
    lock_pid=$(cat "$LOCK_FILE" 2>/dev/null)
    if kill -0 "$lock_pid" 2>/dev/null; then
        log "SKIP — 다른 distill 프로세스 실행 중 (PID: $lock_pid)"
        exit 0
    else
        log "WARN — stale lock 제거 (PID: $lock_pid)"
        rm -f "$LOCK_FILE"
    fi
fi
echo $$ > "$LOCK_FILE"
trap 'rm -f "$LOCK_FILE"' EXIT INT TERM

if [ ! -f "$MEMORY_FILE" ]; then
    log "ERROR — $MEMORY_FILE not found"
    exit 1
fi

TOKENS=$(estimate_tokens)
log "Token estimate: $TOKENS"

if [ "$TOKENS" -le 300 ]; then
    log "SKIP — 증류 불필요 (${TOKENS} tokens ≤ 300)"
    exit 0
fi

# 1. 아카이빙
ARCHIVE_FILE=$(next_session_file)
cp "$MEMORY_FILE" "$ARCHIVE_FILE"
log "ARCHIVED → $ARCHIVE_FILE"

# 2. claude -p headless로 증류
BODY=$(get_body "$MEMORY_FILE")
FRONTMATTER=$(get_frontmatter "$MEMORY_FILE")

DISTILL_PROMPT="다음 대화 메모리를 핵심 결정사항과 맥락만 남기고 200토큰 이내로 압축하라.
형식: \"## YYYY-MM-DD 세션\n- 결정사항 1\n- 결정사항 2\" 유지.
원본:
$BODY"

DISTILLED=$(claude -p "$DISTILL_PROMPT" --max-turns 1 2>/dev/null)

if [ $? -ne 0 ] || [ -z "$DISTILLED" ]; then
    log "WARN — claude -p 증류 실패. fallback: 최근 항목만 유지"
    # Fallback: 본문에서 최근 섹션(마지막 20줄)만 유지
    DISTILLED=$(echo "$BODY" | tail -20)
    if [ -z "$DISTILLED" ]; then
        log "ERROR — fallback도 실패. 원본 유지."
        exit 1
    fi
fi

# 증류 결과가 원본보다 짧은지 검증
ORIGINAL_LINES=$(echo "$BODY" | wc -l | tr -d ' ')
DISTILLED_LINES=$(echo "$DISTILLED" | wc -l | tr -d ' ')

if [ "$DISTILLED_LINES" -ge "$ORIGINAL_LINES" ]; then
    log "WARN — 증류 결과가 원본 이상 길이 (${DISTILLED_LINES} >= ${ORIGINAL_LINES}). fallback 적용"
    DISTILLED=$(echo "$BODY" | tail -20)
fi

# 3. frontmatter + 증류 결과로 덮어쓰기
{
    echo "$FRONTMATTER"
    echo ""
    printf '%s\n' "$DISTILLED"
} > "$MEMORY_FILE"

log "DISTILLED — ${TOKENS} → $(estimate_tokens) tokens"
log "DONE — conversation_memory.md 증류 완료"
