# Sprint 5-3 DD Report: Codex CLI 가용성
*Date: 2026-02-23 21:50 KST*

## Summary
- Codex CLI 설치: ✅ (v0.104.0, `/opt/homebrew/bin/codex`)
- `codex exec` 가용: ✅ (완전 동작)
- Headless 실행: ✅ (`--full-auto` + `--skip-git-repo-check`)
- JSON 출력: ✅ (`--json` → JSONL 이벤트 스트리밍)
- 병렬 실행: ✅ (동시 2개 프로세스 성공)
- **Go/No-Go 판정: 🟢 GO**

## TASK 1 Results: Codex CLI 존재 확인
```
$ which codex
/opt/homebrew/bin/codex

$ codex --version
codex-cli 0.104.0

$ codex --help
주요 서브커맨드:
  exec        Run Codex non-interactively [aliases: e]
  review      Run a code review non-interactively
  mcp         Manage external MCP servers for Codex
  mcp-server  Start Codex as an MCP server (stdio)
  cloud       [EXPERIMENTAL] Browse tasks from Codex Cloud
  sandbox     Run commands within a Codex-provided sandbox
  + login, logout, completion, debug, apply, resume, fork, features, help
```

## TASK 2 Results: `codex exec` 서브커맨드 검증
```
$ codex exec --help
✅ 서브커맨드 존재 확인

핵심 옵션:
  --json                  JSONL 이벤트 출력
  -o, --output-last-message <FILE>  마지막 메시지 파일 저장
  --full-auto             무인 자동 실행 (workspace-write sandbox)
  --skip-git-repo-check   Git repo 외부 실행 허용
  -m, --model <MODEL>     모델 선택
  -s, --sandbox           read-only / workspace-write / danger-full-access
  -C, --cd <DIR>          작업 디렉토리 지정
  --ephemeral             세션 파일 비저장
  --output-schema <FILE>  응답 JSON Schema 지정
```

## TASK 3 Results: Headless 실행 테스트

### 3-1: 간단한 명령 실행 (Plain text)
```
$ codex exec "현재 디렉토리의 파일 목록을 보여줘" --full-auto --skip-git-repo-check

model: gpt-5.3-codex
provider: openai
sandbox: workspace-write
reasoning effort: xhigh

실행 명령: /bin/zsh -lc 'ls -1A'
결과: 파일 목록 정상 출력 (9개 항목)
토큰 사용: 3,012
```

### 3-2: JSON 출력 모드
```
$ codex exec "echo hello" --json --full-auto --skip-git-repo-check

출력 형식: JSONL (한 줄에 한 JSON 객체)

이벤트 시퀀스:
  1. {"type":"thread.started","thread_id":"..."}
  2. {"type":"turn.started"}
  3. {"type":"item.completed","item":{"type":"reasoning",...}}
  4. {"type":"item.completed","item":{"type":"agent_message",...}}
  5. {"type":"item.started","item":{"type":"command_execution","status":"in_progress",...}}
  6. {"type":"item.completed","item":{"type":"command_execution","exit_code":0,"aggregated_output":"hello\n","status":"completed"}}
  7. {"type":"item.completed","item":{"type":"agent_message","text":"hello"}}
  8. {"type":"turn.completed","usage":{"input_tokens":15879,"cached_input_tokens":14848,"output_tokens":185}}
```

## TASK 4 Results: 출력 스트림 형식 분석

| 질문 | 답변 |
|------|------|
| 이벤트 기반 스트리밍인가? | ✅ 예 — JSONL 형식, 라인별 이벤트 |
| 완료 시그널 있는가? | ✅ 예 — `turn.completed` (토큰 사용량 포함) |
| 에러 시 구분 가능한가? | ✅ 예 — `command_execution` 아이템의 `exit_code` + `status` 필드 |

### 이벤트 타입 분류
| type | 설명 | 핵심 필드 |
|------|------|-----------|
| `thread.started` | 세션 시작 | `thread_id` |
| `turn.started` | 턴 시작 | — |
| `item.completed` (reasoning) | 모델 사고 과정 | `text` |
| `item.completed` (agent_message) | 모델 응답 | `text` |
| `item.started` (command_execution) | 명령 실행 시작 | `command`, `status: in_progress` |
| `item.completed` (command_execution) | 명령 실행 완료 | `command`, `aggregated_output`, `exit_code`, `status: completed` |
| `turn.completed` | 턴 완료 | `usage: {input_tokens, cached_input_tokens, output_tokens}` |

