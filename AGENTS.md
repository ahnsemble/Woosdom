# AGENTS.md — Woosdom Brain Vault
*For: All AI coding agents (Claude Code, Codex, Cursor, etc.)*

## Project
Woosdom — AI 페르소나 시스템. Brain(전략) + Hands(실행) + Memory(Obsidian) 아키텍처.

## Structure
```
00_System/       — 프롬프트, 스킬, 템플릿
01_Domains/      — 도메인별 지식 (Finance, Career, Health)
02_Projects/     — 프로젝트별 디렉토리
03_Journal/      — 일지
```

## Skills
8개 스킬 라이브러리가 `00_System/Skills/` + `01_Domains/*/`에 존재.
각 스킬은 `SKILL.md` 포맷.

## Critical Rules
1. 이 볼트는 Obsidian 마크다운 기반. 파일 경로 변경 시 내부 링크 파손 주의.
2. `00_System/Templates/to_[engine].md`는 Brain→Hands 디스패치 채널. 직접 수정 금지.
3. `brain_directive.md`는 시스템 프롬프트. 구조 변경 시 Brain 승인 필수.
4. 금융 데이터 연산을 LLM에 위임하지 말 것.

## Reference
- `00_System/Prompts/Ontology/brain_directive.md` — Brain 핵심 지침
- `00_System/Prompts/Ontology/active_context.md` — 현재 컨텍스트
- `02_Projects/woosdom_app/AGENTS.md` — 대시보드 앱 전용
- `02_Projects/game_crossy/AGENTS.md` — Crossy 게임 전용
