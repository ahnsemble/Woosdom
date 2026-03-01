# Woosdom Dashboard — Architecture Spec v1.2
*Created: 2026-02-24*
*Updated: 2026-02-25 — v1.2 GPT/Gemini Peer Review 반영*
*Reviewed by: GPT Deep Research (7.6/10), Gemini Deep Research (8.5/10)*
*Author: Brain (Claude Opus 4.6)*
*Status: ✅ 승인 — Phase 0부터 실행*

---

## 0. 설계 원칙

**"패널 하나 추가하는 데 파일 1개만 건드리면 된다."**

우즈덤 시스템 아키텍처를 설계할 때의 원칙을 대시보드에도 적용한다:
- `brain_directive.md` 하나 수정하면 Brain 행동이 바뀌듯, **패널 모듈 1개 추가하면 대시보드에 새 섹션이 나타난다**
- `engine_router.md`가 엔진 선택을 중앙화하듯, **데이터 파이프라인이 중앙화**되어 있다
- `agent_corps_spec.md`가 팀별 독립성을 보장하듯, **각 패널은 독립적으로 동작**한다

---

## 1. 현재 구조의 문제 (AS-IS)

```
build_dashboard.py (1,600줄 단일 파일)
├── _pixel_agents_js()  → 500줄 JS를 Python f-string으로 리턴
├── _css()              → 400줄 CSS를 Python f-string으로 리턴
├── _js()               → 100줄 JS를 Python f-string으로 리턴
├── _briefing_html()    → HTML을 Python f-string으로 리턴
├── _training_html()    → HTML을 Python f-string으로 리턴
├── _portfolio_html()   → HTML을 Python f-string으로 리턴
├── ... (15개+ 함수)
└── generate_html()     → 모든 것을 하나의 거대한 f-string으로 합침
```

### 문제점

| # | 문제 | 결과 |
|---|------|------|
| 1 | **JS/CSS가 Python 문자열 안에 갇혀있음** | 따옴표/이스케이프 충돌, 구문 하이라이팅 불가, 브라우저 DevTools 디버깅 불가 |
| 2 | **단일 파일 1,600줄** | 새 기능 추가 시 10곳 수정 필요, 병합 충돌, 가독성 붕괴 |
| 3 | **패널 간 결합도 100%** | Pixel Agents 버그가 전체 대시보드 렌더링을 깨뜨림 |
| 4 | **데이터↔뷰 분리 없음** | parser.py가 만든 JSON 구조 변경 시 HTML 생성 로직 전부 수정 |
| 5 | **테스트 불가** | 개별 패널 단위 테스트가 구조적으로 불가능 |
| 6 | **AI 엔진 수정 실패** | CC/Codex 모두 f-string 안의 JS를 정밀 수정하는 데 반복 실패 |

**비유: 봉투를 밀봉한 채로 안의 편지를 바늘로 수정하는 구조.**

---

## 2. 목표 구조 (TO-BE)

### 2-1. 디렉토리 구조

```
woosdom_app/
├── assets/                      ← 정적 에셋 (이미지, 스프라이트)
│   ├── 32x32folk.png
│   ├── gentle-obj.png
│   └── icons/                   ← 앱 아이콘
│
├── src/                         ← 소스 코드 (분리된 JS/CSS)
│   ├── css/
│   │   ├── base.css             ← 변수, 리셋, 타이포그래피, 테마
│   │   ├── layout.css           ← 헤더, 그리드, 반응형
│   │   └── panels/              ← 패널별 CSS
│   │       ├── briefing.css
│   │       ├── projects.css
│   │       ├── portfolio.css
│   │       ├── training.css
│   │       ├── agents.css
│   │       ├── pixel-agents.css
│   │       ├── sprint.css
│   │       └── litellm.css
│   │
│   ├── js/
│   │   ├── core.js              ← 테마 토글, 필터, 공통 유틸리티
│   │   ├── launcher.js          ← Quick Launcher + PyWebView API 브릿지
│   │   └── panels/              ← 패널별 JS (독립 모듈)
│   │       ├── pixel-agents.js  ← Canvas 렌더러 (현재 500줄 → 독립)
│   │       ├── roadmap.js       ← 마일스톤 필터
│   │       └── training.js      ← 운동 섹션 인터랙션
│   │
│   └── templates/               ← HTML 템플릿 (Jinja2)
│       ├── base.html            ← 공통 레이아웃 (head, header, footer)
│       ├── partials/            ← 패널별 HTML 조각
│       │   ├── briefing.html
│       │   ├── projects.html
│       │   ├── portfolio.html
│       │   ├── training.html
│       │   ├── agents.html
│       │   ├── pixel-agents.html
│       │   ├── sprint.html
│       │   ├── litellm.html
│       │   ├── roadmap.html
│       │   ├── rules.html
│       │   └── completed.html
│
├── build_dashboard.py           ← 빌드 스크립트 (Jinja2 + 패널 자동 디스커버리, ~150줄)
├── parser.py                    ← 데이터 파이프라인 (Obsidian → JSON)
├── desktop.py                   ← PyWebView 래퍼 (http_server=True + window.state)
├── dashboard_data.json          ← parser 출력 (빌드 입력)
├── index.html                   ← 빌드 출력 (최종 결과물)
└── setup.py                     ← py2app 빌드
```