## TASK 5 Results: 프로그래밍적 결과 수집

### 5-1: stdout 캡처
```
$ RESULT=$(codex exec "echo 'DD_TEST_SUCCESS'" --full-auto --skip-git-repo-check 2>&1)
→ DD_TEST_SUCCESS 정상 캡처 ✅
  (단, plain text 모드는 헤더/세션 정보 포함 → 파싱 필요)
```

### 5-2: exit code
```
$ codex exec "echo hello" --full-auto --skip-git-repo-check > /dev/null 2>&1; echo $?
→ EXIT CODE: 0 ✅
```

### 보너스: -o 플래그 테스트
```
$ codex exec "echo 'LAST_MSG_TEST'" --full-auto --skip-git-repo-check -o /tmp/codex_last_msg.txt
→ /tmp/codex_last_msg.txt에 마지막 메시지만 저장 ✅
  내용: `LAST_MSG_TEST`
```

### 결과 수집 권장 방식
1. **최적:** `--json` → JSONL 파싱 (`turn.completed` 감지)
2. **간편:** `-o <file>` → 마지막 메시지만 파일로 저장
3. **단순:** stdout 캡처 (헤더 포함, 파싱 필요)

## TASK 6 Results: 병렬 실행

```
$ codex exec "sleep 3 && echo TASK_A_DONE" --full-auto -o /tmp/a.txt &
$ codex exec "sleep 3 && echo TASK_B_DONE" --full-auto -o /tmp/b.txt &
$ wait

TASK_A: TASK_A_DONE, exit 0 ✅
TASK_B: TASK_B_DONE, exit 0 ✅
병렬 실행: 동시 2개 프로세스 정상 완료 ✅
```

## TASK 7 Results
**SKIP** — `codex exec`이 완전히 동작하므로 대안 조사 불필요.

## Brain에게 전달할 핵심 정보

### Codex MCP 래퍼 구축 가능 여부: **예 ✅**

### 권장 접근 방식: `codex exec` CLI 래핑

**MCP 래퍼 구현에 필요한 핵심 인터페이스:**
```bash
# 비동기 태스크 생성 (spawn)
codex exec "<prompt>" --full-auto --skip-git-repo-check --json -C <workdir> &
PID=$!

# 상태 폴링 (poll)
# → --json 스트림에서 turn.completed 감지

# 결과 수집 (get_result)
# → -o <file> 또는 --json 파싱
```

**Codex CLI의 추가 발견 (Phase 5-3에 유용):**
| 기능 | 설명 | Sprint 5-3 활용 |
|------|------|----------------|
| `codex mcp-server` | Codex를 MCP 서버로 실행 (stdio) | CC에서 MCP 클라이언트로 직접 연결 가능 |
| `codex cloud` | [EXPERIMENTAL] Codex Cloud 태스크 | 향후 클라우드 실행 경로 |
| `--output-schema` | 응답 JSON Schema 지정 | 구조화된 결과 강제 |
| `--ephemeral` | 세션 비저장 | 일회성 태스크에 적합 |
| `-m <model>` | 모델 선택 | gpt-5.3-codex 외 다른 모델 테스트 가능 |
| `codex sandbox` | 명령을 Codex sandbox에서 실행 | 안전한 코드 실행 |

### ⚠️ 주의 사항
1. **MCP 서버 연결 실패:** Codex의 자체 MCP 설정(`.codex/` 설정)에서 `woosdom-executor`, `obsidian-vault` 연결 시도 후 실패. CC의 `.mcp.json`과는 별개 설정.
2. **기본 모델:** `gpt-5.3-codex` (reasoning effort: xhigh) — 비용 주의 필요.
3. **캐시 히트율:** `cached_input_tokens: 14848 / input_tokens: 15879` ≈ 93.5% — 반복 실행 시 비용 절감 효과 큼.

### 추가 조사 필요 항목
- ~~`codex mcp-server`의 제공 도구(tools) 목록 확인~~ → **아래 DD 추가 참조**
- Codex Cloud API 안정성 확인 (현재 EXPERIMENTAL)
- `--output-schema` 활용한 구조화 응답 테스트

---

## DD 추가: codex mcp-server 조사 (2026-02-23)

### TASK 1: 도구 목록

**서버 정보:**
```json
{
  "name": "codex-mcp-server",
  "title": "Codex",
  "version": "0.104.0",
  "protocolVersion": "2024-11-05",
  "capabilities": { "tools": { "listChanged": true } }
}
```

**도구 2개 확인:**

