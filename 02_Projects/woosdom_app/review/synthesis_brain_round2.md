# Brain 종합 판단 — 2차 검증
*Date: 2026-02-25*
*Input: GPT Round 2 + Gemini Round 2*
*Target: ARCHITECTURE.md v1.2 + CLAUDE.md*
*Status: ✅ 완료*

---

## 점수 변화

| 엔진 | 1차 (v1.1) | 2차 (v1.2) | 변화 |
|------|-----------|-----------|------|
| GPT | 7.6/10 | 조건부 합격 (전 관점) | 방향은 인정, 세부 정밀도 요구 |
| Gemini | 8.5/10 | **9.5/10** | 대폭 상승, 거의 최종 승인 수준 |
| **Brain 종합** | **8.0/10** | **8.8/10** | 1차 대비 6개 지적 중 5개 해결 확인 |

---

## 1차 지적 6건 해결 상태

| # | 지적사항 | GPT 판정 | Gemini 판정 | Brain 최종 |
|---|---------|---------|------------|-----------|
| 1 | 렌더링 전략 충돌 | ✅ 해결 (API 예시 부정확 지적) | ✅ 해결 (중첩 객체 평탄화 추가 요구) | ✅ 해결, 세부 보완 필요 |
| 2 | 레지스트리 수동 동기화 | ✅ 해결 (엣지케이스 보완 필요) | ✅ 해결 (.DS_Store 등 필터 필요) | ✅ 해결 |
| 3 | file:// CORS 미반영 | ✅ 해결 | ✅ 해결 | ✅ 해결 |
| 4 | 회귀 검증 부재 | ✅ 해결 (HTML diff 노이즈 우려) | 직접 언급 없음 | ✅ 해결, 정규화 보완 |
| 5 | AI 규칙 파일 미비 | ⚠️ 조건부 (AGENTS.md 병행 권고) | ⚠️ 조건부 (300줄 다이어트 권고) | ⚠️ 조건부 |
| 6 | Scaffold 자동 생성 없음 | ✅ 해결 | ✅ 해결 | ✅ 해결 |

**5/6 해결, 1/6 조건부.** 1차 대비 대폭 개선.

---

## 2차에서 새롭게 발견된 리스크 (6건)

### 🔴 Critical (2건)

**C1. `window.state` 중첩 객체 반응성 상실**
- GPT + Gemini 양쪽 합의
- `window.state.nested_dict['key'] = value` → JS에 전파 안 됨 (Silent Failure)
- `dashboard_data`가 복잡한 중첩 구조이므로, 통째로 재할당하거나 **1-Depth 평탄화** 필요
- **조치:** parser.py → dashboard_data.json 출력 시 1-Depth 키 구조로 설계. 또는 업데이트 시 전체 객체 재할당 (`window.state.dashboard_data = new_data`) 패턴 강제.

**C2. PyInstaller `--onefile` macOS 코드 사이닝 충돌**
- Gemini 단독 발견 (심각)
- `--onefile`은 임시 디렉토리에 압축 해제 → 서명 파손 → Gatekeeper가 즉시 kill
- Apple Silicon에서 특히 치명적
- **조치:** `--onedir` + `--windowed` 강제. `--onefile` 절대 금지. entitlements.plist 필요.

### 🟠 High (2건)

**H1. 좀비 프로세스 / 포트 점유**
- Gemini 단독 발견
- `http_server=True` 모드에서 강제 종료 시 서버 데몬이 좀비로 잔류 → 재시작 시 "Address already in use"
- **조치:** desktop.py 시작 시 psutil로 기존 포트 점유 프로세스 정리하는 방어 로직 추가.

**H2. 패널 자동 발견 시 header/footer 오인**
- GPT 단독 발견
- `src/templates/partials/` 에 header.html, footer.html이 있으면 패널로 인식됨
- **조치:** 두 가지 방안 중 택 1:
  - (A) 규칙: `_` 접두사 파일은 발견 제외 (`_header.html`, `_footer.html`)
  - (B) 구조: include용 파일을 별도 디렉토리 (`src/templates/includes/`)로 분리

### 🟡 Medium (2건)

**M1. CLAUDE.md 비대화 → 컨텍스트 희석**
- Gemini 강조
- 현재 ~200줄이지만, 규칙이 추가될수록 AI가 핵심을 놓침
- **조치:** 300줄 상한 유지. 패널별 세부 규칙은 해당 디렉토리 내 로컬 .md로 분산 (점진적 공개).

**M2. AGENTS.md 미비 (Codex 호환)**
- GPT 강조
- Codex는 AGENTS.md를 읽는다고 공식 명시. CLAUDE.md만으로는 Codex에 규칙 전달이 보장 안 됨.
- **조치:** 루트에 AGENTS.md 추가 → CLAUDE.md 링크/요약.

---

## 엔진 간 불일치

| 주제 | GPT | Gemini | Brain 판단 |
|------|-----|--------|-----------|
| **점수** | 명시 안 함 (모두 조건부 합격) | 9.5/10 | GPT가 더 보수적. **8.8/10** |
| **window.state API 예시** | "프로퍼티 설정 방식으로 통일" 권고 | "1-Depth 평탄화 강제" 권고 | **양쪽 모두 채택.** 평탄화 + 프로퍼티 설정 |
| **pyinstaller 모드** | "Phase 0에서 가볍게 확인" | "--onefile 절대 금지, --onedir 강제" | **Gemini 채택.** --onedir 필수 |
| **CLAUDE.md 방향** | "AGENTS.md 병행 + 규칙 추가" | "300줄 다이어트 + 점진적 공개" | **양쪽 절충.** 300줄 상한 + AGENTS.md 추가 |
| **Phase 0 PoC 범위** | "window.state 이벤트까지 검증" | "좀비 프로세스 정리 로직까지" | **양쪽 모두 채택.** PoC 범위 확장 |

