---
title: "P2: 워치독/heartbeat + 대시보드 2차 통합"
engine: claude_code
status: done
completed: "2026-03-07 10:05"
elapsed_seconds: 369.5
---
# from_claude_code — 실행 결과

## 상태
✅ 성공
소요 시간: 369초

## 출력
## ✅ 완료 보고

**작업:** P2: 워치독/Heartbeat + 대시보드 2차 통합

**결과:**
- **watcher.sh** — 60초마다 `heartbeat.json` 갱신하는 백그라운드 루프 추가. 엔진 상태(active/idle), last_task, errors_last_hour 추적. 기존 핵심 로직 무변경.
- **watchdog.sh** (신규) — cron 5분 주기로 heartbeat 확인, 3분 이상 stale이면 watcher 재시작. 무한 재시작 방지(3회/시간 제한) + TG 알림 훅 포인트.
- **대시보드** — fleet-panel에 "System Health" 섹션 추가. Watcher 상태(alive/stale/dead), Uptime, Last Beat, Errors/hr 표시. CSS 토큰 준수.

**산출물:** `watcher.sh`, `watchdog.sh`(신규), `parsers/fleet.py`, `fleet-panel.html`, `fleet-panel.css`, `build_dashboard_v2.py`, `from_claude_code.md`

**이슈:** 없음

**turns 소모:** ~8/20

