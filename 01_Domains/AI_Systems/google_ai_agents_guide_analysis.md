---
title: "Google AI Agents Guide 분석"
source: "startup_technical_guide_ai_agents_final.pdf (64p)"
analyzed: "2026-03-06"
engine: "antigravity_opus"
tags: [AI, agents, reference, apply]
---

# 📄 Google AI Agents Guide 분석 결과

## 1. 📚 학습 포인트 (우선순위 순)

### 🔴 Priority 1: Memory Distillation
- 장기 대화 히스토리를 LLM으로 동적 압축 → 핵심 사실/선호도만 유지
- `GenerateMemories`(자동 증류) / `CreateMemory`(에이전트 주도 증류) 패턴
- 참고: Section 2, Page 37

### 🔴 Priority 2: AgentOps 4-Layer 평가 프레임워크
1. Component-level (도구 단위 유닛 테스트)
2. Trajectory (ReAct 루프 경로 정확성)
3. Outcome (최종 응답 의미적 정확성)
4. System-level (프로덕션 모니터링)
- 참고: Section 3, Pages 50-52

### 🟠 Priority 3: Agentic RAG
- 복잡한 쿼리 → 다단계 검색 계획 → 도구 순차 호출
- 참고: Section 1, Pages 20-22

### 🟠 Priority 4: GraphRAG
- 벡터 유사도 + 명시적 관계 그래프 결합
- Obsidian 링크/태그 → 지식 그래프 변환 가능
- 참고: Section 1, Pages 19-20

### 🟡 Priority 5: Model Tiering 전략
- Flash-Lite: 단순/고볼륨, Flash: 일반, Pro: 복잡 추론
- 참고: Section 1, Page 9

### 🟡 Priority 6: ADK Workflow Agent 패턴
- SequentialAgent / ParallelAgent / LoopAgent
- 참고: Section 2, Pages 30-32

### 🟡 Priority 7: A2A (Agent2Agent) 프로토콜
- Agent Card(JSON 명함), Task 기반, 멀티모달 지원
- 참고: Section 2, Pages 38-39

---

## 2. ⚙️ 즉시 적용 항목

| # | 항목 | 적용 부분 | 우선순위 |
|---|------|----------|---------|
| 1 | Memory Distillation | conversation_memory.md 관리 | 🔴 즉시 |
| 2 | Model Tiering | engine 선택 기준 명문화 | 🔴 즉시 |
| 3 | Context Poisoning 방지 | to_*.md 필드 정밀화 | 🔴 즉시 |
| 4 | ReAct 루프 명시적 분리 | Brain 오케스트레이션 로직 | 🟠 이번주 |
| 5 | Parallel 패턴 | watcher 데몬 병렬 위임 | 🟠 이번주 |
| 6 | Agent Card | 엔진별 역할 명세 표준화 | 🟡 다음단계 |

---

## 3. 🔍 주목할 인사이트

- **Context Poisoning**: 에이전트 이름/설명/도구명이 모두 프롬프트 — 모호하면 혼란
- **Vibe Testing 탈피**: 자동화된 평가 체계 필요 (watcher 로그 → 성공률 추적)
- **MCP Toolbox for Databases**: 향후 외부 DB 연결 시 활용
- **Few-shot Example Store**: to_*.md에 모범 사례 예시 포함 시 품질 향상
- **BioCorteX 사례**: 도메인 전문 에이전트는 LLM 추론보다 구조화 데이터 탐색이 신뢰성 높음
