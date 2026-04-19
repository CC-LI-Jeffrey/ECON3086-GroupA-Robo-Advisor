import os

import pandas as pd
import yfinance as yf

# Member 2: Data Pipeline & ETF Universe
# Loads the static ETF universe from etf.csv and pulls historical prices from
# Yahoo Finance.

# Resolve etf.csv relative to this file so the loader works no matter what the
# current working directory is when the app is launched.
_ETF_CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "etf.csv")


def get_etf_universe():
    """Return the curated ETF universe as `{symbol: {"Asset Class", "Expense Ratio"}}`.

    Note: expense ratios are kept at full precision (typical values are
    ~0.0003 to ~0.005, i.e. 3-50 basis points). Aggressive rounding here
    would collapse most rows to 0.0 and starve downstream callers (e.g. the
    AI selector) of the data they need to discriminate.
    """
    universe = {}
    df = pd.read_csv(_ETF_CSV_PATH)
    for _, row in df.iterrows():
        symbol = str(row['Symbol']).strip()
        universe[symbol] = {
            "Asset Class": str(row['Asset class']).strip(),
            "Expense Ratio": float(row['Expense ratio']),
        }

    print(f"Successfully loaded {len(universe)} ETFs from {_ETF_CSV_PATH}.")
    return universe


def fetch_etf_data(tickers, period: str = "5y"):
    """Download historical adjusted close prices from Yahoo Finance.

    Returns a DataFrame whose columns are tickers and index is dates. An
    empty DataFrame is returned (with a console warning) if the download
    yielded no data, so callers can degrade gracefully instead of crashing.
    """
    # `auto_adjust=True` returns split/dividend-adjusted Close prices and is
    # the modern yfinance default; we set it explicitly for cross-version
    # stability. `progress=False` keeps the Streamlit log clean.
    df = yf.download(tickers, period=period, auto_adjust=True, progress=False)

    if df.empty:
        print(f"No data found for tickers {tickers}")
        return pd.DataFrame()

    # With auto_adjust=True the adjusted prices live under "Close". Older
    # yfinance behaviour exposed a separate "Adj Close" column; we still
    # support it for safety.
    if 'Adj Close' in df.columns:
        price_df = df['Adj Close']
    else:
        price_df = df['Close']

    # Forward-fill missing values within each ticker (e.g. occasional missing
    # trading days). Do NOT back-fill: that would fabricate prices before an
    # ETF actually started trading and bias the backtest (look-ahead bias).
    # Instead, drop leading rows where any ticker still has NaN so every
    # ticker starts on a common date for a fair side-by-side comparison.
    price_df = price_df.ffill().dropna(how="any")

    # Normalize the single-ticker case to always be a DataFrame.
    if isinstance(price_df, pd.Series):
        price_df = price_df.to_frame()

    return price_df
