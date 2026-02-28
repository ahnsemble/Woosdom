# Antigravity ↔ Obsidian MCP 연동 가이드
*Version: 1.0*

---

## 개요

Brain(Claude)은 MCP를 통해 Obsidian에 접근합니다.
Antigravity(Hands)도 동일한 MCP 서버를 연결하면, Brain과 **동일한 도구**로 Obsidian을 읽고 씁니다.

| MCP 서버 | 역할 | 제공 도구 |
|----------|------|----------|
| **obsidian-vault** (filesystem) | 파일 읽기/쓰기/검색 | `read_file`, `write_file`, `edit_file` 등 |
| **woosdom-executor** (커스텀) | Brain-Hands 위임 + AI 호출 | `delegate_to_engine`, `query_gemini`, `query_gpt` |

---

## 설정 예시

### Google AI Studio / Gemini CLI

```json
{
  "mcpServers": {
    "obsidian-vault": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic/mcp-filesystem",
        "/path/to/your/Woosdom_Brain"
      ]
    },
    "woosdom-executor": {
      "command": "npx",
      "args": ["tsx", "/path/to/mcp_server/src/index.ts"],
      "env": {
        "WOOSDOM_BRAIN_PATH": "/path/to/your/Woosdom_Brain",
        "GEMINI_API_KEY": "<your-key>",
        "OPENAI_API_KEY": "<your-key>"
      }
    }
  }
}
```

### Claude Desktop

`~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):
```json
{
  "mcpServers": {
    "obsidian-vault": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-filesystem", "/path/to/your/Woosdom_Brain"]
    }
  }
}
```

### Other IDEs

| IDE | 설정 파일 위치 |
|-----|---------------|
| Cursor | `.cursor/mcp.json` |
| VS Code (Copilot) | `.vscode/mcp.json` |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` |

---

## 검증 절차

1. **Filesystem 서버:** `read_file` → `active_context.md` 내용 표시되면 성공
2. **Executor 서버:** `read_hands_result` → 내용 또는 "결과 없음" 메시지면 성공
3. **쓰기 검증:** `write_file` → `from_hands.md` 변경 확인

---

## 연결 후 워크플로우 변화

**Before:** Brain → to_hands.md → 사용자가 수동 복사 → 엔진에 붙여넣기 → 결과 수동 복사
**After:** Brain → to_hands.md (MCP) → 사용자가 "to_hands 읽고 실행해" 한 마디 → 엔진이 MCP로 직접 읽기/쓰기

**사용자 개입: "복사-붙여넣기" → "한 마디 지시"로 축소.**

---

## 트러블슈팅

| 문제 | 해결 |
|------|------|
| `npx: command not found` | Node.js 18+ 설치 확인 |
| Permission denied | 볼트 경로 권한 확인 |
| MCP 서버 시작 안 됨 | `npm run dev`로 단독 테스트 |
| API 오류 | `.env` 파일의 API 키 확인 |
| 경로 오류 | 절대 경로 사용 필수. `~` 축약 금지 |
