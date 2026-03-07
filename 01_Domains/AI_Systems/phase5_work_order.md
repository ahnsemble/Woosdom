---
title: "Phase 5 작업지시서 — 3-Engine Hybrid Orchestration"
created: "2026-02-23"
author: "Brain (Claude Opus 4.6)"
status: "APPROVED"
phase: 5
predecessor: "Phase 4 (Sprint 1~3 완료, Sprint 4 → Phase 5 흡수)"
architecture: "3-Engine Hybrid (CC Hub + Codex Cloud + AG GUI)"
---

# Phase 5: 3-Engine Hybrid Orchestration

## 0. Phase 4 종결 선언

Phase 4 (시스템 자동화 기반 구축)는 **Sprint 1~3 완료, Sprint 4 흡수**로 종결한다.

| Sprint | 성과 | 상태 |
|--------|------|------|
| S1 | LiteLLM Docker + Redis exact match 캐시 | ✅ |
| S2 | Task Bridge (Redis Streams + 파일 감시 데몬 + E2E PASS) | ✅ |
| S3 | Claude Code CLI + E2E 5/5 PASS + TG 이중알림 수정 | ✅ |
| S4 | Persona Council (이미 가동) + MCP 원격 (Phase 5 흡수) | → Phase 5 |

**Phase 4 유산 (Phase 5가 계승하는 인프라):**
- Redis Streams 기반 Task Bridge 데몬 2개 가동
- LiteLLM 프록시 (Anthropic/OpenAI/Google 3사 통합)
- Hands-4 (Claude Code) 시스템 등록 + 대시보드 통합
- Gemini CLI + Obsidian MCP 연결
- A2A Protocol v2.16 (query_gemini + query_gpt)

---

## 1. Phase 5 목표

**한 줄 요약:** Claude Code를 Woosdom의 로컬 오케스트레이터 & MCP 허브로 격상하고, 3-엔진 분업 체계를 실전 가동한다.

**해결할 병목:**
- 🔴 수동 릴레이 (Brain → 사용자 복사 → 엔진 → 결과 회수 → Brain)
- 🟡 엔진 간 역할 혼선 (무엇을 어디에 보낼지 매번 판단 필요)
- 🟡 비용 예측 불가 (API 종량제 혼용)

**Phase 5 완료 시 상태:**
- Brain이 to_hands.md에 지시 작성 → **자동으로** Claude Code가 실행 → 결과가 from_hands.md에 기록
- 패턴 B/C/D는 CC가 주력 처리, 패턴 A는 Codex로 자동 라우팅
- 월 $300 이내 안정 운영

---

## 2. 전제 조건 (Prerequisites)

| 항목 | 상태 | 액션 |
|------|------|------|
| 3-엔진 아키텍처 확정 | ✅ | synthesis.md + premise_audit |
| Claude Code 설치 | ✅ | Phase 4 S3에서 완료 |
| Claude Code Max 5x 플랜 | ⬜ | **사용자 액션 필요**: $100/월 플랜 전환 |
| Obsidian MCP 서버 가동 | ✅ | 이미 연결 |
| Codex Pro 플랜 | ✅ | $200/월 유지 |
| fswatch 설치 | ⬜ | Sprint 1에서 설치 |

---

## 3. Sprint 계획

### Sprint 5-1: fswatch 프로토타입 (1주)
> **목표:** to_hands.md 변경 감지 → `claude -p` headless 자동 실행 → from_hands.md 저장

**산출물:**
1. `woosdom_bridge.sh` — fswatch 기반 파일 워처 데몬
2. `cc_executor.sh` — claude -p 래퍼 (--max-turns 15, --allowedTools, --output-format json)
3. `from_hands.md` 자동 업데이트 확인

**상세 스펙:**

