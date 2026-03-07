#!/usr/bin/env python3
from __future__ import annotations

import math
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd

BASE_DIR = Path('/Users/woosung/Documents/New project')
PHASE20_DIR = BASE_DIR / '01_Domains' / 'Finance' / 'analysis' / 'phase20'
PHASE20_1M_DIR = BASE_DIR / '01_Domains' / 'Finance' / 'analysis' / 'phase20_1M'
PHASE20_CODE_DIR = PHASE20_DIR / 'code'

DEV_PHASE20_1M_DIR = Path('/Users/woosung/Desktop/Dev/Woosdom_Brain/01_Domains/Finance/analysis/phase20_1M')

sys.path.insert(0, str(PHASE20_CODE_DIR))
sys.path.insert(0, str(BASE_DIR / 'phase20'))

from cleanroom_backtest import (  # noqa: E402
    build_market_data,
    simulate_portfolio,
    stationary_bootstrap_indices,
    sharpe_ratio,
    simulate_from_twr,
    MarketData,
    _build_point_series_from_returns,
    _ensure_full_period,
    monthly_first_price_from_ticker,
    monthly_total_return_from_ticker,
)


@dataclass
class Boot1M:
    n_boot: int
    block: int
    p30: float
    p35: float
    p40: float
    shortfall_600m: float
    cdar95: float
    term_q: Dict[str, float]
    mdd_q: Dict[str, float]
    sharpe_q: Dict[str, float]


V5_WEIGHTS = {'SCHD': 0.35, 'QQQM': 0.15, 'SMH': 0.10, 'SPMO': 0.10, 'TLT': 0.10, 'GLDM': 0.20}
SPY_WEIGHTS = {'SPY': 1.0}
SIXTY_FORTY_WEIGHTS = {'SPY': 0.60, 'AGG': 0.40}
QS50_WEIGHTS = {'SCHD': 0.50, 'QQQM': 0.50}

BLOCK = 12
N_BOOT = 1_000_000
SEED = 42

OUT_V5 = PHASE20_1M_DIR / 'v5_block12_1M_summary.md'
OUT_SPY = PHASE20_1M_DIR / 'spy_block12_1M_summary.md'
OUT_6040 = PHASE20_1M_DIR / 'sixty_forty_block12_1M_summary.md'
OUT_QS50 = PHASE20_1M_DIR / 'qs50_block12_1M_summary.md'
OUT_FOUR = PHASE20_1M_DIR / 'four_way_comparison_1M.md'
OUT_CODE = PHASE20_1M_DIR / 'code' / 'phase20_1M_bootstrap.py'


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def fmt_pct(v: float, d: int = 2) -> str:
    if not np.isfinite(v):
        return 'n/a'
    return f"{v * 100:.{d}f}%"


def fmt_num(v: float, d: int = 3) -> str:
    if not np.isfinite(v):
        return 'n/a'
    return f"{v:.{d}f}"


def fmt_money(v: float) -> str:
    if not np.isfinite(v):
        return 'n/a'
    return f"{v:,.0f}"


def prop_ci95(p: float, n: int) -> Tuple[float, float]:
    se = math.sqrt(max(p * (1.0 - p), 0.0) / n)
    lo = max(0.0, p - 1.96 * se)
    hi = min(1.0, p + 1.96 * se)
    return lo, hi


