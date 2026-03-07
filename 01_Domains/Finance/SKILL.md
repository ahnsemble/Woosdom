---
name: finance-advisor
description: >
  투자, 포트폴리오, FIRE, DCA, 리밸런싱, MDD, 드리프트, 매수, 적립,
  Trinity, SCHD, QQQM, SMH, SPMO, TLT, GLDM, 3자 회의, 백테스트,
  주식, ETF, 배당, 금리, VIX, 시장 관련 질문 시 트리거.
  Rules.md(금융 헌법)와 portfolio.json을 함께 참조.
---

# Finance Advisor

## Ground Truth Files
- `01_Domains/Finance/Rules.md` — Investment Constitution (최우선 진실)
- `01_Domains/Finance/portfolio.json` — Trinity Portfolio 정의
- Brain 판단 시 위 파일을 **반드시** MCP로 로드 후 응답.

## Standing Rules

1. MDD limit **-40%** (absolute). 모든 추천은 스트레스 시나리오 대비 검증.
2. Benchmark: **SPY**. 초과수익이 목표.
3. IF `10Y Treasury Yield > 4.5%` → JEPQ 검토. **🔒 보류** (Phase 21 미검증).
4. ~~VIX > 30 Halt~~ **폐기.** 적립식 DCA에서 매수 중단은 저가 매수 기회 박탈.
5. Rebalancing: **월 1회**, drift > **±10%** 시 해당 종목만.
6. 포트폴리오 변경 제안 시 → **Hands 백테스팅** (수동 계산 금지).
7. 실시간 시세 필요 시: "실시간 시세 확인이 필요합니다."
8. ~~Defensive DCA~~ → **폐기.** DCA 본질에 반하는 규칙.
9. MDD -35% → 🔴 비상. **3자 회의 소집.**
10. MDD -40% → ⚫ 절대 한도. **3자 회의 + 방어 피벗.**
11. **3자 회의: 선택적 트리거.** 일상 금융 질의는 Brain 단독 OK.

## Portfolio: Trinity v5

| Ticker | Role | Allocation |
|--------|------|-----------|
| SCHD | High-quality dividend anchor | 35% |
| QQQM | Nasdaq 100 growth engine | 15% |
| SMH | Semiconductor / AI infrastructure | 10% |
| SPMO | S&P 500 Momentum factor | 10% |
| TLT | Long-term Treasury hedge | 10% |
| GLDM | Gold / inflation hedge | 20% |

## Robustness 판정 기준

| 기준 | 정의 | 임계값 |
|------|------|--------|
| R1-new | ΔP30(v5-SPY) Block BS L=12 | ≤ -10%p |
| R1b | P(MDD<-40%) Block BS L=12 | ≤ 10% |
| R2 | Adjusted Gap (IS-OOS) | ≤ 0.30 |
| R3 | Deflated Sharpe Ratio | ≥ 0.95 |
| R4 | P5 Terminal Block BS L=12 | ≥ 6억 |
| R5 | 10Y 롤링 Sharpe 승리율 vs SPY | ≥ 70% |

## 복귀 트리거
- TLT 장기 역풍 (금리 상승 3년+) → TLT→IEF 교체 검토
- Fed 긴축 사이클 진입 → TLT 10%→0%, SGOV/현금 이전 검토
- GLDM 역할 실패 (주식-금 상관 6개월+ 0.5 이상) → GLDM 축소
- SCHD-SPMO 위기 상관 >0.85 지속 → SPMO 교체 검토
- 2년 연속 SPY 대비 -5%p → 전면 재검토
- SMH 양자컴 가치이전 — 순수 양자 기업 합산 시총 SMH 20% 돌파 AND 상위 5종목 양자 매출 <5% 2년 지속 → SMH 축소

## 3자 회의 트리거 (필수 조건, OR)
- MDD -35% / -40% 도달
- 리밸런싱 드리프트 ±10% 트리거
- 포트폴리오 구조 변경 (종목 추가/제거/비중 변경)
- 시스템 인프라 파괴 권한

## Brain 판단 원칙
- 모든 분석은 **적립식(DCA) 전제**로 실행 (일시불 아님)
- 초기 400만 + 월 150만, 정수주 매수, 잔여 현금 이월
- LLM에 수학 연산/매매 판단 위임 **절대 금지**
- 계산이 필요하면 → Hands (Codex) 위임
