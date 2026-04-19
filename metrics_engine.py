import numpy as np
import pandas as pd

# Member 3: Backtesting & Metrics Engine
# Calculates financial statistics from cleaned price data produced by Member 2.

# Number of trading days used for annualization of daily-frequency statistics.
TRADING_DAYS_PER_YEAR = 252

# Default annual risk-free rate used in the Sharpe ratio. Kept as a module-level
# constant so it can be tuned in one place without touching callers.
RISK_FREE_RATE = 0.02


def calculate_cumulative_returns(price_df: pd.DataFrame, weights: dict) -> pd.Series:
    """
    Given a DataFrame of prices (columns = tickers, index = dates) and a dict of
    weights, return the daily cumulative return of the portfolio as a Series
    whose first value is 1.0 (interpret as "$1 grows to $X").
    """
    if price_df is None or price_df.empty:
        return pd.Series(dtype=float, name="Portfolio Cumulative Return")

    if not weights:
        raise ValueError("weights must not be empty.")

    available = [t for t in weights if t in price_df.columns]
    if not available:
        raise ValueError(
            "None of the tickers in `weights` are present in `price_df` columns."
        )

    # Require every selected ticker to have a price on each day; otherwise the
    # missing ticker would silently contribute 0% return for that day while its
    # weight stayed unchanged, distorting the portfolio's exposure.
    prices = price_df[available].sort_index().dropna(how="any")

    w = pd.Series({t: float(weights[t]) for t in available}, dtype=float)
    total = w.sum()
    if total <= 0:
        raise ValueError("Sum of weights must be positive.")
    # Re-normalize so weights of the *available* tickers still sum to 1.
    w = w / total

    daily_returns = prices.pct_change().fillna(0.0)
    portfolio_daily = daily_returns.mul(w, axis=1).sum(axis=1)

    cumulative = (1.0 + portfolio_daily).cumprod()
    cumulative.name = "Portfolio Cumulative Return"
    return cumulative


def calculate_metrics(
    portfolio_cum_returns: pd.Series,
    benchmark_cum_returns: pd.Series,
    risk_free_rate: float = RISK_FREE_RATE,
    trading_days: int = TRADING_DAYS_PER_YEAR,
) -> dict:
    """
    Given cumulative return series for the portfolio and the benchmark, return a
    dictionary of performance metrics used by the Streamlit dashboard.

    The keys `Portfolio Return`, `Benchmark Return`, `Portfolio Volatility`,
    `Sharpe Ratio` and `Max Drawdown` are consumed by `app.py` and MUST remain
    present. Additional keys are provided for richer reporting.
    """
    portfolio = _prepare_cumulative(portfolio_cum_returns)
    benchmark = _prepare_cumulative(benchmark_cum_returns)

    # Align on the common date index so every metric is computed over the
    # same time window for both series.
    common_idx = portfolio.index.intersection(benchmark.index)
    if len(common_idx) < 2:
        raise ValueError(
            "Portfolio and benchmark series do not share enough overlapping dates "
            "to compute metrics."
        )
    portfolio = portfolio.loc[common_idx]
    benchmark = benchmark.loc[common_idx]

    p_ann_return = _annualized_return(portfolio, trading_days)
    b_ann_return = _annualized_return(benchmark, trading_days)

    p_ann_vol = _annualized_volatility(portfolio, trading_days)
    b_ann_vol = _annualized_volatility(benchmark, trading_days)

    p_sharpe = _sharpe_ratio(p_ann_return, p_ann_vol, risk_free_rate)
    b_sharpe = _sharpe_ratio(b_ann_return, b_ann_vol, risk_free_rate)

    p_mdd = _max_drawdown(portfolio)
    b_mdd = _max_drawdown(benchmark)

    return {
        "Portfolio Return": p_ann_return,
        "Benchmark Return": b_ann_return,
        "Portfolio Volatility": p_ann_vol,
        "Benchmark Volatility": b_ann_vol,
        "Sharpe Ratio": p_sharpe,
        "Benchmark Sharpe": b_sharpe,
        "Max Drawdown": p_mdd,
        "Benchmark Max Drawdown": b_mdd,
    }


def _prepare_cumulative(series: pd.Series) -> pd.Series:
    """Validate, sort and clean a cumulative-return series.

    Cumulative returns must stay strictly positive (they represent growth of
    $1). If we encounter non-positive values — usually a sign of corrupt
    upstream data — we log a warning and truncate the series to everything
    BEFORE the first bad point, rather than crashing the whole dashboard.
    """
    if series is None or len(series) == 0:
        raise ValueError("Cumulative return series is empty.")

    s = pd.Series(series).sort_index().dropna()

    bad_mask = s <= 0
    if bad_mask.any():
        first_bad = bad_mask.idxmax()
        print(
            f"[metrics_engine] Non-positive cumulative value at {first_bad}; "
            f"truncating series to data before that point."
        )
        s = s.loc[: first_bad].iloc[:-1]
        if len(s) == 0:
            raise ValueError(
                "Cumulative return series has no usable positive values."
            )
    return s


def _daily_returns_from_cumulative(cumulative: pd.Series) -> pd.Series:
    """Recover daily simple returns from a cumulative return series."""
    return cumulative.pct_change().dropna()


def _annualized_return(cumulative: pd.Series, trading_days: int) -> float:
    """CAGR derived from the first and last points of the cumulative series."""
    total_growth = cumulative.iloc[-1] / cumulative.iloc[0]
    years = (len(cumulative) - 1) / trading_days
    if years <= 0:
        return 0.0
    return float(total_growth ** (1.0 / years) - 1.0)


def _annualized_volatility(cumulative: pd.Series, trading_days: int) -> float:
    daily_returns = _daily_returns_from_cumulative(cumulative)
    if len(daily_returns) < 2:
        return 0.0
    return float(daily_returns.std(ddof=1) * np.sqrt(trading_days))


def _sharpe_ratio(ann_return: float, ann_volatility: float, risk_free_rate: float) -> float:
    if ann_volatility == 0:
        return 0.0
    return float((ann_return - risk_free_rate) / ann_volatility)


def _max_drawdown(cumulative: pd.Series) -> float:
    """Largest peak-to-trough decline of the cumulative-return series."""
    running_max = cumulative.cummax()
    drawdown = cumulative / running_max - 1.0
    return float(drawdown.min())
