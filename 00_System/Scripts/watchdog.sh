#!/bin/bash
# Woosdom Watchdog — watcher.sh 생존 감시
# cron으로 5분마다 실행: */5 * * * * /Users/woosung/Desktop/Dev/Woosdom_Brain/00_System/Scripts/watchdog.sh
#
# heartbeat.json의 last_beat가 3분 이상 지났으면:
#   1. watcher.sh PID 확인 → 죽었으면 재시작
#   2. watchdog.log에 이벤트 기록
#   3. TG 알림 훅 포인트 마련

VAULT="/Users/woosung/Desktop/Dev/Woosdom_Brain"
SCRIPTS_DIR="$VAULT/00_System/Scripts"
LOGS="$VAULT/00_System/Logs"
HEARTBEAT_FILE="$LOGS/heartbeat.json"
WATCHDOG_LOG="$LOGS/watchdog.log"
WATCHER_SCRIPT="$SCRIPTS_DIR/watcher.sh"
STALE_THRESHOLD=180  # 3분 (초)
MAX_RESTARTS_PER_HOUR=3
RESTART_COUNTER_FILE="$SCRIPTS_DIR/.watchdog_restart_count"

# ── 로깅 ──────────────────────────────────────────────────

wdlog() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] [watchdog] $*"
    echo "$msg" >> "$WATCHDOG_LOG"
}

# ── TG 알림 훅 ────────────────────────────────────────────
# 외부에서 이 함수를 오버라이드하거나, 여기에 curl 호출을 추가하세요
notify_hook() {
    local event="$1" message="$2"
    # 예: curl -s "https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage" \
    #       -d chat_id="${TG_CHAT_ID}" -d text="[Watchdog] $message" > /dev/null
    :  # no-op — 필요 시 활성화
}

# ── 무한 재시작 루프 방지 ──────────────────────────────────

check_restart_limit() {
    local now
    now=$(date +%s)

    if [ -f "$RESTART_COUNTER_FILE" ]; then
        local last_hour count
        read -r last_hour count < "$RESTART_COUNTER_FILE"
        local elapsed=$(( now - last_hour ))

        if [ "$elapsed" -lt 3600 ]; then
            if [ "$count" -ge "$MAX_RESTARTS_PER_HOUR" ]; then
                wdlog "ERROR: restart limit reached ($MAX_RESTARTS_PER_HOUR/hour). Skipping restart."
                notify_hook "restart_limit" "Watcher restart limit reached ($count/$MAX_RESTARTS_PER_HOUR per hour). Manual intervention required."
                return 1
            fi
            echo "$last_hour $(( count + 1 ))" > "$RESTART_COUNTER_FILE"
        else
            echo "$now 1" > "$RESTART_COUNTER_FILE"
        fi
    else
        echo "$now 1" > "$RESTART_COUNTER_FILE"
    fi
    return 0
}

# ── 메인 로직 ─────────────────────────────────────────────

main() {
    # heartbeat.json이 없으면 → watcher가 한 번도 안 돌았거나 죽음
    if [ ! -f "$HEARTBEAT_FILE" ]; then
        wdlog "WARN: heartbeat.json not found — watcher may have never started"

        # watcher 프로세스가 실제로 돌고 있는지 확인
        if pgrep -f "watcher.sh" > /dev/null 2>&1; then
            wdlog "INFO: watcher.sh process found running (no heartbeat yet)"
            return 0
        fi

        wdlog "ALERT: watcher.sh not running, no heartbeat file"
        if check_restart_limit; then
            restart_watcher
        fi
        return
    fi

    # last_beat 파싱 (python/perl 없이 순수 bash)
    local last_beat
    last_beat=$(grep '"last_beat"' "$HEARTBEAT_FILE" 2>/dev/null | sed 's/.*: *"\(.*\)".*/\1/')

    if [ -z "$last_beat" ]; then
        wdlog "ERROR: failed to parse last_beat from heartbeat.json"
        return 1
    fi

    # last_beat를 epoch으로 변환
    local last_epoch now_epoch
    last_epoch=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${last_beat%%+*}" +%s 2>/dev/null)
    now_epoch=$(date +%s)

    if [ -z "$last_epoch" ]; then
        wdlog "ERROR: failed to convert last_beat to epoch: $last_beat"
        return 1
    fi

    local age=$(( now_epoch - last_epoch ))

    if [ "$age" -gt "$STALE_THRESHOLD" ]; then
        wdlog "ALERT: heartbeat stale (${age}s old, threshold: ${STALE_THRESHOLD}s)"

        # PID 확인
        local stored_pid
        stored_pid=$(grep '"watcher_pid"' "$HEARTBEAT_FILE" 2>/dev/null | sed 's/[^0-9]//g')

        if [ -n "$stored_pid" ] && kill -0 "$stored_pid" 2>/dev/null; then
            wdlog "WARN: watcher PID $stored_pid exists but heartbeat stale — sending SIGTERM"
            kill "$stored_pid" 2>/dev/null
            sleep 2
        fi

        if check_restart_limit; then
            restart_watcher
        fi
    else
        # 정상 — 조용히 종료 (로그 스팸 방지)
        :
    fi
}

restart_watcher() {
    wdlog "ACTION: restarting watcher.sh..."
    notify_hook "restart" "Watcher restarted by watchdog"

    nohup bash "$WATCHER_SCRIPT" >> "$LOGS/watcher.log" 2>&1 &
    local new_pid=$!
    wdlog "ACTION: watcher.sh restarted (PID: $new_pid)"
}

# ── 실행 ──────────────────────────────────────────────────
main
