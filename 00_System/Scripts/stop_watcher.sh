#!/bin/bash
# Woosdom Watcher — 데몬 중지
SCRIPTS_DIR="/Users/woosung/Desktop/Dev/Woosdom_Brain/00_System/Scripts"
PID_FILE="$SCRIPTS_DIR/watcher.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "Watcher is not running (no PID file)"
    exit 0
fi

pid=$(cat "$PID_FILE")
if kill -0 "$pid" 2>/dev/null; then
    kill "$pid"
    # 최대 3초 대기
    for i in 1 2 3; do
        sleep 1
        kill -0 "$pid" 2>/dev/null || break
    done
    # 여전히 살아있으면 강제 종료
    if kill -0 "$pid" 2>/dev/null; then
        kill -9 "$pid"
    fi
    echo "Watcher stopped (PID: $pid)"
else
    echo "Watcher process not found (PID: $pid). Cleaning up PID file."
fi

rm -f "$PID_FILE"