def build_market_with_agg(base_market: MarketData) -> Tuple[MarketData | None, Dict[str, float], bool]:
    agg = monthly_total_return_from_ticker('AGG')
    vbm = monthly_total_return_from_ticker('VBMFX')

    overlap_idx = agg.index.intersection(vbm.index)
    overlap = pd.DataFrame({'AGG': agg.reindex(overlap_idx), 'VBMFX': vbm.reindex(overlap_idx)}).dropna()
    corr = float(overlap['AGG'].corr(overlap['VBMFX'])) if len(overlap) >= 3 else float('nan')
    td = float((overlap['VBMFX'] - overlap['AGG']).mean() * 12.0) if len(overlap) else float('nan')
    te = float((overlap['VBMFX'] - overlap['AGG']).std(ddof=0) * math.sqrt(12.0)) if len(overlap) else float('nan')

    info = {
        'overlap_months': float(len(overlap)),
        'corr': corr,
        'td': td,
        'te': te,
    }

    if not np.isfinite(corr) or corr < 0.95:
        return None, info, False

    cut = agg.index.min()
    agg_full = pd.concat([vbm[vbm.index < cut], agg]).sort_index()
    agg_full = agg_full[~agg_full.index.duplicated(keep='last')]
    agg_full = _ensure_full_period(agg_full, 'AGG', fallback=base_market.ret_df['SPY'] * 0.2)

    agg_anchor = monthly_first_price_from_ticker('AGG')
    agg_point = _build_point_series_from_returns(agg_full, agg_anchor)

    ret_df = base_market.ret_df.copy()
    ret_df['AGG'] = agg_full
    point_df = base_market.point_df.copy()
    point_df['AGG'] = agg_point

    m = MarketData(periods=base_market.periods, points=base_market.points, ret_df=ret_df, point_df=point_df)
    return m, info, True


def bootstrap_1m(twr: np.ndarray, *, n_boot: int, block: int, seed: int, name: str) -> Tuple[Boot1M, np.ndarray, np.ndarray, np.ndarray]:
    twr = np.asarray(twr, dtype=np.float64)
    n = len(twr)
    rng = np.random.default_rng(seed)

    terms = np.empty(n_boot, dtype=np.float64)
    mdds = np.empty(n_boot, dtype=np.float64)
    sharpes = np.empty(n_boot, dtype=np.float64)

    c30 = c35 = c40 = cshort = 0

    t0 = time.time()
    checkpoints = [250_000, 500_000, 750_000, n_boot]

    for i in range(n_boot):
        idx = stationary_bootstrap_indices(n, block, rng)
        twr_s = twr[idx]
        term, mdd = simulate_from_twr(twr_s)
        sh = sharpe_ratio(twr_s)

        terms[i] = term
        mdds[i] = mdd
        sharpes[i] = sh

        if mdd < -0.30:
            c30 += 1
        if mdd < -0.35:
            c35 += 1
        if mdd < -0.40:
            c40 += 1
        if term < 600_000_000.0:
            cshort += 1

        j = i + 1
        if j in checkpoints:
            elapsed = time.time() - t0
            rate = j / elapsed if elapsed > 0 else float('nan')
            eta = (n_boot - j) / rate if np.isfinite(rate) and rate > 0 else float('nan')
            log(f"{name}: {j:,}/{n_boot:,} | elapsed={elapsed/60:.1f}m | rate={rate:,.0f}/s | ETA={eta/60:.1f}m")

    tq = np.quantile(terms, [0.05, 0.25, 0.50, 0.75, 0.95])
    mq = np.quantile(mdds, [0.05, 0.25, 0.50, 0.75, 0.95])
    sh_valid = sharpes[np.isfinite(sharpes)]
    sq = np.quantile(sh_valid, [0.05, 0.25, 0.50, 0.75, 0.95]) if len(sh_valid) else np.array([np.nan]*5)

    x = np.sort(mdds)
    k = max(1, int(len(x) * 0.05))
    cdar95 = float(np.mean(x[:k]))

    out = Boot1M(
        n_boot=n_boot,
        block=block,
        p30=float(c30 / n_boot),
        p35=float(c35 / n_boot),
        p40=float(c40 / n_boot),
        shortfall_600m=float(cshort / n_boot),
        cdar95=cdar95,
        term_q={'p5': float(tq[0]), 'p25': float(tq[1]), 'p50': float(tq[2]), 'p75': float(tq[3]), 'p95': float(tq[4])},
        mdd_q={'p5': float(mq[0]), 'p25': float(mq[1]), 'p50': float(mq[2]), 'p75': float(mq[3]), 'p95': float(mq[4])},
        sharpe_q={'p5': float(sq[0]), 'p25': float(sq[1]), 'p50': float(sq[2]), 'p75': float(sq[3]), 'p95': float(sq[4])},
    )
    return out, terms, mdds, sharpes


