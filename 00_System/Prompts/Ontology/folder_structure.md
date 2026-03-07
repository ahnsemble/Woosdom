# Obsidian Vault Folder Structure v4.0
## Woosdom Brain — Classification Rules & Architecture

*Last Updated: 2026-02-24*
*Previous: v3.0 (2026-02-18)*

---

## 0. Dev Folder Top-Level Structure

```
Dev/
├── Woosdom_Brain/          ← 옵시디언 볼트 (지식/문서)
├── Projects/               ← 활성 코드 저장소
│   ├── arch_news_bot/
│   ├── cad_tools/
│   ├── mcp_server/         ← woosdom-executor MCP 서버
│   └── telegram_cronbot/
├── Archive/                ← 비활성 코드 프로젝트
│   ├── fde_woosdom_v1/
│   └── trinity_backtest/
└── _scratch/               ← 임시 파일
```

**원칙:** Woosdom_Brain = 지식/문서, Projects = 코드. 완전 분리.

> ⚠️ **예외:** `02_Projects/` 내 일부 프로젝트(woosdom_app, game_crossy, obsidian_rag 등)는 볼트와 밀접하게 결합되어 볼트 내 코드 포함. 장기적으로 Dev/Projects/로 분리 검토.

---

## 1. Vault Internal Structure

```
Woosdom_Brain/
│
├── 00_System/                         ← AI 운영 체제 (Hot Memory)
│   ├── Prompts/
│   │   ├── Ontology/                  ← Brain 핵심 정의
│   │   │   ├── brain_directive.md     ← Brain 헌법 v3.0
│   │   │   ├── active_context.md      ← Hot Memory (≤500 토큰)
│   │   │   ├── premise_audit_protocol.md
│   │   │   ├── folder_structure.md    ← 이 문서
│   │   │   └── modules/              ← 도메인별 모듈 (필요 시 로드)
│   │   │       ├── finance_protocol.md
│   │   │       ├── engine_router.md
│   │   │       ├── career_life_protocol.md
│   │   │       └── changelog.md
│   │   ├── Swarm/                     ← Swarm 에이전트 페르소나
│   │   │   ├── README.md
│   │   │   ├── quant.md / scout.md / engineer.md / critic.md
│   │   ├── antigravity_hands_executor.md
│   │   ├── deep_research_system_evolution.md
│   │   ├── gemini_sub_brain.md
│   │   ├── gpt_sub_brain.md
│   │   └── system_manual.md
│   ├── Templates/                     ← Brain ↔ Hands 통신
│   │   ├── to_hands.md / from_hands.md
│   │   ├── to_codex.md
│   │   └── council_log_template.md
│   ├── Specs/                         ← 시스템 스펙 문서
│   │   ├── agent_corps_spec.md
│   │   └── agent_corps/
│   │       └── codex_team_protocol.md
│   ├── Exports/                       ← 외부 내보내기용
│   ├── Guides/                        ← 셋업 가이드
│   ├── Logs/                          ← 시스템 로그
│   ├── Research/                      ← 시스템 리서치 (활성만)
│   └── Scripts/                       ← 셸 스크립트
│
├── 01_Domains/                        ← 도메인별 영구 지식 (Warm Memory)
│   ├── Finance/
│   │   ├── Rules.md                   ← 투자 헌법
│   │   ├── portfolio.json             ← Trinity v5 배분
│   │   ├── analysis/                  ← INDEX.md + fire_simulation/
│   │   ├── research/                  ← 딥리서치 리포트
│   │   ├── reference/                 ← 투자설명서, 프롬프트 원본
│   │   └── execution/                 ← 매매 기록
│   ├── AI_Systems/
│   │   ├── README.md                  ← Warm Memory 진입점
│   │   ├── engine_evaluation/         ← 6개 딥리서치 + synthesis
│   │   └── (기타 아키텍처 참조 문서)
│   ├── Architecture/
│   │   └── codes.md
│   ├── Career/
│   │   ├── MOC.md                     ← Warm Memory 진입점
│   │   ├── References/
│   │   └── research/
│   ├── Health/
│   │   ├── MOC.md                     ← Warm Memory 진입점
│   │   └── training_protocol.md
│   └── life_roadmap.md
│
├── 02_Projects/                       ← 시한 있는 프로젝트
│   ├── woosdom_app/                   ← MC 대시보드 (PyWebView)
│   ├── game_crossy/                   ← Project Crossy (Godot→Roblox)
│   ├── obsidian_rag/                  ← RAG 파이프라인
│   ├── task_bridge/                   ← Brain↔Hands 브릿지
│   ├── engine_watch/                  ← 엔진 감시
│   └── ai-town/                       ← 참조 클론 (Pixel Agents용)
│
├── 03_Journal/                        ← Episodic Memory (Cold)
│   ├── daily/                         ← YYYY-MM-DD[_topic].md
│   ├── weekly/                        ← week_YYYY-WNN.md (ISO)
│   └── monthly/                       ← YYYY-MM.md
│
└── 04_Archive/                        ← 비활성 보관소
    ├── Research/                      ← 완료된 리서치
    ├── completed_projects/            ← 폐기/완료 프로젝트
    ├── deprecated_domains/
    ├── finance_phases/                ← Phase 6~22 전체 이력
    ├── pkl_checkpoints/               ← 레거시 백테스트 체크포인트
    ├── promoted_sources/              ← 승격된 원본 자료
    ├── templates_retired/             ← 폐기 템플릿
    ├── templates_static_phases/       ← 과거 Phase별 고정 템플릿
    └── obsidian_defaults/             ← Obsidian 기본 파일
```

