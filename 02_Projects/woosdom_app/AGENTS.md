# AGENTS.md — Woosdom Dashboard
*For: All AI coding agents (Claude Code, Codex, Cursor, etc.)*

## Project

Woosdom Dashboard — PyWebView 기반 데스크톱 대시보드. Obsidian 볼트 데이터를 시각화.

## Tech Stack

- **Build:** Python 3 + Jinja2 (정적 HTML 생성)
- **Frontend:** Vanilla CSS + Vanilla JS (ES2015+, no React/npm)
- **Runtime:** PyWebView (http_server=True)
- **Package:** PyInstaller --onedir (NOT --onefile)

## Build

```bash
python3 build_dashboard.py          # dev (external CSS/JS)
python3 build_dashboard.py --prod   # prod (inline bundle)
python3 build_dashboard.py --new-panel <id>  # scaffold
```

## Critical Rules

Full rules: see `CLAUDE.md`

1. **One panel per task.** Never modify multiple panels simultaneously.
2. **Do not modify:** `build_dashboard.py`, `core.js`, `base.html` without Brain approval.
3. **Do not edit:** `index.html` (generated output).
4. **CSS:** Use tokens only (`var(--color-*)`, `var(--space-*)`). No hardcoded values.
5. **JS:** IIFE wrapper. No globals except `Dashboard`.
6. **No fetch().** Data via inline `<script type="application/json">` or `window.state`.
7. **window.state:** Top-level reassignment only. No nested mutation.
8. **PyInstaller:** `--onedir` only. `--onefile` breaks macOS code signing.
9. **Panel discovery:** Files in `src/templates/partials/`. `_` prefix = excluded.

## File Structure

```
src/
├── css/base.css, layout.css, panels/*.css
├── js/core.js, launcher.js, panels/*.js
└── templates/base.html, partials/*.html, includes/_*.html, macros.html
```

## Reference

- `ARCHITECTURE.md` — Full architecture spec
- `CLAUDE.md` — Detailed rules
- `CC_EXECUTION_GUIDE.md` — Phase-by-phase execution plan
