#!/bin/bash
# Woosdom Task Watcher — 통합 엔진 감시 데몬
# fswatch로 to_*.md 3개 파일 감시 → 변경 시 해당 엔진 CLI 자동 실행

VAULT="/Users/woosung/Desktop/Dev/Woosdom_Brain"
TEMPLATES="$VAULT/00_System/Templates"
LOGS="$VAULT/00_System/Logs"
LOG_FILE="$LOGS/watcher.log"
SCRIPTS_DIR="$VAULT/00_System/Scripts"
LOCK_DIR="$SCRIPTS_DIR/.watcher_locks"
ENGINE_TIMEOUT=600  # 10분 타임아웃
HEARTBEAT_FILE="$LOGS/heartbeat.json"
HEARTBEAT_INTERVAL=60  # 60초마다 heartbeat 갱신
WATCHER_START_TIME=$(date +%s)

# 감시 대상
TO_CC="$TEMPLATES/to_claude_code.md"
TO_CODEX="$TEMPLATES/to_codex.md"
TO_AG="$TEMPLATES/to_antigravity.md"

# 결과 저장 대상
FROM_CC="$TEMPLATES/from_claude_code.md"
FROM_CODEX="$TEMPLATES/from_codex.md"
FROM_AG="$TEMPLATES/from_antigravity.md"

mkdir -p "$LOCK_DIR" "$LOGS"

# ── Heartbeat ─────────────────────────────────────────────

# 엔진별 마지막 작업 시간 추적 (메모리)
declare -A ENGINE_LAST_TASK
ENGINE_LAST_TASK=([claude_code]="null" [codex]="null" [antigravity]="null")

# 엔진 상태 추적
declare -A ENGINE_STATUS
ENGINE_STATUS=([claude_code]="idle" [codex]="idle" [antigravity]="idle")

# 최근 1시간 에러 카운트
ERRORS_LAST_HOUR=0

update_heartbeat() {
    local now
    now=$(date -u '+%Y-%m-%dT%H:%M:%S+09:00')
    local uptime=$(( $(date +%s) - WATCHER_START_TIME ))

    # pending 파일 목록
    local pending_files="[]"
    local pf_list=""
    for pair in "$TO_CC|claude_code" "$TO_CODEX|codex" "$TO_AG|antigravity"; do
        IFS='|' read -r tf eng <<< "$pair"
        if [ -f "$tf" ]; then
            local st
            st=$(yaml_field "$tf" "status" 2>/dev/null)
            if [ "$st" = "pending" ]; then
                [ -n "$pf_list" ] && pf_list="$pf_list, "
                pf_list="$pf_list\"$eng\""
            fi
        fi
    done
    [ -n "$pf_list" ] && pending_files="[$pf_list]"

    # JSON 생성 (jq 없이 단순 echo)
    cat > "$HEARTBEAT_FILE" <<HEARTBEAT_EOF
{
  "watcher_pid": $$,
  "last_beat": "$now",
  "uptime_seconds": $uptime,
  "engines": {
    "claude_code": {"status": "${ENGINE_STATUS[claude_code]}", "last_task": ${ENGINE_LAST_TASK[claude_code]}},
    "codex": {"status": "${ENGINE_STATUS[codex]}", "last_task": ${ENGINE_LAST_TASK[codex]}},
    "antigravity": {"status": "${ENGINE_STATUS[antigravity]}", "last_task": ${ENGINE_LAST_TASK[antigravity]}}
  },
  "pending_files": $pending_files,
  "errors_last_hour": $ERRORS_LAST_HOUR
}
HEARTBEAT_EOF
}

# 백그라운드 heartbeat 루프
start_heartbeat_loop() {
    while true; do
        update_heartbeat
        sleep "$HEARTBEAT_INTERVAL"
    done
}

# ── 유틸리티 ──────────────────────────────────────────────

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    echo "$msg" >> "$LOG_FILE"
    echo "$msg" >&2
}

# YAML frontmatter에서 특정 필드 값 파싱
yaml_field() {
    local file="$1" field="$2"
    sed -n '/^---$/,/^---$/p' "$file" 2>/dev/null \
        | grep -E "^${field}:" | head -1 \
        | sed "s/^${field}:[[:space:]]*//" | tr -d '"' | tr -d "'"
}

# frontmatter 이후 본문 추출
get_body() {
    awk 'BEGIN{n=0} /^---$/{n++; next} n>=2{print}' "$1"
}

# status를 done으로 업데이트
set_status_done() {
    sed -i '' 's/^status:[[:space:]]*.*/status: done/' "$1" 2>/dev/null
}

# ── 엔진 실행 ─────────────────────────────────────────────

