# AGENTS.md — Project Crossy
*For: All AI coding agents (Claude Code, Codex, Cursor, etc.)*

## Project
Project Crossy — Godot 4.x 기반 캐주얼 모바일 러너 게임.

## Tech Stack
- **Engine:** Godot 4.x (GDScript)
- **Target:** iOS / Android
- **Art:** Pixel art (Aseprite)

## Directory
```
agents/          — AI 에이전트 역할 프로필 (art_director, engineer 등)
gdd/             — Game Design Document
research/        — 시장 조사, 레퍼런스
project/         — 마일스톤, 스프린트
decisions/       — 설계 결정 기록
```

## Critical Rules
1. GDScript 코드 스타일은 GDD의 코딩 컨벤션을 따를 것.
2. 에이전트 역할 프로필은 `agents/` 참조.
3. 설계 변경은 반드시 `decisions/`에 기록.
4. 아트 에셋은 Aseprite 소스 파일 포함.

## Reference
- `crossy_master_roadmap_v1.md` — 마스터 로드맵
- `agents/` — 5개 에이전트 역할 (art_director, engineer_godot, game_designer, market_analyst, qa_critic)
