# to_claude_code — D-5: Brain 관제 HUD + v3 IPC 프론트엔드 연결
*Created: 2026-03-01*
*Status: draft (D-4 완료 후 pending으로 전환)*
*Engine: CC (Hands-4)*

## 목표
D-4에서 추가된 v3 IPC 이벤트를 Renderer 쪽에서 수신하여 에이전트 캐릭터가 실시간 반응하고, Brain 관제 HUD 오버레이로 3팀 상태를 한눈에 보여준다.

## 사전 조건
- [ ] D-4 완료 (v3 IPC 이벤트가 main→renderer로 포워딩되는 상태)
- [ ] `npx tsc --noEmit` 통과 상태

## 프로젝트 경로
`/Users/woosung/Desktop/Dev/Woosdom_Brain/02_Projects/pixel-agents-woosdom`

## 태스크

### T1: IPCHandlers.ts — v3 이벤트 리스너 추가 (~5min)
- **파일:** `src/ipc/IPCHandlers.ts`
- **작업:**
  `setupIPCListeners()` 내에 새 이벤트 핸들러 추가. preload.ts에 이미 `onVaultToCC`, `onVaultFromCC`, `onVaultToAG`, `onVaultFromAG`, `onVaultFromCodex` 정의돼 있음. 활용할 것.

  1. **`onVaultToCC`** → Brain에 'communicating' 버블 + CC방으로 이동 + CC팀 전원 isActive=true
  2. **`onVaultFromCC`** → CC팀 전원 idle + Brain에 'done' 버블(3초)
  3. **`onVaultToAG`** → Brain에 'communicating' 버블 + AG방으로 이동 + AG팀 전원 isActive=true
  4. **`onVaultFromAG`** → AG팀 전원 idle + Brain에 'done' 버블
  5. **`onVaultFromCodex`** → Codex팀 전원 idle + Brain에 'done' 버블

  각 이벤트에 `EventLogStore.addEntry()` 기록 포함.
  
  **⚠️ 기존 `onVaultToHands` / `onVaultFromHands` 핸들러는 삭제하지 않고 유지** (하위호환).
  
- **검증:** `npx tsc --noEmit — 0 errors`
- **예상:** ~5min

### T2: BrainHUD 컴포넌트 생성 (~8min)
- **파일:** `src/components/BrainHUD.tsx` (신규)
- **작업:**
  캔버스 위 좌측 상단에 오버레이되는 미니 HUD 컴포넌트. 

  표시 정보:
  - **팀 상태 인디케이터**: CC 🟢/🔴, Codex 🟢/🔴, AG 🟢/🔴 (active/idle)
  - **활성 태스크 카운트**: 현재 isActive인 에이전트 수
  - **마지막 디스패치**: "CC 3분 전" / "AG 방금" 식의 상대 시간

  데이터 소스: `EventLogStore` 구독 (subscribe 패턴 사용, 이미 구현돼 있음).

  스타일:
  - `position: absolute; top: 8px; left: 8px`
  - 반투명 다크 배경 `rgba(0,0,0,0.7)`, 라운드 코너
  - 폰트 12px, 색상 #ccc / #e8a87c (기존 앱 톤)
  - 최소 크기: 가로 160px, 세로 auto

- **검증:** `npx tsc --noEmit — 0 errors`
- **예상:** ~8min

### T3: AppLayout에 BrainHUD 삽입 (~2min)
- **파일:** `src/components/AppLayout.tsx`
- **작업:**
  OfficeCanvas 위에 BrainHUD를 오버레이로 삽입.
  캔버스 컨테이너(`position: relative` 이미 있는 div) 안에 BrainHUD 배치.
  customizeMode 시에는 숨김.
- **검증:** `npx tsc --noEmit — 0 errors`
- **예상:** ~2min

### T4: ElectronAPI 타입 보강 (~2min)
- **파일:** `src/vite-env.d.ts` 또는 관련 타입 파일
- **작업:**
  `window.electronAPI`에 새 v3 메서드 타입이 반영되어 있는지 확인.
  preload.ts의 `ElectronAPI` 타입은 이미 export되고 있으므로, renderer 쪽에서 import 경로 확인.
  타입 에러가 있다면 수정.
- **검증:** `npx tsc --noEmit — 0 errors`
- **예상:** ~2min

### T5: 빌드 + 런타임 검증 (~3min)
- **검증 1:** `npx tsc --noEmit — 0 errors`
- **검증 2:** `npm run build — 빌드 성공`
- **검증 3:** `npm run dev`로 앱 실행 → 콘솔에 IPC 이벤트 로그 확인
- **예상:** ~3min

## 완료 시 행동
- [ ] from_claude_code.md에 결과 기록
- [ ] 변경 파일 목록 + 빌드 결과 보고

## brain_followup
D-5 완료 확인 후 → B-5 (.dmg 패키징) 즉시 위임.
런타임 E2E 검증(실제 to_claude_code.md 변경 → 캐릭터 반응)은 B-5 후 통합 테스트에서.