```bash
# woosdom_bridge.sh (개념)
#!/bin/bash
VAULT="/Users/woosung/Desktop/Dev/Woosdom_Brain"
TO_HANDS="$VAULT/00_System/Templates/to_hands.md"
FROM_HANDS="$VAULT/00_System/Templates/from_hands.md"

fswatch -o "$TO_HANDS" | while read; do
  CONTENT=$(cat "$TO_HANDS")
  if [[ "$CONTENT" == *"EMPTY"* ]] || [[ -z "$CONTENT" ]]; then
    continue  # 빈 파일 무시
  fi
  
  # 실행 락 (중복 방지)
  LOCK="/tmp/woosdom_bridge.lock"
  if [ -f "$LOCK" ]; then continue; fi
  touch "$LOCK"
  
  # Claude Code headless 실행
  cd "$VAULT"
  RESULT=$(claude -p "$CONTENT" \
    --allowedTools "Read,Edit,Bash" \
    --max-turns 15 \
    --output-format json 2>&1)
  
  # 결과 저장
  echo "$RESULT" > "$FROM_HANDS"
  
  # 알림 (기존 TG 봇 활용)
  # python3 notify.py "CC 실행 완료: $(echo $CONTENT | head -1)"
  
  # 정리
  echo "EMPTY — 실행 완료 $(date)" > "$TO_HANDS"
  rm -f "$LOCK"
done
```

**검증 기준:**
- [ ] Brain이 to_hands.md에 "현재 디렉토리의 파일 목록을 알려줘" 작성
- [ ] 10초 이내 CC가 자동 실행
- [ ] from_hands.md에 결과 기록 확인
- [ ] 빈 파일/중복 트리거 방지 확인
- [ ] --max-turns 15 초과 시 안전 종료 확인

**위임:** Hands-4 (Claude Code) 직접 실행. Brain이 설계, 사용자가 데몬 실행.

---

### Sprint 5-2: CC MCP 허브 구성 (1주)
> **목표:** Claude Code에 Obsidian MCP + 기존 도구를 연결하여 vault 직접 읽기/쓰기 가능하게 만듦

**산출물:**
1. `.mcp.json` — CC 프로젝트 설정 (Obsidian vault MCP 서버 등록)
2. `~/.claude/CLAUDE.md` — 글로벌 시스템 프롬프트 (금융 룰셋 하드코딩)
3. CC → Obsidian vault 읽기/쓰기 E2E 검증

**상세 스펙:**

```json
// .mcp.json (Woosdom_Brain 루트)
{
  "mcpServers": {
    "obsidian-vault": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic-ai/mcp-server-filesystem",
        "/Users/woosung/Desktop/Dev/Woosdom_Brain"
      ]
    }
  }
}
```

```markdown
<!-- ~/.claude/CLAUDE.md -->
# Woosdom System Rules (Claude Code Global)

## 절대 금지
- 수학 연산(백테스팅/MDD 계산) 직접 수행 금지 — Codex로 위임
- portfolio.json 또는 Rules.md의 비율/규칙 임의 변경 금지
- MDD -40% 방어 규칙은 절대적. 환각에 의한 변경 원천 차단
- DCA v5 비율 임의 조정 금지
- 외부 매매 트랜잭션 API 호출 금지

## 작업 범위
- 코드 수정/빌드/테스트/디버그: 허용
- Obsidian vault 파일 읽기/쓰기: 허용
- Git 워크플로: 허용
- 웹 검색/데이터 수집: 허용 (Scout 역할)
- 결과 리포트 작성: 허용

## 비용 안전
- --max-turns 15 기본 (사용자가 명시적으로 올리지 않는 한)
- 무한 루프 감지 시 즉시 중단하고 상태 저장
```

**검증 기준:**
- [ ] CC에서 `claude mcp add` 또는 `.mcp.json`으로 vault 연결
- [ ] CC가 vault 내 파일 읽기 성공 (active_context.md)
- [ ] CC가 vault 내 파일 쓰기 성공 (테스트 파일)
- [ ] `~/.claude/CLAUDE.md` 금융 룰셋이 CC 세션에 적용됨 확인
- [ ] 금지된 작업 시도 시 CC가 거부하는지 확인

**위임:** Hands-4 (Claude Code) + 사용자 설정 작업.

---

### Sprint 5-3: Codex MCP 래퍼 (2주)
> **목표:** Brain이 MCP 도구로 Codex 태스크를 직접 생성/조회할 수 있는 브리지 구축

**산출물:**
1. `codex-mcp-wrapper/` — Node.js Express MCP 서버
2. MCP 도구: `spawn_codex_task`, `poll_codex_status`, `get_codex_result`
3. `claude_desktop_config.json`에 등록

**상세 스펙:**

