# CLAUDE.md — Woosdom Dashboard AI 작업 규칙
*Version: 1.0*
*Date: 2026-02-25*
*Authority: Brain (Claude Opus 4.6)*

---

## 이 문서의 목적

이 파일은 CC팀(Claude Code), Codex, Antigravity 등 **모든 AI 코딩 에이전트**가 이 프로젝트에서 작업할 때 반드시 따라야 하는 규칙이다.

**반드시 먼저 읽을 것:** `ARCHITECTURE.md` (v1.2+)

---

## 🔴 절대 규칙 (위반 시 작업 즉시 중단)

1. **한 번에 한 패널만 수정한다.** 여러 패널을 동시에 수정하지 않는다.
2. **`build_dashboard.py` 본체는 Brain 승인 없이 수정 금지.** 빌드 로직 변경은 설계 변경이다.
3. **`core.js`는 Brain 승인 없이 수정 금지.** 공유 코드 변경은 전체에 영향을 준다.
4. **`base.html`은 Brain 승인 없이 수정 금지.** 레이아웃 변경은 설계 변경이다.
5. **CSS 하드코딩 금지.** 색상, 간격, 폰트 사이즈를 직접 값으로 넣지 않는다. 반드시 `base.css`의 토큰(CSS Variable)을 참조한다.
   - ❌ `color: #4ecdc4;`
   - ✅ `color: var(--color-accent);`
6. **`panel_registry.json`을 수동으로 만들거나 수정하지 않는다.** 레지스트리는 빌드 시 자동 생성된다.
7. **`fetch('dashboard_data.json')`을 사용하지 않는다.** file:// CORS 문제. 런타임 데이터는 `window.state`만 사용.
8. **`index.html`을 직접 수정하지 않는다.** 빌드 생성물이다. `python3 build_dashboard.py`로만 생성.
9. **`window.state` 데이터는 1-Depth 또는 전체 재할당만.** 중첩 객체 내부 mutation은 JS에 전파되지 않는다.
   - ❌ `window.state.dashboard_data['portfolio']['total'] = 100`
   - ✅ `window.state.dashboard_data = new_data_object`
10. **PyInstaller `--onefile` 절대 금지.** macOS 코드 사이닝 파손. `--onedir` + `--windowed`만 사용.

---

## 🟡 작업 규칙

### 파일 구조 규칙

- **새 패널 추가:** `python3 build_dashboard.py --new-panel {id}` 사용. 수동 생성하지 않는다.
- **패널 파일 위치:**
  - HTML: `src/templates/partials/{id}.html`
  - CSS: `src/css/panels/{id}.css`
  - JS: `src/js/panels/{id}.js`
- **패널 ID = 파일명.** `id`가 `foo`이면 파일명도 `foo.html`, `foo.css`, `foo.js`.
- **패널 메타데이터 오버라이드가 필요하면** `src/templates/partials/{id}/_panel.json` 생성.

### CSS 규칙

- 모든 색상은 `var(--color-xxx)` 토큰 사용
- 모든 간격은 `var(--space-xxx)` 토큰 사용
- 모든 폰트 사이즈는 `var(--font-size-xxx)` 토큰 사용
- 모든 라운딩은 `var(--radius-xxx)` 토큰 사용
- **CSS 선택자 중첩은 3단계 이하.** `.panel-foo .card .badge` (3단계) OK. `.panel-foo .card .body .badge span` (5단계) ❌
- **패널 CSS는 `.panel-{id}` 네임스페이스로 시작.** 전역 스타일 오염 금지.
  - ✅ `.panel-portfolio .metric { ... }`
  - ❌ `.metric { ... }` (전역 오염)

### JS 규칙

- **패널 JS는 IIFE로 감싼다.** 전역 스코프 오염 금지.
  ```javascript
  (function() {
    const MyPanel = { render(data) { ... } };
    Dashboard.registerPanel('my-panel', MyPanel);
  })();
  ```
- **다른 패널의 DOM을 직접 조작하지 않는다.**
- **전역 변수를 만들지 않는다.** `Dashboard` 객체만 전역.
- **ES2015+ 문법.** `let`, `const`, arrow function, template literal OK. `import`/`export` ❌ (모듈 번들러 없음). `async/await` ❌ (PyWebView WebKit 호환성).
- **외부 라이브러리 추가 시 Brain 승인 필요.**

### Jinja2 템플릿 규칙

- **반복 패턴은 `macros.html`의 매크로 사용.** badge, card, status_dot 등.
- **데이터 참조는 `dashboard_data.json`의 스키마에 정의된 키만 사용.**
- **undefined 변수는 빌드 실패를 유발한다** (`StrictUndefined` 정책). 데이터가 없을 수 있으면 `{% if data.xxx is defined %}` 로 방어.

### Python 규칙

- **`desktop.py`에서 `http_server=True` 제거 금지.** CORS 방어 필수.
- **`parser.py` 출력은 `dashboard_data.json` 스키마를 준수해야 한다.**

---

## 🟢 작업 흐름

### 새 패널을 추가할 때

```
1. python3 build_dashboard.py --new-panel {id}
2. partials/{id}.html 편집
3. (필요시) css/panels/{id}.css 편집
4. (필요시) js/panels/{id}.js 편집
5. python3 build_dashboard.py
6. 브라우저에서 index.html 확인
```

### 기존 패널을 수정할 때

```
1. 해당 패널의 .html / .css / .js만 수정
2. python3 build_dashboard.py
3. 브라우저에서 해당 패널만 확인
4. 다른 패널에 영향 없는지 확인
```

### 버그를 수정할 때

```
1. 어떤 패널의 버그인지 확인
2. 해당 패널 파일만 수정 (3파일 이내)
3. python3 build_dashboard.py
4. Golden Master와 비교 (해당 패널 외 변경 없어야 함)
```

---

## 🚫 금지 패턴

| 패턴 | 이유 |
|------|------|
| Python f-string 안에 JS/CSS 작성 | 이 프로젝트가 리팩토링된 근본 원인 |
| `document.getElementById` 로 다른 패널 DOM 접근 | 패널 독립성 위반 |
| 인라인 `style="color: #xxx"` | 토큰 시스템 우회 |
| `!important` 남용 | 디버깅 지옥 |
| 500줄 이상의 단일 파일 생성 | 분할 필요 |
| `setTimeout`/`setInterval`로 데이터 폴링 | window.state 사용 |
| `var` 키워드 (JS) | `let`/`const` 사용 |

---

## 📋 빌드 & 검증

```bash
# 빌드
python3 build_dashboard.py

# 프로덕션 빌드 (인라인 번들링)
python3 build_dashboard.py --prod

# 새 패널 스캐폴드
python3 build_dashboard.py --new-panel {id}

# 검증: 빌드 출력 로그에서 확인
# [BUILD] 패널 N개 발견: ...
# [BUILD] ✅ css: N개 | js: N개 | orphan: 0개
# [BUILD] ✅ index.html 생성 완료
```

---

## 참조 문서

- `ARCHITECTURE.md` — 전체 아키텍처 설계서 (반드시 먼저 읽을 것)
- `review/synthesis_brain.md` — GPT/Gemini 리뷰 종합 판단
- `review/result_gpt_deep_research.md` — GPT 리뷰 전문
- `review/result_gemini_deep_research.md` — Gemini 리뷰 전문
