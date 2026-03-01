# CC팀 실행 지시서 — Woosdom Dashboard 리팩토링
*Version: 1.0*
*Date: 2026-02-25*
*Authority: Brain (Claude Opus 4.6)*
*Target: CC팀 (Claude Code CLI)*

---

## 프로젝트 개요

**목표:** `build_dashboard.py` (99KB, ~1,600줄) 모놀리식 구조를 Jinja2 기반 모듈형 구조로 전환.

**핵심 제약:**
- 리팩토링 전후 **대시보드가 동일하게 보여야 한다**
- 각 Phase 완료 시 반드시 빌드 → Golden Master 비교
- **한 번에 한 파일만 수정**, 확인 후 다음 파일

**프로젝트 경로:** `/Users/woosung/Desktop/Dev/Woosdom_Brain/02_Projects/woosdom_app/`

**반드시 먼저 읽을 것:**
- `ARCHITECTURE.md` — 전체 설계서
- `CLAUDE.md` — 작업 규칙

---

## 현재 구조 (AS-IS)

```
woosdom_app/
├── build_dashboard.py   ← 99KB, HTML/CSS/JS를 Python f-string으로 생성
├── parser.py            ← Obsidian → dashboard_data.json
├── desktop.py           ← PyWebView 래퍼 (file:// 사용 중)
├── dashboard_data.json  ← parser 출력
├── index.html           ← build 출력
├── assets/              ← 스프라이트, 이미지
├── setup.py             ← py2app (폐기 예정)
└── tests/
```

**핵심 문제:** JS/CSS가 Python f-string 안에 있어서 수정 불가, 디버깅 불가, AI 편집 실패.

---

## 절대 규칙 (모든 Phase에서 적용)

