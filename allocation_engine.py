# Member 4: Portfolio Allocation Logic
# Your job: Write the logic that translates a user's profile into specific ETF weights.

import numpy as np
import pandas as pd

CATEGORY_TICKER_MAP = {
    "Broad US Equity": ["VOO", "IVV", "SPY", "VTI", "RSP", "SCHX", "ITOT", "SCHB", "IWB", "VV", "DIA", "DFAC", "SPYM", "DYNF", "QUAL"],
    "International Equity": ["VXUS", "VEA", "IEMG", "VWO", "EFA", "VEU", "SCHF", "IXUS", "VGK", "SPDW", "IDEV", "EFV"],
    "Global Equity": ["VT", "ACWI"],
    "Small/Mid Cap Equity": ["IJH", "IJR", "VO", "VB", "IWM", "IWR", "VBR"],
    "Growth Equity": ["VUG", "SCHG", "VONG", "SPYG", "IVW", "IWF", "MGK"],
    "Value & Dividends": ["VTV", "SCHD", "VYM", "VIG", "DGRO", "IWD", "IVE", "CGDV", "SPYV", "JEPI", "JEPQ"],
    "Technology": ["QQQ", "VGT", "XLK", "QQQM", "SMH", "FTEC"],
    "Healthcare": ["XLV", "VHT"],
    "Financials": ["XLF", "VFH"],
    "Energy": ["XLE", "VDE"],
    "Industrials": ["XLI", "VIS"],
    "Real Estate": ["VNQ", "SCHH"],
    "Treasury Bonds": ["SGOV", "IEF", "BIL", "TLT", "GOVT", "VGIT", "VGSH"],
    "Corporate & Broad Bonds": ["BND", "AGG", "VCIT", "BSV", "MUB", "VCSH", "VTEB", "MBB", "JPST", "IUSB", "LQD", "BNDX"],
    "Commodities": ["GLD", "IAU", "SLV", "GLDM", "GDX", "DBC"],
    "Crypto": ["IBIT", "FBTC"]
}

