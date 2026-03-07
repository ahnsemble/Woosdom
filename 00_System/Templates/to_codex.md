---
title: "memory_distill.sh cron 등록"
engine: "codex"
reason: "crontab 수정 + 셸 스크립트 실행 테스트 — 로컬 시스템 설정 작업이므로 Codex"
brain_followup: "from_codex 수신 후:\n1. crontab 등록 성공 여부 확인\n2. 드라이런에서 에러 없는지 검증\n3. 성공이면 active_context \"memory_distill cron ✅\" 업데이트\n4. 실패 시 에러 원인 분석 후 수정 지시\n5. bridge 재시작 후 pending 파일 미감지 버그 → CC에 수정 위임 필요 여부 판단"
created: "2026-03-05T21:56:16.667Z"
status: pending
---

# 실행 지시서

## 작업: memory_distill.sh cron 등록

### 목표
`/Users/woosung/Desktop/Dev/Woosdom_Brain/00_System/Scripts/memory_distill.sh`를
**매 6시간마다 자동 실행**되도록 crontab에 등록.

### 실행 조건
- 스크립트 내부에 이미 "300토큰 이하면 SKIP" 로직 있음 → 안전하게 자주 돌려도 됨
- claude -p headless 실행 포함 → 6시간 간격이 적절

### 작업 순서

#### 1. 현재 crontab 확인
```bash
crontab -l 2>/dev/null || echo "crontab 없음"
```

#### 2. 스크립트 실행 권한 확인 및 부여
```bash
chmod +x /Users/woosung/Desktop/Dev/Woosdom_Brain/00_System/Scripts/memory_distill.sh
ls -la /Users/woosung/Desktop/Dev/Woosdom_Brain/00_System/Scripts/memory_distill.sh
```

#### 3. 드라이런 테스트
```bash
/Users/woosung/Desktop/Dev/Woosdom_Brain/00_System/Scripts/memory_distill.sh 2>&1 | tail -5
```

#### 4. crontab 등록 (중복 방지: 이미 있으면 스킵)
```bash
if crontab -l 2>/dev/null | grep -q "memory_distill"; then
  echo "이미 등록됨"
else
  (crontab -l 2>/dev/null; echo "0 */6 * * * /Users/woosung/Desktop/Dev/Woosdom_Brain/00_System/Scripts/memory_distill.sh >> /Users/woosung/Desktop/Dev/Woosdom_Brain/00_System/Logs/memory_distill.log 2>&1") | crontab -
  echo "등록 완료"
fi
```

#### 5. 등록 확인
```bash
crontab -l | grep memory_distill
```

### 완료 보고 (from_codex.md)
- 등록된 crontab 라인 전문
- 드라이런 결과 (SKIP or 증류 실행 여부)
- 다음 실행 예정 시각
- 실패 시: 에러 메시지 + 원인
