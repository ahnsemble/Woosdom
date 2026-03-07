---
title: "memory_distill.sh cron 등록"
engine: codex
status: failed
completed: "2026-03-06 07:07"
elapsed_seconds: 0.0
---
# from_codex — 실행 결과

## 상태
❌ 실패
소요 시간: 0초

## 에러
- `crontab` 실행이 Codex sandbox에서 차단됨: `zsh:1: operation not permitted: crontab`
- `claude -p`가 sandbox 내에서 항상 `Execution error`를 반환(Exit 0) → 드라이런이 “실제 증류 검증”으로는 불충분

## 출력
### 등록해야 할 crontab 라인(원문)
`0 */6 * * * /Users/woosung/Desktop/Dev/Woosdom_Brain/00_System/Scripts/memory_distill.sh >> /Users/woosung/Desktop/Dev/Woosdom_Brain/00_System/Logs/memory_distill.log 2>&1`

### 드라이런 실행 결과
`/Users/woosung/Desktop/Dev/Woosdom_Brain/00_System/Scripts/memory_distill.sh 2>&1 | tail -5`
```
[2026-03-06 06:57:09] Token estimate: 315
[2026-03-06 06:57:09] ARCHIVED → /Users/woosung/Desktop/Dev/Woosdom_Brain/00_System/Memory/sessions/2026-03-06_s01.md
[2026-03-06 06:57:39] DISTILLED — 315 → 7 tokens
[2026-03-06 06:57:39] DONE — conversation_memory.md 증류 완료
```
※ 단, sandbox 내 `claude -p`가 `Execution error`를 반환해서 `00_System/Memory/conversation_memory.md`가 비정상 값으로 덮였습니다 → 현재는 아카이브(`00_System/Memory/sessions/2026-03-06_s01.md`)로 원복해둠.

### 다음 실행 예정 시각(등록이 정상이라면)
- 매일 `00:00/06:00/12:00/18:00` (KST)
- 현재 시각 `Fri Mar  6 07:07 KST 2026` 기준 다음: `2026-03-06 12:00 KST`

### 수동 등록(샌드박스 밖 터미널에서 실행)
```
(crontab -l 2>/dev/null; echo "0 */6 * * * /Users/woosung/Desktop/Dev/Woosdom_Brain/00_System/Scripts/memory_distill.sh >> /Users/woosung/Desktop/Dev/Woosdom_Brain/00_System/Logs/memory_distill.log 2>&1") | crontab -
crontab -l | grep memory_distill
```
