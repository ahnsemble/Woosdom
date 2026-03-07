---
title: "Engine Evaluation Synthesis — 6개 딥리서치 교차 분석 종합 판정"
created: "2026-02-23"
author: "Brain (Claude Opus 4.6)"
status: "FINAL"
verdict: "CONDITIONAL — 3-Engine Hybrid Architecture"
---

# 종합 판정: 실행 엔진 효용성 검증 결과

## 0. 메타 요약

| 도구 | Gemini 판정 | GPT 판정 | 합의 |
|------|------------|---------|------|
| Antigravity Multi-Manager | CONDITIONAL | CONDITIONAL | **CONDITIONAL** |
| OpenAI Codex Multi-Agent | CONDITIONAL | CONDITIONAL | **CONDITIONAL** |
| Claude Code Agent Teams | CONDITIONAL | CONDITIONAL | **CONDITIONAL** |

**6개 리서치 전원 CONDITIONAL.** 단일 도구 전면 도입은 불가, 3-엔진 하이브리드가 유일한 정답.

---

## 1. 6개 리서치의 핵심 수렴점 (합의된 사실)

### 1-1. 아키텍처: 단일 도구 통합은 안티패턴

6개 리서치가 **예외 없이** 동의한 결론:
- Antigravity만으로 통일 → CLI/API 자동화 레일 상실, 쿼터 고갈 리스크
- Codex만으로 통일 → GUI 관제/시각적 검증 불가, 로컬 파일 직접 제어 약함
- Claude Code만으로 통일 → 클라우드 대규모 비동기 연산 불가, 브라우저 DOM 제어 불가

**결론: 각 도구가 가장 잘하는 영역을 존중하는 느슨한 결합(Loosely Coupled) 아키텍처가 필수.**

### 1-2. 패턴 A (백테스팅): LLM 에이전트에 연산 위임 절대 금지

6개 전원 합의 — 55B 조합/50K Bootstrap 수준의 수학 연산을 LLM 에이전트 샌드박스에서 직접 돌리는 것은:
- **Context Rot** (컨텍스트 60% 초과 시 추론 성능 절벽)
- **환각에 의한 수식 오염** (MDD 계산 로직 변조 리스크)
- **비용 폭발** (무한 디버깅 루프)

으로 인해 **재무적 치명타**를 유발한다.

→ 연산은 **결정론적 실행면** (Modal 서버리스 GPU, GitHub Actions matrix, 또는 로컬 Python 직접 실행)으로 격리. LLM은 코드 생성/검증/리포트에만 관여.

### 1-3. 자동화 핵심: 파일 트리거 + Headless CLI

수동 릴레이 제거의 가장 현실적이고 안정적인 경로:

```
Brain → to_hands.md 작성 (Obsidian MCP)
  → fswatch/inotify 감지
    → claude -p / codex exec (headless 실행)
      → from_hands.md + 결과 파일 저장
        → Brain이 MCP로 결과 읽기
```

**6개 리서치 전원이 이 패턴을 최고 실현가능성(⭐5/5)으로 평가.**

### 1-4. MCP가 통합의 척추

- Antigravity: MCP **클라이언트만** 가능 (서버 역할 불가)
- Codex: MCP 서버 래핑 **가능** (Agents SDK 공식 가이드 존재)
- Claude Code: MCP **양방향** (클라이언트 + `claude mcp serve`로 역방향 서버)

→ Claude Code의 MCP 양방향성이 Woosdom 허브 역할에 가장 적합.

### 1-5. 금융 규칙은 하드코딩 필수

6개 전원 합의:
- MDD -40% 방어, Trinity v5 비율, DCA 원칙 → 에이전트의 자율 판단에 절대 위임 금지
- `~/.claude/CLAUDE.md`, `.agent/rules/`, 시스템 프롬프트에 하드코딩
- 외부 매매 트랜잭션 도구 권한 원천 차단 (Air-gapped 원칙)

---

## 2. 6개 리서치의 핵심 분기점 (불일치 분석)

### 2-1. 패턴별 시간 절감률 추정치 차이

