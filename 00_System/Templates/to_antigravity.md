---
title: "대시보드 레퍼런스 영상 분석 — ScreenRecording 03-06-2026"
engine: "antigravity_sonnet"
reason: "로컬 .mov 영상 파일의 UI/UX 시각적 분석이 필요. AG(Sonnet)는 멀티모달 + 시각 검증 담당."
brain_followup: "from_antigravity 수신 후:\n1. 분석 결과를 현재 woosdom_app 대시보드 구조와 대조\n2. 적용 가치 있는 UI 패턴 → 개선 사항으로 active_context에 기록\n3. 변경 범위가 크면 별도 Phase로 등록 여부 판단\n4. woosdom_app 대시보드 현황 파악 필요 시 02_Projects/woosdom_app/ 먼저 확인"
created: "2026-03-05T21:26:38.936Z"
status: completed
---

# 실행 지시서

## 작업: 대시보드 레퍼런스 영상 분석

### 대상 파일
`/dev/ScreenRecording_03-06-2026 06-23-21_1.mov`

### 분석 목적
이 영상은 Instagram Reel에서 가져온 **대시보드/HUD UI 레퍼런스**입니다.
현재 우즈덤 시스템의 `woosdom_app/` PyWebView 대시보드 변경을 검토 중이며, 이 영상의 UI를 참고하려 합니다.

### 분석 항목 (영상을 보면서 캡처/메모)
1. **전체 레이아웃** — 몇 개의 패널? 그리드 구조? 사이드바 유무?
2. **핵심 UI 컴포넌트** — 카드, 차트, 리스트, 프로그레스바 등 어떤 요소?
3. **색상 테마** — 다크모드? 라이트모드? 주요 accent 색상?
4. **인터랙션 패턴** — 클릭, 드래그, 실시간 업데이트 등 보이는 동작?
5. **워크플로우/에이전트 상태 표시 방식** — 태스크 현황, 진행률, 알림 표시 방법?
6. **현재 woosdom_app과의 차이점** — 현재 대시보드 대비 눈에 띄는 차별점?

### 결과 형식 (from_antigravity.md에 작성)
- 항목별 간단한 설명 + 주목할 UI 패턴 3~5개
- "woosdom에 적용할 수 있는 요소" vs "불필요/과잉인 요소" 분류
- 전반적인 인상 한 줄 요약

### 주의
- 영상이 길면 처음 30초 + 핵심 장면만 캡처해도 됩니다
- .mov 파일이 재생 불가한 경우, 해당 사실과 대안(ffmpeg 프레임 추출 등)을 보고해 주세요