```
Brain (claude.ai) 
  → MCP tool call: spawn_codex_task("Run backtest stage 2")
    → codex-mcp-wrapper (Node.js)
      → codex exec --json "Run backtest stage 2"
        → JSONL event stream 수집
          → turn.completed 감지
            → 결과를 MCP 응답으로 반환
```

**검증 기준:**
- [ ] Brain에서 `spawn_codex_task` 호출 시 Codex가 실행됨
- [ ] `poll_codex_status`로 실행 상태 조회 가능
- [ ] `get_codex_result`로 완료된 결과 수신 가능
- [ ] 실패 시 에러 메시지 정상 반환
- [ ] 동시 2개 태스크 병렬 실행 가능

**위임:** Hands-3 (Codex) 코드 생성 + Hands-4 (CC) 로컬 테스트.

**⚠️ 조건부:** Codex API 접근이 2026-02 기준 "soon"으로 명시됨. `codex exec` CLI가 안정적으로 동작하는지 먼저 확인. 불가 시 **수동 릴레이 유지 + Phase 5-3을 보류**.

---

### Sprint 5-4: 패턴별 E2E 검증 (2주)
> **목표:** 4개 패턴(A/B/C/D)을 3-엔진 체제로 실제 가동하고 시간 절감/품질을 측정

**검증 순서:** B → C → D → A (ROI 높은 순)

#### 패턴 B — MCP 도구 개발 E2E
```
Brain: "woosdom-executor MCP 서버에 새 도구 추가해줘"
  → to_hands.md (자동 트리거)
    → CC: 파일 탐색 → 코드 작성 → npm run build → 에러 시 자동 수정
      → from_hands.md: "빌드 성공, 도구 등록 완료"
```
- 측정: 기존 수동 릴레이 대비 소요 시간
- 목표: **25% 이상 절감**

#### 패턴 C — 리서치 & 자동화 E2E
```
Brain: "최근 AI 에이전트 동향 리서치해서 vault에 저장해줘"
  → to_hands.md (자동 트리거)
    → CC: 웹 검색 → 정보 수집 → 마크다운 작성 → vault 저장
      → from_hands.md: "01_Domains/AI_Systems/trend_report.md 저장 완료"
```
- 측정: Brain → 결과 확인까지 전체 소요 시간
- 목표: **40% 이상 절감**

#### 패턴 D — Finance Brief E2E
```
Brain: "이번 주 포트폴리오 드리프트 점검해줘"
  → to_hands.md (자동 트리거)
    → CC Scout: Yahoo Finance에서 현재가 수집
    → CC Quant: portfolio.json 대비 드리프트 계산
      → from_hands.md: "드리프트 리포트 저장 완료"
        → Brain: 리포트 검토 → 리밸런싱 필요 여부 판단
```
- 측정: 수동 릴레이 대비 소요 시간 + 데이터 정확도
- 목표: **20% 이상 절감**, 데이터 오차 1% 이내
- **⚠️ 금융 규칙 위반 여부 반드시 검증** (MDD, 비율 변경 시도 등)

#### 패턴 A — 백테스팅 E2E (Codex 경유)
```
Brain: "Stage 2 백테스팅 실행해줘"
  → to_hands.md → Codex (수동 또는 MCP 래퍼)
    → codex exec: Python 스크립트 실행
      → 결과 CSV/리포트 → vault 저장
        → Brain: 결과 분석 → 다음 Stage 판단
```
- 측정: 수동 릴레이 대비 소요 시간
- 목표: **15% 이상 절감**
- **⚠️ LLM이 수식 로직을 변경하지 않았는지 diff 검증 필수**

**산출물:**
1. `phase5_benchmark.md` — 4개 패턴 시간/품질 측정 결과
2. 패턴별 실제 절감률 vs 예상 절감률 비교

---

### Sprint 5-5: 안전장치 & 모니터링 (1주)
> **목표:** 비용 모니터링 + 안전장치 강화 + 운영 매뉴얼 작성

**산출물:**
1. `cost_monitor.py` — 일일 비용 추적 스크립트 (CC `/cost` 파싱 + Codex 크레딧 조회)
2. `~/.claude/hooks/` — PreToolUse 훅 (위험 명령 차단)
3. `phase5_operations_guide.md` — 3-엔진 운영 매뉴얼
4. `woosdom_bridge.sh` 프로덕션 버전 (에러 핸들링, 로깅, TG 알림 통합)