def allocate_portfolio(age: int, risk_tolerance: str, income: float, preferred_categories: list, horizon: int, panic_response: str, price_df: pd.DataFrame = None) -> tuple:
    """
    Data-Driven Portfolio Allocation:
    1. Selects the BEST ETF from each category based on historical Sharpe Ratio.
    2. Builds a portfolio using Inverse-Volatility or Markowitz-like logic.
    Returns:
        tuple: (weights_dict, selection_metrics_dict)
    """
    # Fallback to older signature if no data
    if price_df is None or price_df.empty:
        weights = _rule_based_allocation(age, risk_tolerance, income, preferred_categories, horizon, panic_response)
        return weights, {}

    # --- 1. DATA-DRIVEN ETF SELECTION (Intra-Category) ---
    daily_returns = price_df.pct_change().dropna()
    chosen_assets = {}
    selection_metrics = {} # To store the "Why" for Member 5 to visualize
    
    for cat in preferred_categories:
        if cat in CATEGORY_TICKER_MAP:
            candidates = [t for t in CATEGORY_TICKER_MAP[cat] if t in daily_returns.columns]
            if candidates:
                # Pick the one with the highest Sharpe Ratio
                best_ticker = None
                best_sharpe = -np.inf
                cat_metrics = {}
                
                for t in candidates:
                    mean_ret = daily_returns[t].mean() * 252
                    vol = daily_returns[t].std() * np.sqrt(252)
                    sharpe = (mean_ret - 0.02) / vol if vol > 0 else 0
                    
                    # Store metrics for all candidates in this category
                    cat_metrics[t] = {
                        "Sharpe": round(sharpe, 2),
                        "Return": round(mean_ret * 100, 2),
                        "Volatility": round(vol * 100, 2)
                    }
                    
                    if sharpe > best_sharpe:
                        best_sharpe = sharpe
                        best_ticker = t
                        
                if best_ticker:
                    chosen_assets[cat] = best_ticker
                    # Store the winning ticker and the stats of all competitors
                    selection_metrics[cat] = {
                        "Winner": best_ticker,
                        "Competitors": cat_metrics
                    }
                    
    # --- 1.5 CORRELATION PENALTY (Avoid Concentration Risk) ---
    # If two chosen assets are highly correlated (> 0.90), we want to flag it.
    # We will remove the lower-performing one to prevent overlaps (e.g., QQQ and VUG).
    if len(chosen_assets) > 1:
        selected_tickers = list(chosen_assets.values())
        corr_matrix = daily_returns[selected_tickers].corr()
        
        to_drop = set()
        for i in range(len(selected_tickers)):
            for j in range(i + 1, len(selected_tickers)):
                ticker_a = selected_tickers[i]
                ticker_b = selected_tickers[j]
                
                # Check if correlation is extremely high
                if corr_matrix.loc[ticker_a, ticker_b] > 0.90:
                    # They are too similar. Keep the one with the higher Sharpe Ratio.
                    sharpe_a = (daily_returns[ticker_a].mean() * 252 - 0.02) / (daily_returns[ticker_a].std() * np.sqrt(252))
                    sharpe_b = (daily_returns[ticker_b].mean() * 252 - 0.02) / (daily_returns[ticker_b].std() * np.sqrt(252))
                    
                    if sharpe_a > sharpe_b:
                        to_drop.add(ticker_b)
                        print(f"Correlation Flag: Dropped {ticker_b} in favor of {ticker_a} (Corr: {corr_matrix.loc[ticker_a, ticker_b]:.2f})")
                    else:
                        to_drop.add(ticker_a)
                        print(f"Correlation Flag: Dropped {ticker_a} in favor of {ticker_b} (Corr: {corr_matrix.loc[ticker_a, ticker_b]:.2f})")
        
        # Remove the correlated losers from the chosen assets dictionary
        chosen_assets = {cat: ticker for cat, ticker in chosen_assets.items() if ticker not in to_drop}


    # Ensure we actually picked *something*
    if not chosen_assets:
        return {"VOO": 0.60, "BND": 0.40}

    # --- 2. DATA-DRIVEN WEIGHT OPTIMIZATION (Inverse Volatility / Risk Parity) ---
    # Determine the risk limits based on user profile
    # The classic 110 - Age rule for baseline equity percentage
    base_equity_pct = (110 - age) / 100.0
    if risk_tolerance == "Low": base_equity_pct -= 0.15
    elif risk_tolerance == "High": base_equity_pct += 0.10
    if horizon < 5: base_equity_pct -= 0.20
    elif horizon > 20: base_equity_pct += 0.10
    if "Sell everything" in panic_response: base_equity_pct = min(base_equity_pct, 0.50)
    
    equity_pct = max(0.10, min(0.95, base_equity_pct))
    bond_pct = 1.0 - equity_pct
    
    core_bonds = ["Treasury Bonds", "Corporate & Broad Bonds"]
    bond_tickers = [t for cat, t in chosen_assets.items() if cat in core_bonds]
    equity_tickers = [t for cat, t in chosen_assets.items() if cat not in core_bonds]

    portfolio = {}

    # Weighting the Bond portion
    if bond_tickers:
        vols = {t: daily_returns[t].std() for t in bond_tickers}
        inv_vol_sum = sum(1.0 / v for v in vols.values() if v > 0)
        for t, v in vols.items():
            if v > 0:
                portfolio[t] = ((1.0 / v) / inv_vol_sum) * bond_pct
            else:
                portfolio[t] = bond_pct / len(bond_tickers)
    else:
        # If no bonds selected but bonds are needed, force BND
        portfolio["BND"] = bond_pct

    # Weighting the Equity portion
    if equity_tickers:
        vols = {t: daily_returns[t].std() for t in equity_tickers}
        inv_vol_sum = sum(1.0 / v for v in vols.values() if v > 0)
        for t, v in vols.items():
            if v > 0:
                portfolio[t] = ((1.0 / v) / inv_vol_sum) * equity_pct
            else:
                portfolio[t] = equity_pct / len(equity_tickers)
    else:
        # If no equities selected but equities are needed, force VOO
        portfolio["VOO"] = equity_pct

    # Return normalized and rounded dictionary, plus the selection metrics
    final_weights = {k: round(v, 4) for k, v in portfolio.items() if v > 0}
    return final_weights, selection_metrics

