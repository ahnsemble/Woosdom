# Pixel Agents Woosdom — B-1 코드 진단 보고서

**진단일:** 2026-03-01
**진단자:** Foreman (CC팀)
**대상 브랜치:** HEAD
**총 LOC:** ~4,009 (src + electron, config 제외)

---

## 1. 프로젝트 개요

### 기술 스택

| 레이어 | 기술 | 버전 |
|--------|------|------|
| 런타임 | Electron | 33.4.11 |
| UI 프레임워크 | React | 19.2.0 |
| 렌더링 | Canvas 2D API | — |
| 언어 | TypeScript | 5.9.3 |
| 빌드 | Vite | 7.3.1 (실행 시) |
| 파일 감시 | chokidar | 4.0.3 |
| 패키징 | electron-builder | 26.0.12 |

### 핵심 의존성

```
Runtime:  react@19.2.0, react-dom@19.2.0, chokidar@4.0.3
Dev:      electron, typescript, vite, vite-plugin-electron, vite-plugin-electron-renderer
Optional: pngjs (설치됨, 현재 미사용), @types/pngjs
```

### 빌드 구조

```
pixel-agents-woosdom/
├── src/              React + Canvas 게임 로직 (TypeScript)
│   ├── agents/       AgentDefinition 타입
│   ├── canvas/       렌더러, 캐릭터 FSM, 경로탐색
│   ├── components/   React UI 컴포넌트
│   ├── config/       Layout I/O + 타입
│   ├── contexts/     AppContext (전역 UI 상태)
│   ├── editor/       편집기 상태/액션/TilePalette
│   ├── input/        InputManager (클릭, 휠)
│   ├── ipc/          IPC 이벤트 핸들러
│   ├── loaders/      AssetLoader
│   ├── state/        EventLogStore (Observable)
│   └── types/        EventLog 타입
├── electron/         Electron 메인 프로세스
│   ├── main.ts       창 생성, IPC, 이벤트 라우팅
│   ├── preload.ts    contextBridge 보안 API
│   ├── windowState.ts 창 상태 영속성
│   └── watchers/     파일 감시 (Vault, CC, AG, Codex)
├── config/           layout.json, tileset-*.json
├── dist/             빌드 출력 (React)
└── dist-electron/    빌드 출력 (Electron 메인)
```

---

## 2. 아키텍처 분석

### Electron IPC 패턴

```
Main Process                    Renderer (React)
─────────────                   ────────────────
VaultWatcher ──┐
CCWatcher ─────┤
AGWatcher ─────┤→ EventBus → forwardToRenderer() ──→ ipcMain.send()
CodexWatcher ──┘                                        │
                                                        ↓
                                               preload.ts (contextBridge)
                                                        │
                                                        ↓
                                               window.electronAPI
                                                        │
                                                        ↓
                                               IPCHandlers.ts
                                               (game state mutations)
```

**채널 맵:**

| 채널 | 방향 | 용도 |
|------|------|------|
| `app:ready` | R→M | 렌더러 초기화 완료 신호 |
| `layout:read` | R→M (invoke) | layout.json 읽기 |
| `layout:write` | R→M (invoke) | layout.json 쓰기 |
| `vault:to-hands` | M→R | 팀에 작업 디스패치 |
| `vault:from-hands` | M→R | 팀 결과 보고 |
| `vault:to-codex` | M→R | Codex 작업 트리거 |
| `vault:active-context` | M→R | 컨텍스트 업데이트 |
| `agent:tool-start` | M→R | 에이전트 도구 시작 |
| `agent:tool-done` | M→R | 에이전트 도구 완료 |
| `agent:status` | M→R | 에이전트 idle/active |

### React 컴포넌트 계층

