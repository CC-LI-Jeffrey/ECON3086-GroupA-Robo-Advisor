import pandas as pd
import yfinance as yf  # Member 2 will use this


# Member 2: Data Pipeline & ETF Universe
# Your job: Scrape/download real historical data and define the static ETF universe.

def get_etf_universe():
    """
    Returns the curated list of ETFs allowed in the app.
    """
    # MOCK DATA: Replace with real ETF list, assets classes, and expense ratios.
    # return {
    #     "VOO": {"Asset Class": "US Equity", "Expense Ratio": 0.0003},
    #     "AGG": {"Asset Class": "US Bonds", "Expense Ratio": 0.0003},
    #     "GLD": {"Asset Class": "Commodities", "Expense Ratio": 0.0040},
    #     "VNQ": {"Asset Class": "Real Estate", "Expense Ratio": 0.0012}
    # }
    file_path = "etf.csv"
    universe = {}
    df = pd.read_csv(file_path)
    for _, row in df.iterrows():
        # Get the symbol as the key for dictionary
        symbol = str(row['Symbol']).strip()

        # Store the Asset Class and Expense Ration into Dictionary
        universe[symbol] = {
            "Asset Class": str(row['Asset class']).strip(),
            "Expense Ratio": round(row['Expense ratio'],2)
        }

    print(f"Successfully loaded {len(universe)} of data from the CSV.")
    return universe


def fetch_etf_data(tickers, period: str = "5y"):
    """
    Given a list of tickers, returns a pandas DataFrame of historical adjusted close prices.
    Columns = tickers, Index = Date.
    """
    # MOCK DATA: Member 2 needs to use yfinance to fetch REAL data here!
    # Example: data = yf.download(tickers, period=period)['Adj Close']

    # Get data form yFinance
    df = yf.download(tickers, period=period)

    # Cannot get the data from yFinance
    if df.empty:
        print(f"No data found for tickers {tickers}")
        return pd.DataFrame()

    # Handle Stock Split,
    if 'Adj Close' in df.columns:
        price_df = df['Adj Close']
    else:
        price_df = df['Close']

    # If data missing, fill with the prev/next data
    price_df = price_df.ffill().bfill()

    # If only 1 ETF, change it to dataframe
    if isinstance(price_df, pd.Series):
        price_df = price_df.to_frame()

    return price_df
