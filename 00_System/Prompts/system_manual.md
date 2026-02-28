# FDE Unified System — System Manual v2.2
*Purpose: Woosdom 시스템 전체를 이해하기 위한 사용설명서*

---

## 1. 한 줄 요약

> **생각은 Brain이 하고, 실행은 Hands가 하고, 기억은 Obsidian이 한다.**

---

## 2. 시스템 아키텍처

```
사용자
     │
     ▼
🧠 Brain (전략 두뇌) ───────────────────────────────────────┐
│  Primary: Claude Opus (MCP로 Obsidian 직접 연결)            │
│  Sub-1:   GPT (Custom GPT)                                  │
│  Sub-2:   Gemini (Gem)                                      │
├──────────────────────────────────────────────────────────────┘
│
├─→ 🖐️ Hands Swarm (실행 에이전트)
│   ├─ Quant (퀀트)     — 백테스트, 통계   → Antigravity / Codex
│   ├─ Scout (정찰병)   — 시장 데이터 수집  → Antigravity Gemini
│   ├─ Engineer (엔지니어) — 코드, 자동화   → Codex / Antigravity
│   └─ Critic (비평가)  — 검증, 반론       → GPT / Gemini (교차 엔진)
│
└─→ 💾 Memory: Obsidian Vault (로컬 마크다운, MCP 연결)
```

### 핵심 규칙
- **Brain은 절대로 직접 계산, 코딩, 데이터 수집을 하지 않는다.**
- **금융 의사결정은 반드시 3자 회의** (Brain + GPT + Gemini).
- **진실 우선순위:** 외부 입력 > Obsidian 파일 > 사용자 텍스트 > 학습 데이터.

---

## 3. 각 구성 요소

### Brain (전략 두뇌)
판단, 전략, 리스크 분석, Pre-Mortem, 철학 정렬.

### Hands Swarm (실행 에이전트)
| 에이전트 | 전문 분야 | 주 엔진 | 페르소나 파일 |
|---------|----------|---------|-------------|
| **Quant** | 백테스트, 통계 | Antigravity / Codex | `Swarm/quant.md` |
| **Scout** | 실시간 시세, 뉴스 | Antigravity Gemini | `Swarm/scout.md` |
| **Engineer** | 코드, MCP, 자동화 | Codex / Antigravity | `Swarm/engineer.md` |
| **Critic** | 출력 검증, 반론 | GPT / Gemini (교차) | `Swarm/critic.md` |

### Memory (3-Tier)
| Tier | 파일 | 로드 시점 |
|------|------|----------|
| **Hot** | `active_context.md` + `brain_directive.md` | 매 대화 시작 |
| **Warm** | `01_Domains/` 하위 파일 | 해당 도메인 질문 시 |
| **Cold** | `03_Journal/daily/` | 명시적 요청 시만 |

---

## 4. 폴더 구조

```
Woosdom_Brain/
├── 00_System/            ← AI 운영 체제 (Hot Memory)
│   ├── Prompts/Ontology/ ← Brain 행동 규칙 + 모듈
│   ├── Prompts/Swarm/    ← Hands 에이전트 페르소나
│   ├── Templates/        ← to_hands.md / from_hands.md
│   └── Specs/            ← 시스템 설계서
├── 01_Domains/           ← 도메인별 지식 (Warm Memory)
├── 02_Projects/          ← 활성 프로젝트
├── 03_Journal/           ← 시간 기반 기록 (Cold Memory)
└── 04_Archive/           ← 완료/비활성 항목
```

---

## 5. 핵심 프로토콜

### Finance Brief (주 2회)
| 요일 | 유형 | 워크플로우 |
|------|------|-----------|
| 월 | 주간 스냅샷 | Scout(시세+매크로) → Brain(헌법 체크) |
| 목 | 심층 분석 | Scout+Quant(드리프트) → Critic(검증) → 3자 회의 |

### 3자 회의 (금융 필수)
Brain 분석 → GPT에 동일 데이터 → Gemini에 동일 데이터 → 독립 분석 비교 → Brain 최종 판단

### Premise Audit (전제 감사)
Phase 전환 시 전제 재검토. "기록되지 않은 유지는 관성이고, 기록된 유지는 판단이다."

---

## 6. MCP 도구

| 도구 | 기능 |
|------|------|
| `delegate_to_engine` | to_hands.md 자동 저장 + 엔진 추천 |
| `query_gemini` | Gemini API 직접 호출 |
| `query_gpt` | GPT API 직접 호출 |
| `read_hands_result` | from_hands.md 읽기 + 초기화 |

---

## 7. User Profile

<!-- ⚠️ CUSTOMIZE: Replace with your own profile -->
| 항목 | 값 |
|------|---|
| 이름 | [Your name] |
| 직위 | [Your role and company] |
| 재정 목표 | FIRE |
| 커리어 목표 | [Your career target] |
| 기술 스택 | Antigravity + Claude + Gemini + Codex + Obsidian + n8n |
| 철학 | Hexagonal Life (체력, 가정, 기술, 재산) |

---

## 8. 용어 사전

| 용어 | 의미 |
|------|------|
| **Brain** | 전략적 판단 AI (Claude / GPT / Gemini) |
| **Hands** | 실행 엔진 |
| **Swarm** | Hands 에이전트 4명 (Quant/Scout/Engineer/Critic) |
| **Antigravity** | Agentic IDE 워크플로우 시스템 |
| **Codex** | OpenAI Codex (로컬 데스크톱 앱) |
| **MCP** | Model Context Protocol |
| **MDD** | Maximum Drawdown — 최대 낙폭 (한도 -40%) |
| **FIRE** | Financial Independence, Retire Early |
| **Hexagonal Life** | 체력/가정/기술/재산 4축 인생 철학 |
| **Role Gate** | Brain/Hands 판별 관문 |
| **3자 회의** | Brain + GPT + Gemini 독립 분석 후 합의 |
