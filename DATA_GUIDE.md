# ⚠️ Data Source & Network Configuration Guide

## Current Status

Your environment **blocks all access to Yahoo Finance API** at the DNS level. 

### Network Diagnostic Results ✓ CONFIRMED
```
DNS Test Result:    Can't find query.yahooapis.com: No answer
Network:           School/Corporate filtered DNS (172.28.64.10)
Block Type:        DNS-level filtering (most restrictive)
Implications:      Cannot access Yahoo Finance on this network
```

This confirms your network actively prevents ALL connections to Yahoo Finance - even basic DNS queries are blocked.

### Error Messages You're Seeing
```
Failed to get ticker 'VOO' reason: Expecting value: line 1 column 1 (char 0)
```

This JSONDecodeError occurs because the DNS block prevents any response from Yahoo Finance servers.

---

## Temporary Solution (Development)

For **development and testing**, sample data has been generated and cached in `./data_cache/`

### To Use Sample Data Now

1. The sample data is **already created** - you can run the app immediately:
```bash
streamlit run app.py
```

2. The app will load from cached CSV files automatically

### ⚠️ Important: This is NOT Real Data

The sample data is **mathematically realistic** but **not real market data**:
- Based on historical volatility/return patterns
- Good for algorithm testing and development
- **NOT suitable for final project submission**

---

## Solution for Real Data (Course Submission)

### ⭐ FASTEST: Option 0 - Use Your Phone's Hotspot (5 minutes)

**This is the simplest solution:**

```bash
# 1. Enable WiFi hotspot on your iPhone/Android
# 2. Connect your Mac to it
# 3. Run in terminal:
python download_historical_data.py

# 4. Wait 2-5 minutes (downloading 5 years × 92 ETFs)
# 5. Done! You now have real data cached locally
# 6. Switch back to school/work WiFi - app works offline
```