### 2-2. 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────┐
│                    데이터 파이프라인                          │
│                                                             │
│  Obsidian Vault ──→ parser.py ──→ dashboard_data.json       │
│  (active_context,    (파싱 전담)     (단일 진실 소스)          │
│   agent_activity,                                           │
│   portfolio.json,                                           │
│   training_protocol)                                        │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    빌드 파이프라인                            │
│                                                             │
│  dashboard_data.json ──→ build_dashboard.py ──→ index.html  │
│                          (Jinja2 렌더러)                     │
│                          + panel_registry.json              │
│                          + src/templates/**                  │
│                          + src/css/** (인라인 또는 링크)      │
│                          + src/js/**  (인라인 또는 링크)      │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    런타임                                     │
│                                                             │
│  desktop.py (PyWebView)                                     │
│    └── webview.create_window(url='index.html')              │
│         └── index.html                                      │
│              ├── <link href="src/css/...">                   │
│              ├── <script src="src/js/...">                   │
│              └── assets/ (이미지, 스프라이트)                  │
│                                                             │
│  OR 브라우저에서 직접 index.html 열기 (동일 결과)              │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 핵심 설계 결정

### 3-1. 패널 디스커버리 (Auto-Discovery Plugin System)

> **v1.2 변경: 수동 registry 폐기 → 빌드 시 디렉토리 스캨으로 자동 발견**
> *근거: GPT/Gemini 양쪽 합의 — 수동 JSON 관리는 AI 에이전트가 파일 추가/삭제 시 반드시 동기화를 놓침*

**"패널 1개 추가 = 파일 3개 생성. 끝."**

#### 자동 발견 규칙

`build_dashboard.py`가 빌드 시 `src/templates/partials/` 디렉토리를 `os.walk`로 스캨:

```
id = "foo" 이면:
  ├─ 템플릿: src/templates/partials/foo.html        (필수 — 이것이 있어야 패널 인식)
  ├─ CSS:    src/css/panels/foo.css               (선택 — 존재하면 자동 포함)
  └─ JS:     src/js/panels/foo.js                 (선택 — 존재하면 자동 포함)
```

#### 메타데이터 오버라이드 (선택)

패널별 설정이 필요한 경우 `_panel.json` 파일을 템플릿 옆에 배치:

`src/templates/partials/foo/_panel.json`:
```json
{
  "order": 75,
  "size": "half",
  "collapsible": true,
  "default_collapsed": false,
  "enabled": true
}
```

`_panel.json`이 없으면 기본값 적용: `order=999, size="full", collapsible=true, enabled=true`

#### 빌드 시 정합성 검증

`build_dashboard.py`가 빌드 시 자동 수행:
- ✅ 템플릿 파일 존재 여부 확인
- ✅ css/js 파일 존재 여부 확인 (규칙 기반)
- ✅ order 중복 탐지 → 경고
- ✅ 발견된 패널 목록 출력 (stdout)
- ❌ 템플릿 없는 css/js 파일 → 경고 (orphan 감지)

#### 패널 Scaffold 자동 생성

```bash
python3 build_dashboard.py --new-panel {id}
```

자동 생성:
- `src/templates/partials/{id}.html` (스켈레톤 포함)
- `src/css/panels/{id}.css` (네임스페이스 설정됨)
- `src/js/panels/{id}.js` (IIFE + Dashboard.registerPanel 포함)

#### 확장 방법
1. `src/templates/partials/new_panel.html` 생성 (또는 `--new-panel` 사용)
2. (필요시) `.css` + `.js` 생성
3. `python3 build_dashboard.py` 실행 → 끝. **registry 수정 불필요.**

#### 비활성화 방법
- `_panel.json`에 `"enabled": false` → 빌드 시 패널 제외. 코드 삭제 불필요.

### 3-2. Jinja2 템플릿 엔진

Python f-string 대신 Jinja2를 사용하는 이유:
- **HTML/JS/CSS가 네이티브 구문으로 존재** → 에디터 하이라이팅, 린팅 작동
- **상속(extends)과 포함(include)** → base.html에서 공통 구조, partial에서 개별 패널
- **필터와 매크로** → 반복 패턴 (badge, card) 재사용
- **자동 이스케이프** → XSS 방지
- **AI 엔진이 수정 가능** → 순수 HTML 파일이므로 CC/Codex 모두 정밀 편집 가능

`src/templates/base.html` 구조:
```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Woosdom Mission Control</title>
  <!-- CSS: 기본 + 패널별 -->
  <link rel="stylesheet" href="src/css/base.css">
  <link rel="stylesheet" href="src/css/layout.css">
  {% for panel in panels %}
  {% if panel.css %}<link rel="stylesheet" href="{{ panel.css }}">{% endif %}
  {% endfor %}
</head>
<body>
  {% include 'partials/header.html' %}
  
  {% for panel in panels %}
  <!-- Panel: {{ panel.id }} -->
  {% include 'partials/' + panel.template %}
  {% endfor %}
  
  {% include 'partials/footer.html' %}
  
  <!-- JS: 코어 + 패널별 -->
  <script src="src/js/core.js"></script>
  <script src="src/js/launcher.js"></script>
  {% for panel in panels %}
  {% if panel.js %}<script src="{{ panel.js }}"></script>{% endif %}
  {% endfor %}
</body>
</html>
```

### 3-3. 렌더링 전략 + 빌드 모드

> **v1.2 변경: 렌더링 책임을 단일화. fetch/polling 폐기.**
> *근거: GPT — "빌드타임 vs 런타임 충돌 해결 필수", Gemini — "fetch polling은 로컬 앱에서 안티패턴"*

#### 렌더링 책임 결정 (단일 방향)

| 모드 | 렌더링 책임 | 데이터 갱신 |
|------|------------|----------|
| **브라우저** | **빌드타임 (Jinja2)** — 데이터까지 포함한 완성 HTML | 빌드 후 새로고침 |
| **앱 (PyWebView)** | **빌드타임 + `window.state`** — Jinja2로 초기 HTML, Python이 `window.state`로 부분 갱신 | 실시간 (네트워크 없음) |

~~fetch('dashboard_data.json')~~ → **폐기.** file:// CORS 문제 원천 차단.

#### PyWebView 런타임 제약 (필수)

> *근거: Gemini — "file:// CORS로 에셋 로딩 실패", GPT — "내장 HTTP 서버 또는 JS API 브릿지 필요"*

- `desktop.py`: **`http_server=True` 강제** (file:// 사용 금지)
- 상대경로 기반 에셋 로딩이 정상 동작하려면 HTTP 서버 필수
- py2app Applications 폴더 샌드박스 버그 인지 → pyinstaller 대안 병행 테스트

#### 빌드 모드

| 모드 | 용도 | 출력 |
|------|------|------|
| **dev** (기본) | 개발 중 | `<link href>`, `<script src>` — 외부 파일 참조. DevTools 디버깅 가능 |
| **prod** | 앱 빌드용 | CSS/JS 인라인 번들링. 오프라인 동작 보장 |

```bash
python3 build_dashboard.py          # dev
python3 build_dashboard.py --prod   # prod (인라인 번들링)
python3 build_dashboard.py --new-panel foo  # 스캐폴드 생성
```

### 3-4. 데이터 계약 (Data Contract)

`dashboard_data.json`의 스키마를 명시적으로 정의한다. parser.py와 템플릿 사이의 **계약**.

```
parser.py는 이 스키마를 출력한다 (보장)
  ↓
dashboard_data.json
  ↓
템플릿은 이 스키마를 입력으로 받는다 (기대)
```

스키마 변경 시 양쪽 모두 업데이트해야 하므로, 스키마 정의 파일을 별도로 관리:
`src/schema/dashboard_data.schema.json` (JSON Schema)

→ 추후 parser.py 실행 시 스키마 검증 단계 추가 가능.

#### Jinja2 정책 (필수)

> *v1.2 추가. 근거: GPT — "autoescape/undefined 정책 미확정은 AI 에이전트 빌드 실패 원인"*

```python
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

env = Environment(
    loader=FileSystemLoader('src/templates'),
    autoescape=select_autoescape(['html', 'htm']),  # XSS 방지
    undefined=StrictUndefined,  # 누락 변수 → 빌드 실패 (침묵 실패 방지)
)
```

#### 관측성 (Observability)

> *v1.2 추가. 근거: GPT — "침묵 실패 방지를 위한 최소 관측성"*

빌드 시 stdout 으로 표준 포맷 출력:
```
[PARSE] ✅ obsidian (5 keys) | ✅ portfolio | ✅ training | ❌ litellm (timeout)
[BUILD] 패널 12개 발견: sprint(10), summary(20), briefing(30), ...
[BUILD] ✅ css: 8개 | js: 3개 | orphan: 0개
[BUILD] ⚠️ order 중복: portfolio(70), finance-chart(70)
[BUILD] ✅ index.html 생성 완료 (142KB)
```

### 3-5. 패널 독립성 (Fault Isolation)

각 패널은 다른 패널의 실패에 영향받지 않아야 한다.

**규칙:**
- 각 패널 JS는 IIFE `(function() { ... })()` 또는 모듈 패턴으로 격리
- 각 패널 CSS는 `.panel-{id}` 네임스페이스로 스코핑
- 패널 데이터가 없으면 (예: `training` 키가 JSON에 없으면) 해당 패널 섹션이 조용히 빈 상태로 렌더링 — 에러 아님
- Pixel Agents 캔버스가 깨져도 나머지 대시보드는 정상 동작

---

## 4. 확장성 레이어 (v1.1 보강)

> **설계 철학: "지금 당장 필요 없더라도, 나중에 추가할 때 기존 코드를 깨지 않는 구조"**

아래 4개 레이어는 Phase 1~2에서 기반만 깔아놓고, 실제 기능은 필요할 때 켜는 방식이다.
과잘 엔지니어링 방지: 기반 구조만 만들고, 실제 구현은 필요 시점에.

### 4-1. 디자인 시스템 (Design System)

**문제:** 현재 badge, card, status-dot 같은 UI 패턴이 파일마다 중복 정의되어 있다. 디자인을 바꾸려면 모든 파일을 하나씩 열어야 한다.

**해결:**

#### a) 디자인 토큰 (CSS Variables)

`src/css/base.css`의 `:root`에 **모든 시각적 결정**을 중앙화:

```css
:root {
  /* 색상 팔레트 */
  --color-bg:      #0d0d1a;
  --color-surface: #181830;
  --color-border:  #252545;
  --color-text:    #e2e2f0;
  --color-muted:   #7a7a9a;
  --color-accent:  #4ecdc4;
  
  /* 도메인 색상 */
  --color-finance: #4ecdc4;
  --color-game:    #ff6b6b;
  --color-system:  #a29bfe;
  --color-career:  #ffeaa7;
  --color-health:  #55efc4;
  
  /* 상태 색상 */
  --color-active:  #00b894;
  --color-warning: #fdcb6e;
  --color-error:   #e74c3c;
  --color-idle:    #636e72;
  
  /* 간격 */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 36px;
  
  /* 타이포그래피 */
  --font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'SF Mono', 'Fira Code', monospace;
  --font-size-xs: 0.7rem;
  --font-size-sm: 0.78rem;
  --font-size-base: 0.88rem;
  --font-size-lg: 1.1rem;
  --font-size-xl: 1.75rem;
  
  /* 커뮨 스타일 */
  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-pill: 20px;
  --shadow-card: 0 6px 30px rgba(0,0,0,.4);
  --shadow-hover: 0 8px 40px rgba(0,0,0,.5);
}