def write_port_md(path: Path, title: str, b: Boot1M) -> None:
    p30_ci = prop_ci95(b.p30, b.n_boot)
    p35_ci = prop_ci95(b.p35, b.n_boot)
    p40_ci = prop_ci95(b.p40, b.n_boot)
    s_ci = prop_ci95(b.shortfall_600m, b.n_boot)

    lines = [
        f"# {title}",
        "",
        "## 핵심 통계",
        "",
        "| 지표 | 값 | 95% CI |",
        "|------|-----|--------|",
        f"| P(MDD<-30%) | {fmt_pct(b.p30)} | [{fmt_pct(p30_ci[0])}, {fmt_pct(p30_ci[1])}] |",
        f"| P(MDD<-35%) | {fmt_pct(b.p35)} | [{fmt_pct(p35_ci[0])}, {fmt_pct(p35_ci[1])}] |",
        f"| P(MDD<-40%) | {fmt_pct(b.p40)} | [{fmt_pct(p40_ci[0])}, {fmt_pct(p40_ci[1])}] |",
        f"| CDaR95 | {fmt_pct(b.cdar95)} | — |",
        f"| Shortfall P(T<6억) | {fmt_pct(b.shortfall_600m)} | [{fmt_pct(s_ci[0])}, {fmt_pct(s_ci[1])}] |",
        "",
        "## 분포",
        "",
        "| Quantile | Terminal (KRW) | MDD | Sharpe |",
        "|----------|---------------:|----:|-------:|",
        f"| P5 | {fmt_money(b.term_q['p5'])} | {fmt_pct(b.mdd_q['p5'])} | {fmt_num(b.sharpe_q['p5'])} |",
        f"| P25 | {fmt_money(b.term_q['p25'])} | {fmt_pct(b.mdd_q['p25'])} | {fmt_num(b.sharpe_q['p25'])} |",
        f"| P50 | {fmt_money(b.term_q['p50'])} | {fmt_pct(b.mdd_q['p50'])} | {fmt_num(b.sharpe_q['p50'])} |",
        f"| P75 | {fmt_money(b.term_q['p75'])} | {fmt_pct(b.mdd_q['p75'])} | {fmt_num(b.sharpe_q['p75'])} |",
        f"| P95 | {fmt_money(b.term_q['p95'])} | {fmt_pct(b.mdd_q['p95'])} | {fmt_num(b.sharpe_q['p95'])} |",
        "",
    ]
    path.write_text('\n'.join(lines), encoding='utf-8')


