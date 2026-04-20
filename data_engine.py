import os

import pandas as pd
import yfinance as yf
from tradingview_screener import Query, Column

# Member 2: Data Pipeline & ETF Universe
# Loads the static ETF universe from etf.csv and pulls historical prices from
# Yahoo Finance.

# Resolve etf.csv relative to this file so the loader works no matter what the
# current working directory is when the app is launched.
_ETF_CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "etf.csv")


def get_etf_universe():
    """
    Retrieves a dictionary of ETFs and their metadata.

    Workflow:
    1. Attempts to query live data from TradingView's 'america' market.
    2. Filters for primary ETF listings on major US exchanges (AMEX, NYSE, NASDAQ).
    3. Maps internal TradingView hex-IDs to human-readable asset classes (Equity, Bonds, etc.).
    4. Provides a fallback to a local CSV file if the API call fails or the library is unavailable.

    Returns:
        dict: A dictionary keyed by ticker symbol, containing Asset Class, Expense Ratio, and ETF Type.
    """
    universe = {}

    ASSET_CLASS_MAP = {
        "c05f85d35d1cd0be6ebb2af4be16e06a": "Equity",  # Stocks
        "b6e443a6c4a8a2e7918c5dbf3d45c796": "Fixed Income",  # Bonds
        "8fe80395f389e29e3ea42210337f0350": "Commodity",  # Commodities
        "1af0389838508d7016a9841eb6273962": "Cryptocurrency",
        "4071518f1736a5a43dae51b47590322f": "Alternative",  # Real Estate/Alt
    }

    try:
        # Querying the American market for ETFs across major exchanges
        q = (Query()
             .set_markets('america')
             .select(
            'name', 'exchange', 'asset_class',
            'expense_ratio', 'is_primary'
        )
             .where(Column("type") == "fund")
             .where(Column("typespecs").has("etf"))
             .where(Column("exchange").isin(["AMEX", "NYSE", "NASDAQ"]))
             .where(Column("is_primary") == True)
             .limit(10000)
             .get_scanner_data())

        count, df = q

        if df.empty:
            raise ValueError("TradingView returned an empty dataset.")

        for _, row in df.iterrows():
            symbol = str(row['name']).strip()

            # 1. Map raw asset class IDs to human-readable strings
            raw_asset_class = str(row['asset_class']) if pd.notnull(row['asset_class']) else ""
            asset_label = ASSET_CLASS_MAP.get(raw_asset_class, "N/A")

            # Skip ETFs without a valid asset class mapping
            if asset_label == "N/A":
                continue

            # 2. Process Expense Ratio (keeping precision for downstream filtering)
            raw_exp = row['expense_ratio']
            exp_ratio = float(raw_exp) if pd.notnull(raw_exp) else 0.0

            universe[symbol] = {
                "Asset Class": asset_label,
                "Expense Ratio": exp_ratio,
            }

        print(f"Successfully loaded {len(universe)} ETFs via API.")
        return universe

    except Exception as e:
        # Fallback mechanism if API fails (e.g., no internet or module error)
        print(f"API Fetch failed ({e}). Switching to local CSV fallback...")

        if not os.path.exists(_ETF_CSV_PATH):
            print(f"Error: Backup file {_ETF_CSV_PATH} not found.")
            return {}

        # Read from the local etf.csv as defined in the original project contract
        df_csv = pd.read_csv(_ETF_CSV_PATH)
        for _, row in df_csv.iterrows():
            symbol = str(row['Symbol']).strip()
            universe[symbol] = {
                "Asset Class": str(row['Asset class']).strip(),
                "Expense Ratio": float(row['Expense ratio']),
            }

        print(f"Loaded {len(universe)} ETFs from local CSV.")
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
