---
title: "Woosdom vs External Systems — Langent / Opus Dashboard 비교 분석"
type: reference
source: "03_Journal/daily/시스템 사례-2.md"
promoted_date: "2026-02-14"
promoted_by: "Brain (Opus)"
tags: [Langent, LangGraph, Opus-dashboard, Woosdom-comparison, observability, knowledge-graph]
---

# Woosdom vs External Systems 비교 분석

> **핵심 결론**: "같은 설계도, 다른 시공법."
> Woosdom의 방향성은 맞다. 부족한 부분(지식 그래프, 자동 오케스트레이션, 운용 가시성)은 명확히 식별됨.

---

## 1. Langent (LangGraph + Agent)

LangChain 생태계 기반 셀프호스팅 에이전트 프레임워크.
- Docker 컨테이너 9개 (API Gateway, PDF Decoder, Embedding, TrustGraph 등)
- TrustGraph (Neo4j 기반 지식 그래프) → FastAPI 노출
- DeepAgents 스킬 + Sub-Agent 구조

```
LANGENT
├── THINKER (DeepAgents) ↔ CONNECTOR (MCP) ↔ MEMORY (TrustGraph)
├── SUB-AGENTS (Researcher | Analyst | Coder | ...)
└── SKILLS (Market Research | Valuation | ...)
```

## 2. 1:1 매핑

| Langent | Woosdom | 평가 |
|---------|--------|------|
| THINKER (DeepAgents) | Brain (Claude Opus 4.6) | **Woosdom 우위** — LLM 추론 품질 격차 |
| CONNECTOR (MCP) | MCP Server (woosdom-executor) | 동일 |
| MEMORY (TrustGraph/Neo4j) | Obsidian Vault (.md) | **Langent 우위** — 그래프DB vs 플랫파일 |
| SUB-AGENTS (내부 오케스트레이션) | Hands (GPT/Gemini/Codex 외부 위임) | **Langent 우위** — 자동 vs 수동 |
| SKILLS (코드 로드) | Domain Ontology (.md 로드) | 동등 |

## 3. Opus 멀티에이전트 대시보드 사례

- Opus를 메인 Brain으로, 하위 AI를 에이전트로 운용
- 에이전트 간 업무 분배를 **실시간 UI 대시보드**로 모니터링
- 25초간 연쇄 이벤트: `file_edited` → `task_complete` 자동 보고 패턴

**핵심 시사점: 아키텍처가 아니라 운용 가시성(Observability)**

| 항목 | Opus 대시보드 | Woosdom 현재 |
|------|--------------|-------------|
| 에이전트 상태 확인 | 실시간 UI | ❌ |
| 작업 진행률 | 이벤트 로그 | ❌ |
| 에이전트 배치 현황 | 방/프로젝트별 시각화 | ❌ |

## 4. Woosdom 로드맵 반영

### 단기: 현 구조 유지, 안정화
### 중기 (Phase 11):
- Sub-Agent 내부 호출 자동화 (Langent 참조)
- 운용 가시성: 최소 텍스트 로그 → 이상 웹 대시보드
### 장기 (Phase 12+):
- 경량 그래프DB 검토 (.md 관계 추론 한계 극복)
- Agent Pool 개념 도입 (역할별 자동 배정)

## 5. 패턴 비교표

| 패턴 | Langent | Opus 대시보드 | Woosdom |
|------|---------|--------------|--------|
| 중앙 Brain + Sub-Agent | ✅ | ✅ | ✅ |
| MCP 기반 연결 | ✅ | ? | ✅ |
| 지식 그래프 메모리 | ✅ | ? | ❌ |
| 자동 오케스트레이션 | ✅ | ✅ | ❌ |
| 운용 가시성 대시보드 | ❌ | ✅ | ❌ |
| 멀티엔진 유연성 | ❌ | ? | ✅ |
| Brain 추론 품질 | 중 | 상 | 상 |

> **장기 목표: Woosdom의 두뇌 + Langent급 자동화 몸체 + 대시보드급 가시성**
