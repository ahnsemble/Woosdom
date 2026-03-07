# Woosdom Monitor v2 — 설계 스펙
*Created: 2026-03-03*
*Status: 설계 중 — Brain 승인 후 CC 위임*
*Base: ARCHITECTURE.md v1.2 (Jinja2 + 패널 자동 디스커버리)*

---

## 개요

픽셀 에이전트 HQ 아카이브 → 커맨드 센터 리디자인. WorldMonitor OSINT 미학 + Intelligence Gap Reporting 통합.

### 디자인 언어

| 항목 | 값 |
|------|-----|
| 테마 | 다크 기본 (#0d0d1a 배경) |
| 헤딩 폰트 | IBM Plex Sans (700) |
| 본문/데이터 폰트 | JetBrains Mono (400/500) |
| 액센트 | #4ecdc4 (틸) |
| 카드 스타일 | 둥근 모서리 (8px), 미묘한 보더 (#252545), 그림자 최소 |
| 그리드 | 2-column (1024px+), 1-column (모바일) |
| 정보 밀도 | 높음 — 스크롤 최소화, 한 화면에 핵심 메트릭 전부 |

---

## 6패널 구조

### P1: system-status (half)

엔진 4개의 실시간 상태 카드.

```
┌─ Brain (Claude Opus 4.6) ──┐  ┌─ Claude Code ──────────────┐
│ ● ONLINE                   │  │ ● ONLINE                   │
│ 연속 실패: 0/3             │  │ 오늘: 5건 / 평균 45초      │
│ 일일 콜백: 12/30           │  │ 총 턴: ~120                │
│ Sub-Brain: STANDBY         │  │                            │
└────────────────────────────┘  └────────────────────────────┘
┌─ Codex ────────────────────┐  ┌─ Antigravity ──────────────┐
│ ● ONLINE                   │  │ ● IDLE (12h)               │
│ 오늘: 2건                  │  │ 오늘: 0건                  │
└────────────────────────────┘  └────────────────────────────┘
```

**데이터:**
- brain_callback: failover_status (consecutive_failures, threshold)
- brain_callback: daily_stats (calls_made, calls_remaining)
- cost_monitor: 엔진별 tasks, total_seconds
- task_bridge 프로세스 alive 여부

**WorldMonitor P3 적용:**
- 연속 실패 카운터 시각화 (0/3 → 1/3 🟡 → 2/3 🟠 → 3/3 🔴)
- 3/3 도달 시 Brain 카드 배경 빨간색 + "Sub-Brain 인수 대기" 텍스트
- 엔진 상태: ONLINE(🟢) / IDLE(⚪ N시간) / ERROR(🔴) / OFFLINE(⚫)

**파서:** `parsers/system.py`
- .cost_stats.json 읽기
- brain_callback.get_failover_status() (또는 JSON export)
- task_bridge 프로세스 존재 여부 (pgrep)

---

### P2: agent-grid (half)

39개 에이전트 컴팩트 그리드. 부서별 그룹핑.

```
Operations (5)
  foreman    T1  ● 10m   🟢
  dispatcher T2  ● 2h    🟢
  scheduler  T2  ● 5h    🟢
  escalation T3  ○ never ⚪
  life-integ T3  ○ never ⚪

QA (4)
  critic     T1  ● 3d    🔴 STALE
  tester     T2  ● 1d    🟡
  ...
```

**WorldMonitor P1 적용 — Intelligence Gap Reporting:**

| 신선도 | 조건 | 아이콘 | 의미 |
|--------|------|--------|------|
| Fresh | 24h 이내 활동 | 🟢 | 정상 |
| Aging | 24~72h 미활동 | 🟡 | 주의 — 곧 stale |
| Stale | 72h+ 미활동 | 🔴 | 경고 — 에이전트 미사용 또는 장애 |
| Never | 활동 이력 없음 | ⚪ | 스펙만 존재, 아직 한 번도 실행 안 됨 |

**그리드 상단 요약:**
```
39 agents | 🟢 12 Fresh | 🟡 3 Aging | 🔴 2 Stale | ⚪ 22 Never
```

**데이터:**
- agent_activity.md 파싱 (에이전트별 마지막 활동 시각)
- 00_System/Specs/agents/*.md (에이전트 메타: 부서, 티어)

**파서:** `parsers/agents.py`
- agents/*.md frontmatter 읽기 (이름, 부서, 티어)
- agent_activity.md에서 last_seen 추출
- 현재 시각 대비 신선도 계산

---

### P3: activity-feed (full)

최근 엔진 실행 로그. 터미널 스타일 모노스페이스.

```
21:05  CC   ✅ GitHub Day 3 Push              81c3c57   45s
21:00  CC   ⚠️ git push blocked (safety)      —         —
20:30  CC   ✅ rsync task_bridge               —         12s
19:45  CB   ✅ Brain callback DONE             depth=0   3s
18:20  CC   ✅ Sprint 8 E2E-A5                 chain     70s
```

**칼럼:** 시각 | 엔진 | 상태 | 설명 | 참조 | 소요시간

**데이터:**
- /tmp/woosdom-taskbridge.log 최근 50~100줄 파싱
- chain_execution.log (체인 이력)

**파서:** `parsers/activity.py`
- 로그 파일 tail 읽기
- 정규식으로 구조화 (시각, 엔진, 상태, 메시지)

---

### P4: sprint (half)

현재 Sprint 진행 상황 + 완료 카운트.

```
Sprint 8: Agent Chaining          ████████████████░░ 90%
  ✅ 완료: 8  |  🔄 진행: 1  |  ⬜ 대기: 0

최근 완료:
  • E2E-A5 풀 체인 성공 (3/3)
  • Hotfix-2 state 리셋 (3/3)
  • T1 스펙 7개 수정 (3/3)
```

**데이터:**
- active_context.md "진행 중" 섹션 파싱

**파서:** `parsers/obsidian.py` (기존 확장)

---

### P5: portfolio (half)

Trinity v5 현재 비율 vs 목표 비율 + 드리프트.

```
Trinity v5 Portfolio
┌──────┬────────┬────────┬─────────┐
│ ETF  │ Target │ Actual │ Drift   │
├──────┼────────┼────────┼─────────┤
│ SCHD │  35%   │  34.2% │  -0.8%  │
│ QQQM │  15%   │  15.8% │  +0.8%  │
│ SMH  │  10%   │  10.1% │  +0.1%  │
│ SPMO │  10%   │   9.5% │  -0.5%  │
│ TLT  │  10%   │  10.3% │  +0.3%  │
│ GLDM │  20%   │  20.1% │  +0.1%  │
└──────┴────────┴────────┴─────────┘
다음 드리프트 점검: 2026-03-31 (D-28)
```

드리프트 ±10% 넘으면 해당 행 🔴 하이라이트.

**데이터:**
- 01_Domains/Finance/portfolio.json

**파서:** `parsers/portfolio.py` (기존)

---

### P6: cost (full)

엔진별 일일/월간 비용 트래킹.

```
💰 비용 현황 (2026-03-03)
┌────────────────┬───────┬────────┬──────────┬───────────┐
│ Engine         │ Tasks │ Turns  │ Seconds  │ 월 추정   │
├────────────────┼───────┼────────┼──────────┼───────────┤
│ Claude Code    │  5    │  ~120  │   225s   │ $35/$100  │
│ Codex          │  2    │  ~40   │   180s   │ $15/$200  │
│ Antigravity    │  0    │  0     │   0s     │ $0/$0     │
├────────────────┼───────┼────────┼──────────┼───────────┤
│ Brain Callback │  12   │  —     │   —      │           │
│ 위험 차단      │  1    │  —     │   —      │           │
└────────────────┴───────┴────────┴──────────┴───────────┘
월 상한: $300 | 현재: $50 (17%)
```

**데이터:**
- .cost_stats.json (일일)
- .cost_history/ (월간 누적)

**파서:** `parsers/cost.py`

---

## 구현 전략

ARCHITECTURE.md Phase 0~4 그대로 따르되, **패널 내용을 v2 6패널로 교체.**

### 실행 순서

| 단계 | 내용 | 위임 |
|------|------|------|
| 1 | 파서 6개 작성 (parsers/*.py) | CC |
| 2 | 패널 HTML 6개 (partials/*.html) | CC |
| 3 | 패널 CSS 6개 (panels/*.css) | CC |
| 4 | 패널 JS (activity-feed 스크롤, agent-grid 필터) | CC |
| 5 | build_dashboard.py v2 (Jinja2 자동 디스커버리) | CC |
| 6 | desktop.py window.state 통합 | CC |
| 7 | 통합 테스트 + .dmg 빌드 | CC |

### 우선순위

**MVP (1차):** system-status + agent-grid + activity-feed — 핵심 운영 모니터링
**2차:** cost + sprint — 비용/진행 관리
**3차:** portfolio — 재무 (데이터 축적 후 의미 있음)

---

## 레퍼런스

- WorldMonitor 패턴 로드맵: `02_Projects/woosdom_app/레퍼런스/worldmonitor-patterns-roadmap.md`
- 기존 ARCHITECTURE.md: `02_Projects/woosdom_app/ARCHITECTURE.md`
- 세션 #10 목업: A+B 하이브리드 (6패널, OSINT 미학, 다크테마)
