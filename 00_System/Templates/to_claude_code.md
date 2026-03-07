---
title: "볼트→레포 rsync + 보안 검증 + 로컬 커밋"
engine: "claude_code"
reason: "rsync + git commit = CC 네이티브. 원격 전송 명령은 포함하지 않음."
brain_followup: "from_claude_code.md에서 (1) rsync 전송 파일 수, (2) git diff --stat, (3) 커밋 해시 확인."
created: "2026-03-07T01:39:04.255Z"
status: pending
---

# 실행 지시서

## 💻 볼트→레포 동기화 + 보안 검증 + 커밋

### 구조
- 볼트 (소스): `/Users/woosung/Desktop/Dev/Woosdom_Brain/`
- 레포 (타겟): `/Users/woosung/Desktop/Dev/woosdom-brain-repo/`

### 1단계: rsync 동기화
```bash
rsync -av --delete \
  --exclude='.git' \
  --exclude='.obsidian' \
  --exclude='node_modules' \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='chroma_db' \
  --exclude='build' \
  --exclude='dist' \
  --exclude='dist-electron' \
  --exclude='release' \
  --exclude='.DS_Store' \
  --exclude='.env' \
  --exclude='.env.*' \
  --exclude='*.pid' \
  --exclude='*.db' \
  --exclude='*.db-shm' \
  --exclude='*.db-wal' \
  --exclude='*.log' \
  --exclude='*.bak' \
  --exclude='*.tmp' \
  --exclude='.claude' \
  --exclude='.gemini' \
  --exclude='04_Archive' \
  --exclude='data/bot.db*' \
  --exclude='.mcp.json' \
  /Users/woosung/Desktop/Dev/Woosdom_Brain/ \
  /Users/woosung/Desktop/Dev/woosdom-brain-repo/
```

### 2단계: 기존 트래킹 위험 파일 제거
```bash
cd /Users/woosung/Desktop/Dev/woosdom-brain-repo
git rm -r --cached 04_Archive/ 2>/dev/null || true
git rm -r --cached data/ 2>/dev/null || true
git rm -r --cached .obsidian/ 2>/dev/null || true
git rm -r --cached .claude/ 2>/dev/null || true
git rm -r --cached .gemini/ 2>/dev/null || true
```

### 3단계: 스테이징 + 보안 검증
```bash
git add .gitignore
git add -A
git diff --cached --name-only | grep -iE '\.env|api.key|token|secret|bot\.db|node_modules|\.venv|chroma_db|__pycache__|\.DS_Store|\.pid|04_Archive' && echo "🔴 위험 파일 발견!" && exit 1 || echo "✅ 보안 검증 통과"
```

### 4단계: 커밋
```bash
git commit -m "feat: P2 watchdog/heartbeat + vault cleanup + codex config + FDE roadmap

- P2: watcher heartbeat 60s + watchdog.sh (5min cron) + dashboard System Health
- Security: .gitignore 강화
- Codex: 멀티에이전트 config.toml (9 agents)
- Career: FDE roadmap v1.0
- Docs: engine_agent_cards v3.2
- Cleanup: 볼트 대청소"
```

### ⚠️ 원격 전송은 이 작업 범위에 포함되지 않음. 로컬 커밋까지만 수행.

### --max-turns 15
