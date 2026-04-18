# Member 4: Portfolio Allocation Logic
# Your job: Write the logic that translates a user's profile into specific ETF weights.

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

def allocate_portfolio(age: int, risk_tolerance: str, income: float, preferred_categories: list, horizon: int, panic_response: str) -> dict:
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
