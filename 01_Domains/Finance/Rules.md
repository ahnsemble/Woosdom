# Finance Ontology — Investment Constitution
*Last Updated: 2026-02-20 (Ruleset v2.9)*
*Portfolio: Trinity v5 (P1 Hedged Growth) — Phase 20 검산 PASS*

---

## 1. Investment Philosophy
- **Primary Goal:** Economic Freedom (FIRE).
- **Risk Tolerance:** Conservative Growth. MDD limit is **-40%**.
- **Benchmark:** SPY (S&P 500)
- **Rebalancing:** 월 1회 모니터링 + ±10% 드리프트 임계치. 임계치 초과 종목만 리밸런싱. (Phase 21 검증: ±5%→±10% 변경, 성과 동등 + 거래 23% 감소)

## 1.1 Investment Execution (불변 전제)
- **투자 방식:** 적립식 (DCA). 일시불 아님.
- **초기 투자금:** 400만원 (~$2,960 @ 1,350원)
- **월 적립금:** 150만원 (~$1,111 @ 1,350원)
- **정수 주 매수만 허용** (한국 증권사 기준, fractional shares 미지원)
- **잔여 현금:** 다음 달로 이월 (현금 버퍼)
- **배당금:** 수령 즉시 현금 버퍼에 추가 → 다음 매수 시 활용
- ⚠️ **모든 백테스트·시뮬레이션·전략 분석은 이 적립식 조건을 기본 전제로 실행할 것.**

## 2. Portfolio: Trinity v5 (P1 Hedged Growth)

| Ticker | Role | Allocation | 비고 |
|--------|------|-----------|------|
| SCHD | High-quality dividend anchor | 35% | — |
| QQQM | Nasdaq 100 growth engine | 15% | QQQ→QQQM (비용 절감) |
| SMH | Semiconductor / AI infrastructure | 10% | — |
| SPMO | S&P 500 Momentum factor | 10% | ⚠️ 6개월 모니터링 (2026-02-15~) |
| TLT | Long-term Treasury hedge | 10% | v4 대비 15%→10% 축소 |
| GLDM | Gold / inflation hedge | 20% | v4 대비 15%→20% 확대 |

### Phase 20 검산 결과 (2026-02-17)
- **판정: PASS** (5 Track + 벤치마크 비교 전 기준 통과)
- R1-new ΔP30(vs SPY): -35.67%p (기준 ≤-10%p) ✅
- P(MDD<-40%): 9.27% (기준 ≤10%) ✅
- DSR: 1.000 (기준 ≥0.95) ✅ — 과최적화 아님
- P5 Terminal: 8.90억 (기준 ≥6억) ✅
- 10Y 롤링 Sharpe 승리: 17/17 (100%) ✅
- 전구간 Sharpe: 0.781 (SPY 0.569, 60/40 0.699)
- P50 Terminal: 20.3억 (SPY 16.4억, 60/40 12.7억)

### Robustness 판정 기준 (Phase 20 확정)
| 기준 | 정의 | 임계값 |
|------|------|--------|
| R1-new | ΔP30(v5-SPY) Block BS L=12 | ≤ -10%p |
| R1b | P(MDD<-40%) Block BS L=12 | ≤ 10% |
| R2 | Adjusted Gap (IS-OOS) | ≤ 0.30 |
| R3 | Deflated Sharpe Ratio | ≥ 0.95 |
| R4 | P5 Terminal Block BS L=12 | ≥ 6억 |
| R5 | 10Y 롤링 Sharpe 승리율 vs SPY | ≥ 70% |

### 복귀 트리거
- TLT 장기 역풍 (금리 상승 지속 3년+) → TLT→IEF 교체 검토
- **Fed 긴축 사이클 진입 시 → TLT 10%→0% 축소, SGOV/현금 이전 검토** (2022 검증: TLT -48%)
- GLDM 역할 실패 (주식-금 상관 6개월+ 0.5 이상) → GLDM 비중 축소 검토
- **SPMO 6개월 모니터링** — 벤치마크 대비 -5%p+ 부진 시 SPMO 10%→QQQM 흡수 (QQQM 25%)
- SCHD-SPMO 위기 상관 지속 상승 (>0.85) → SPMO 교체 검토
- 2년 연속 SPY 대비 -5%p underperform → 전면 재검토
- **SMH 양자컴 가치이전 리스크** — 순수 양자 기업(IonQ/IONQ, Rigetti/RGTI, PsiQuantum 등) 합산 시총이 SMH 총 자산의 20% 돌파 **AND** SMH 상위 5개 종목의 양자 매출 비중 5% 미만 상태가 2년 지속 → SMH 비중 축소 검토 (QTUM 등 대체). (2026-02-18 확정, Brain 단독 판단 — 양자컴은 반도체의 대체재가 아닌 확장판이므로 현재 SMH 유지)