```
App
└── AppContextProvider          (전역 UI 상태: selectedAgent, customizeMode)
    └── AppLayout               (주 레이아웃 + 편집기 툴바 + 패널)
        ├── OfficeCanvas        (캔버스 초기화 + 게임 루프 + IPC 수신)
        │   └── [GameLoop, IPCHandlers, InputManager - 비컴포넌트]
        ├── EditorToolbar       (customizeMode=true 시 표시)
        │   └── TilePalette     (타일/가구 선택 UI)
        ├── ActivityLogPanel    (EventLogStore 구독, panelView='log')
        └── AgentDetailPanel    (selectedAgent 시 표시, panelView='agent')
```

### 상태 관리

| 레이어 | 상태 | 관리 방식 |
|--------|------|-----------|
| 전역 UI | selectedAgent, customizeMode, panelView | React Context (AppContext) |
| 이벤트 로그 | entries[] (max 200) | 싱글톤 Observable (EventLogStore) |
| 레이아웃 | layoutConfig | 싱글톤 캐시 (LayoutLoader) |
| 캐릭터 위치/상태 | Character[] | ref (OfficeCanvas → charactersRef) |
| 편집기 | tool, selectedTile, dirty | 로컬 useState (AppLayout) |

**패턴 평가:**
- Context는 가볍게 사용 (UI 제어 신호만, 게임 상태 없음) → 적절
- 게임 루프 상태는 ref로 관리 (리렌더링 없음) → 올바른 선택
- EventLogStore Observable이 컴포넌트와 직접 연동 → 구조적으로 깔끔

### Canvas 렌더링 파이프라인

```
GameLoop.startGameLoop() [rAF]
│
├─ update(dt)
│  └─ characters.forEach(ch => updateCharacter(ch, dt, walkableTiles, ...))
│     └─ Character FSM (IDLE → WALK → TYPE)
│
└─ render(ctx)
   └─ Renderer.renderFrame(ctx, state, isCustomize)
      1. Clear (VOID_COLOR 배경)
      2. translate + scale (카메라 + 줌)
      3. renderFloors()          바닥 타일 (색 + 스프라이트)
      4. renderWalls()           벽 타일 (색 + 패턴/스프라이트)
      5. renderFurnitureAndCharacters()  Y-sort → 후방부터 렌더
      6. renderCharacterOverlays()      이름표 + 말풍선 (페이드)
      7. renderRoomLabels()             방 이름
      8. (customize) renderGridOverlay() + renderSeatMarkers()
```

**Y-Sort 방식:** 가구는 하단 엣지(y + sh), 캐릭터는 발 위치(y + TILE_SIZE) 기준.
**VX 타일:** 오버사이즈 VX 타일을 16×16 타일 경계로 축소 처리.

### 데이터 흐름 (이벤트 수신 → 화면 반영)

```
Obsidian Vault 파일 변경
  → chokidar (VaultWatcher/CCWatcher/AGWatcher/CodexWatcher)
  → EventBus.emit()
  → electron/main.ts: forwardToRenderer()
  → ipcRenderer.send() → contextBridge → window.electronAPI
  → src/ipc/IPCHandlers.ts
  → Character 상태 변경 (isActive, currentTool, bubbleType)
  → EventLogStore.addEntry()
  → ActivityLogPanel / AgentDetailPanel 리렌더
  → 다음 rAF에서 Renderer가 변경된 상태 반영
```

---

## 3. 코드 품질

### TypeScript Strict 여부

```json
// tsconfig.app.json
"strict": true,
"noUnusedLocals": true,
"noUnusedParameters": true,
"noFallthroughCasesInSwitch": true
```

**strict 완전 활성화.** tsconfig.node.json도 동일.

### any 사용

**0건.** 전 파일 검색 결과 `: any` 사용 없음.

### 에러 핸들링

| 위치 | 패턴 |
|------|------|
| AssetLoader.ts | `.catch(() => null)` (선택적 타일셋, 무음 실패) |
| OfficeCanvas.tsx | try/catch on IPC layout:read |
| CCWatcher.ts | try/catch on JSONL 파싱, JSON.parse |
| VaultWatcher.ts | try/catch on frontmatter 파싱 |
| electron/main.ts | try/catch on layout:read/write IPC handlers |
| InputManager.ts | 이벤트 핸들러 내 방어적 null 체크 |

