#!/usr/bin/env python3
"""
Download historical price data for all ETFs in CATEGORY_TICKER_MAP.
Saves to CSV cache files so the app can use them even if yfinance API is unavailable.

Run this script ONCE (or periodically to update data):
    python download_historical_data.py

This will create .csv files in the ./data_cache/ folder.
"""

import os
import sys
import pandas as pd
import yfinance as yf
from allocation_engine import CATEGORY_TICKER_MAP

# Create cache directory
CACHE_DIR = os.path.join(os.path.dirname(__file__), "data_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def download_all_ticker_data(period: str = "5y"):
    """Download historical data for all tickers in CATEGORY_TICKER_MAP."""
    
    # Collect all unique tickers
    all_tickers = set()
    for tickers in CATEGORY_TICKER_MAP.values():
        all_tickers.update(tickers)
    
    # Add benchmark
    all_tickers.add("^SPX")
    
    all_tickers = sorted(list(all_tickers))
    
    print(f"Downloading historical data for {len(all_tickers)} tickers...")
    print(f"Period: {period}")
    print(f"Cache directory: {CACHE_DIR}")
    print()
    
    successful = 0
    failed = 0
    failed_tickers = []
    
    # Download individually for better error handling
    for i, ticker in enumerate(all_tickers):
        print(f"[{i+1}/{len(all_tickers)}] Downloading {ticker}...", end=" ", flush=True)
        
        try:
            df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
            
            if df.empty:
                print(f"⚠️  No data returned")
                failed += 1
                failed_tickers.append(ticker)
                continue
            
            # Extract Close prices
            if 'Close' in df.columns:
                prices = df['Close']
            elif 'Adj Close' in df.columns:
                prices = df['Adj Close']
            else:
                print(f"⚠️  No price column found")
                failed += 1
                failed_tickers.append(ticker)
                continue
            
            # Convert to DataFrame
            if not isinstance(prices, pd.DataFrame):
                prices = prices.to_frame()
            
            # Forward fill and drop NaN
            prices = prices.ffill().dropna()
            
            # Save to CSV
            csv_path = os.path.join(CACHE_DIR, f"{ticker}.csv")
            prices.to_csv(csv_path)
            print(f"✓ ({len(prices)} rows)")
            successful += 1
        
        except Exception as e:
            print(f"✗ Error: {str(e)[:50]}")
            failed += 1
            failed_tickers.append(ticker)
    
    print()
    print("=" * 60)
    print(f"✅ Download complete!")
    print(f"   Successful: {successful}/{len(all_tickers)}")
    if failed > 0:
        print(f"   Failed: {failed}/{len(all_tickers)}")
        print(f"   Failed tickers: {', '.join(failed_tickers)}")
    print(f"📂 Data cached in: {CACHE_DIR}")
    print("=" * 60)
    print()
    
    if successful == 0:
        print("⚠️  WARNING: No data was downloaded!")
        print("   Your network may be blocking Yahoo Finance API.")
        print("   Try:")
        print("     1. Using a VPN")
        print("     2. Downloading from a different network")
        print("     3. Checking your firewall/proxy settings")
        sys.exit(1)
    
    print("You can now run the Streamlit app. It will use this cached data.")

if __name__ == "__main__":
    download_all_ticker_data(period="5y")