---

## ARCHITECTURE.md v1.3 반영 사항

### 즉시 반영 (Phase 0 착수 전)

**1. window.state 사용 규칙 명문화**
- 프로퍼티 설정 방식: `window.state.dashboard_data = new_data` (재할당)
- 중첩 객체 내부 mutation 금지 (반응성 상실)
- JS 측: `pywebview.state.addEventListener('change', ...)` 구독 표준 패턴 추가
- parser.py 출력 시 1-Depth 권장 (또는 전체 재할당 패턴 강제)

**2. PyInstaller 배포 규칙**
- `--onefile` 절대 금지 (macOS 코드 사이닝 충돌)
- `--onedir` + `--windowed` 강제
- entitlements.plist (JIT 메모리 실행 권한) 필수
- py2app은 공식 폐기 (Applications 폴더 샌드박스 버그)

**3. 자동 디스커버리 제외 규칙**
- `_` 접두사 파일 제외 (`_header.html`, `_footer.html`, `_panel.json`)
- 숨김 파일 (`.DS_Store`, `.gitkeep`) 제외
- `__pycache__` 디렉토리 제외
- 탐색 범위: `partials/` 최상위만 (재귀 금지)
- 정렬: order → id 알파벳순 (결정성 보장)

**4. 좀비 프로세스 방어**
- desktop.py 시작 시 psutil로 기존 포트 점유 프로세스 정리
- 정상 종료 훅 (atexit) 등록

**5. Phase 0 PoC 범위 확장**
- (기존) http_server=True 에셋 로딩 확인
- (추가) window.state 프로퍼티 변경 → JS change 이벤트 수신 확인
- (추가) 좀비 프로세스 정리 로직 동작 확인
- (추가) pyinstaller --onedir 더미 빌드 + Applications 폴더 테스트

**6. JS 초기 데이터 주입 표준**
- GPT 제안 채택: `<script type="application/json" id="dashboard-data">...</script>`
- core.js가 파싱 → `Dashboard.init(data)` 호출
- 앱 모드: `pywebview.state` change 이벤트로 덮어쓰기
- 브라우저 모드: 정적 HTML의 인라인 JSON 사용 (fetch 불필요)

### 문서 보강

**7. CLAUDE.md 개선**
- 300줄 상한 유지 (현재 ~200줄, 여유 있음)
- 추가 규칙:
  - `index.html` 직접 수정 금지 (생성물)
  - `window.state` 데이터는 1-Depth 또는 전체 재할당만 허용
  - `--onefile` 금지
  - header/footer는 `_` 접두사 사용
- "ES5+ 문법" → "ES2015+ (let/const/arrow OK, import/export 금지)" 로 명확화

**8. AGENTS.md 생성**
- 루트에 배치
- CLAUDE.md 핵심 규칙 요약 + 링크
- Codex 호환 보장

### 보류 (YAGNI)

- 패널별 로컬 CLAUDE.md 분산 → 패널이 10개 이상 될 때 재검토
- parsers/ 플러그인 구조 → 외부 API 연동 시점에
- 헤드리스 스크린샷 비주얼 회귀 → Phase 2 이후

---

## 최종 결정

### **Phase 0 착수 승인 (Conditional GO)**

GPT: 조건부 합격 / Gemini: 9.5/10 조건부 승인 / **Brain: GO**

**Phase 0 착수 전 필수 작업 (3건):**

| # | 작업 | 예상 소요 |
|---|------|---------|
| 1 | ARCHITECTURE.md → v1.3 업데이트 (위 6개 즉시 반영 항목) | Brain 작업 |
| 2 | CLAUDE.md 보강 (4개 규칙 추가 + 명확화) | Brain 작업 |
| 3 | AGENTS.md 생성 | Brain 작업 |

이 3건 완료 후 → CC팀에 Phase 0 위임.

---

## Phase 0 위임 지시서 (CC팀용)

```
Phase 0: 안전망 + PoC

목표: 리팩토링 시작 전 안전망 확보 + 핵심 기술 결정 검증

작업:
1. Golden Master 스냅샷
   - 현재 build_dashboard.py 실행 → index_golden.html 저장
   - 동일 dashboard_data.json 보관

2. PyWebView PoC (최소 더미 앱)
   - http_server=True로 정적 에셋 (CSS/JS/이미지) 로딩 확인
   - window.state 프로퍼티 변경 → JS change 이벤트 수신 확인
   - 좀비 프로세스 정리 로직 (psutil) 동작 확인

3. PyInstaller PoC
   - --onedir + --windowed 더미 빌드
   - Applications 폴더 이동 후 정상 동작 확인
   - entitlements.plist 코드 사이닝 테스트

완료 기준:
- [ ] index_golden.html 존재
- [ ] 더미 앱에서 에셋 3종 (CSS, JS, 이미지) 정상 로딩
- [ ] window.state 변경 → JS 콘솔에 change 이벤트 출력
- [ ] pyinstaller 앱이 Applications 폴더에서 정상 실행
- [ ] 좀비 정리 후 재시작 성공

참조: ARCHITECTURE.md v1.3, CLAUDE.md, AGENTS.md
```