---

## 2. Folder Definitions

### 00_System/ — AI 운영 체제
**판별:** "이 파일 없으면 Brain이 부팅 불가?" → Yes → 여기

| 하위 | 용도 |
|------|------|
| `Prompts/Ontology/` | Brain 헌법, Hot Memory, 구조 정의, 모듈 |
| `Prompts/Swarm/` | Swarm 에이전트 페르소나 |
| `Prompts/*.md` | Sub-Brain + 기타 프롬프트 |
| `Templates/` | Brain ↔ Hands 통신 템플릿 |
| `Specs/` | Agent Corps 등 시스템 스펙 |
| `Research/` | 활성 시스템 리서치 (완료 시 Archive 이동) |
| `Logs/` | 시스템 로그 |
| `Scripts/` | 셸 스크립트 |
| `Guides/` | 셋업 가이드 |
| `Exports/` | 외부 내보내기 |

### 01_Domains/ — 도메인별 영구 지식
**판별:** "프로젝트 끝나도 유효?" → Yes → 여기

| 도메인 | 트리거 키워드 | 진입점 |
|--------|-------------|--------|
| `Finance/` | 투자, 포트폴리오, FIRE, 리밸런싱 | `Rules.md` + `portfolio.json` |
| `AI_Systems/` | 멀티에이전트, 오케스트레이션, MCP | `README.md` |
| `Architecture/` | 건축, BIM, 설계 | `codes.md` |
| `Career/` | FDE, 로드맵, 이직, 수익화, 영앤리치 | `MOC.md` |
| `Health/` | 운동, Big 3, 복싱, 커팅 | `MOC.md` |

### 02_Projects/ — 시한 있는 프로젝트
**판별:** "'완료'라고 말할 수 있는 시점 존재?" → Yes → 여기

### 03_Journal/ — Episodic Memory (Cold)
**판별:** "'언제' 일어났는지가 중요?" → Yes → 여기

| 하위 | 파일명 규칙 |
|------|------------|
| `daily/` | `YYYY-MM-DD.md` 또는 `YYYY-MM-DD_topic.md` |
| `weekly/` | `week_YYYY-WNN.md` (ISO 주차) |
| `monthly/` | `YYYY-MM.md` |

### 04_Archive/ — 비활성 보관소
**판별:** "현재 진행 중이거나 참조 필요?" → No → 여기

---

## 3. AI Routing Table

| 감지 키워드 | 로드 경로 | Tier |
|------------|----------|------|
| (매 대화 시작) | `brain_directive.md` + `active_context.md` | Hot |
| 투자, 포트폴리오, FIRE | `Finance/Rules.md` + `portfolio.json` | Warm |
| 멀티에이전트, Swarm | `AI_Systems/README.md` | Warm |
| FDE, 커리어, 로드맵 | `Career/MOC.md` | Warm |
| 건축, BIM | `Architecture/codes.md` | Warm |
| 운동, 헬스, Big 3 | `Health/MOC.md` | Warm |
| "지난번에", "기억나" | `03_Journal/` 검색 | Cold |

---

## 4. State Transitions

```
[새 관심사] → 01_Domains/[New]/README.md 생성
[프로젝트 시작] → 02_Projects/[name]/ + active_context 등록
[프로젝트 완료] → 영구 지식 추출 → 01_Domains/ + 폴더 → 04_Archive/
[active_context > 500 토큰] → 오래된 항목 → 03_Journal/weekly/
[도메인 1년 미사용] → 04_Archive/deprecated_domains/
[Research 완료] → 00_System/Research/ → 04_Archive/Research/
```

---

*끝. 시스템 변경 시 이 문서를 업데이트할 것.*