run_engine() {
    local to_file="$1" from_file="$2" engine="$3"
    local lock_file="$LOCK_DIR/${engine}.lock"

    # 중복 실행 방지 (lock)
    if [ -f "$lock_file" ]; then
        log "SKIP $engine — lock exists"
        return
    fi

    # status 확인 — pending일 때만 실행
    local status
    status=$(yaml_field "$to_file" "status")
    if [ "$status" != "pending" ]; then
        log "SKIP $engine — status='$status'"
        return
    fi

    # title 파싱 (로그용)
    local title
    title=$(yaml_field "$to_file" "title")

    # Lock 획득
    echo $$ > "$lock_file"
    ENGINE_STATUS[$engine]="active"
    update_heartbeat
    log "START $engine — $title"

    # 프롬프트 추출 (본문만, 임시 파일 경유)
    local prompt_file
    prompt_file=$(mktemp)
    get_body "$to_file" > "$prompt_file"

    local result="" exit_code=0
    local result_file timed_out=false
    result_file=$(mktemp)

    case "$engine" in
        claude_code)
            ( cd "$VAULT" && env -u CLAUDECODE claude -p "$(cat "$prompt_file")" --max-turns 30 > "$result_file" 2>&1 ) &
            ;;
        codex)
            ( cd "$VAULT" && /opt/homebrew/bin/codex exec --skip-git-repo-check "$(cat "$prompt_file")" > "$result_file" 2>&1 ) &
            ;;
        antigravity)
            log "SKIP antigravity — GUI app, manual execution only"
            rm -f "$lock_file" "$result_file" "$prompt_file"
            return
            ;;
    esac

    local engine_pid=$!

    # Watchdog: 타임아웃 초과 시 엔진 프로세스 kill
    ( sleep "$ENGINE_TIMEOUT" && kill "$engine_pid" 2>/dev/null ) &
    local watchdog_pid=$!

    wait "$engine_pid" 2>/dev/null
    exit_code=$?

    # Watchdog 정리
    kill "$watchdog_pid" 2>/dev/null
    wait "$watchdog_pid" 2>/dev/null

    # 타임아웃 감지 (SIGTERM=143, SIGKILL=137)
    if [ $exit_code -eq 143 ] || [ $exit_code -eq 137 ]; then
        timed_out=true
        exit_code=124
        echo "ERROR: $engine timed out after ${ENGINE_TIMEOUT}s" > "$result_file"
        log "TIMEOUT $engine — killed after ${ENGINE_TIMEOUT}s"
    fi

    result=$(cat "$result_file")
    rm -f "$prompt_file" "$result_file"

    # 결과를 from_[engine].md에 저장
    local result_status="completed"
    [ "$timed_out" = true ] && result_status="timeout"
    {
        echo "---"
        echo "title: \"$title\""
        echo "engine: \"$engine\""
        echo "executed: \"$(date -u '+%Y-%m-%dT%H:%M:%SZ')\""
        echo "exit_code: $exit_code"
        echo "status: \"$result_status\""
        echo "---"
        echo ""
        echo "# 실행 결과"
        echo ""
        printf '%s\n' "$result"
    } > "$from_file"

    # to_ 파일 status → done
    set_status_done "$to_file"

    # Lock 해제
    rm -f "$lock_file"

    # Heartbeat 상태 갱신
    ENGINE_STATUS[$engine]="idle"
    ENGINE_LAST_TASK[$engine]="\"$(date -u '+%Y-%m-%dT%H:%M:%S+09:00')\""
    if [ $exit_code -ne 0 ]; then
        ERRORS_LAST_HOUR=$(( ERRORS_LAST_HOUR + 1 ))
    fi
    update_heartbeat

    log "DONE $engine — $title (exit: $exit_code)"
}

# ── 변경 이벤트 핸들러 ────────────────────────────────────

handle_change() {
    local name
    name=$(basename "$1")
    case "$name" in
        to_claude_code.md) run_engine "$TO_CC" "$FROM_CC" "claude_code" & ;;
        to_codex.md)       run_engine "$TO_CODEX" "$FROM_CODEX" "codex" & ;;
        to_antigravity.md)
            log "SKIP antigravity — GUI app, manual execution only"
            rm -f "$LOCK_DIR/antigravity.lock"
            return
            ;;
    esac
}

# ── 정리 ──────────────────────────────────────────────────

cleanup() {
    log "WATCHER STOPPED"
    # fswatch 등 자식 프로세스 정리
    pkill -P $$ 2>/dev/null
    rm -f "$LOCK_DIR"/*.lock 2>/dev/null
    rm -f "$HEARTBEAT_FILE" 2>/dev/null
}
trap cleanup EXIT INT TERM

# ── 의존성 확인 ───────────────────────────────────────────

if ! command -v fswatch &>/dev/null; then
    log "fswatch not found — installing via Homebrew..."
    brew install fswatch || { log "ERROR: fswatch 설치 실패"; exit 1; }
fi

# ── 메인 루프 ─────────────────────────────────────────────

# ── Heartbeat 루프 시작 (백그라운드) ────────────────────
start_heartbeat_loop &
HEARTBEAT_PID=$!

log "WATCHER STARTED — monitoring 3 engine files (heartbeat PID: $HEARTBEAT_PID)"
log "  → $TO_CC"
log "  → $TO_CODEX"
log "  → $TO_AG"

# ── startup scan: 재시작 전 pending 파일 감지 ─────────────

startup_scan() {
    log "STARTUP SCAN — checking for pending to_ files..."
    local pair to_f from_f eng
    for pair in "$TO_CC|$FROM_CC|claude_code" "$TO_CODEX|$FROM_CODEX|codex" "$TO_AG|$FROM_AG|antigravity"; do
        IFS='|' read -r to_f from_f eng <<< "$pair"
        if [ -f "$to_f" ]; then
            local status
            status=$(yaml_field "$to_f" "status")
            if [ "$status" = "pending" ]; then
                log "STARTUP FOUND pending — $eng"
                handle_change "$to_f"
            fi
        fi
    done
}

startup_scan

fswatch "$TO_CC" "$TO_CODEX" "$TO_AG" | while read -r changed_file; do
    sleep 0.5  # debounce
    handle_change "$changed_file"
done
