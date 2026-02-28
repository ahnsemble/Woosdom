# Woosdom Agent Corps — 전체 설계서
*Version: 1.0*
*Status: Working System*

---

## 0. 설계 철학

**"형은 한 줄만 말하면 된다."**

사용자는 Brain에게 자연어로 지시 1회. Brain이 판단해서 적절한 팀에 분배하고,
팀장이 팀원을 돌려서 결과물을 만들고, Brain이 종합해서 보고한다.

**지시 횟수 목표: 사용자 1회 지시 → 1회 승인/수정 = 최대 2회 인터랙션.**

---

## 1. 조직도

```
┌────────────────────────────────────────────┐
│           사용자 (최종 의사결정권자)          │
└──────────────────┬─────────────────────────┘
                   │
┌──────────────────▼─────────────────────────┐
│      Brain (Claude Opus @ claude.ai)        │
│  전략 참모 & 3팀 관리자                      │
└───────┬──────────┬─────────────┬───────────┘
        │          │             │
   ┌────▼────┐ ┌───▼─────┐ ┌───▼────┐
   │ CC팀    │ │ Codex팀 │ │ AG팀   │
   │ (로컬)  │ │ (클라우드)│ │ (GUI)  │
   └────┬────┘ └───┬─────┘ └───┬────┘
        │          │             │
   Foreman    Compute Lead   Scout Lead
    ├ Engineer   ├ Quant       ├ Web Scout
    ├ Critic     ├ Backtester  ├ Architect
    ├ Git Ops    └ Builder     └ Experimenter
    └ Vault Keeper
```

---

## 2. CC팀 (Claude Code) — 주력

| 팀원 | 역할 | 모델 |
|------|------|------|
| **Foreman** | 총괄 매니저 | Opus (메인) |
| Engineer | 코드 작성/수정 | Sonnet (비용 효율) |
| Critic | 코드 리뷰 | Sonnet |
| Git Ops | 버전 관리 | Haiku (저비용) |
| Vault Keeper | 볼트 메모리 관리 | Haiku (저비용) |

**워크플로우:** Engineer → Critic(리뷰) → Git Ops(커밋) → Vault Keeper(기록)

---

## 3. Codex팀 — 연산 전담

| 팀원 | 역할 |
|------|------|
| **Compute Lead** | 총괄 |
| Quant | 수학 연산, 시뮬레이션 |
| Backtester | 백테스팅 전담 |
| Builder | 대규모 빌드, PR 자동화 |

---

## 4. AG팀 (Antigravity) — 리서치

| 팀원 | 역할 | 모델 |
|------|------|------|
| **Scout Lead** | 총괄 | Gemini |
| Web Scout | 웹 리서치 | Gemini (브라우저) |
| Architect | 아키텍처 검증 | Claude Opus |
| Experimenter | 멀티모델 비교 | 가변 |

---

## 5. 팀 간 협업

**핵심 원칙: 팀 간 직접 소통은 없다. 모든 정보는 Brain을 경유한다.**

### 패턴 1: 리서치 → 구현
Brain → AG팀(리서치) → Brain 검토 → CC팀(구현) → 사용자 보고

### 패턴 2: 코드 → 연산
Brain → CC팀(코드 생성) → Brain → Codex팀(실행) → 사용자 보고

### 패턴 3: 3자 회의
Brain 분석 → query_gemini + query_gpt → 충돌 감지 → 토론 → 최종 판정

---

## 6. 안전 체계

| 규칙 | 적용 |
|------|------|
| portfolio.json, Rules.md 수정 금지 | 전체 3팀 |
| MDD -40% 로직 변경 금지 | Codex팀 |
| 매매 판단/추천 금지 | 전체 (Brain 3자회의만 가능) |
| 파괴적 명령 차단 | CC팀 (pre_bash.sh 훅) |
| API 키/토큰 외부 전송 금지 | 전체 |
