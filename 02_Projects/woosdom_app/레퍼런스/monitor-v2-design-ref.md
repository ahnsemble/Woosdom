# Woosdom Monitor v2 — 디자인 레퍼런스
*Created: 2026-03-03*

## 컨셉 목업
- `woosdom_app/레퍼런스/monitor-v2-mockup.html` — A+B 하이브리드 목업 (Brain 제작)

## 디자인 방향: Grafana × WorldMonitor 하이브리드
- **레이아웃**: Grafana 스타일 카드 그리드
- **미학**: WorldMonitor OSINT 커맨드 센터 다크 톤
- **폰트**: JetBrains Mono (데이터) + IBM Plex Sans (본문)
- **컬러**: 다크 기본 (#0a0e17), 상태 색상(초록/노랑/빨강), 시안 액센트

## 6패널 구성
1. Agent Grid — 부서별 에이전트 카드, 상태 점, Intelligence Gap 경고
2. Activity Feed — 실시간 체인/위임/완료 로그, LIVE 인디케이터
3. System Status — 업타임, Brain 콜백 잔여, Bridge 버전, Failover 상태
4. Sprint Tracker — 현재 스프린트 진행률 + 태스크 체크리스트
5. Portfolio — 배분 비율 바 차트, 드리프트 경고
6. Cost Monitor — 엔진별 월간 비용 바, 잔여 예산

## 핵심 UI 요소
- 헤더 승계 레벨 뱃지: `L0 NOMINAL` (초록) → `L2 SUB-BRAIN` (빨강 깜빡임)
- 엔진 상태 필: CC/Codex/AG/TG Bot 각각 on/off 점
- 미세 스캔라인 + 노이즈 오버레이 (커맨드 센터 질감)
