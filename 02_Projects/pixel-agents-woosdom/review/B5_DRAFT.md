# to_claude_code — B-5: .dmg 패키징 + 통합 E2E 검증
*Created: 2026-03-01*
*Status: draft (D-5 완료 후 pending으로 전환)*
*Engine: CC (Hands-4)*

## 목표
Pixel Agents Woosdom을 macOS .dmg로 패키징하여 더블클릭 설치 가능한 상태로 만들고, 전체 E2E 동작을 검증한다.

## 사전 조건
- [ ] D-5 완료 (v3 IPC + BrainHUD 빌드 통과)
- [ ] `npm run build` 성공 상태

## 프로젝트 경로
`/Users/woosung/Desktop/Dev/Woosdom_Brain/02_Projects/pixel-agents-woosdom`

## 태스크

### T1: electron-builder 설정 점검 (~2min)
- **파일:** `electron-builder.yml`, `package.json`
- **작업:**
  1. `electron-builder.yml`이 현재 상태로 빌드 가능한지 확인
  2. `files` 패턴에 `config/` 디렉토리 포함 확인 (layout.json, app-config.json 필요)
  3. `asar: true` 상태에서 chokidar가 외부 파일 감시 가능한지 확인
     - chokidar는 Electron 메인 프로세스에서 실행 → asar 외부 → 문제 없음
  4. assets 폴더(스프라이트, 타일셋) 포함 확인
     - `src/assets/` → Vite 빌드 시 `dist/assets/`로 복사되는지 확인
     - 안 되면 `electron-builder.yml`의 `files`에 `src/assets` 또는 `dist/assets` 추가
- **검증:** 설정 파일 리뷰 완료
- **예상:** ~2min

### T2: 빌드 + 패키징 실행 (~5min)
- **작업:**
  ```bash
  cd /Users/woosung/Desktop/Dev/Woosdom_Brain/02_Projects/pixel-agents-woosdom
  npm run package
  ```
  이 명령은 `npm run build && electron-builder` 실행.
- **검증:** `release/` 디렉토리에 .dmg 파일 생성 확인
- **예상:** ~5min (빌드 시간 포함)

### T3: 빌드 에러 대응 (조건부, ~5min)
- **작업:**
  T2에서 에러 발생 시 대응:
  - `files` 패턴 누락 → `electron-builder.yml` 수정
  - 타입 에러 → `npx tsc --noEmit`으로 에러 위치 확인 → 수정
  - code signing 에러 → `"mac": { "identity": null }` 추가 (로컬 빌드용)
  - assets 미포함 → `extraResources` 또는 `extraFiles` 설정 추가
- **검증:** `npm run package` 재실행 → .dmg 생성
- **예상:** ~5min (에러 있을 때만)

### T4: .dmg 산출물 확인 (~2min)
- **작업:**
  1. `ls -la release/*.dmg` → 파일 존재 + 크기 확인
  2. `release/` 내 .dmg 파일명과 버전 확인
- **검증:** .dmg 파일 존재, 크기 > 50MB (Electron 앱 최소 크기)
- **예상:** ~2min

## 완료 시 행동
- [ ] from_claude_code.md에 결과 기록
- [ ] .dmg 파일 경로 + 크기 보고
- [ ] 에러가 있었다면 수정 내역 보고

## brain_followup
B-5 완료 확인 후:
1. 사용자에게 .dmg 설치 + 런타임 E2E 테스트 요청:
   - .dmg 더블클릭 → 앱 실행
   - task_bridge 실행 상태에서 to_claude_code.md 변경 → 캐릭터 반응 확인
   - BrainHUD 표시 확인
2. active_context.md 업데이트 (D-4~D-5 + B-5 완료)