def _rule_based_allocation(age: int, risk_tolerance: str, income: float, preferred_categories: list, horizon: int, panic_response: str) -> dict:
    """
    Takes user inputs (including preferred ETF categories) and returns a dictionary of ETF tickers and their decimal weights.
    Weights MUST sum to 1.0.
    """
    # --- 1. ESTABLISH BASE EQUITY/BOND SPLIT ---
    # The classic 110 - Age rule for baseline equity percentage
    base_equity_pct = (110 - age) / 100.0
    
    # Adjust based on Risk Tolerance
    if risk_tolerance == "Low":
        base_equity_pct -= 0.15
    elif risk_tolerance == "High":
        base_equity_pct += 0.10
        
    # Adjust based on Investment Horizon (Longer horizon = higher capacity for risk)
    if horizon < 5:
        base_equity_pct -= 0.20
    elif horizon > 20:
        base_equity_pct += 0.10
        
    # Adjust based on Behavioral Panic Response (The Ultimate Override)
    if "Sell everything" in panic_response:
        # Cap equity at 50% if they are prone to panic selling
        base_equity_pct = min(base_equity_pct, 0.50)
        
    # Ensure equity percentage stays within sane bounds (10% to 95%)
    equity_pct = max(0.10, min(0.95, base_equity_pct))
    bond_pct = 1.0 - equity_pct

    # --- 2. CATEGORIZE USER PREFERENCES ---
    core_equity = ["Broad US Equity", "Global Equity"]
    core_bonds = ["Treasury Bonds", "Corporate & Broad Bonds"]
    
    # Fallback if somehow nothing valid is selected (Handled by UI now, but safe to keep)
    if not preferred_categories:
        return {"VOO": equity_pct, "BND": bond_pct}

    # Extract exactly 1 ticker per chosen category
    chosen_assets = {}
    for cat in preferred_categories:
        if cat in CATEGORY_TICKER_MAP and CATEGORY_TICKER_MAP[cat]:
            chosen_assets[cat] = CATEGORY_TICKER_MAP[cat][0]

    # --- 3. ALLOCATE SATELLITES & TILTS (From the Equity Bucket) ---
    portfolio = {}
    remaining_equity = equity_pct
    
    # Process high-risk satellites first (Strict Caps)
    if "Crypto" in chosen_assets:
        # Cap crypto at 5% of total portfolio, drawn from equity
        crypto_weight = min(0.05, remaining_equity)
        portfolio[chosen_assets["Crypto"]] = crypto_weight
        remaining_equity -= crypto_weight
        
    # Process sector tilts
    tilt_categories = [c for c in chosen_assets if c not in core_equity and c not in core_bonds and c != "Crypto"]
    if tilt_categories:
        # Give each tilt 10% of the eq bucket, or whatever is left
        tilt_weight_each = min(0.10 * equity_pct, remaining_equity / len(tilt_categories))
        for cat in tilt_categories:
            portfolio[chosen_assets[cat]] = tilt_weight_each
            remaining_equity -= tilt_weight_each

    # --- 4. DISTRIBUTE REMAINDER TO CORE ---
    # Put all remaining equity into a core equity fund (Default VOO if none selected)
    core_eq_cats_selected = [c for c in chosen_assets if c in core_equity]
    core_eq_ticker = chosen_assets[core_eq_cats_selected[0]] if core_eq_cats_selected else "VOO"
    
    if core_eq_ticker in portfolio:
        portfolio[core_eq_ticker] += remaining_equity
    else:
        portfolio[core_eq_ticker] = remaining_equity

    # Put all bond allocation into a core bond fund (Default BND if none selected)
    core_bond_cats_selected = [c for c in chosen_assets if c in core_bonds]
    core_bond_ticker = chosen_assets[core_bond_cats_selected[0]] if core_bond_cats_selected else "BND"
    
    portfolio[core_bond_ticker] = bond_pct

    # Clean up any zero weights and return
    return {k: round(v, 4) for k, v in portfolio.items() if v > 0}
