# Finance Protocol (Brain Module)
*Source: brain_directive.md 분리*
*로드 조건: Finance 도메인 감지 시 Warm Memory로 로드*

---

## Ground Truth Files (Obsidian)
- `/01_Domains/Finance/Rules.md` — Investment constitution
- `/01_Domains/Finance/portfolio.json` — Portfolio definition

## Standing Rules
1. MDD limit **-40%** (absolute). 모든 추천은 스트레스 시나리오 대비 검증.
2. Benchmark: **SPY**. 초과수익이 목표.
3. ~~VIX > 30 Halt~~ **폐기.** 적립식 DCA에서 매수 중단은 저가 매수 기회 박탈.
4. Rebalancing: **월 1회**, drift > **±10%** 시 해당 종목만.
5. ~~Defensive DCA~~ → **폐기.** DCA 본질에 반하는 규칙.
6. MDD -35% → 🔴 비상. **3자 회의 소집.**
7. MDD -40% → ⚫ 절대 한도. **3자 회의 + 방어 피벗.**
8. **3자 회의: 선택적 트리거.** 일상 금융 질의는 Brain 단독 OK.
9. **DCA는 어떤 상황에서도 원래 비율대로 유지** — 동적 규칙 전부 폐기.

## Example Portfolio

<!-- ⚠️ CUSTOMIZE: Replace with your own portfolio -->
| Ticker | Role | Allocation |
|--------|------|-----------|
| VOO | S&P 500 core | 100% |

## Robustness 판정 기준

| 기준 | 정의 | 임계값 |
|------|------|--------|
| R1 | ΔP30(portfolio-SPY) | ≤ -10%p |
| R1b | P(MDD<-40%) | ≤ 10% |
| R2 | Adjusted Gap (IS-OOS) | ≤ 0.30 |
| R3 | Deflated Sharpe Ratio | ≥ 0.95 |
| R5 | 10Y 롤링 Sharpe 승리율 vs SPY | ≥ 70% |
