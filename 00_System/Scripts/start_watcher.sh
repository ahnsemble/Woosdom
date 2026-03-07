#!/bin/bash
# Woosdom Watcher — 데몬 시작
SCRIPTS_DIR="/Users/woosung/Desktop/Dev/Woosdom_Brain/00_System/Scripts"
PID_FILE="$SCRIPTS_DIR/watcher.pid"
WATCHER="$SCRIPTS_DIR/watcher.sh"

if [ -f "$PID_FILE" ]; then
    pid=$(cat "$PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
        echo "Watcher already running (PID: $pid)"
        exit 0
    else
        echo "Stale PID file found. Cleaning up..."
        rm -f "$PID_FILE"
    fi
fi

nohup "$WATCHER" > /dev/null 2>&1 &
disown
echo $! > "$PID_FILE"
echo "Watcher started (PID: $!)"
