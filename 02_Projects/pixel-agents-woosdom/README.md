# pixel-agents-woosdom

Real-time pixel art visualization of Woosdom's AI agent orchestration.

An Electron desktop app that watches your Obsidian vault and brings AI agents to life as pixel art characters working in a virtual office.

## Features

- 🏢 3 team rooms (CC / AG / Codex) + Brain command center
- 📋 File-based IPC: Brain writes `to_hands.md` → agents activate
- ⌨️ Real-time status: typing (working), walking (idle), ✅ (done), ❌ (error)
- 🎨 Customizable office layout via `config/layout.json`
- 🔄 Auto-refresh on vault file changes

## Prerequisites

- Node.js 18+
- This app must be inside a Woosdom vault (it reads `to_hands.md` / `from_hands.md` via relative paths)
- RPG Maker VX Ace compatible tileset PNGs in `src/assets/tilesets/vx_ace/` (not included, see [tileset README](./src/assets/tilesets/vx_ace/README.md))

## Install & Run

```bash
npm install
npm run dev
```

For production build:
```bash
npm run build
```

## Configuration

- `config/layout.json` — Office room layout, desk positions, door locations
- `config/tileset-map.json` — Tileset sprite mapping
- Agent roles and names are defined in the main Woosdom vault's `brain_directive.md`

## Acknowledgments

- Inspired by [pablodelucca/pixel-agents](https://github.com/pablodelucca/pixel-agents) — the original VS Code extension that turns Claude Code agents into pixel art characters
- Office simulation concept influenced by [a16z-infra/ai-town](https://github.com/a16z-infra/ai-town)
- Tileset assets require separate RPG Maker VX Ace compatible tilesets (not included due to licensing)

## License

MIT © ahnsemble
