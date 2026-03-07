# FIRE Simulation Summary

## 1) One-line conclusion
- Current setup (KRW 1.5M/month) hits KRW 857M at P50 in **17.50 years**; if business net income +KRW 2.0M/month starts at Y1 (2027-03), P50 becomes **11.58 years**.

## 2) Recommended FIRE target amount
- Recommended target: **KRW 857M (3.5% rule)**.
- Reason: higher cushion than 4% rule while preserving a materially earlier median FIRE date than 3% rule.

## 3) Contribution sensitivity
- Average FIRE acceleration per +KRW 500k monthly contribution: **2.19 years**.

| Scenario | Monthly contribution | P10 years | P50 years | P90 years |
|---|---:|---:|---:|---:|
| S1 | 1,000,000 | 17.17 | 20.83 | 26.00 |
| S2 | 1,500,000 | 14.42 | 17.50 | 22.17 |
| S3 | 2,000,000 | 12.50 | 15.17 | 19.25 |
| S4 | 2,500,000 | 11.17 | 13.42 | 17.00 |
| S5 | 3,000,000 | 10.08 | 12.08 | 15.42 |

## 4) Business income effect
| Start | Extra income/month | P50 years | Shortened vs baseline |
|---|---:|---:|---:|
| Y1 | 5,000,000 | 8.08 | 9.42 |
| Y2 | 5,000,000 | 8.83 | 8.67 |
| Y3 | 5,000,000 | 9.58 | 7.92 |

## 5) Withdrawal strategy recommendation
- Recommended strategy: **W3_3pct** (40y survival 97.79%; first-year median withdrawal 30,000,000 KRW).

| Strategy | 40y survival | Final asset P50 | Depletion P50 year (if failed) |
|---|---:|---:|---:|
| W1_4pct | 92.41% | 16,151,382,832 | 28.00 |
| W2_3.5pct | 95.63% | 18,855,903,333 | 29.00 |
| W3_3pct | 97.79% | 21,672,433,407 | 30.83 |
| W4_guardrails | 96.42% | 12,024,946,847 | 33.08 |
| W5_dividend_only | 100.00% | 18,531,602,453 | n/a |

- W5 dividend-only check:
  first-year median cash income 19,144,725 KRW (coverage probability: >=30M 0.00%, >=36M 0.00%).

## 6) FIRE roadmap milestones
- Median crossing points (baseline): KRW 100M at 4.25y, KRW 300M at 9.75y, KRW 500M at 13.42y, KRW 857M at 17.92y.

| Year from 2026-03 | Median asset | Milestone |
|---:|---:|---|
| 5 | 123,971,902 | accumulation phase |
| 10 | 311,702,589 | accumulation phase |
| 15 | 610,864,364 | accumulation phase |
| 20 | 1,085,340,215 | 3% target crossed |
| 25 | 1,849,022,725 | 3% target crossed |
| 30 | 3,034,918,248 | 3% target crossed |

## Deterministic CAGR reference (non-bootstrap)
| Scenario | CAGR | 4% target years | 3.5% target years | 3% target years |
|---|---:|---:|---:|---:|
| Optimistic_10.5pct | 10.50% | 16.25 | 17.33 | 18.58 |
| Base_8.0pct | 8.00% | 18.42 | 19.83 | 21.42 |
| Pessimistic_6.0pct | 6.00% | 20.92 | 22.58 | 24.58 |

## Notes
- Monte Carlo: stationary block bootstrap, block=12, n=10000.
- Accumulation horizon: 2026-03 to 2056-02.
- Withdrawal simulation starts with KRW 1,000,000,000 for 40 years.
- Dividend-only strategy assumes constant portfolio cash-yield 1.83%/yr (approximation for cash-flow feasibility analysis).
