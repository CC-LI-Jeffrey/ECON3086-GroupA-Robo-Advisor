#!/usr/bin/env python3
"""
Create sample historical price data in the cache folder for development.

This generates realistic sample data to allow the app to run during development.
FOR YOUR FINAL PROJECT SUBMISSION, you MUST replace these with real data from
Yahoo Finance, Alpha Vantage, or another financial data provider.

Run this to create sample data:
    python create_sample_data.py
"""

import os
import pandas as pd
import numpy as np

CACHE_DIR = os.path.join(os.path.dirname(__file__), "data_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Realistic historical returns and volatilities by asset class
TICKER_PARAMS = {
    # Broad US Equity
    "VOO": {"annual_return": 0.10, "volatility": 0.15, "name": "Vanguard S&P 500 ETF"},
    "IVV": {"annual_return": 0.10, "volatility": 0.15, "name": "iShares Core S&P 500 ETF"},
    "SPY": {"annual_return": 0.10, "volatility": 0.15, "name": "SPDR S&P 500 ETF"},
    "VTI": {"annual_return": 0.10, "volatility": 0.15, "name": "Vanguard Total Stock Market"},
    "RSP": {"annual_return": 0.10, "volatility": 0.16, "name": "Invesco S&P 500 Equal Weight"},
    "SCHX": {"annual_return": 0.10, "volatility": 0.15, "name": "Schwab U.S. Large-Cap ETF"},
    "ITOT": {"annual_return": 0.10, "volatility": 0.15, "name": "iShares Core S&P Total U.S. Stock"},
    "SCHB": {"annual_return": 0.10, "volatility": 0.15, "name": "Schwab U.S. Broad Market ETF"},
    "IWB": {"annual_return": 0.10, "volatility": 0.15, "name": "iShares Russell 1000 ETF"},
    "VV": {"annual_return": 0.10, "volatility": 0.15, "name": "Vanguard Large-Cap ETF"},
    "DIA": {"annual_return": 0.10, "volatility": 0.16, "name": "SPDR Dow Jones Industrial Average"},
    "DFAC": {"annual_return": 0.11, "volatility": 0.16, "name": "Dimensional U.S. Core Equity"},
    "SPYM": {"annual_return": 0.10, "volatility": 0.17, "name": "SPDR Portfolio S&P 1500 Composite"},
    "DYNF": {"annual_return": 0.09, "volatility": 0.14, "name": "Invesco Dynamic Financials ETF"},
    "QUAL": {"annual_return": 0.12, "volatility": 0.18, "name": "iShares MSCI USA Quality Factor"},
    
    # International Equity
    "VXUS": {"annual_return": 0.08, "volatility": 0.18, "name": "Vanguard International Stock ETF"},
    "VEA": {"annual_return": 0.08, "volatility": 0.17, "name": "Vanguard Developed Markets Index"},
    "IEMG": {"annual_return": 0.09, "volatility": 0.20, "name": "iShares MSCI Emerging Markets ETF"},
    "VWO": {"annual_return": 0.09, "volatility": 0.21, "name": "Vanguard Emerging Markets ETF"},
    "EFA": {"annual_return": 0.08, "volatility": 0.17, "name": "iShares MSCI EAFE ETF"},
    "VEU": {"annual_return": 0.08, "volatility": 0.17, "name": "Vanguard FTSE All-World ex-US"},
    
    # Global Equity
    "VT": {"annual_return": 0.09, "volatility": 0.16, "name": "Vanguard Total World Stock ETF"},
    "ACWI": {"annual_return": 0.09, "volatility": 0.16, "name": "iShares MSCI All Country World"},
    
    # Small/Mid Cap Equity
    "IJH": {"annual_return": 0.11, "volatility": 0.19, "name": "iShares S&P Mid-Cap 400 ETF"},
    "IJR": {"annual_return": 0.11, "volatility": 0.20, "name": "iShares S&P SmallCap 600 ETF"},
    "VO": {"annual_return": 0.11, "volatility": 0.19, "name": "Vanguard Mid-Cap ETF"},
    "VB": {"annual_return": 0.11, "volatility": 0.20, "name": "Vanguard Small-Cap ETF"},
    "IWM": {"annual_return": 0.11, "volatility": 0.21, "name": "iShares Russell 2000 ETF"},
    "IWR": {"annual_return": 0.10, "volatility": 0.19, "name": "iShares Russell Mid-Cap ETF"},
    "VBR": {"annual_return": 0.10, "volatility": 0.19, "name": "Vanguard Small-Cap Value Index"},
    
    # Growth Equity
    "VUG": {"annual_return": 0.12, "volatility": 0.18, "name": "Vanguard Growth ETF"},
    "SCHG": {"annual_return": 0.12, "volatility": 0.18, "name": "Schwab U.S. Large-Cap Growth ETF"},
    "VONG": {"annual_return": 0.12, "volatility": 0.19, "name": "Vanguard U.S. Growth Index"},
    "SPYG": {"annual_return": 0.12, "volatility": 0.19, "name": "SPDR Portfolio S&P 500 Growth ETF"},
    "IVW": {"annual_return": 0.12, "volatility": 0.19, "name": "iShares S&P 500 Growth ETF"},
    "IWF": {"annual_return": 0.12, "volatility": 0.19, "name": "iShares Russell 1000 Growth ETF"},
    "MGK": {"annual_return": 0.12, "volatility": 0.19, "name": "Vanguard Mega Cap Growth ETF"},
    
    # Value & Dividends
    "VTV": {"annual_return": 0.09, "volatility": 0.16, "name": "Vanguard Value ETF"},
    "SCHD": {"annual_return": 0.09, "volatility": 0.15, "name": "Schwab U.S. Dividend Equity ETF"},
    "VYM": {"annual_return": 0.08, "volatility": 0.15, "name": "Vanguard High Dividend Yield ETF"},
    "VIG": {"annual_return": 0.09, "volatility": 0.15, "name": "Vanguard Dividend Appreciation ETF"},
    "DGRO": {"annual_return": 0.08, "volatility": 0.15, "name": "iShares Core Dividend Growth ETF"},
    "IWD": {"annual_return": 0.09, "volatility": 0.17, "name": "iShares Russell 1000 Value ETF"},
    "IVE": {"annual_return": 0.09, "volatility": 0.16, "name": "iShares S&P 500 Value ETF"},
    "CGDV": {"annual_return": 0.08, "volatility": 0.15, "name": "Invesco S&P 500 Dividend Aristocrats"},
    "SPYV": {"annual_return": 0.09, "volatility": 0.16, "name": "SPDR Portfolio S&P 500 Value ETF"},
    "JEPI": {"annual_return": 0.07, "volatility": 0.12, "name": "JPMorgan Equity Premium Income ETF"},
    "JEPQ": {"annual_return": 0.06, "volatility": 0.11, "name": "JPMorgan Nasdaq Equity Premium Income"},
    
    # Technology
    "QQQ": {"annual_return": 0.13, "volatility": 0.22, "name": "Invesco QQQ Trust"},
    "VGT": {"annual_return": 0.13, "volatility": 0.21, "name": "Vanguard Information Technology ETF"},
    "XLK": {"annual_return": 0.12, "volatility": 0.20, "name": "Technology Select Sector SPDR"},
    "QQQM": {"annual_return": 0.13, "volatility": 0.22, "name": "Invesco QQQ Trust Mini"},
    "SMH": {"annual_return": 0.12, "volatility": 0.23, "name": "VanEck Semiconductor ETF"},
    "FTEC": {"annual_return": 0.13, "volatility": 0.21, "name": "Fidelity MSCI Information Technology"},
    
    # Healthcare
    "XLV": {"annual_return": 0.10, "volatility": 0.16, "name": "Health Care Select Sector SPDR"},
    "VHT": {"annual_return": 0.10, "volatility": 0.16, "name": "Vanguard Healthcare ETF"},
    
    # Financials
    "XLF": {"annual_return": 0.09, "volatility": 0.18, "name": "Financial Select Sector SPDR"},
    "VFH": {"annual_return": 0.09, "volatility": 0.18, "name": "Vanguard Financials ETF"},
    
    # Energy
    "XLE": {"annual_return": 0.08, "volatility": 0.25, "name": "Energy Select Sector SPDR"},
    "VDE": {"annual_return": 0.08, "volatility": 0.25, "name": "Vanguard Energy ETF"},
    
    # Industrials
    "XLI": {"annual_return": 0.10, "volatility": 0.17, "name": "Industrial Select Sector SPDR"},
    "VIS": {"annual_return": 0.10, "volatility": 0.17, "name": "Vanguard Industrials ETF"},
    
    # Real Estate
    "VNQ": {"annual_return": 0.08, "volatility": 0.19, "name": "Vanguard Real Estate ETF"},
    "SCHH": {"annual_return": 0.08, "volatility": 0.19, "name": "Schwab U.S. REIT ETF"},
    
    # Treasury Bonds
    "SGOV": {"annual_return": 0.03, "volatility": 0.04, "name": "iShares U.S. Treasury Bond ETF"},
    "IEF": {"annual_return": 0.03, "volatility": 0.06, "name": "iShares 7-10 Year Treasury Bond ETF"},
    "BIL": {"annual_return": 0.04, "volatility": 0.01, "name": "SPDR Bloomberg 1-3 Month T-Bill ETF"},
    "TLT": {"annual_return": 0.02, "volatility": 0.10, "name": "iShares 20+ Year Treasury Bond ETF"},
    "GOVT": {"annual_return": 0.03, "volatility": 0.05, "name": "iShares U.S. Treasury Bond ETF"},
    "VGIT": {"annual_return": 0.03, "volatility": 0.05, "name": "Vanguard Intermediate-Term Treasury ETF"},
    "VGSH": {"annual_return": 0.04, "volatility": 0.02, "name": "Vanguard Short-Term Treasury ETF"},
    
    # Corporate & Broad Bonds
    "BND": {"annual_return": 0.04, "volatility": 0.06, "name": "Vanguard Total Bond Market ETF"},
    "AGG": {"annual_return": 0.04, "volatility": 0.06, "name": "iShares Core U.S. Aggregate Bond ETF"},
    "VCIT": {"annual_return": 0.04, "volatility": 0.05, "name": "Vanguard Intermediate-Term Corporate Bond"},
    "BSV": {"annual_return": 0.04, "volatility": 0.03, "name": "Vanguard Short-Term Bond ETF"},
    "MUB": {"annual_return": 0.03, "volatility": 0.05, "name": "iShares National Muni Bond ETF"},
    "VCSH": {"annual_return": 0.04, "volatility": 0.03, "name": "Vanguard Short-Term Corporate Bond ETF"},
    "VTEB": {"annual_return": 0.03, "volatility": 0.05, "name": "Vanguard Tax-Exempt Bond ETF"},
    "MBB": {"annual_return": 0.04, "volatility": 0.04, "name": "iShares MBS ETF"},
    "JPST": {"annual_return": 0.04, "volatility": 0.02, "name": "JPMorgan Ultra-Short Income ETF"},
    "IUSB": {"annual_return": 0.04, "volatility": 0.05, "name": "iShares Broad USD Bond ETF"},
    "LQD": {"annual_return": 0.05, "volatility": 0.07, "name": "iShares Investment Grade Corporate Bond"},
    "BNDX": {"annual_return": 0.03, "volatility": 0.06, "name": "Vanguard Total International Bond ETF"},
    
    # Commodities
    "GLD": {"annual_return": 0.05, "volatility": 0.14, "name": "SPDR Gold Shares"},
    "IAU": {"annual_return": 0.05, "volatility": 0.14, "name": "iShares Gold Trust"},
    "SLV": {"annual_return": 0.05, "volatility": 0.18, "name": "iShares Silver Trust"},
    "GLDM": {"annual_return": 0.05, "volatility": 0.14, "name": "SPDR Gold MiniShares"},
    "GDX": {"annual_return": 0.06, "volatility": 0.25, "name": "VanEck Gold Miners ETF"},
    "DBC": {"annual_return": 0.04, "volatility": 0.16, "name": "Commodities Select Sector SPDR Fund"},
    
    # Crypto
    "IBIT": {"annual_return": 0.20, "volatility": 0.70, "name": "iShares Bitcoin Mini Trust"},
    "FBTC": {"annual_return": 0.20, "volatility": 0.70, "name": "Fidelity Wise Origin Bitcoin Mini Trust"},
    
    # Benchmark
    "^SPX": {"annual_return": 0.10, "volatility": 0.14, "name": "S&P 500 Composite Index"},
}

def generate_sample_prices(ticker: str, params: dict, n_days: int = 1260) -> pd.DataFrame:
    """Generate realistic sample historical prices."""
    
    annual_return = params["annual_return"]
    annual_vol = params["volatility"]
    
    # Daily parameters
    daily_return = annual_return / 252
    daily_std = annual_vol / np.sqrt(252)
    
    # Generate random returns
    np.random.seed(hash(ticker) % 2**32)  # Consistent seed per ticker
    daily_returns = np.random.normal(daily_return, daily_std, n_days)
    
    # Generate prices starting at $100
    prices = 100 * np.cumprod(1 + daily_returns)
    
    # Create date index (trading days, 5 years back)
    dates = pd.bdate_range(end=pd.Timestamp.now(), periods=n_days)
    
    df = pd.DataFrame({ticker: prices}, index=dates)
    return df

def main():
    """Generate and save sample data for all tickers."""
    print(f"Creating sample historical price data...")
    print(f"Cache directory: {CACHE_DIR}\n")
    
    n_days = 1260  # ~5 years of trading days
    
    for i, (ticker, params) in enumerate(sorted(TICKER_PARAMS.items()), 1):
        try:
            df = generate_sample_prices(ticker, params, n_days)
            csv_path = os.path.join(CACHE_DIR, f"{ticker}.csv")
            df.to_csv(csv_path)
            print(f"[{i:2d}/{len(TICKER_PARAMS)}] ✓ {ticker:6s} ({params['name']})")
        except Exception as e:
            print(f"[{i:2d}/{len(TICKER_PARAMS)}] ✗ {ticker:6s} - Error: {e}")
    
    print(f"\n{'='*70}")
    print(f"✅ Sample data created!")
    print(f"   Location: {CACHE_DIR}")
    print(f"   Files: {len(TICKER_PARAMS)} ETF price histories")
    print(f"{'='*70}")
    print("\n⚠️  IMPORTANT FOR PROJECT SUBMISSION:")
    print("   This sample data is for DEVELOPMENT & TESTING ONLY.")
    print("   For your final submission, replace with REAL data from:")
    print("   - Yahoo Finance (yfinance)")
    print("   - Alpha Vantage")
    print("   - IEX Cloud")
    print("   - Or other financial data providers")
    print("\n   Instructions:")
    print("   1. Delete ./data_cache/ folder")
    print("   2. Download real data using a VPN or different network")
    print("   3. Or modify fetch_etf_data() to use alternative data source")

if __name__ == "__main__":
    main()