/* 라이트 테마 — 변수만 덮어쓰면 된다 */
body.light {
  --color-bg:      #f5f5f8;
  --color-surface: #ffffff;
  --color-border:  #d8d8e8;
  --color-text:    #1a1a2e;
  --color-muted:   #6b6b8a;
  --color-accent:  #2da89e;
  /* ... 나머지 동일 패턴 ... */
}
```

**확장:** 새 테마 추가 = `:root` 변수 세트 1개 추가. 기존 CSS 수정 없음.

#### b) 컴포넌트 라이브러리 (Jinja2 매크로)

`src/templates/macros.html`에 재사용 컴포넌트를 정의:

```html
{# ── Badge 컴포넌트 ── #}
{% macro badge(text, color, variant='outline') %}
<span class="badge badge--{{ variant }}" 
      style="--badge-color: {{ color }};">
  {{ text }}
</span>
{% endmacro %}

{# ── Status Dot 컴포넌트 ── #}
{% macro status_dot(status) %}
{% set colors = {'active':'var(--color-active)', 'idle':'var(--color-idle)', 
                 'error':'var(--color-error)', 'done':'var(--color-active)'} %}
<span class="status-dot status-dot--{{ status }}" 
      style="background: {{ colors[status] }};"></span>
{% endmacro %}

{# ── Card Wrapper 컴포넌트 ── #}
{% macro card(title, domain='', id='') %}
<div class="card panel-card" {% if domain %}data-domain="{{ domain }}"{% endif %}
     {% if id %}id="{{ id }}"{% endif %}>
  {% if title %}<div class="card__header">{{ title }}</div>{% endif %}
  <div class="card__body">
    {{ caller() }}
  </div>
</div>
{% endmacro %}
```

**확장:** badge 디자인 변경 = `macros.html`의 badge 매크로 1곳 수정. 전체 대시보드에 자동 반영.

### 4-2. 데이터 레이어 (Data Layer)

**문제:** 새 데이터 소스를 추가하려면 parser.py + build_dashboard.py + 템플릿 3곳을 전부 수정해야 한다.

**해결:** parser.py를 **플러그인 구조**로 개편:

```
parser.py (v2)
├── parsers/              ← 데이터 소스별 파서
│   ├── base.py            ← BaseParser 추상 클래스
│   ├── obsidian.py        ← Obsidian 볼트 파싱 (active_context, agent_activity 등)
│   ├── portfolio.py       ← portfolio.json 파싱
│   ├── training.py        ← training_protocol.md 파싱
│   ├── litellm.py         ← LiteLLM 상태 확인
│   └── github.py          ← (추후) GitHub API 연동
└── parser_registry.json   ← 어떤 파서를 실행할지 등록
```

각 파서는 동일한 인터페이스:

```python
class BaseParser:
    """All parsers output a dict that gets merged into dashboard_data.json"""
    def parse(self) -> dict:
        raise NotImplementedError
    
    def schema_key(self) -> str:
        """Top-level key in dashboard_data.json (e.g. 'portfolio', 'training')"""
        raise NotImplementedError
```

**확장:** 새 데이터 소스 추가 = 파서 파일 1개 생성 + registry에 1줄 추가. parser.py 본체 수정 없음.

### 4-3. 실시간 업데이트 (Realtime Layer)

> **v1.2 변경: fetch/polling 전면 폐기 → PyWebView 6.0 `window.state` 기반**
> *근거: Gemini — "로컬 앱에서 HTTP polling은 안티패턴. window.state는 네트워크 오버헤드 0"*

**현재:** 정적 빌드. `python3 build_dashboard.py` 실행해야 데이터 반영.

#### 패널 등록 구조 (Phase 1~2에서 깔아놓을 것)

```javascript
// src/js/core.js
const Dashboard = {
  data: {},
  
  init(initialData) {
    this.data = initialData || {};
    this.render();
  },
  
  update(newData) {
    this.data = newData;
    this.render();
  },
  
  render() {
    Object.values(Dashboard.panels).forEach(p => {
      try {
        if (p.render) p.render(this.data);
      } catch (e) {
        console.error(`[Panel ${p.id}] render failed:`, e);
        // 패널 실패해도 나머지 계속
      }
    });
  },
  
  panels: {},
  
  registerPanel(id, module) {
    module.id = id;
    this.panels[id] = module;
  }
};
```

각 패널 JS는 자신을 등록:

```javascript
// src/js/panels/pixel-agents.js
(function() {
  const PixelAgents = {
    render(data) {
      const activity = data.agent_activity || {};
      // Canvas 로직...
    }
  };
  Dashboard.registerPanel('pixel-agents', PixelAgents);
})();
```

#### 데이터 갱신 전략 (2가지 모드)

| 모드 | 방식 | 작동 방식 |
|------|------|--------|
| **브라우저** | 정적 빌드 | Jinja2가 데이터까지 포함한 HTML 생성. 새로고침으로 반영. |
| **앱 (PyWebView)** | `window.state` | Python이 상태 변경 → JS 콜백이 DOM 부분 갱신. 네트워크 0. |

#### PyWebView `window.state` 통신 구조 (Phase 3)

```python
# desktop.py
import webview

def create_dashboard():
    window = webview.create_window(
        'Woosdom Mission Control',
        url='index.html',
        http_server=True,  # 필수: file:// CORS 문제 방지
    )
    
    # Python → JS 상태 전달 (네트워크 없음)
    window.state = {
        'dashboard_data': load_dashboard_data(),
        'last_updated': datetime.now().isoformat()
    }
    
    webview.start()
```

```javascript
// src/js/core.js — 앱 모드에서만 활성화
if (window.pywebview) {
  // Python이 window.state 변경 시 자동 호출
  window.addEventListener('pywebviewready', () => {
    const state = window.pywebview.state;
    if (state && state.dashboard_data) {
      Dashboard.update(state.dashboard_data);
    }
  });
}
```

**제약 사항:**
- `window.state`는 최상위 객체 재할당만 반응성 트리거 (중첩 객체 내부 변경은 감지 못함)
- PyWebView 6.0+ 필요

#### ~~폐기된 방식~~
- ~~fetch('dashboard_data.json')~~ → file:// CORS 문제
- ~~HTTP Polling (setInterval + fetch)~~ → 로컬 앱에서 안티패턴
- ~~WebSocket~~ → 과잉 엔지니어링 (window.state로 충분)

### 4-4. 레이아웃 시스템 (Layout Layer)

**문제:** 패널 순서 변경, 너비 조절, 패널 접기/펼치기 등이 하드코딩되어 있다.

**기반 설계:**

#### a) 레이아웃 설정은 각 패널의 `_panel.json`에서 관리 (자동 디스커버리 연동)

각 패널의 `_panel.json` 예시:
```json
{"order": 100, "size": "full", "collapsible": true, "default_collapsed": false}
```

기본값: `order=999, size="full", collapsible=true, enabled=true`

#### b) CSS Grid 기반 레이아웃:

```css
/* src/css/layout.css */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-lg);
  max-width: var(--layout-max-width, 1440px);
  margin: 0 auto;
  padding: 0 var(--space-xl);
}

/* size: half → 2칸 그리드 */
.panel--half { grid-column: span 1; }
.panel--full { grid-column: 1 / -1; }

@media (min-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr 1fr;
  }
}
```

**확장 경로 (지금 만들지 않음):**

| 단계 | 방식 |
|------|------|
| **현재** | registry에서 order/size 설정 |
| **Step 1** | 패널 접기/펼치기 (상태 localStorage 저장) |
| **Step 2** | 드래그 순서 변경 (SortableJS) |
| **Step 3** | 대시보드 레이아웃 프리셋 (예: "금융 모드", "개발 모드") |

### 4-5. 확장성 검증 체크리스트

마이그레이션 완료 후, 아래 시나리오가 **기존 코드 수정 없이** 가능해야 합격:

> **v1.2 업데이트: 자동 디스커버리 + window.state 반영**

| # | 시나리오 | 건드려야 할 파일 | 절대 건드리면 안 되는 파일 |
|---|----------|----------------|--------------------|
| 1 | **새 패널 추가** | new_panel.html + .css + .js (**registry 수정 불필요**) | build_dashboard.py, core.js, base.html |
| 2 | **전체 색상 변경** | base.css의 :root 변수만 | 개별 패널 CSS |
| 3 | **새 테마 추가** | base.css에 body.{theme} 변수 세트 추가 | 개별 패널 CSS |
| 4 | **패널 순서 변경** | 해당 패널의 `_panel.json` order 값만 | 어떤 파일도 |
| 5 | **패널 비활성화** | 해당 패널의 `_panel.json` enabled: false | 어떤 파일도 |
| 6 | **새 데이터 소스** | parsers/ 에 파일 1개 + registry 1줄 | parser.py 본체 |
| 7 | **Badge/Card 디자인 변경** | macros.html 1곳 | 개별 패널 템플릿 |
| 8 | **모바일 대응** | layout.css 미디어 쿼리 | JS, Python |
| 9 | **Pixel Agents 방 추가** | pixel-agents.js의 ROOMS 객체만 | 다른 파일 전부 |
| 10 | **실시간 업데이트 전환** | desktop.py에 window.state 바인딩 + core.js에 리스너 | 패널 JS, 템플릿 |

**↑ 이 표의 "절대 건드리면 안 되는 파일" 칸이 비어있어야 합격이다.**

---

## 5. 마이그레이션 전략

> **v1.2 변경: Phase 0 추가, 레지스트리 자동생성 반영, Phase 3에 window.state**

### Phase 0: 안전망 + PoC (NEW)
> *근거: GPT — "Golden Master 기반 회귀 검증을 Phase 0으로", Gemini — "py2app 샌드박스 조기 확인"*

1. **Golden Master 스냅샷:** 현재 `build_dashboard.py` 실행 → `index_golden.html` 저장
2. **더미 앱 PoC:** 최소 파일로 PyWebView + `http_server=True` 로딩 확인
3. **pyinstaller 테스트:** 더미 앱을 pyinstaller로 빌드 → Applications 폴더 이동 후 정상 동작 확인
4. **검증:** Golden Master 존재 + PoC 로딩 성공

### Phase 1: 골격 구조 생성
1. `src/` 디렉토리 구조 생성
2. `_css()` → `src/css/base.css` + `src/css/layout.css` + 패널별 CSS로 분리
3. `_js()` → `src/js/core.js` + `src/js/launcher.js`로 분리
4. `_pixel_agents_js()` → `src/js/panels/pixel-agents.js`로 분리
5. `build_dashboard.py`를 Jinja2 기반으로 재작성 (~150줄)
   - 패널 자동 디스커버리 (`os.walk`) 포함
   - 빌드 시 정합성 검증 포함
   - `StrictUndefined` + `select_autoescape` 정책 적용
   - 관측성 출력 포함
6. `http_server=True` 적용된 `desktop.py` 수정
7. **검증:** `python3 build_dashboard.py` → `index.html` → Golden Master와 비교

### Phase 2: 템플릿 분리 + 디자인 토큰
1. `generate_html()` 내의 각 섹션을 `src/templates/partials/`로 추출
2. 각 `_xxx_html()` 함수를 Jinja2 템플릿으로 변환
3. `base.html` + `macros.html` 작성
4. CSS Variables 디자인 토큰 적용
5. **검증:** 패널별로 하나씩 전환하면서 Golden Master와 비교

### Phase 3: 버그 수정 + window.state 실시간
1. Pixel Agents 상태 매핑 수정 (순수 JS 파일에서 직접 편집)
2. 팀별 로그 필터링 구현
3. Done 상태 착석 로직 수정
4. 에이전트 간 대화 기록 추가
5. `window.state` 기반 실시간 업데이트 구현 (desktop.py + core.js)
6. **검증:** 각 수정사항 DevTools 확인 + 앱에서 실시간 갱신 확인

### Phase 4: 프로덕션 빌드
1. `--prod` 인라인 빌드 모드 구현
2. py2app + **pyinstaller 병행 테스트**
3. Chart.js 로컬 vendoring (오프라인 동작 보장)
4. **검증:** Woosdom.app에서 브라우저와 동일한 결과 + Applications 폴더 정상 동작

---

## 6. 파일별 역할 요약

| 파일 | 역할 | 수정 빈도 | 누가 수정 |
|------|------|----------|----------|
| `parser.py` | Obsidian → JSON | 낮음 (데이터 소스 변경 시) | CC팀 |
| `build_dashboard.py` | JSON + 템플릿 → HTML | 낮음 (빌드 로직 변경 시만) | CC팀 |
| `_panel.json` (각 패널) | 패널 순서/활성화 오버라이드 | 낮음 (기본값으로 충분) | CC팀 |
| `src/templates/partials/*.html` | 패널 HTML | 높음 (UI 변경 시) | CC팀 |
| `src/css/panels/*.css` | 패널 스타일 | 높음 (디자인 변경 시) | CC팀 |
| `src/js/panels/*.js` | 패널 인터랙션 | 높음 (기능 변경 시) | CC팀 |
| `src/js/core.js` | 공통 기능 | 낮음 | CC팀 |
| `desktop.py` | PyWebView 래퍼 | 매우 낮음 | CC팀 |
| `dashboard_data.json` | 빌드 입력 데이터 | 자동 생성 | parser.py |
| `index.html` | 빌드 출력 | 자동 생성 | build_dashboard.py |

---

## 7. 확장 시나리오

### "새로운 Finance 차트 패널 추가"
```bash
python3 build_dashboard.py --new-panel finance-chart  # 스캐폴드 자동 생성
```
1. `src/templates/partials/finance-chart.html` 편집
2. `src/css/panels/finance-chart.css` 편집
3. `src/js/panels/finance-chart.js`에 Chart.js 로직 추가
4. (선택) `_panel.json` 생성해 order 지정
5. `parser.py`에 차트 데이터 파싱 추가 (필요시)
6. `python3 build_dashboard.py` → 끝. **registry 수정 불필요.**

### "Pixel Agents에 새로운 방 추가"
1. `src/js/panels/pixel-agents.js`에서 `ROOMS` 객체에 새 방 추가
2. `src/js/panels/pixel-agents.js`에서 `AGENT_DEFS`에 새 에이전트 추가
3. 끝. 다른 파일 수정 불필요.

### "모바일용 대시보드"
1. `src/css/base.css`의 미디어 쿼리 보강
2. 무거운 패널(Pixel Agents)의 `_panel.json`에 `"mobile_enabled": false` 옵션 추가 (추후)

---

## 8. 기술 스택

| 구성 | 선택 | 이유 |
|------|------|------|
| 템플릿 엔진 | **Jinja2** | Python 표준, pip 설치 1줄, 문법 직관적 |
| CSS | **Vanilla CSS + CSS Variables** | 빌드 도구 불필요, 테마 전환 용이 |
| JS | **Vanilla JS (ES5+)** | 빌드 도구 불필요, PyWebView 호환성 최대 |
| 차트 (추후) | **Chart.js CDN** | 경량, 인터랙티브, CDN 또는 로컬 번들 |
| 패키지 관리 | **pip (Jinja2만)** | 최소 의존성 |

**No React, No Webpack, No npm.** 빌드 복잡도를 최소화한다. `python3 build_dashboard.py` 한 줄이면 끝나야 한다.

---

## 9. 제약 사항

- Jinja2 의존성 추가 (pip install jinja2) — 이미 Python 생태계 표준
- **PyWebView 6.0+ 필수** — `window.state` 사용 (현재 설치 버전 확인 필요)
- **`http_server=True` 강제** — file:// 사용 금지 (CORS 문제)
- 마이그레이션 중 기존 기능 회귀 없어야 함 — Golden Master와 비교 필수
- py2app Applications 폴더 샌드박스 버그 인지 — pyinstaller 대안 병행 테스트
- Chart.js 외부 라이브러리는 **로컬 vendoring** 필요 (CDN 오프라인 시 불가)
- CSS 선택자 중첩 3-depth 이하 권고 (WebKit 렌더링 성능)

---

## 10. 변경 이력

| 버전 | 날짜 | 변경 내용 |
|-------|------|----------|
| v1.0 | 2026-02-24 | 초기 설계 — 문제 분석, 목표 구조, 핵심 설계 결정 |
| v1.1 | 2026-02-25 | 확장성 레이어 4개 추가 (Design System, Data Layer, Realtime, Layout) |
| **v1.2** | **2026-02-25** | **GPT/Gemini Peer Review 반영:** 패널 자동 디스커버리, 렌더링 전략 단일화(window.state), PyWebView 런타임 제약 반영, Phase 0 추가, Jinja2 정책/관측성, Scaffold 자동생성 |

---

*Phase 0부터 실행합니다.*
