import os
import time

import pandas as pd
import yfinance as yf

# Member 2: Data Pipeline & ETF Universe
# Loads the static ETF universe from etf.csv and pulls historical prices from
# Yahoo Finance.

# Resolve etf.csv relative to this file so the loader works no matter what the
# current working directory is when the app is launched.
_ETF_CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "etf.csv")

# Cache directory for historical prices
_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_cache")


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
    
    Attempts to fetch data in this order:
    1. Load from cached CSV files (./data_cache/TICKER.csv)
    2. Download from Yahoo Finance via yfinance
    
    Returns a DataFrame whose columns are tickers and index is dates.
    Raises ValueError if no data is available.
    """
    # Step 1: Try to load from cache first
    cached_data = _load_from_cache(tickers)
    if not cached_data.empty:
        print(f"[fetch_etf_data] Loaded {len(cached_data.columns)} tickers from cache")
        return cached_data
    
    # Step 2: Try yfinance with retries
    print(f"[fetch_etf_data] Cache miss. Attempting to download from Yahoo Finance...")
    max_retries = 2
    for attempt in range(max_retries):
        try:
            df = yf.download(tickers, period=period, auto_adjust=True, progress=False)
            
            if not df.empty:
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

                print(f"[fetch_etf_data] Successfully downloaded {len(price_df.columns)} tickers from Yahoo Finance")
                return price_df
            else:
                print(f"No data found for tickers {tickers}")
                if attempt < max_retries - 1:
                    print(f"Retrying in 2 seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(2)
                    continue
        
        except Exception as e:
            print(f"[fetch_etf_data] Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
    
    # All attempts failed
    raise ValueError(
        f"Could not fetch historical data for {len(tickers)} tickers. "
        f"Yahoo Finance API is unavailable in your environment.\n\n"
        f"To fix this, run the data download script FIRST:\n"
        f"  python download_historical_data.py\n\n"
        f"This will cache real historical data to ./data_cache/ and the app will use it."
    )


def _load_from_cache(tickers: list) -> pd.DataFrame:
    """Attempt to load historical price data from cached CSV files.
    
    Returns an empty DataFrame if any ticker is missing from cache.
    """
    if not os.path.exists(_CACHE_DIR):
        return pd.DataFrame()
    
    cached_tickers = {}
    for ticker in tickers:
        csv_path = os.path.join(_CACHE_DIR, f"{ticker}.csv")
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
                cached_tickers[ticker] = df[ticker]
            except Exception as e:
                print(f"[cache] Failed to load {ticker}: {e}")
                return pd.DataFrame()  # Return empty if any ticker fails
        else:
            # Ticker not in cache
            return pd.DataFrame()
    
    # All tickers found in cache - combine them
    if cached_tickers:
        return pd.DataFrame(cached_tickers)
    return pd.DataFrame()
