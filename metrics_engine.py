import pandas as pd
import numpy as np

# Member 3: Backtesting & Metrics Engine
# Your job: Calculate all the financial statistics.

def calculate_cumulative_returns(price_df: pd.DataFrame, weights: dict) -> pd.Series:
    """
    Given a DataFrame of prices and a dictionary of weights,
    calculate the daily cumulative return of the portfolio.
    """
    # MOCK DATA: Replace with real math!
    # Hint: Calculate daily pct_change(), multiply by weights, sum, then calculate cumulative product.
    
    dates = price_df.index
    mock_cum_returns = np.linspace(1.0, 1.5, len(dates)) # Fake smooth upward trend
    return pd.Series(mock_cum_returns, index=dates)

def calculate_metrics(portfolio_cum_returns: pd.Series, benchmark_cum_returns: pd.Series) -> dict:
    """
    Given cumulative returns for the portfolio and benchmark, calculate key performance metrics.
    """
    # MOCK DATA: Replace with real math (annualized return, volatility, max drawdown, sharpe).
    
    return {
        "Portfolio Return": 0.085,      # 8.5%
        "Benchmark Return": 0.072,      # 7.2%
        "Portfolio Volatility": 0.12,   # 12.0%
        "Sharpe Ratio": 1.15,
        "Max Drawdown": -0.15           # -15%
    }
