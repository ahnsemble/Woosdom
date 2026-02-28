# Woosdom Brain — Claude Code Configuration

This is the Obsidian vault for the Woosdom AI orchestration system.

## Structure
- `00_System/` — AI operating system (prompts, templates, specs)
- `01_Domains/` — Domain knowledge (finance, health, career)
- `02_Projects/` — Active projects
- `03_Journal/` — Time-based records
- `04_Archive/` — Completed items

## Key Files

| Purpose | Path |
|---------|------|
| Brain rules | `00_System/Prompts/Ontology/brain_directive.md` |
| Current state | `00_System/Prompts/Ontology/active_context.md` |
| Agent activity | `00_System/Logs/agent_activity.md` |
| Work orders (out) | `00_System/Templates/to_hands.md` |
| Work reports (in) | `00_System/Templates/from_hands.md` |
| Finance (read-only) | `01_Domains/Finance/portfolio.json`, `01_Domains/Finance/Rules.md` |

## Rules for Claude Code
- Read `brain_directive.md` before starting any task
- Write results to `from_hands.md`
- Never modify `brain_directive.md` or `active_context.md` without Brain approval
- All file paths use absolute VAULT_ROOT prefix

## Brain 보고 포맷

```markdown
## ✅ 완료 보고
**작업:** [한 줄 요약]
**결과:** [핵심 결과 1-3줄]
**산출물:** [파일 경로/PR URL]
**이슈:** [있을 경우]
**turns 소모:** [N/max-turns]
```