### 코드 중복

| 패턴 | 위치 | 심각도 |
|------|------|--------|
| "readable tool" 목록 중복 정의 | `IPCHandlers.ts:READING_TOOLS` + `main.ts:mapToolToCCAgent` 내 패턴 매칭 | L |
| 타일셋 이름 → 인덱스 매핑 | AssetLoader + Renderer + OfficeCanvas에 산재 | M |
| 에이전트 role → 캐릭터 lookup | IPCHandlers 내 `characters.find(c => c.role === agentRole)` 반복 | L |

### 파일별 LOC

| 파일 | LOC |
|------|-----|
| src/canvas/Renderer.ts | 472 |
| src/editor/TilePalette.tsx | 335 |
| src/components/AppLayout.tsx | 295 |
| src/canvas/Characters.ts | 276 |
| src/components/AgentDetailPanel.tsx | 210 |
| src/ipc/IPCHandlers.ts | 195 |
| src/components/OfficeCanvas.tsx | 166 |
| electron/watchers/CCWatcher.ts | 148 |
| electron/watchers/VaultWatcher.ts | 115 |
| src/editor/EditorActions.ts | 136 |
| src/components/EditorToolbar.tsx | 117 |
| src/input/InputManager.ts | 100 |
| electron/watchers/CodexWatcher.ts | 100 |
| src/canvas/Pathfinding.ts | 97 |
| src/canvas/OfficeLayout.ts | 99 |
| 기타 (소형 파일) | ~500 |
| **합계** | **~4,009** |

---

## 4. 기술 부채 목록

| # | 위치 | 문제 | 심각도 | 수정 난이도 |
|---|------|------|--------|-------------|
| 1 | `AssetLoader.ts` | 타일셋 로드 실패 무음 처리 — 사용자가 자산 누락을 인지 못함 | M | L (로그 추가) |
| 2 | `electron/main.ts` | HMR debounce 로직(`app:ready` 중복 방지)이 magic number 500ms 하드코딩 | L | L (상수화) |
| 3 | `OfficeCanvas.tsx` | 레이아웃 폴백 fetch가 `/config/layout.json`을 하드코딩 — dev 전용 경로 | M | M (환경 분기) |
| 4 | `src/ipc/IPCHandlers.ts` | `READING_TOOLS` 상수가 IPC 핸들러 파일 내부에 인라인 — `electron/main.ts`의 도구 분류 로직과 이중 관리 | M | M (공유 상수로 분리) |
| 5 | `Renderer.ts` | `renderWalls()` 벽 패턴 사이클링 인덱스가 row/col modulo로 계산 — 창 리사이즈 시 패턴이 시프트될 수 있음 | L | M |
| 6 | `Characters.ts` | 캐릭터 `wanderLimit` (5)이 하드코딩 — 에이전트별 성격 반영 불가 | L | L (AgentDef에 추가) |
| 7 | `Pathfinding.ts` | BFS만 구현 — 대형 맵에서 성능 열화 가능성 (현재 맵 크기에선 무관) | L | H (A* 대체) |
| 8 | `VaultWatcher.ts` | vault 경로가 하드코딩 (`/Users/woosung/Desktop/Dev/Woosdom_Brain`) — 이식성 없음 | M | M (설정 파일/환경변수화) |
| 9 | `pngjs` 의존성 | 설치됨 + `@types/pngjs` 있으나 실제 사용 없음 — 번들 크기 영향 없으나 혼란 유발 | L | L (제거) |
| 10 | `AppLayout.tsx` | `handleEditorTileClick`이 295줄 컴포넌트 내부에 인라인 — 컴포넌트 과비대 | M | M (EditorActions로 위임) |
| 11 | `EventLogStore.ts` | 중복 제거 로직이 10초 타임윈도우 기반 — 빠른 연속 동일 이벤트가 드롭될 수 있음 | L | L (임계값 조정 또는 설정화) |
| 12 | `electron-builder.yml` | `files` 섹션이 `!**/*` 후 dist 포함 — asar true로 패키징되나 VX Ace 타일셋 5개가 dist/assets에 번들 (합계 ~44KB, 미미함) | L | L |