#### 1. `codex` — 세션 실행
```
description: "Run a Codex session. Accepts configuration parameters matching the Codex Config struct."
required: ["prompt"]
```

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `prompt` **(required)** | string | 초기 사용자 프롬프트 |
| `cwd` | string | 작업 디렉토리 (상대 경로 시 서버 CWD 기준) |
| `model` | string | 모델 오버라이드 (e.g. `gpt-5.2`, `gpt-5.2-codex`) |
| `sandbox` | enum | `read-only` / `workspace-write` / `danger-full-access` |
| `approval-policy` | enum | `untrusted` / `on-failure` / `on-request` / `never` |
| `base-instructions` | string | 기본 지시 대체 |
| `developer-instructions` | string | 개발자 role 메시지 주입 |
| `config` | object | config.toml 오버라이드 |
| `profile` | string | 설정 프로파일 |
| `compact-prompt` | string | 대화 압축 시 프롬프트 |

outputSchema: `{ threadId: string, content: string }`

#### 2. `codex-reply` — 대화 계속
```
description: "Continue a Codex conversation by providing the thread id and prompt."
required: ["prompt"]
```

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `prompt` **(required)** | string | 다음 사용자 프롬프트 |
| `threadId` | string | 세션 스레드 ID (codex 도구 반환값) |
| `conversationId` | string | (DEPRECATED → threadId 사용) |

outputSchema: `{ threadId: string, content: string }`

### TASK 2: 도구 분석

| 질문 | 답변 |
|------|------|
| 태스크 실행 도구가 있는가? | ✅ `codex` 도구 = 완전한 에이전트 세션 실행 |
| 비동기 실행이 가능한가? | ⚠️ MCP 호출 자체는 동기식이지만, 실행 중 `codex/event` 알림으로 스트리밍 이벤트 전달. `threadId` 기반 세션 유지로 멀티턴 가능 |
| 결과 조회 도구가 있는가? | ✅ `codex-reply`로 기존 세션에 후속 질문 (threadId 기반) |
| 파일 I/O 도구가 있는가? | ❌ 별도 도구 없음. Codex 에이전트가 내부적으로 셸 명령으로 처리 |

**핵심 인사이트:**
- `codex` 도구 하나로 `spawn_codex_task` + `get_codex_result`를 동시에 해결
- `codex-reply`로 `poll_codex_status` 및 후속 지시 가능
- **Node.js 래퍼에서 설계했던 3개 도구(spawn/poll/get_result) 대신, 빌트인 2개 도구로 충분**

### TASK 3: CC 연결 테스트

```
# 현재 .mcp.json (Woosdom_Brain)
{
  "mcpServers": {
    "obsidian-vault": { ... }  ← 기존 MCP 서버 (수정 안 함)
  }
}

# CC에 codex-server 등록
$ claude mcp add codex-server -- codex mcp-server
→ ✅ "Added stdio MCP server codex-server"
→ 저장 위치: ~/.claude.json (project: /Users/woosung/Desktop/Dev)

# 등록 확인
~/.claude.json → projects./Desktop/Dev.mcpServers.codex-server
{
  "type": "stdio",
  "command": "codex",
  "args": ["mcp-server"],
  "env": {}
}
```

### TASK 4: 도구 호출 테스트

`claude -p`는 중첩 세션 제약으로 사용 불가하여, Python으로 MCP 프로토콜 직접 호출하여 검증.

```
테스트: codex mcp-server → tools/call → codex 도구
프롬프트: "echo DD_MCP_TEST_SUCCESS"

이벤트 수신: 91개
주요 이벤트 흐름:
  [0]  session_configured (model: gpt-5.3-codex, sandbox: workspace-write)
  [1-3] mcp_startup_update (MCP 서버 시작 시도)
  [7]  task_started
  [14] token_count
  [18-28] reasoning_content_delta (모델 사고 과정 스트리밍)
  [32-59] agent_message_content_delta (응답 스트리밍)
  [65] exec_command_begin
  [66] exec_command_end
  [70-85] agent_message_content_delta (최종 응답)
  [89] task_complete
  [90] FINAL RESULT → "DD_MCP_TEST_SUCCESS" ✅
```

**스트리밍 이벤트 타입 (codex/event):**
| type | 설명 |
|------|------|
| `session_configured` | 세션 설정 완료 (모델, sandbox, CWD 등) |
| `mcp_startup_update` | MCP 서버 시작 상태 |
| `task_started` | 태스크 시작 |
| `reasoning_content_delta` | 추론 과정 스트리밍 |
| `agent_message_content_delta` | 응답 텍스트 스트리밍 |
| `exec_command_begin` | 셸 명령 실행 시작 |
| `exec_command_end` | 셸 명령 실행 완료 |
| `token_count` | 토큰 사용량 업데이트 |
| `task_complete` | 태스크 완료 |