def write_compare_md(
    *,
    v5: Boot1M,
    spy: Boot1M,
    s6040: Boot1M,
    qs50: Boot1M,
    sh_v5: float,
    sh_spy: float,
    sh_6040: float,
    sh_qs50: float,
) -> None:
    lines = [
        "# 4종 비교 — Block Bootstrap 1M (Block=12)",
        "",
        "| 지표 | v5 | SPY | 60/40 | QS50 | Δ(v5-SPY) | Δ(v5-QS50) |",
        "|------|----:|----:|------:|-----:|-----------:|------------:|",
        f"| P(MDD<-30%) | {fmt_pct(v5.p30)} | {fmt_pct(spy.p30)} | {fmt_pct(s6040.p30)} | {fmt_pct(qs50.p30)} | {fmt_pct(v5.p30-spy.p30)} | {fmt_pct(v5.p30-qs50.p30)} |",
        f"| P(MDD<-35%) | {fmt_pct(v5.p35)} | {fmt_pct(spy.p35)} | {fmt_pct(s6040.p35)} | {fmt_pct(qs50.p35)} | {fmt_pct(v5.p35-spy.p35)} | {fmt_pct(v5.p35-qs50.p35)} |",
        f"| P(MDD<-40%) | {fmt_pct(v5.p40)} | {fmt_pct(spy.p40)} | {fmt_pct(s6040.p40)} | {fmt_pct(qs50.p40)} | {fmt_pct(v5.p40-spy.p40)} | {fmt_pct(v5.p40-qs50.p40)} |",
        f"| CDaR95 | {fmt_pct(v5.cdar95)} | {fmt_pct(spy.cdar95)} | {fmt_pct(s6040.cdar95)} | {fmt_pct(qs50.cdar95)} | {fmt_pct(v5.cdar95-spy.cdar95)} | {fmt_pct(v5.cdar95-qs50.cdar95)} |",
        f"| P5 Terminal | {fmt_money(v5.term_q['p5'])} | {fmt_money(spy.term_q['p5'])} | {fmt_money(s6040.term_q['p5'])} | {fmt_money(qs50.term_q['p5'])} | {fmt_money(v5.term_q['p5']-spy.term_q['p5'])} | {fmt_money(v5.term_q['p5']-qs50.term_q['p5'])} |",
        f"| P50 Terminal | {fmt_money(v5.term_q['p50'])} | {fmt_money(spy.term_q['p50'])} | {fmt_money(s6040.term_q['p50'])} | {fmt_money(qs50.term_q['p50'])} | {fmt_money(v5.term_q['p50']-spy.term_q['p50'])} | {fmt_money(v5.term_q['p50']-qs50.term_q['p50'])} |",
        f"| Sharpe P50 | {fmt_num(v5.sharpe_q['p50'])} | {fmt_num(spy.sharpe_q['p50'])} | {fmt_num(s6040.sharpe_q['p50'])} | {fmt_num(qs50.sharpe_q['p50'])} | {fmt_num(v5.sharpe_q['p50']-spy.sharpe_q['p50'])} | {fmt_num(v5.sharpe_q['p50']-qs50.sharpe_q['p50'])} |",
        f"| Sharpe(전구간) | {fmt_num(sh_v5)} | {fmt_num(sh_spy)} | {fmt_num(sh_6040)} | {fmt_num(sh_qs50)} | {fmt_num(sh_v5-sh_spy)} | {fmt_num(sh_v5-sh_qs50)} |",
        f"| Shortfall P(T<6억) | {fmt_pct(v5.shortfall_600m)} | {fmt_pct(spy.shortfall_600m)} | {fmt_pct(s6040.shortfall_600m)} | {fmt_pct(qs50.shortfall_600m)} | {fmt_pct(v5.shortfall_600m-spy.shortfall_600m)} | {fmt_pct(v5.shortfall_600m-qs50.shortfall_600m)} |",
        "",
        "## 50K 기준값 대비 점검",
        "",
        "| 지표 | v5(50K) | v5(1M) | SPY(50K) | SPY(1M) | 60/40(50K) | 60/40(1M) | QS50(50K) | QS50(1M) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        f"| P(MDD<-30%) | 38.32% | {fmt_pct(v5.p30)} | 73.99% | {fmt_pct(spy.p30)} | 8.89% | {fmt_pct(s6040.p30)} | 90.82% | {fmt_pct(qs50.p30)} |",
        f"| P(MDD<-35%) | 19.86% | {fmt_pct(v5.p35)} | 63.43% | {fmt_pct(spy.p35)} | 2.57% | {fmt_pct(s6040.p35)} | 84.63% | {fmt_pct(qs50.p35)} |",
        f"| P(MDD<-40%) | 9.27% | {fmt_pct(v5.p40)} | 50.87% | {fmt_pct(spy.p40)} | 0.74% | {fmt_pct(s6040.p40)} | 72.54% | {fmt_pct(qs50.p40)} |",
        f"| P5 Terminal | 890,000,000 | {fmt_money(v5.term_q['p5'])} | 614,000,000 | {fmt_money(spy.term_q['p5'])} | 728,000,000 | {fmt_money(s6040.term_q['p5'])} | 556,000,000 | {fmt_money(qs50.term_q['p5'])} |",
        f"| P50 Terminal | 2,030,000,000 | {fmt_money(v5.term_q['p50'])} | 1,639,000,000 | {fmt_money(spy.term_q['p50'])} | 1,270,000,000 | {fmt_money(s6040.term_q['p50'])} | 1,902,000,000 | {fmt_money(qs50.term_q['p50'])} |",
        "",
    ]
    OUT_FOUR.write_text('\n'.join(lines), encoding='utf-8')


