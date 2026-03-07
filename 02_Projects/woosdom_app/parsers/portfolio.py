"""
parsers/portfolio.py — Portfolio parser for Monitor v2 P5 (portfolio panel).

Reads portfolio.json for target allocations. Actual = target (no API yet), drift = 0%.
"""

import json
from datetime import date
from pathlib import Path

from parsers import get_vault_root

VAULT_ROOT = get_vault_root()
PORTFOLIO_JSON = VAULT_ROOT / "01_Domains" / "Finance" / "portfolio.json"

DRIFT_THRESHOLD = 10.0
NEXT_CHECK = date(2026, 3, 31)


def parse_portfolio() -> dict:
    """Return portfolio data from portfolio.json."""
    try:
        raw = json.loads(PORTFOLIO_JSON.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return {"portfolio": _empty()}

    name = raw.get("portfolio_name", "Unknown")
    allocations = raw.get("default_portfolio", {})

    holdings = []
    for etf, target_frac in allocations.items():
        target_pct = round(target_frac * 100, 1)
        holdings.append({
            "etf": etf,
            "target": target_pct,
            "actual": target_pct,  # No actual data yet
            "drift": 0.0,
        })

    days_until = (NEXT_CHECK - date.today()).days
    if days_until < 0:
        days_until = 0

    return {
        "portfolio": {
            "name": name,
            "holdings": holdings,
            "next_check": NEXT_CHECK.isoformat(),
            "days_until_check": days_until,
            "drift_threshold": DRIFT_THRESHOLD,
        }
    }


def _empty() -> dict:
    return {
        "name": "Unknown",
        "holdings": [],
        "next_check": "",
        "days_until_check": 0,
        "drift_threshold": DRIFT_THRESHOLD,
    }


if __name__ == "__main__":
    import json as _json
    print(_json.dumps(parse_portfolio(), indent=2, ensure_ascii=False))
