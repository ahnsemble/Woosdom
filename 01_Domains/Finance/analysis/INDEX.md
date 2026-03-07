# Portfolio Backtest Analysis — Phase Index
*Last Updated: 2026-02-18 (Phase 22 완료, Ruleset v2.8)*

---

## 현행 포트폴리오
**Trinity v5 (P1 Hedged Growth):** SCHD 35% / QQQM 15% / SMH 10% / SPMO 10% / TLT 10% / GLDM 20%
- **MDD 한도:** -40% (경고 -30%, 비상 -35%)
- **Phase 20 검산: PASS** (5 Track + 벤치마크 비교 + QS50 비교 전 기준 통과, 2026-02-17)
- **포트폴리오 설계 Phase 종료. 실전 투입 승인.**

---

## Phase 이력

### 정적 포트폴리오 설계 (Phase 1~20) — 완료

| Phase | 목적 | 핵심 결과 | 폴더 |
|-------|------|----------|------|
| **1** | QQQM/SCHD 투자설명서 정밀 해부 | Prospectus 구조 분석, 한국 세금 렌즈 | `../archive/` `../reference/` |
| **2** | ETF 비교 리서치 (Gemini) | QQQM vs QQQ, SCHD 대안 탐색 | `../research/` |
| **3** | 1차 DCA 백테스트 | Trinity v1 검증, MDD -15% 설정 | `../archive/` |
| **4** | 확장 백테스트 (v2 후보) | SCHD 비중 확대 테스트 | `../archive/` |
| **5** | 브루트포스 1차 + FDE 알파 | v1 기본 조합 탐색 | `../archive/` `../research/` |
| **6** | 통합 백테스트 (12개 후보) | BF-S1 종합 2위 → 1차 확정 | `phase6/` |
| **7** | 확장 검증 (45개 후보 + IS/OOS) | BF-S1 종합 1위 유지 | `phase7/` |
| **8** | 정밀 검증 (3자 회의 + 상관관계) | BF-S1 유지 확정 (신뢰도 85%) | `phase8/` |
| **9** | 편향 제거 3자 교차검증 | "조건부 유지" (신뢰도 70%) | `phase9/` |
| **10** | 통일 조건 최종 대결 | BF-S1→**F-03** 전환 (신뢰도 85%) | `phase10/` |
| **11** | GFC 검증 + 7포트 비교 + MDD 완화 | F-03→**P1** 전환. MDD -25%→-35% | `phase11/` |
| **12** | 적립식(DCA) 실전 검증 + SCHD 보정 | P1→**P1-6m** 확정. QQQ→QQQM, GLD→GLDM | `phase12/` |
| **13** | 유니버스 확장 브루트포스 (19개, 3.34억) | Stage 3 전멸. Robust=0/10 | `phase13/` |
| **14** | P1-6m vs QS50 초정밀 DCA 대결 | QS50 Terminal +4.9억 우위 | `phase14/` |
| **15** | 전면 재설계 (Layer1+2, 3자회의×2) | JEPQ 80% 폐기. Robust=0/30 | `phase15/` |
| **16** | 통합 자유 브루트포스 (22개, 샘플링 1,935만) | Robust=1 (QS50). Track2 Top1: 38.4억 | `phase16/` |
| **16b** | **전수 재실행 (24개, 17.4억 조합)** | Robust=1 (QS50). Track2 Top1: 46.1억 | `phase16b/` |
| **17** | 닷컴 확장 + GLD/TLT (29.5억, 26개, 312개월) | Robust=0. GLD 필수 확정, TLT 방어만 | `phase17/` |
| **18** | SPMO 도입 + 모멘텀 팩터 전수 (9,455만) | v5 후보 도출 (TLT 10%, GLDM 20%) | `phase18/` |
| **19~19d** | SPMO 프록시 정교화 + Robustness 재판정 | FF→DIY→통합 프록시. R3 ratio 기준 개선 | `phase19/` `phase19b~d/` |
| **20** | **5-Track 교차검증 + 벤치마크 비교** | **v5 PASS.** ΔP30=-35.67%p, DSR=1.000 | `phase20/` |
| **20-F** | SPY/60-40 Block BS 비교 | v5 Sharpe 1위, 꼬리 리스크 절반 | `phase20/` |
| **20-G** | QS50 비교 (4종 정밀 비교) | v5 복잡성 프리미엄 확인. 파산확률 8배 차이 | `phase20/` |

### Block Bootstrap 1M 정밀도 검증 — 완료

| 항목 | 결과 | 폴더 |
|------|------|------|
| 목적 | Phase 20 50K → 1M 확대. 통계적 정밀도 검증 | `phase20_1M/` |
| 판정 | **수렴 확인.** 전 지표 50K 대비 ±0.5%p 이내 | |
| v5 P(MDD<-40%) | 9.21% [9.15%, 9.27%] — R1b 마진 0.73%p 확인 | |
| 핵심 결론 | 50K 결과는 샘플링 운이 아닌 구조적 결과. Phase 20 판정 변경 없음 | |

### 동적 리밸런싱 탐색 (Phase 21~) — 완료

| Phase | 목적 | 핵심 결과 | 폴더 |
|-------|------|----------|------|
| **21** | Defensive DCA / VIX 규칙 / 리밸런싱 빈도 (64개 시나리오) | **VIX Halt 폐기, D-DCA(D1) 검증, ±10% 완화, JEPQ 보류.** 3자 회의 완료. | `phase21/` |
| **22** | Defensive DCA 진입/복귀 임계치 민감도 (13개 시나리오) | 3자 회의 후 **Defensive DCA 전체 폐기.** DCA 본질에 반하는 규칙. | `phase22/` |

### FIRE 시뮬레이션 — 완료

| 항목 | 결과 | 폴더 |
|------|--------|--------|
| FIRE 목표 | 8.57억 (3.5% 룰) | `fire_simulation/` |
| P50 달성 | 17.5년 (49세) | |
| 인출 전략 | 3% 룰 (97.8% 생존) | |
| 사업소득 +200만 | 43세 (−6년) | |

---

## 누적 통계 요약
- **총 탐색 조합:** ~55억+ (Phase 13~19 누적)
- **포트폴리오 버전:** v1 → v2 → v3 → v4 → v4(6m) → **v5** (6회 전환)
- **MDD 헌법 변경:** -15% → -25% → -35% → **-40%** (4단계)
- **Premise Audit:** 4회 (Ph11→12, Ph16b→17, Ph19→20, Ph20→21)
- **상세:** `phase_statistics_report.md` 참조

---

## History (포트폴리오 변천)
- **Trinity v1:** QQQM 50% / SCHD 20% / KMLM 15% / SGOV 15% — MDD -15%
- **Trinity v2 (BF-S1):** SCHD 50% / QQQ 30% / SMH 10% / SPMO 10% — MDD -25%
- **Trinity v3 (F-03):** SCHD 50% / QQQ 25% / SMH 15% / SPMO 10% — MDD -25%
- **Trinity v4 (P1):** SCHD 35% / QQQ 15% / SMH 10% / SPMO 10% / TLT 15% / GLD 15% — MDD -35%
- **Trinity v4 (P1-6m):** SCHD 35% / QQQM 15% / SMH 10% / SPMO 10% / TLT 15% / GLDM 15% — MDD -35%
- **Trinity v5 (P1):** SCHD 35% / QQQM 15% / SMH 10% / SPMO 10% / TLT 10% / GLDM 20% — **MDD -40%** ← **현행**