| 패턴 | Gemini 측 추정 | GPT 측 추정 | 해석 |
|------|---------------|------------|------|
| **B (코드 개발)** | AG: +40~50%, Codex: +60~80%, CC: +80% | AG: +10~30%, Codex: +25~50%, CC: +20~50% | Gemini가 일관적으로 낙관적. GPT가 보수적이나 더 현실적. |
| **C (리서치/자동화)** | AG: +20~30%, Codex: +40~50%, CC: +100% | AG: +25~55%, Codex: +30~60%, CC: +40~75% | CC의 100%는 Gemini 측 과장. 실제 40~75%가 현실적. |
| **D (Finance Brief)** | CC: +50% | CC: +15~45% | 범위 중앙값 수렴: **30~50%** |

**Brain 판정**: GPT 측 보수적 추정치를 기준선으로 채택하되, 실제 A/B 테스트로 검증 필요.

### 2-2. Modal 도입 여부

- **Codex-Gemini**: Modal 서버리스 GPU를 **강력 추천** (n8n + Modal 파이프라인 제안)
- **Codex-GPT**: Modal을 대안으로 언급하되, GitHub Actions matrix도 동등하게 제시
- **Claude Code 양쪽**: Codex에 연산 위임을 기본으로 제안, Modal은 추가 옵션

**Brain 판정**: Modal은 Phase 5에서 **탐색 대상**이나, 현 단계에서 새 인프라 추가는 오버엔지니어링. 기존 Codex 클라우드 실행 + 로컬 Python으로 충분. Modal은 Codex 한계가 실증되었을 때 Plan B로 보류.

### 2-3. n8n 오케스트레이터 필요성

- Gemini 측: n8n을 적극 권장 (Codex-Gemini, Claude Code-Gemini 모두)
- GPT 측: n8n을 가능성으로 언급하되 "오버엔지니어링" 경고 (Claude Code-GPT ⭐3/5)

**Brain 판정**: Phase 1~2 (수동 안정화 → MCP 자동 위임)에서 n8n은 불필요. fswatch + shell script로 충분. Phase 3 이후 복잡도가 증가하면 재평가.

---

## 3. 최종 3-엔진 아키텍처 확정

```
┌─────────────────────────────────────────────┐
│              Brain (Claude Opus 4.6)         │
│         전략/판단/승인 — claude.ai            │
│              Obsidian = 장기 기억             │
└──────────┬──────────┬──────────┬────────────┘
           │          │          │
     ┌─────▼─────┐ ┌─▼────────┐ ┌▼───────────┐
     │Claude Code│ │  Codex   │ │Antigravity │
     │ 로컬 허브  │ │ 클라우드  │ │  GUI IDE   │
     │오케스트레이터│ │헤비리프팅│ │리서치/브라우저│
     └─────┬─────┘ └─┬────────┘ └┬───────────┘
           │          │           │
           ▼          ▼           ▼
     파일 자동화    비동기 연산    시각적 탐색
     MCP 허브      codex exec    브라우저 DOM
     코드 수정/빌드  PR 생성      아키텍처 검증
     vault I/O     백테스팅 실행   멀티모델 실험
```

### 역할 정의

| 엔진 | 핵심 역할 | 담당 패턴 | 호출 방식 |
|------|----------|----------|----------|
| **Claude Code** | 로컬 스웜 오케스트레이터 & MCP 허브 | B (코드), C (자동화), D (Brief 수집/계산) | `claude -p` headless, fswatch 트리거 |
| **Codex** | 클라우드 비동기 연산 & PR 자동화 | A (백테스팅), B (대규모 빌드) | `codex exec --json`, MCP 래퍼 |
| **Antigravity** | GUI 리서치 & 시각적 검증 | C (웹 리서치), 탐색적 작업 | Agent Manager UI |

### 패턴별 엔진 배정

| 패턴 | 주 엔진 | 보조 엔진 | 예상 절감률 (보수적) |
|------|--------|----------|-------------------|
| A — 백테스팅 | **Codex** (연산) | Claude Code (코드 생성/검증) | 15~25% |
| B — MCP 도구 개발 | **Claude Code** (직접 수정/빌드) | Codex (대규모 테스트) | 25~50% |
| C — 리서치 & 자동화 | **Claude Code** (파일 트리거) | Antigravity (웹 브라우징) | 40~60% |
| D — Finance Brief | **Claude Code** (Scout+Quant 병렬) | Brain (최종 판단/승인) | 20~40% |