## 3. Execution Rules (헌법)
- ~~IF `VIX` > 30: Halt ALL buying.~~ → **폐기 (Phase 21).** 적립식 투자에서 매수 중단은 회복장 저가 매수 기회를 박탈하여 장기 성과를 훼손. 3자 회의 만장일치.
- IF `10Y_Treasury_Yield` > 4.5%: JEPQ 비중 확대 검토. → **🔒 보류.** Phase 21에서 미검증. 단일 금리 임계치 기반 스위칭은 과최적화 소지. 검증 게이트 통과 전까지 Ruleset 편입 금지.
- IF portfolio drift > ±10% from target: Trigger rebalancing. (Phase 21: ±5%→±10% 완화)
- ~~IF MDD approaches -30%: Defensive DCA 발동~~ → **폐기 (Phase 22 후 사용자 판단).** 폭락장에서 싸게 사는 것이 DCA의 본질. 방어 모드는 "슼 때 사지 않고 비쌀 때 사는" 역행. 적립식에서는 원래 비율대로 DCA 유지가 최선.
- IF MDD breaches -35%: 🔴 비상. 3자 회의 소집.
- IF MDD breaches -40%: ⚫ 절대 한도. 방어 피벗 검토.

## 4. 3자 회의 규칙 (v2.9 개정: 2026-02-20)

### 4.1 선택적 트리거 (v2.9)
~~모든 금융 의사결정은 3자 회의 필수~~ → **폐기 (v2.9).** 딥리서치 3자 종합 결과: 전건 3자회의는 API 비용 + 지연 시간의 극치. 환각 리스크 대비 비용이 압도하는 경우에만 교차검증.

**3자 회의 필수 조건 (OR):**
- MDD -35% 비상 트리거 발동
- MDD -40% 절대 한도 도달
- 리밸런싱 드리프트 (±10%) 트리거 발동
- 포트폴리오 구조 변경 (종목 추가/제거/비중 변경)
- 시스템 인프라 파괴 권한 (DB 삭제, 규칙 변경 등)

**Brain 단독 판단 허용:**
- 월별 DCA 매수 주문서 생성
- 주간 Brief / 시장 동향 요약
- 복귀 트리거 모니터링 (판단 전 단계)
- 일반 금융 질의응답

### 4.2 회의 절차 (불변)
- Brain이 최종 판단, GPT/Gemini는 독립 분석 제출.
- Critic 에이전트가 교차 검증.

### 4.3 개정 이력
- v2.8 (2026-02-15): 모든 금융 의사결정 3자 회의 필수
- v2.9 (2026-02-20): 선택적 트리거로 전환 (GPT+Gemini 딥리서치 종합)

## 5. History
- **Trinity v1** (deprecated 2026-02-15): QQQM 50% / SCHD 20% / KMLM 15% / SGOV 15%, MDD -15%
- **Trinity v2 (BF-S1)** (deprecated 2026-02-15): SCHD 50% / QQQ 30% / SMH 10% / SPMO 10%, MDD -25%
- **Trinity v3 (F-03)** (deprecated 2026-02-15): SCHD 50% / QQQ 25% / SMH 15% / SPMO 10%, MDD -25%
- **Trinity v4 (P1)** (deprecated 2026-02-15): SCHD 35% / QQQ 15% / SMH 10% / SPMO 10% / TLT 15% / GLD 15%, MDD -35%
- **Trinity v4 (P1-6m)** (deprecated 2026-02-17): SCHD 35% / QQQM 15% / SMH 10% / SPMO 10% / TLT 15% / GLDM 15%, MDD -35% — Phase 12 확정
- **Trinity v5 (P1)** (active): SCHD 35% / QQQM 15% / SMH 10% / SPMO 10% / TLT 10% / GLDM 20%, MDD -40% — Phase 18 도출, Phase 20 검산 PASS