---

## 5. 확장성 평가

### 새 에이전트/방 추가

**용이성: 높음.**

```
1. config/layout.json: agents[] 배열에 항목 추가
   { "id": "new_agent", "role": "new_role", "seatId": "seat_X", "spriteRow": N, ... }
2. layout.json: seats[] 배열에 좌석 추가
3. (선택) electron/watchers에서 role 매핑 확인
```

AgentDefs는 layout.json의 agents[]에서 동적 로드 — 코드 수정 불필요.
방 추가도 layout.json rooms[] 배열 편집만으로 가능.

### 외부 데이터 연동

**현재 구조:**
- 파일 감시 기반 (chokidar) → 파일 I/O 이벤트만 지원
- WebSocket/REST API 연동 구조 없음

**연동 시 필요 작업:**
- `electron/watchers/`에 새 Watcher 추가 (e.g., `WebSocketWatcher.ts`)
- EventBus에 새 이벤트 타입 등록
- `main.ts`: `setupEventForwarding()`에 새 채널 추가
- `preload.ts`: 새 listener 노출
- `IPCHandlers.ts`: 새 이벤트 처리 추가

구조가 확장을 고려해 설계됨 — Watcher 패턴이 일관적이어서 새 소스 추가가 용이.

### woosdom_app 통합 가능성

**평가: 중간 수준의 작업 필요.**

| 항목 | 현황 | 통합 방법 |
|------|------|-----------|
| 레이아웃 공유 | layout.json 파일 직접 읽기 | IPC API 이미 추상화됨 → 공유 경로 설정으로 해결 가능 |
| 이벤트 공유 | 파일 기반 (Vault .md) | 공유 SQLite/pub-sub 추가 필요 |
| 스프라이트 에셋 | 로컬 번들 | 에셋 서버 또는 공유 경로 필요 |
| 에이전트 정의 | layout.json 내부 | 외부 JSON/DB로 분리 권장 |

---

## 6. 버그/이슈

### 기존 알려진 이슈

| # | 이슈 | 상태 |
|---|------|------|
| B1 | Canvas fit-to-screen (줌 리셋) | 코드 확인: `InputManager.ts`의 resize 핸들러가 `centerCamera()`를 호출하나, zoom 레벨을 fitted zoom으로 재계산하는 로직이 있음. 상세 동작 확인 필요 |
| B2 | Activity Log 동작 이슈 | `EventLogStore.addEntry()`의 10초 중복 제거가 의도치 않게 정상 이벤트를 드롭할 가능성 있음 |
| B3 | 식물 타일 이슈 | TilePalette의 VX Ace 타일 렌더링 — `renderFrame`에서 VX 타일을 16×16으로 축소하는 로직이 있으나 원본 크기 불일치 시 비율 왜곡 가능 |

### 새로 발견된 잠재 이슈

| # | 위치 | 이슈 | 심각도 |
|---|------|------|--------|
| N1 | `OfficeCanvas.tsx:~80` | HMR 환경에서 IPC 리스너가 중복 등록될 수 있음 — `app:ready` 디바운스가 주 프로세스 보호하지만 렌더러 측 cleanup 의존성 주의 | M |
| N2 | `Characters.ts` | 캐릭터가 경로 없음(BFS 실패) 시 조용히 IDLE로 전환 — 디버그 로그 없음 | L |
| N3 | `Renderer.ts:renderSpeechBubble` | 말풍선 텍스트가 긴 도구 이름에서 버블 경계를 넘칠 수 있음 (min 60px width 있으나 max 없음) | L |
| N4 | `AgentDetailPanel.tsx` | 2초 interval 타이머가 panelRefreshCounter 의존 — selectedAgent null 시에도 타이머 유지됨 | L |
| N5 | `LayoutLoader.ts:getFloorColor` | 어떤 방에도 속하지 않는 타일이 hallway 색을 반환 — hallway 바깥 VOID 타일도 동일 처리 | L |

