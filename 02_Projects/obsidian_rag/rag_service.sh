#!/bin/bash
# Obsidian RAG 서비스 관리 스크립트
# 사용법: ./rag_service.sh {start|stop|status|restart|reindex}

RAG_DIR="/Users/woosung/Desktop/Dev/Woosdom_Brain/02_Projects/obsidian_rag"
SERVER_PLIST="$HOME/Library/LaunchAgents/com.woosdom.rag-server.plist"
WATCHER_PLIST="$HOME/Library/LaunchAgents/com.woosdom.rag-watcher.plist"

case "$1" in
  start)
    launchctl load "$SERVER_PLIST"
    launchctl load "$WATCHER_PLIST"
    echo "✅ RAG services started"
    sleep 2
    curl -s http://localhost:8100/ 2>/dev/null && echo "🟢 Server responding" || echo "⚠️ Server not yet ready (check logs)"
    ;;
  stop)
    launchctl unload "$SERVER_PLIST"
    launchctl unload "$WATCHER_PLIST"
    echo "⛔ RAG services stopped"
    ;;
  status)
    echo "=== launchctl 상태 ==="
    launchctl list | grep woosdom
    echo ""
    echo "=== API 서버 상태 ==="
    curl -s http://localhost:8100/ 2>/dev/null || echo "Server not responding"
    ;;
  restart)
    "$0" stop
    sleep 2
    "$0" start
    ;;
  reindex)
    echo "🔄 전체 볼트 재인덱싱 시작..."
    cd "$RAG_DIR"
    GEMINI_API_KEY="${GEMINI_API_KEY:?GEMINI_API_KEY 환경변수가 설정되지 않았습니다}" .venv/bin/python indexer.py
    ;;
  logs)
    TARGET="${2:-server}"
    echo "=== ${TARGET} stdout ==="
    tail -30 "$RAG_DIR/logs/${TARGET}_stdout.log" 2>/dev/null || echo "(비어 있음)"
    echo ""
    echo "=== ${TARGET} stderr ==="
    tail -20 "$RAG_DIR/logs/${TARGET}_stderr.log" 2>/dev/null || echo "(비어 있음)"
    ;;
  *)
    echo "사용법: $0 {start|stop|status|restart|reindex|logs [server|watcher]}"
    exit 1
    ;;
esac