**훅 예시:**
```bash
# ~/.claude/hooks/pre_bash.sh
#!/bin/bash
# 위험 명령 차단
COMMAND="$1"
if echo "$COMMAND" | grep -qE "rm -rf|DROP TABLE|DELETE FROM|rmdir"; then
  echo "BLOCKED: 파괴적 명령 감지. Brain 승인 필요."
  exit 1
fi
```

**검증 기준:**
- [ ] 일일 비용이 $10 초과 시 TG 알림
- [ ] `rm -rf` 시도 시 훅이 차단
- [ ] 월말 비용이 $300 이내
- [ ] 운영 매뉴얼로 새 세션에서도 3-엔진 체제 즉시 재현 가능

**위임:** Hands-4 (Claude Code) 구현 + Brain 매뉴얼 작성.

---

## 4. 타임라인

```
Week 1: Sprint 5-1 (fswatch 프로토타입)
Week 2: Sprint 5-2 (CC MCP 허브)
Week 3-4: Sprint 5-3 (Codex MCP 래퍼) — 조건부
Week 5-6: Sprint 5-4 (패턴별 E2E 검증)
Week 7: Sprint 5-5 (안전장치 & 모니터링)
```

**총 예상 기간: 7주**

> ⚠️ Crossy Week 1~10과 병렬 진행. Crossy가 우선순위 1이므로, Phase 5는 **Crossy 작업 틈새 시간**에 진행.

---

## 5. 리스크 & 방어

| # | 리스크 | 확률 | 영향 | 방어 |
|---|--------|------|------|------|
| R1 | CC Max 5x 쿼터 고갈 | 중 | 🟡 | --max-turns 제한 + 모델 다운시프트 (Sonnet 4.5) |
| R2 | fswatch 데몬 크래시 | 중 | 🟡 | launchd/systemd 서비스 등록 + 자동 재시작 |
| R3 | Codex API "soon" → 지연 | 높 | 🟡 | Sprint 5-3 보류, 수동 릴레이 유지 (fallback) |
| R4 | CC 무한 루프 비용 폭발 | 낮 | 🔴 | --max-turns 15 하드코딩 + API 크레딧 거절 |
| R5 | CC 환각으로 vault 파일 훼손 | 낮 | 🔴 | Git worktree 격리 + PreToolUse 훅 + 주기적 백업 |
| R6 | 금융 룰셋 환각 위반 | 극낮 | 🔴 | CLAUDE.md 하드코딩 + Air-gapped (매매 도구 미연결) |

---

## 6. 성공 기준 (Phase 5 완료 판정)

| 기준 | 목표 | 필수/권장 |
|------|------|----------|
| fswatch 자동 트리거 성공률 | ≥ 90% | **필수** |
| CC → vault 읽기/쓰기 E2E | PASS | **필수** |
| 패턴 B 시간 절감 | ≥ 25% | **필수** |
| 패턴 C 시간 절감 | ≥ 40% | **필수** |
| 패턴 D 시간 절감 + 데이터 정확도 | ≥ 20% + 오차 ≤ 1% | **필수** |
| 패턴 A 시간 절감 | ≥ 15% | 권장 |
| 월 비용 | ≤ $300 | **필수** |
| Codex MCP 래퍼 가동 | E2E PASS | 권장 (조건부) |
| 금융 룰셋 위반 사례 | 0건 | **필수** |

---

## 7. Phase 5 이후 전망

Phase 5 완료 시 Woosdom은:
- **Brain**: 전략/판단만 집중 (실행 위임 완전 자동화)
- **Claude Code**: 24/7 로컬 오케스트레이터 (fswatch 데몬)
- **Codex**: 클라우드 연산 전담 (MCP 또는 수동)
- **Antigravity**: 필요 시 GUI 리서치

**Phase 6 후보:**
- Modal 서버리스 GPU 도입 (Codex 한계 실증 시)
- n8n 오케스트레이션 (워크플로우 복잡도 증가 시)
- `claude mcp serve` 역방향 서버 (Brain → CC 직접 원격 호출)
- Persona Council 자동화 (3자 회의 → CC가 자동 소집)

---

*Approved by Brain (Claude Opus 4.6) — 2026-02-23*
*Phase 4 종결 + Phase 5 작업지시서 확정*