---

## 7. 리팩토링 우선순위

| 순위 | 작업 | 이유 | 예상 공수 |
|------|------|------|-----------|
| 1 | `READING_TOOLS` 상수 공유화 (부채 #4) | `IPCHandlers.ts`와 `main.ts` 이중 관리 → 도구 추가 시 누락 위험 | 0.5h |
| 2 | vault 경로 설정 파일화 (부채 #8) | 하드코딩된 개인 경로 → 이식성 제로, 협업/배포 시 문제 | 1h |
| 3 | `AppLayout.tsx` 분리 (부채 #10) | 295줄 컴포넌트에 편집기 상태/핸들러 혼재 → EditorContext 또는 커스텀 훅으로 분리 | 2h |
| 4 | `AssetLoader.ts` 실패 가시화 (부채 #1) | 자산 로드 실패 무음 처리 → 최소한 console.warn 추가 | 0.5h |
| 5 | `pngjs` 의존성 제거 (부채 #9) | 미사용 의존성 정리 | 0.25h |
| 6 | HMR `app:ready` magic number 상수화 (부채 #2) | 가독성 + 유지보수성 | 0.25h |
| 7 | 말풍선 max-width 처리 (이슈 N3) | 긴 도구명 시 UI 깨짐 방지 | 0.5h |
| 8 | AgentDetailPanel 타이머 조건화 (이슈 N4) | selectedAgent null 시 불필요한 타이머 실행 방지 | 0.25h |

**총 예상 공수: ~5.25h (B-2 작업 후보)**

---

## 8. 빌드 결과

```
$ npm run build 2>&1 | tail -30

vite v7.3.1 building client environment for production...
transforming...
✓ 67 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                                         0.51 kB │ gzip:  0.35 kB
dist/assets/A4 Office Walls-USHmevyC.png                5.54 kB
dist/assets/A2 Office Floors-B_XYiiUc.png               9.46 kB
dist/assets/B-C-D-E Office 1 No Shadows-dOqzC7vX.png   12.89 kB
dist/assets/B-C-D-E Office 2 No Shadows-jWzHQ_gt.png   16.85 kB
dist/assets/tileset2-W3z_ctH-.png                      17.04 kB
dist/assets/tileset-LBzoEltP.png                       20.63 kB
dist/assets/tileset-vx-map-Dq93cMfF.json               81.92 kB │ gzip:  2.58 kB
dist/assets/tileset-map-COBSC_8Y.json                  87.26 kB │ gzip:  6.67 kB
dist/assets/layout-CfZOtAPy.json                      114.08 kB │ gzip:  6.05 kB
dist/assets/tileset2-map-BmjaDU8d.json                117.31 kB │ gzip:  8.67 kB
dist/assets/sprites-C6ksP6yR.png                      179.18 kB
dist/assets/index-C__QKEAX.js                         241.56 kB │ gzip: 76.34 kB
✓ built in 333ms

vite v7.3.1 building client environment for production...
transforming...
✓ 10 modules transformed.
rendering chunks...
computing gzip size...
dist-electron/main.js  32.87 kB │ gzip: 11.50 kB
✓ built in 36ms

vite v7.3.1 building client environment for production...
transforming...
✓ 1 modules transformed.
rendering chunks...
computing gzip size...
dist-electron/preload.js  0.66 kB │ gzip: 0.33 kB
✓ built in 3ms
```

**결과: 빌드 성공. 에러/경고 없음.**

빌드 산출물:
- `dist/assets/index-*.js`: 241.56 kB (gzip 76.34 kB) — React + 게임 로직
- `dist-electron/main.js`: 32.87 kB — Electron 메인 프로세스
- `dist-electron/preload.js`: 0.66 kB — contextBridge 브릿지

---

*보고서 작성: Foreman (CC팀) — Track B-1 완료*
