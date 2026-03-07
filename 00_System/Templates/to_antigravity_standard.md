---
title: "[작업 제목 — 동사+목적어로 구체적으로. 예: '포트폴리오 리밸런싱 시나리오 3개 비교 분석']"
engine: "[antigravity_sonnet | antigravity_opus | antigravity_gemini3pro]"
# 엔진 선택 기준:
#   sonnet  → 분석/요약/보통 추론 (기본값)
#   opus    → 심층 추론/복잡 설계/철학적 판단 (실제로 필요한 경우만)
#   gemini3 → 웹 리서치/최신정보/멀티모달
reason: "[엔진 선택 이유 — 'Opus 품질 필요'처럼 모호하게 쓰지 말 것. 예: '3개 시나리오 비교는 복잡 추론 필요, Sonnet으로 불충분']"
status: pending
priority: "[high | normal | low]"
created_by: brain
---

## 🎯 REASON (Brain 판단)

**왜 이 작업을 AG에 위임하는가:**
[구체적 이유. 예: "Finance 에이전트가 포트폴리오 데이터 접근 권한 있음"]

**기대 결과:**
[예: "3개 시나리오별 MDD/CAGR 비교표 + Brain 판단용 요약"]

**실패 시 Plan B:**
[예: "Codex로 수치만 계산 후 Brain이 직접 해석"]

---

## ▶️ ACT — 작업 지시

### 투입 에이전트 (선택 — 미입력 시 AG 자율 선발)
- [agent-id] — [역할]

### 작업 내용
[구체적이고 명확한 지시. 모호한 표현 금지 — Context Poisoning 방지]

### 출력 형식
[자유 서술 | 3-Layer(결론/논리/리스크) | 비교 분석 | 실행 계획]

### 제약
- GPT 최대: 4회
- Gemini 최대: 4회
- 기타: [특이사항]

---

## 🔍 OBSERVE — Brain 수신 후 확인 포인트

- [ ] [확인항목 1 — 예: 시나리오 3개 모두 포함됐는가]
- [ ] [확인항목 2 — 예: MDD 수치 근거 명시됐는가]
- [ ] [확인항목 3]
