"""Local smoke test for the robo-advisor pipeline.

Runs the same call chain `app.py` would, but with synthetic price data so it
does not hit yfinance or the HKBU GenAI API. Verifies:

1. allocation_engine returns the new 3-tuple.
2. weights sum to ~1.0.
3. metrics_engine produces all the keys app.py reads.
4. selection_metrics has the legacy shape visuals_engine relies on.

Exits non-zero on the first failure.
"""

from __future__ import annotations

import sys
import traceback

import numpy as np
import pandas as pd

from allocation_engine import (
    BENCHMARK_TICKER,
    CATEGORY_TICKER_MAP,
    allocate_portfolio,
)
from metrics_engine import calculate_cumulative_returns, calculate_metrics


REQUIRED_METRIC_KEYS = {
    "Portfolio Return",
    "Benchmark Return",
    "Portfolio Volatility",
    "Sharpe Ratio",
    "Max Drawdown",
}


def _make_fake_prices(tickers: list[str], n_days: int = 1260) -> pd.DataFrame:
    """Geometric-Brownian-like price paths with a deterministic seed."""
    rng = np.random.default_rng(42)
    dates = pd.bdate_range(end="2025-01-01", periods=n_days)

    cols = {}
    for i, t in enumerate(tickers):
        # Different drift/vol per ticker so AI/Sharpe pick is non-trivial.
        drift = 0.0002 + 0.00005 * (i % 5)
        vol = 0.008 + 0.002 * (i % 4)
        daily_returns = rng.normal(loc=drift, scale=vol, size=n_days)
        prices = 100.0 * np.exp(np.cumsum(daily_returns))
        cols[t] = prices
    return pd.DataFrame(cols, index=dates)


def _check(name: str, condition: bool, detail: str = "") -> None:
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {name}{(' — ' + detail) if detail else ''}")
    if not condition:
        raise AssertionError(name)


def main() -> int:
    print("=== Robo-Advisor smoke test ===")

    # 1. Build a fake price universe covering a few categories + benchmark + fallbacks.
    preferred = ["Broad US Equity", "Technology", "Treasury Bonds"]
    candidate_tickers: list[str] = []
    for cat in preferred:
        candidate_tickers.extend(CATEGORY_TICKER_MAP[cat])
    universe = list(dict.fromkeys(candidate_tickers + [BENCHMARK_TICKER, "VOO", "BND"]))
    prices = _make_fake_prices(universe)
    print(f"Built fake price frame: {prices.shape[0]} rows × {prices.shape[1]} tickers")

    # 2. Run the full allocation (AI is unavailable → Sharpe fallback path).
    weights, selection_metrics, ai_analysis = allocate_portfolio(
        age=30,
        risk_tolerance="Medium",
        income=75000,
        preferred_categories=preferred,
        horizon=20,
        panic_response="Do nothing and wait for recovery",
        price_df=prices,
    )
    print(f"Got weights={weights}")
    print(f"Got selection_metrics keys={list(selection_metrics.keys())}")
    print(f"AI analysis length={len(ai_analysis)} (expected 0 without API key)")

    # 3. Contract checks.
    _check("returns 3-tuple unpacked OK", True)
    _check("weights non-empty", bool(weights), f"len={len(weights)}")
    _check(
        "weights sum ~ 1.0",
        abs(sum(weights.values()) - 1.0) < 1e-3,
        f"sum={sum(weights.values()):.4f}",
    )
    _check(
        "all weights non-negative",
        all(w >= 0 for w in weights.values()),
    )
    _check(
        "selection_metrics shape compatible with visuals_engine",
        all(
            "Winner" in info and "Competitors" in info
            for info in selection_metrics.values()
        ),
    )
    # Each competitor row must keep the legacy keys.
    for cat, info in selection_metrics.items():
        for ticker, stats in info["Competitors"].items():
            assert {"Sharpe", "Return", "Volatility"}.issubset(stats), (
                f"{cat}/{ticker} missing legacy keys: {stats}"
            )
    _check("competitor rows keep Sharpe/Return/Volatility", True)
    sources = {info.get("Selected By") for info in selection_metrics.values()}
    _check(
        "Selected By tagged with a known source",
        sources.issubset({"AI", "Sharpe fallback"}) and len(sources) >= 1,
        f"sources={sources}",
    )

    # 4. Run metrics_engine on the chosen portfolio + benchmark.
    port_prices = prices[list(weights.keys())]
    bench_prices = prices[[BENCHMARK_TICKER]]
    port_cum = calculate_cumulative_returns(port_prices, weights)
    bench_cum = calculate_cumulative_returns(bench_prices, {BENCHMARK_TICKER: 1.0})
    metrics = calculate_metrics(port_cum, bench_cum)
    print(f"metrics keys={sorted(metrics)}")
    print(
        "metrics:",
        {k: round(metrics[k], 4) for k in sorted(metrics)},
    )

    _check(
        "metrics has all keys app.py reads",
        REQUIRED_METRIC_KEYS.issubset(metrics.keys()),
        f"missing={REQUIRED_METRIC_KEYS - metrics.keys()}",
    )
    _check(
        "Sharpe is finite",
        np.isfinite(metrics["Sharpe Ratio"]),
        f"value={metrics['Sharpe Ratio']}",
    )
    _check(
        "Max Drawdown is non-positive",
        metrics["Max Drawdown"] <= 0,
        f"value={metrics['Max Drawdown']}",
    )
    _check(
        "Portfolio cumulative starts at 1.0",
        abs(port_cum.iloc[0] - 1.0) < 1e-9,
        f"value={port_cum.iloc[0]}",
    )

    print("\nAll smoke checks passed.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