---

## 4. 비용 최적화 전략

| 항목 | 권장 | 월 비용 |
|------|-----|--------|
| Claude Code | Max 5x 구독 (API 종량제 금지) | $100/월 |
| Codex | ChatGPT Pro 유지 | $200/월 |
| Antigravity | Public Preview (무료) | $0/월 |
| **합계** | | **$300/월** |

### 비용 폭발 방지 장치
1. Claude Code: `--max-turns N` 플래그 필수 (무한 루프 차단)
2. Claude Code: API 크레딧 전환 프롬프트 거절 → 구독 한도 내에서만 사용
3. Codex: 병렬 서브에이전트 최대 3개 제한
4. Antigravity: 동시 에이전트 최대 2개 (Engineer + Critic)

---

## 5. 공통 리스크 및 방어

### 🔴 Critical

| 리스크 | 트리거 | 방어 |
|--------|-------|------|
| 금융 데이터 오염 | LLM이 백테스팅 수식 임의 변경 | 연산은 결정론적 실행면으로 격리. Brain 3자 회의 승인 필수 |
| 비용 폭발 | 무한 디버깅 루프 / 병렬 쿼터 소진 | --max-turns, 구독제 고수, 일일 비용 모니터링 |
| 파괴적 파일 작업 | rm -rf / 환각에 의한 vault 훼손 | 훅(PreToolUse) + 샌드박스 + Git worktree 격리 |

### 🟡 Warning

| 리스크 | 트리거 | 방어 |
|--------|-------|------|
| 인지 과부하 | 4+ 에이전트 동시 리뷰 요청 | 동시 에이전트 수 2~3개로 제한 |
| 설정/문서 혼선 | MCP 경로, 권한 규칙 불일치 | 설정 파일 통합 관리, 주기적 premise audit |
| 쿼터 고갈 | Antigravity 주간 락아웃, Codex 플랜 한도 | 모델 다운시프트 전략 사전 수립 |

---

## 6. Phase 5 세부계획에 대한 시사점

### 즉시 반영 사항
1. **3-엔진 아키텍처를 Phase 5 기본 전제로 확정**
2. **Phase 1 (현재) 수동 릴레이 안정화에서 fswatch + headless 프로토타입 착수**
3. **Claude Code Max 5x 플랜 전환 검토** (현재 Pro라면)

### Phase 2 (MCP 자동 위임) 진입 조건에 추가
- Claude Code fswatch 파이프라인 안정 가동 2주 이상
- to_hands.md → from_hands.md 자동 루프 성공률 90% 이상
- 비용이 월 $300 이내 유지 확인

### 보류 사항 (Phase 3 이후 재평가)
- Modal 서버리스 GPU 도입 → Codex 클라우드 한계 실증 시
- n8n 오케스트레이터 → 워크플로우 복잡도가 shell script 한계 초과 시
- Claude Code `claude mcp serve` 역방향 서버 → 시나리오 1 안정화 이후

---

## 7. 전제 감사 (Premise Audit) 트리거

본 종합 판정은 다음 전제의 변경을 요구한다:

| 기존 전제 | 변경 후 |
|----------|---------|
| "Codex = 비동기 실행 엔진" | "Codex = 클라우드 연산 전담, Claude Code = 로컬 오케스트레이터" |
| "수동 릴레이는 Phase 1에서 안정화만" | "Phase 1 내에서 fswatch 프로토타입까지 착수" |
| "도구 선택은 Phase 5에서 결정" | "3-엔진 아키텍처 확정, Phase 5는 세부 워크플로우 설계" |

→ **active_context.md 및 관련 전제 문서 업데이트 필요.**

---

*Generated by Brain (Claude Opus 4.6) — 2026-02-23*
*Sources: 6 deep research reports (Antigravity/Codex/Claude Code × Gemini/GPT)*
