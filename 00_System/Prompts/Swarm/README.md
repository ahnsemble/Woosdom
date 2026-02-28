# Hands Swarm — Agent Personas

## 개요
Brain(Claude)이 Hands(실행 엔진)에 작업을 위임할 때, 각 에이전트 페르소나를 주입하여 역할 특화된 출력을 얻기 위한 프롬프트 모음.

## 에이전트 목록

| # | 콜사인 | 파일 | 역할 | 주 엔진 |
|---|--------|------|------|---------|
| 1 | **Quant** | `quant.md` | 정량 분석, 백테스트, 포트폴리오 수학 | Antigravity / Codex |
| 2 | **Scout** | `scout.md` | 실시간 시장 정보, 뉴스, 매크로 수집 | Antigravity Gemini |
| 3 | **Engineer** | `engineer.md` | 코드 생성, MCP, 자동화 | Codex / Antigravity |
| 4 | **Critic** | `critic.md` | 출력 검증, 반론, 팩트체크 | GPT / Gemini (교차 엔진) |

## 사용법
1. Brain이 작업을 분류하고 에이전트를 선택
2. `swarm_dispatch_template.md` 형식으로 `to_hands.md` 작성
3. 사용자가 해당 페르소나 + 지시를 엔진에 전달
4. 결과는 `from_hands.md`에 저장 → Brain이 읽고 후속 판단

## Phase Roadmap
- **Phase 0**: 페르소나 문서 작성 ✅
- **Phase 1**: 주 2회 Finance Brief 파일럿 (수동 릴레이)
- **Phase 2**: MCP 자동 위임 (to_hands → 엔진 자동 호출)
- **Phase 3**: 에이전트 간 체이닝 자동화
