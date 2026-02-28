# Engine Router & A2A Protocol (Brain Module)
*Source: brain_directive.md 분리*
*로드 조건: Role Gate에서 Hands 위임 판정 시 OR 3자 회의 트리거 시*

---

## 3-Engine Architecture

```
Brain (Claude Opus) — 전략/판단/승인
  ├── Hands-4: Claude Code (로컬 허브) ← 주력 실행 엔진
  ├── Hands-3: Codex (로컬 앱) ← 코드 실행·비동기 연산
  ├── Hands-1: Antigravity Sonnet/Opus (GUI 보조)
  └── Hands-2: Antigravity Gemini (웹 리서치)
```

> ⚠️ 단일 도구 통합은 안티패턴. 각 엔진의 강점 영역을 존중하는 느슨한 결합 유지.
> ⚠️ LLM 에이전트에 수학 연산(백테스팅/MDD 계산) 위임 절대 금지.

---

## Engine Router (패턴 기반)

| 워크플로우 패턴 | 주 엔진 | 보조 엔진 |
|---------------|--------|----------|
| **A — 백테스팅/대규모 연산** | Codex | CC (코드 생성) |
| **B — MCP 도구/코드 개발** | Claude Code | Codex (대규모 빌드) |
| **C — 리서치 & 자동화** | Claude Code | AG (웹 브라우징) |
| **D — Finance Brief** | Claude Code | Brain (최종 판단) |

## 특성 기반 라우팅

| Task | Engine | Reason |
|------|--------|--------|
| 파일 수정 + 빌드 + 테스트 루프 | Claude Code | headless, 자가 치유 |
| Git 워크플로 | Claude Code | 터미널 네이티브 |
| 장시간 비동기 (30min+) | Codex | 백그라운드 실행 |
| 대규모 수학 연산 | Codex (실행만) | 결정론적 실행 |
| GUI 웹 리서치 | Antigravity | 브라우저 DOM 제어 |
| 멀티모델 실험 | Antigravity Gemini | IDE 내 멀티모델 |

## 금지 사항

| 절대 금지 | 이유 |
|----------|------|
| LLM으로 대규모 연산 직접 실행 | Context rot + 환각 |
| 수식 로직의 LLM 자율 변경 | MDD 계산 오염 리스크 |
| Claude Code API 종량제 | 무한 루프 시 비용 폭발 |

---

## Dispatch Protocol

### Hands-4 (Claude Code) — 주력

```
Brain → to_hands.md (Obsidian MCP)
  → fswatch 감지
    → claude -p --max-turns 15
      → from_hands.md + 결과 파일 저장
```

### Hands-3 (Codex) — 클라우드 비동기

to_hands.md 수동 전달 또는 MCP 래퍼

### Hands-1/2 (Antigravity) — GUI 보조

to_hands.md 수동 전달

---

## A2A Protocol (3자 회의)

**발동 조건:** MDD -35%/-40%, 리밸런싱 드리프트, 포트폴리오 구조 변경 시.

**오케스트레이션 4단계:**
1. Phase 1: 독립 분석 (병렬) — GPT + Gemini에 동일 질문
2. Phase 2: 충돌 감지 — 일치→Phase 4 / 불일치→Phase 3
3. Phase 3: 토론 루프 (최대 2회)
4. Phase 4: Brain 최종 판정 + council_log 저장

**제한:** 1회 회의당 GPT 최대 4호출, Gemini 최대 4호출.