def sync_to_dev() -> None:
    DEV_PHASE20_1M_DIR.mkdir(parents=True, exist_ok=True)
    (DEV_PHASE20_1M_DIR / 'code').mkdir(parents=True, exist_ok=True)

    for p in [OUT_V5, OUT_SPY, OUT_6040, OUT_QS50, OUT_FOUR]:
        if p.exists():
            shutil.copy2(p, DEV_PHASE20_1M_DIR / p.name)

    if OUT_CODE.exists():
        shutil.copy2(OUT_CODE, DEV_PHASE20_1M_DIR / 'code' / OUT_CODE.name)


def run() -> None:
    PHASE20_1M_DIR.mkdir(parents=True, exist_ok=True)
    (PHASE20_1M_DIR / 'code').mkdir(parents=True, exist_ok=True)

    shutil.copy2(Path(__file__), OUT_CODE)

    t_all = time.time()
    log('Building market data...')
    base_market = build_market_data()

    log('Building 60/40 market with AGG proxy splice...')
    market_6040, agg_info, agg_ok = build_market_with_agg(base_market)
    if not agg_ok or market_6040 is None:
        raise RuntimeError(f"AGG proxy gate failed: corr={agg_info.get('corr')}")

    log('Simulating base paths...')
    v5_res = simulate_portfolio(base_market, V5_WEIGHTS)
    spy_res = simulate_portfolio(base_market, SPY_WEIGHTS)
    qs50_res = simulate_portfolio(base_market, QS50_WEIGHTS)
    s6040_res = simulate_portfolio(market_6040, SIXTY_FORTY_WEIGHTS)

    log('Bootstrap v5 (1,000,000, block=12)')
    v5_b, _, _, _ = bootstrap_1m(v5_res.twr, n_boot=N_BOOT, block=BLOCK, seed=SEED + 10, name='v5')

    log('Bootstrap SPY (1,000,000, block=12)')
    spy_b, _, _, _ = bootstrap_1m(spy_res.twr, n_boot=N_BOOT, block=BLOCK, seed=SEED + 20, name='SPY')

    log('Bootstrap 60/40 (1,000,000, block=12)')
    s6040_b, _, _, _ = bootstrap_1m(s6040_res.twr, n_boot=N_BOOT, block=BLOCK, seed=SEED + 30, name='60/40')

    log('Bootstrap QS50 (1,000,000, block=12)')
    qs50_b, _, _, _ = bootstrap_1m(qs50_res.twr, n_boot=N_BOOT, block=BLOCK, seed=SEED + 40, name='QS50')

    write_port_md(OUT_V5, 'v5 Block Bootstrap 1M (Block=12)', v5_b)
    write_port_md(OUT_SPY, 'SPY Block Bootstrap 1M (Block=12)', spy_b)
    write_port_md(OUT_6040, '60/40 Block Bootstrap 1M (Block=12)', s6040_b)
    write_port_md(OUT_QS50, 'QS50 Block Bootstrap 1M (Block=12)', qs50_b)

    write_compare_md(
        v5=v5_b,
        spy=spy_b,
        s6040=s6040_b,
        qs50=qs50_b,
        sh_v5=float(v5_res.sharpe),
        sh_spy=float(spy_res.sharpe),
        sh_6040=float(s6040_res.sharpe),
        sh_qs50=float(qs50_res.sharpe),
    )

    sync_to_dev()
    elapsed = time.time() - t_all
    log(f'Phase20 1M complete | elapsed={elapsed/60:.1f}m')
    log(f'Output: {PHASE20_1M_DIR}')


if __name__ == '__main__':
    run()