테스트 후 `claude mcp remove codex-server`로 정리 완료.

### 최종 판정

| 항목 | 판정 |
|------|------|
| **경로 A (codex mcp-server 직접 연결)** | 🟢 **GO** |
| **경로 B (Node.js 래퍼) 필요 여부** | **아니오** — 불필요 |
| **권장 접근** | **경로 A (직접 연결)** |

**근거:**
1. `codex mcp-server`가 `codex` + `codex-reply` 2개 도구를 이미 제공
2. CC에서 `claude mcp add codex-server -- codex mcp-server`로 즉시 연결 가능
3. Node.js Express MCP 래퍼에서 계획했던 `spawn_codex_task`, `poll_codex_status`, `get_codex_result` 3개 도구가 빌트인으로 대체됨
4. 스트리밍 이벤트(`codex/event`)로 실시간 진행 상황 확인 가능
5. `threadId`로 멀티턴 대화 유지 → 복잡한 작업도 단계적 실행 가능

**Sprint 5-3 수정 권장사항:**
- ~~Node.js Express MCP 서버 개발~~ → `codex mcp-server` 직접 등록으로 대체
- 스프린트 범위를 "MCP 서버 개발"에서 "MCP 연결 설정 + E2E 검증 + 패턴 A 워크플로 테스트"로 축소
- 예상 절감: 개발 시간 1~2주 → 설정+검증 1~2일

---

## Sprint 5-3 실행 결과 (2026-02-23)

### MCP 등록
- codex-server 등록: ✅ (`claude mcp add codex-server -- codex mcp-server`, 프로젝트: Woosdom_Brain)
- CLAUDE.md 정책 추가: ✅ (Codex MCP 사용 규칙 섹션 추가, 기존 내용 유지)

### 응답 구조 발견
```json
{
  "content": [{"type": "text", "text": "5050"}],
  "structuredContent": {
    "threadId": "019c8aa7-7ad1-...",
    "content": "5050"
  }
}
```
- `content[0].text`: 응답 텍스트 (plain)
- `structuredContent.threadId`: 세션 ID (멀티턴에 필요)
- `structuredContent.content`: 응답 텍스트

### E2E 결과
| 테스트 | 결과 | 비고 |
|--------|------|------|
| TASK 3: 단순 실행 (sum 1..100) | ✅ | `codex` 도구 호출 → 5050 반환, threadId 취득 |
| TASK 4: 멀티턴 (sum 1..1000) | ✅ | `codex-reply` + threadId → 500500 반환, 세션 유지 확인 |
| TASK 5: 패턴 A 미니 (portfolio 검증) | ✅ | vault 파일 읽기 → 비중 합계 1.0 검증 → 결과 파일 저장. portfolio.json 무결성 확인 |

### 상세 결과

#### TASK 3: 단순 실행
- 프롬프트: `print(sum(range(1,101))) 실행`
- 모델: `gpt-5.3-codex`
- 결과: `5050` ✅
- threadId: `019c8aa7-7ad1-71d1-8ad3-c1d1672740b2`

#### TASK 4: 멀티턴
- 프롬프트: `print(sum(range(1,1001))) 실행`
- threadId 재사용: ✅ (동일 세션)
- 결과: `500500` ✅

#### TASK 5: 패턴 A 미니
- Codex가 `portfolio.json` 읽기 → `default_portfolio` 6종목 비중 합산 → 1.0 = PASS
- 결과 파일 `codex_pattern_a_test.md` 생성 확인 ✅
- portfolio.json 무결성 검증 (키/값 불변) ✅
- Codex가 "수정하지 않음" 명시적 보고 ✅

### Sprint 5-3 완료 판정: ✅ PASS

**Sprint 5-3 달성 사항:**
1. `codex mcp-server` 직접 연결 경로 확립 (Node.js 래퍼 불필요)
2. CC ↔ Codex MCP 양방향 통신 검증 완료
3. 멀티턴 세션(threadId) 정상 동작 확인
4. 패턴 A 워크플로(vault 읽기 → 연산 → vault 저장) E2E 성공
5. 금융 파일 안전성(읽기 전용) 확인
6. CLAUDE.md에 Codex 사용 정책 공식화