1. `build_dashboard.py` 원본을 **절대 삭제하지 않는다**. `build_dashboard_legacy.py`로 보관.
2. 매 Phase 완료 시 `python3 build_dashboard.py` 실행 → 결과가 Golden Master와 시각적으로 동일해야 한다.
3. CSS 하드코딩 금지. 반드시 CSS Variable 사용. `color: #4ecdc4` ❌ → `color: var(--color-accent)` ✅
4. 패널 JS는 IIFE로 감싼다. 전역 변수 금지.
5. `_` 접두사 파일은 패널 자동 발견에서 제외된다. (`_header.html`, `_footer.html`, `_panel.json`)
6. `fetch('dashboard_data.json')` 사용 금지. (file:// CORS 문제)
7. Git: 각 Phase 완료 시 커밋. 메시지 형식: `refactor(dashboard): Phase N — 설명`

---

## Phase 0: 안전망 + PoC

### 목표
리팩토링 시작 전 안전망 확보 + PyWebView 핵심 기술 검증

### 작업

#### 0-1. Golden Master 스냅샷
```bash
cd /Users/woosung/Desktop/Dev/Woosdom_Brain/02_Projects/woosdom_app
python3 build_dashboard.py
cp index.html index_golden.html
cp dashboard_data.json dashboard_data_golden.json
```

#### 0-2. build_dashboard.py 원본 보관
```bash
cp build_dashboard.py build_dashboard_legacy.py
```

#### 0-3. PyWebView PoC — 최소 더미 앱

`poc/` 디렉토리에 최소 앱을 만들어 3가지를 검증:

**검증 A: http_server=True 에셋 로딩**

`poc/poc_app.py`:
```python
import webview
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    window = webview.create_window(
        'PoC Test',
        url=os.path.join(SCRIPT_DIR, 'poc_index.html'),
        width=800, height=600,
        http_server=True,  # 필수
    )
    webview.start()
```

`poc/poc_index.html`:
```html
<!DOCTYPE html>
<html>
<head><link rel="stylesheet" href="poc_style.css"></head>
<body>
  <h1 id="title">PoC Test</h1>
  <img src="../assets/32x32folk.png" alt="sprite">
  <script src="poc_script.js"></script>
</body>
</html>
```

`poc/poc_style.css`: 아무 스타일 (h1 색상 변경 등)
`poc/poc_script.js`: `document.getElementById('title').textContent += ' — JS OK';`

→ 실행 후 확인: CSS 적용됨, 이미지 보임, JS 실행됨.

**검증 B: window.state 이벤트**

`poc/poc_state.py`:
```python
import webview
import time
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def update_state(window):
    time.sleep(3)
    # 프로퍼티 설정 방식 (전체 재할당)
    window.state.counter = 1
    time.sleep(2)
    window.state.counter = 2
    time.sleep(2)
    window.state.message = 'Hello from Python'

if __name__ == '__main__':
    window = webview.create_window(
        'State PoC',
        url=os.path.join(SCRIPT_DIR, 'poc_state.html'),
        width=600, height=400,
        http_server=True,
    )
    webview.start(func=update_state, args=(window,))
```

`poc/poc_state.html`:
```html
<!DOCTYPE html>
<html><body>
<h1>State: <span id="out">waiting...</span></h1>
<script>
window.addEventListener('pywebviewready', function() {
  if (window.pywebview && window.pywebview.state) {
    window.pywebview.state.addEventListener('change', function(e) {
      document.getElementById('out').textContent = 
        'counter=' + (window.pywebview.state.counter || '?') + 
        ' msg=' + (window.pywebview.state.message || '');
      console.log('[STATE CHANGE]', e);
    });
  }
});
</script>
</body></html>
```

→ 실행 후 확인: 3초 후 counter=1, 5초 후 counter=2, 7초 후 message 표시.
→ **만약 pywebview 6.0 미만이라면**: `pip install pywebview --upgrade` 후 재시도.
→ **만약 window.state가 지원되지 않으면**: 이 기능은 Phase 3에서 사용. Phase 0~2는 영향 없음. 결과를 기록하고 진행.

**검증 C: 좀비 프로세스 방어**

`poc/poc_zombie.py`:
```python
import psutil
import os
import signal

def kill_zombie_servers(port=23948):
    """지정 포트를 점유 중인 프로세스 정리."""
    killed = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.laddr.port == port and conn.status == 'LISTEN':
            try:
                proc = psutil.Process(conn.pid)
                proc.kill()
                killed.append(conn.pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    return killed

if __name__ == '__main__':
    result = kill_zombie_servers()
    print(f"정리된 프로세스: {result if result else '없음'}")
```

→ 실행 확인. psutil 없으면 `pip install psutil`.

#### 0-4. PyInstaller PoC

```bash
pip install pyinstaller
cd poc/
pyinstaller --onedir --windowed --add-data "poc_index.html:." --add-data "poc_style.css:." --add-data "poc_script.js:." poc_app.py
```

→ `poc/dist/poc_app.app/` 생성됨.
→ `dist/poc_app.app`을 `/Applications/`로 복사 → 실행 → 에셋 로딩 확인.
→ 실패하면 결과 기록. (Phase 4에서 대응)

### 완료 기준
- [ ] `index_golden.html` 존재
- [ ] `build_dashboard_legacy.py` 존재
- [ ] PoC A: 에셋 3종 (CSS, JS, 이미지) 정상 로딩
- [ ] PoC B: window.state 변경 → JS 반영 (또는 미지원 시 기록)
- [ ] PoC C: psutil 좀비 정리 실행 성공
- [ ] PyInstaller: 더미 앱 빌드 성공 (Applications 이동 결과 기록)
- [ ] Git 커밋: `refactor(dashboard): Phase 0 — golden master + poc`

### 예상 소요: 1~2시간

---

## Phase 1: 골격 구조 생성

### 목표
1,600줄 단일 파일에서 CSS/JS를 독립 파일로 추출. Jinja2 빌드러너 작성.

### 작업

#### 1-1. 디렉토리 구조 생성

```bash
mkdir -p src/css/panels
mkdir -p src/js/panels
mkdir -p src/templates/partials
mkdir -p src/templates/includes
```

#### 1-2. CSS 추출

`build_dashboard.py`에서 `_css()` 함수 (또는 CSS를 반환하는 부분)의 내용을 추출:

1. 공통 변수, 리셋, 타이포 → `src/css/base.css`
   - 모든 하드코딩 색상을 CSS Variable로 변환
   - `:root` 에 디자인 토큰 정의 (ARCHITECTURE.md 섹션 4-1 참조)
2. 헤더, 그리드, 반응형 → `src/css/layout.css`
3. 패널별 CSS → `src/css/panels/{id}.css`
   - 각 패널 CSS는 `.panel-{id}` 네임스페이스로 감싸기

**검증:** 추출한 CSS를 `index_golden.html`에 `<link>`로 연결해서 동일하게 보이는지 확인.

#### 1-3. JS 추출

1. `_pixel_agents_js()` → `src/js/panels/pixel-agents.js` (IIFE로 감싸기)
2. `_js()` 중 공통 유틸 → `src/js/core.js`
3. Quick Launcher 관련 → `src/js/launcher.js`

**core.js 기본 구조:**
```javascript
const Dashboard = {
  data: {},
  init: function(initialData) {
    this.data = initialData || {};
    this.render();
  },
  update: function(newData) {
    this.data = newData;
    this.render();
  },
  render: function() {
    var panels = Object.keys(Dashboard.panels);
    for (var i = 0; i < panels.length; i++) {
      var p = Dashboard.panels[panels[i]];
      try {
        if (p.render) p.render(this.data);
      } catch (e) {
        console.error('[Panel ' + p.id + '] render failed:', e);
      }
    }
  },
  panels: {},
  registerPanel: function(id, module) {
    module.id = id;
    this.panels[id] = module;
  }
};
```

#### 1-4. Jinja2 빌드러너 작성

`build_dashboard.py`를 Jinja2 기반으로 재작성 (~150줄 목표):

```python
#!/usr/bin/env python3
"""build_dashboard.py v2.0 — Jinja2 기반 모듈형 빌드."""
import json, os, sys, glob
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── 패널 자동 디스커버리 ──────────────────────
def discover_panels(partials_dir):
    """partials/ 최상위 .html 파일을 스캔하여 패널 목록 반환.
    _접두사 파일은 제외 (include용)."""
    panels = []
    for f in sorted(os.listdir(partials_dir)):
        if f.startswith('_') or f.startswith('.'):
            continue
        if not f.endswith('.html'):
            continue
        panel_id = f.replace('.html', '')
        
        # 메타데이터 (_panel.json)
        meta_path = os.path.join(partials_dir, panel_id, '_panel.json')
        meta = {'order': 999, 'size': 'full', 'enabled': True}
        if os.path.exists(meta_path):
            with open(meta_path) as mf:
                meta.update(json.load(mf))
        
        if not meta.get('enabled', True):
            continue
        
        # CSS/JS 존재 여부 (규칙 기반)
        css_path = os.path.join(SCRIPT_DIR, 'src', 'css', 'panels', f'{panel_id}.css')
        js_path = os.path.join(SCRIPT_DIR, 'src', 'js', 'panels', f'{panel_id}.js')
        
        panels.append({
            'id': panel_id,
            'template': f,
            'css': f'src/css/panels/{panel_id}.css' if os.path.exists(css_path) else None,
            'js': f'src/js/panels/{panel_id}.js' if os.path.exists(js_path) else None,
            'order': meta.get('order', 999),
            'size': meta.get('size', 'full'),
        })
    
    # order → id 정렬 (결정성 보장)
    panels.sort(key=lambda p: (p['order'], p['id']))
    return panels

# ─── 빌드 ──────────────────────────────────────
def build(mode='dev'):
    partials_dir = os.path.join(SCRIPT_DIR, 'src', 'templates', 'partials')
    panels = discover_panels(partials_dir)
    
    # 관측성 출력
    panel_names = ', '.join(f"{p['id']}({p['order']})" for p in panels)
    css_count = sum(1 for p in panels if p['css'])
    js_count = sum(1 for p in panels if p['js'])
    print(f"[BUILD] 패널 {len(panels)}개 발견: {panel_names}")
    print(f"[BUILD] css: {css_count}개 | js: {js_count}개")
    
    # 데이터 로드
    data_path = os.path.join(SCRIPT_DIR, 'dashboard_data.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Jinja2 환경
    env = Environment(
        loader=FileSystemLoader(os.path.join(SCRIPT_DIR, 'src', 'templates')),
        autoescape=select_autoescape(['html', 'htm']),
        undefined=StrictUndefined,
    )
    
    template = env.get_template('base.html')
    
    if mode == 'prod':
        # 인라인 번들링: CSS/JS 파일 내용을 읽어서 전달
        # (Phase 4에서 구현)
        pass
    
    html = template.render(
        data=data,
        panels=panels,
        mode=mode,
        build_time=__import__('datetime').datetime.now().isoformat(),
    )
    
    output_path = os.path.join(SCRIPT_DIR, 'index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    size_kb = os.path.getsize(output_path) / 1024
    print(f"[BUILD] ✅ index.html 생성 완료 ({size_kb:.0f}KB)")
    return output_path

# ─── 스캐폴드 ──────────────────────────────────
def scaffold_panel(panel_id):
    """새 패널의 boilerplate 파일 3개 생성."""
    partials_dir = os.path.join(SCRIPT_DIR, 'src', 'templates', 'partials')
    css_dir = os.path.join(SCRIPT_DIR, 'src', 'css', 'panels')
    js_dir = os.path.join(SCRIPT_DIR, 'src', 'js', 'panels')
    
    # HTML
    html_path = os.path.join(partials_dir, f'{panel_id}.html')
    if not os.path.exists(html_path):
        with open(html_path, 'w') as f:
            f.write(f'''<!-- Panel: {panel_id} -->
<section class="panel panel-{panel_id}" id="panel-{panel_id}">
  <h2>{panel_id}</h2>
  <p>New panel content here.</p>
</section>
''')
    
    # CSS
    css_path = os.path.join(css_dir, f'{panel_id}.css')
    if not os.path.exists(css_path):
        with open(css_path, 'w') as f:
            f.write(f'''/* Panel: {panel_id} */
.panel-{panel_id} {{
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: var(--space-lg);
}}
''')
    
    # JS
    js_path = os.path.join(js_dir, f'{panel_id}.js')
    if not os.path.exists(js_path):
        with open(js_path, 'w') as f:
            f.write(f'''/* Panel: {panel_id} */
(function() {{
  var {panel_id.replace('-', '_').title()} = {{
    render: function(data) {{
      // TODO: implement
    }}
  }};
  Dashboard.registerPanel('{panel_id}', {panel_id.replace('-', '_').title()});
}})();
''')
    
    print(f"[SCAFFOLD] ✅ {panel_id} 생성: .html + .css + .js")

# ─── CLI ────────────────────────────────────────
if __name__ == '__main__':
    if '--new-panel' in sys.argv:
        idx = sys.argv.index('--new-panel')
        if idx + 1 < len(sys.argv):
            scaffold_panel(sys.argv[idx + 1])
        else:
            print("Usage: python3 build_dashboard.py --new-panel <id>")
        sys.exit(0)
    
    mode = 'prod' if '--prod' in sys.argv else 'dev'
    build(mode)
```

**중요:** 이 코드는 참조용입니다. 실제 구현 시 `build_dashboard_legacy.py`의 generate_html() 출력과 동일한 결과를 만들어야 합니다.

#### 1-5. base.html 작성

`src/templates/base.html`:
```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Woosdom Mission Control</title>
  <link rel="stylesheet" href="src/css/base.css">
  <link rel="stylesheet" href="src/css/layout.css">
  {% for panel in panels %}
  {% if panel.css %}<link rel="stylesheet" href="{{ panel.css }}">{% endif %}
  {% endfor %}
</head>
<body>
  {% include 'includes/_header.html' %}
  
  <main class="dashboard-grid">
    {% for panel in panels %}
    {% include 'partials/' + panel.template %}
    {% endfor %}
  </main>
  
  {% include 'includes/_footer.html' %}
  
  <!-- 초기 데이터 주입 (fetch 대신) -->
  <script type="application/json" id="dashboard-data">
  {{ data | tojson }}
  </script>
  
  <script src="src/js/core.js"></script>
  <script src="src/js/launcher.js"></script>
  {% for panel in panels %}
  {% if panel.js %}<script src="{{ panel.js }}"></script>{% endif %}
  {% endfor %}
  
  <script>
    // 인라인 JSON에서 데이터 로드
    var rawData = document.getElementById('dashboard-data');
    if (rawData) {
      try {
        Dashboard.init(JSON.parse(rawData.textContent));
      } catch(e) {
        console.error('[Dashboard] init failed:', e);
      }
    }
  </script>
</body>
</html>
```

#### 1-6. desktop.py 수정

현재 `desktop.py`의 변경 사항:
1. `url=file_url` → `url='index.html'` + `http_server=True`
2. 시작 시 좀비 프로세스 정리 추가
3. `build_html()` → 새 `build_dashboard.py`의 `build()` 호출로 변경
4. js_api 유지 (Quick Launcher)

### 검증
```bash
python3 build_dashboard.py
# 브라우저에서 index.html 열기 → index_golden.html과 비교
# 주요 확인: 레이아웃, 색상, 패널 순서, 텍스트 내용
```

### 완료 기준
- [ ] `src/` 디렉토리 구조 생성됨
- [ ] CSS가 `src/css/`에 독립 파일로 존재
- [ ] JS가 `src/js/`에 독립 파일로 존재
- [ ] `build_dashboard.py` v2.0 (Jinja2 기반, 패널 자동 디스커버리)
- [ ] `python3 build_dashboard.py` 실행 → `index.html` 생성
- [ ] 브라우저에서 Golden Master와 시각적으로 동일
- [ ] `python3 desktop.py` → 앱에서 정상 렌더링
- [ ] Git 커밋: `refactor(dashboard): Phase 1 — jinja2 build + file separation`

### 예상 소요: 4~8시간 (가장 고통스러운 Phase)

---

## Phase 2: 템플릿 분리 + 디자인 토큰

### 목표
generate_html() 내의 각 섹션을 개별 Jinja2 partial로 전환. 매크로 도입.

### 작업

#### 2-1. 패널 partial 추출

`build_dashboard_legacy.py`의 각 HTML 생성 함수를 Jinja2 partial로 변환:

| 레거시 함수 | 새 파일 |
|------------|---------|
| 브리핑 히어로 섹션 | `src/templates/partials/briefing.html` |
| 프로젝트 카드 | `src/templates/partials/projects.html` |
| 포트폴리오 | `src/templates/partials/portfolio.html` |
| 훈련 | `src/templates/partials/training.html` |
| 에이전트 상태 | `src/templates/partials/agents.html` |
| Pixel Agents HQ | `src/templates/partials/pixel-agents.html` |
| 스프린트 진행 | `src/templates/partials/sprint.html` |
| LiteLLM | `src/templates/partials/litellm.html` |
| 로드맵 | `src/templates/partials/roadmap.html` |
| 규칙 | `src/templates/partials/rules.html` |
| 완료 항목 | `src/templates/partials/completed.html` |

**패널별로 하나씩 전환.** 한 패널 전환 → 빌드 → 확인 → 다음 패널.

#### 2-2. include 파일

| 파일 | 내용 |
|------|------|
| `src/templates/includes/_header.html` | 헤더 (타이틀, 날짜, 요약 카드) |
| `src/templates/includes/_footer.html` | Quick Launcher 바 |

`_` 접두사이므로 패널 자동 발견에서 제외됨.

#### 2-3. 매크로 라이브러리

`src/templates/macros.html`:
- `badge(text, color)` — 상태/도메인 배지
- `status_dot(status)` — 상태 표시 점
- `card(title, domain)` — 카드 래퍼

base.html 상단에 `{% import 'macros.html' as ui %}` 추가.
각 partial에서 `{{ ui.badge('Finance', 'var(--color-finance)') }}` 식으로 사용.

### 검증
각 패널 전환마다:
```bash
python3 build_dashboard.py
# 브라우저에서 해당 패널이 Golden Master와 동일한지 확인
```

### 완료 기준
- [ ] 모든 패널이 `src/templates/partials/`에 개별 파일로 존재
- [ ] `macros.html` 생성 + 최소 3개 매크로 (badge, status_dot, card)
- [ ] `_header.html`, `_footer.html` 분리
- [ ] 전체 대시보드가 Golden Master와 시각적으로 동일
- [ ] Git 커밋: `refactor(dashboard): Phase 2 — template partials + macros`

### 예상 소요: 4~6시간

---

## Phase 3: 버그 수정 + window.state 실시간

### 목표
Pixel Agents 버그 6건 수정 + PyWebView 실시간 갱신 도입.

### 작업

#### 3-1. Pixel Agents 버그 수정

파일: `src/js/panels/pixel-agents.js` (독립 파일이므로 안전하게 편집 가능)

수정 대상 (이전 세션에서 진단된 6건):
1. 에이전트 상태 매핑 오류 (active/idle/done 불일치)
2. 팀별 로그 필터링 미구현
3. Done 상태 에이전트 착석 로직 오류
4. 에이전트 간 대화 기록 미반영
5. Canvas 렌더링 깨짐 (특정 상태 조합)
6. 방 배정 로직 오류

**각 버그 수정 후 빌드 → 브라우저에서 확인.**

#### 3-2. window.state 실시간 갱신

**Phase 0 PoC B 결과에 따라 분기:**

**PoC 성공 시 (window.state 지원됨):**

`desktop.py` 수정:
```python
def watcher_loop(window):
    """파일 변경 감지 → window.state로 데이터 푸시."""
    check_files_changed()
    while not _shutdown.is_set():
        _shutdown.wait(POLL_INTERVAL)
        if _shutdown.is_set():
            break
        try:
            if check_files_changed():
                new_data = load_dashboard_data()
                # 전체 재할당 (중첩 객체 반응성 보장)
                window.state.dashboard_data = new_data
                window.state.last_updated = datetime.now().isoformat()
                print(f"[MC] State updated at {time.strftime('%H:%M:%S')}")
        except Exception as e:
            if _shutdown.is_set():
                break
            print(f"[MC] Watcher error: {e}")
```

`src/js/core.js`에 추가:
```javascript
// 앱 모드: window.state 변경 시 자동 갱신
if (window.pywebview) {
  window.addEventListener('pywebviewready', function() {
    if (window.pywebview.state) {
      window.pywebview.state.addEventListener('change', function() {
        var newData = window.pywebview.state.dashboard_data;
        if (newData) {
          Dashboard.update(newData);
        }
      });
    }
  });
}
```

**PoC 실패 시 (window.state 미지원):**

현재 방식 유지 (파일 감시 → window.load_url). Phase 3에서는 버그 수정에 집중.

### 완료 기준
- [ ] Pixel Agents 버그 6건 중 최소 4건 수정
- [ ] 앱 모드에서 Obsidian 파일 변경 시 대시보드 자동 갱신
- [ ] Git 커밋: `refactor(dashboard): Phase 3 — bug fixes + realtime`

### 예상 소요: 3~5시간

---

## Phase 4: 프로덕션 빌드 + 패키징

### 목표
인라인 번들링 모드 구현 + pyinstaller 패키징.

### 작업

#### 4-1. --prod 인라인 빌드

`build_dashboard.py`의 `build(mode='prod')` 구현:
- 모든 CSS 파일 → `<style>` 태그로 인라인
- 모든 JS 파일 → `<script>` 태그로 인라인
- 이미지 → base64 인라인 (기존 방식 유지)

#### 4-2. PyInstaller 배포

```bash
# 절대 --onefile 사용 금지 (macOS 코드 사이닝 충돌)
pyinstaller --onedir --windowed \
  --add-data "src:src" \
  --add-data "assets:assets" \
  --add-data "index.html:." \
  --add-data "dashboard_data.json:." \
  --name "Woosdom" \
  desktop.py
```

빌드 후:
1. `dist/Woosdom.app/` 생성 확인
2. `/Applications/`로 복사 → 실행 확인
3. (선택) 코드 사이닝: `codesign --deep --force --sign - dist/Woosdom.app`

#### 4-3. Chart.js vendoring (선택)

차트 패널이 필요할 때:
```bash
# CDN에서 다운로드 → 로컬 보관
curl -o src/js/vendor/chart.min.js https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js
```

### 완료 기준
- [ ] `python3 build_dashboard.py --prod` → 인라인 번들 index.html 생성
- [ ] PyInstaller 빌드 → `Woosdom.app` 생성
- [ ] Applications 폴더에서 정상 실행
- [ ] Git 커밋: `refactor(dashboard): Phase 4 — production build + packaging`

### 예상 소요: 2~4시간

---

## Phase 사이 병렬 가능 구간

```
Phase 0 (순차) → Phase 1 (순차) → Phase 1 완료 후:
  ├── CC팀:  Phase 2 (패널 전환)        ← 순차 진행
  └── Codex: pixel-agents.js 버그 수정  ← 독립 파일이므로 병렬 가능
              → Phase 2 완료 시점에 merge
```

Phase 1 결과물을 보고 병렬 여부를 최종 판단.

---

## 비상 시 롤백

어떤 Phase에서든 대시보드가 심각하게 깨지면:
```bash
cp build_dashboard_legacy.py build_dashboard.py
python3 build_dashboard.py
# → 원래 index.html 복원
```

`build_dashboard_legacy.py`는 **절대 삭제하지 않는다.**

---

## 요약

| Phase | CC팀 작업 | 우성님 확인 | 예상 |
|-------|----------|-----------|------|
| 0 | Golden Master + PoC 4종 | 앱 뜨는지 | 1~2h |
| 1 | 파일 분리 + Jinja2 빌드러너 | Golden Master 비교 | 4~8h |
| 2 | 패널 partial 전환 + 매크로 | 눈으로 확인 | 4~6h |
| 3 | 버그 수정 + window.state | 버그 확인 | 3~5h |
| 4 | 인라인 빌드 + pyinstaller | 앱 실행 | 2~4h |

**총 CC팀 작업: 14~25시간 / 우성님 개입: ~30분**
