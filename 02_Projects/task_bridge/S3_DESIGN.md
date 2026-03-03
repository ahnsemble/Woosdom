# S-3 v2: 양방향 Telegram (mrstack 참고)

*Updated: 2026-03-02*
*참고: github.com/whynowlab/mrstack*

---

## 아키텍처 변경: 자체 구현 → claude-code-telegram 베이스

### Before (S-3 v1)
자체 telegram_bot.py + python-telegram-bot → 복잡, 시간 많이 걸림

### After (S-3 v2 — mrstack 방식)
```
[claude-code-telegram]        ← 베이스 봇 (nicepkg 오픈소스)
  ├── TG ↔ Claude Code 통신   ← 이미 구현됨
  ├── 세션 유지                ← 이미 구현됨
  ├── 음성/파일 처리           ← 이미 구현됨
  └── LaunchAgent 데몬         ← 이미 구현됨

[Woosdom Brain Layer]          ← 우리가 추가하는 부분
  ├── CLAUDE.md (Brain 시스템 프롬프트)
  ├── Vault 접근 (APPROVED_DIRECTORY)
  ├── task_bridge 연동 (to_/from_ 파일)
  └── 커스텀 명령어 (/vault, /context, /engines)
```

---

## 구현 계획

### Step 1: claude-code-telegram 설치
```bash
uv tool install claude-code-telegram
# 또는
pip install claude-code-telegram
```

### Step 2: .env 설정
```bash
TELEGRAM_BOT_TOKEN=<기존 TG_BOT_TOKEN 사용>
TELEGRAM_BOT_USERNAME=woosdom_brain_bot
APPROVED_DIRECTORY=/Users/woosung/Desktop/Dev/Woosdom_Brain
ALLOWED_USERS=<우성님 TG user ID>
USE_SDK=true
```

### Step 3: CLAUDE.md 작성 (Brain 시스템 프롬프트)
APPROVED_DIRECTORY 루트에 CLAUDE.md를 두면 claude-code-telegram이 자동으로 읽음.

```markdown
# Woosdom Brain — Telegram Interface

당신은 Woosdom 시스템의 Brain입니다.
사용자가 Telegram에서 메시지를 보내고 있습니다.

## 핵심 규칙
1. 항상 한국어로 응답
2. 존대말 사용
3. TG 특성상 간결하게 (200자 이내 권장, 필요시 확장)

## Vault 구조
- 00_System/Prompts/Ontology/brain_directive.md → Brain 지시서
- 00_System/Prompts/Ontology/active_context.md → 현재 진행 상황
- 00_System/Templates/to_[engine].md → 엔진 작업 위임
- 00_System/Templates/from_[engine].md → 엔진 실행 결과
- 01_Domains/ → 도메인별 지식 (Finance, Health, Career)
- 02_Projects/ → 프로젝트 파일
- 03_Journal/ → 일지

## 작업 위임 방법
코드 실행이나 파일 수정이 필요하면:
1. to_claude_code.md에 작업지시서 작성 → task_bridge가 자동 실행
2. to_codex.md에 작성 → Codex 자동 실행
3. to_antigravity.md에 작성 → Gemini CLI 자동 실행

## 사용자 질문 유형별 처리
- 간단한 질문 → 직접 답변
- Vault 조회 → 파일 읽고 답변
- 코드 실행 → to_[engine].md 작성 후 "작업을 위임했습니다" 보고
- 진행 상황 → active_context.md 읽고 요약

## 응답 포맷 (TG 최적화)
- 이모지 적극 활용 (가독성)
- 코드블록은 짧게
- 긴 내용은 핵심만 요약 + "상세 내용은 Vault에서 확인하세요"
```

### Step 4: LaunchAgent 등록
```xml
<!-- com.woosdom.telegram-bot.plist -->
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.woosdom.telegram-bot</string>
  <key>ProgramArguments</key>
  <array>
    <string>/Users/woosung/.local/bin/claude-code-telegram</string>
  </array>
  <key>WorkingDirectory</key>
  <string>/Users/woosung/Desktop/Dev/Woosdom_Brain</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>TELEGRAM_BOT_TOKEN</key>
    <string>REPLACE</string>
    <key>TELEGRAM_BOT_USERNAME</key>
    <string>woosdom_brain_bot</string>
    <key>APPROVED_DIRECTORY</key>
    <string>/Users/woosung/Desktop/Dev/Woosdom_Brain</string>
    <key>ALLOWED_USERS</key>
    <string>REPLACE</string>
  </dict>
  <key>KeepAlive</key>
  <true/>
  <key>RunAtLoad</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/tmp/woosdom-tg-bot.log</string>
  <key>StandardErrorPath</key>
  <string>/tmp/woosdom-tg-bot.err</string>
</dict>
</plist>
```

### Step 5: task_bridge 연동
기존 task_bridge는 그대로 유지.
Brain이 TG에서 to_[engine].md를 쓰면 → task_bridge가 감지 → 엔진 실행 → 결과 TG 알림.

연동 포인트:
- Brain(CC)이 to_ 파일 직접 작성 가능 (APPROVED_DIRECTORY 안이므로)
- task_bridge의 TG 알림은 기존대로 동작 (별도 봇 or 같은 봇)

### Step 6: 🐛 task_bridge v4.4 버그 수정
```python
# status:done 재감지 방지
if "status: done" in content[:200] or "status: complete" in content[:200]:
    continue
```

---

## mrstack 대비 차이점

| mrstack | Woosdom S-3 |
|---------|-------------|
| Jarvis Mode (5분 시스템 스캔) | ❌ S-4에서 검토 |
| Memory (people/projects/daily) | Vault가 이미 담당 |
| Pattern Learning (interactions.jsonl) | ❌ S-4에서 검토 |
| Daily Coaching Report | ❌ S-4에서 검토 |
| Persona Layer (톤 조절) | CLAUDE.md에 간단 규칙만 |
| Scheduler (cron 9개) | LaunchAgent 이미 있음 |
| MCP 연동 | ❌ 추후 |

**S-3 = 양방향 TG 기본 통신만. 나머지는 S-4+에서.**

---

## CC 위임 태스크

### T1: claude-code-telegram 설치 + .env 설정
### T2: CLAUDE.md 작성 (Woosdom Brain 시스템 프롬프트)
### T3: 새 TG 봇 생성 또는 기존 봇 재활용 확인
### T4: LaunchAgent plist 생성 + 등록
### T5: task_bridge v4.4 버그 수정 (status:done)
### T6: E2E 테스트

**예상 소요: 2~3시간 (기존 7~8시간에서 대폭 단축)**