**Why this works:**
- Bypasses your school/corporate network completely
- Uses your phone's cellular data instead of network
- Data is cached afterwards (doesn't need internet again)
- Takes only 5-10 minutes total

---

### Option 1: Use a Different Network (If hotspot unavailable)

Download the real data from a location where Yahoo Finance is accessible:

```bash
# On a computer with unrestricted internet (home, coffee shop, etc.)
python download_historical_data.py
```

This creates real data files in `./data_cache/` that you can then use on your restricted network.

**Why this works:**
- Once cached, the app doesn't need API access
- Only need real data once for the download step
- Then use anywhere (including your restricted network)

---

### Option 2: Use VPN

1. Connect to a VPN service
2. Run the download script:
```bash
python download_historical_data.py
```

**Note:** Since your network uses DNS-level filtering, VPN may or may not work depending on which VPN service you use.

### Option 3: Use Alternative Data Source

Modify [data_engine.py](data_engine.py) to use a different financial data provider:

```python
# Example: Use Alpha Vantage instead
import requests

API_KEY = os.getenv("ALPHA_VANTAGE_KEY")
def fetch_from_alpha_vantage(ticker):
    url = f"https://www.alphavantage.co/query?..."
    # ... implementation
```

**Free alternatives to Yahoo Finance:**
- **Alpha Vantage** - Free tier available
- **Polygon.io** - Free tier available
- **Yahoo Finance CSV export** - Download manually via browser
- **QUANDL** - Financial data API

### Option 4: Manual Download & Cache

1. Visit: https://finance.yahoo.com/quote/VOO/history
2. Download CSV for each ticker you need
3. Place in `./data_cache/TICKER.csv`

Format should match:
```
Date,VOO
2024-04-20,475.23
2024-04-19,474.81
...
```

---

## Diagnosing Network Issues

### Check if Yahoo Finance is Blocked

```bash
# Test 1: DNS resolution
nslookup query.yahooapis.com

# Test 2: HTTP request
curl -v https://query1.finance.yahoo.com

# Test 3: Via Python
python -c "import yfinance; print(yfinance.Ticker('VOO').info)"
```

If any of these fail, your network is blocking Yahoo Finance.

### Common Causes

| Symptom | Likely Cause | Solution |
|---------|---------|---------|
| `curl` fails | Firewall/proxy | Contact IT, try VPN |
| `curl` works but Python fails | Proxy settings | Configure Python proxy |
| All HTTPS fails | VPN/filtering | Try different network |
| Intermittent failures | Rate limiting | Retry with delay |

---

## Project Submission Checklist

Before submitting your final project:

- [ ] **Have real data in `./data_cache/`** (not sample data)
- [ ] Verify data was downloaded from Yahoo Finance, Alpha Vantage, or other financial provider
- [ ] Confirm app runs without errors on your system
- [ ] Document in comments which data source was used
- [ ] If you used sample data for development, **replace before submission**

### To Replace Sample Data With Real Data

```bash
# 1. Delete sample data
rm -rf ./data_cache/

# 2. Download real data (on unrestricted network)
python download_historical_data.py

# 3. Verify
ls -la ./data_cache/ | head -10
```

---

## Technical Details: How Data Caching Works

### App Flow

```
1. User clicks "Generate Portfolio"
   ↓
2. App calls fetch_etf_data(tickers)
   ↓
3. fetch_etf_data() tries:
   a. Load from ./data_cache/TICKER.csv ← WORKS OFFLINE
   b. Download from Yahoo Finance ← Requires internet
   c. Raise error if both fail
   ↓
4. Allocate portfolio & show results
```

### File Format

Each ticker has its own CSV file:

```
./data_cache/
├── VOO.csv
├── QQQ.csv
├── BND.csv
├── ...
└── ^SPX.csv
```

Example file content:
```csv
Date,VOO
2021-04-20,355.12
2021-04-21,356.43
...
2026-04-20,475.23
```

---

## Scripts Reference

### Create Sample Data (Development)
```bash
python create_sample_data.py
```
Creates 92 ETF price histories for testing.

### Download Real Data
```bash
python download_historical_data.py
```
Downloads 5 years of real data from Yahoo Finance for all ETFs in your categories.

### Run the App
```bash
streamlit run app.py
```
Launches the Robo-Advisor at http://localhost:8501

---

## FAQ

**Q: Can I just submit the project with sample data?**
A: Check your course requirements. Most courses require real financial data for accuracy and academic integrity.

**Q: The download script doesn't work for me. What now?**
A: Try:
1. Different network (home, mobile hotspot, café)
2. VPN service
3. Alternative data source (Alpha Vantage, Polygon)
4. Manual CSV download from Yahoo Finance website

**Q: How much data do I need?**
A: The app uses 5 years of trading day data (≈1,260 rows per ticker). You can adjust in the scripts.

**Q: Can I use different tickers?**
A: Yes! Modify `CATEGORY_TICKER_MAP` in [allocation_engine.py](allocation_engine.py) to add/remove ETFs.

**Q: What if the VPN is too slow?**
A: Download data in batches or reduce `period` to "2y" or "1y" in the script.

---

## Support

If you get stuck:

1. **Check error message** - Run `python download_historical_data.py` to see exact errors
2. **Test network** - Use the diagnostic commands above
3. **Review logs** - Streamlit logs are at: [/tmp/streamlit.log](/tmp/streamlit.log)
4. **Alternative approaches** - Consider Alpha Vantage, Polygon, or manual download

---

**Last Updated:** 2026-04-20  
**Status:** App working with sample data. Real data download requires unrestricted internet access.

## Data Source
- **Method**: Online API via yfinance Python library
- **Source**: Yahoo Finance API  
- **Process**: 
  1. download_historical_data.py calls yfinance.download() for each ETF
  2. Fetches real market data online from Yahoo Finance API
  3. Caches to CSV files for offline use and performance
- **Data**: 98 ETFs × 5 years = 1,256 trading days per ticker