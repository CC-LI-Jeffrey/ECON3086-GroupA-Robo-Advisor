# Member 4: Portfolio Allocation Logic
# Your job: Write the logic that translates a user's profile into specific ETF weights.

import numpy as np
import pandas as pd

from ai import ai_analyze_portfolio, ai_pick_best_in_category
from metrics_engine import (
    RISK_FREE_RATE,
    calculate_cumulative_returns,
    calculate_metrics,
)

# Benchmark used when computing per-ticker `calculate_metrics` for the AI.
# Must be available in `price_df` (app.py already fetches it alongside the
# candidate tickers).
BENCHMARK_TICKER = "^SPX"

# Cache the ETF universe (expense ratios etc.) at import time. The CSV is
# small and the function is idempotent, so loading once per process is fine.
# Wrapped in try/except so missing/corrupt CSV does not break allocation.
try:
    from data_engine import get_etf_universe

    _ETF_UNIVERSE = get_etf_universe()
except Exception as _exc:  # noqa: BLE001
    print(f"[allocation_engine] Could not load ETF universe: {_exc}")
    _ETF_UNIVERSE = {}

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
    1. Selects the BEST ETF from each category. The AI is asked to pick using
       per-ticker `calculate_metrics` output + expense ratio; if the AI is
       unavailable or returns an invalid answer, we fall back to the highest
       historical Sharpe Ratio.
    2. Builds a portfolio using Inverse-Volatility / Risk-Parity-like logic.
    3. Asks the AI to write a short qualitative analysis of the final
       portfolio given the user's full questionnaire response.
    Returns:
        tuple: (weights_dict, selection_metrics_dict, ai_analysis_text)
    """
    # Fallback to older signature if no data
    if price_df is None or price_df.empty:
        weights = _rule_based_allocation(age, risk_tolerance, income, preferred_categories, horizon, panic_response)
        return weights, {}, ""

    # Pre-compute the benchmark cumulative once so per-ticker metrics share
    # a consistent baseline.
    bench_cum = None
    if BENCHMARK_TICKER in price_df.columns:
        try:
            bench_cum = calculate_cumulative_returns(
                price_df[[BENCHMARK_TICKER]], {BENCHMARK_TICKER: 1.0}
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[allocation_engine] Benchmark cumulative failed: {exc}")
            bench_cum = None

    # Build the user profile up-front so the AI can tailor BOTH the per-
    # category pick and the final analysis to this specific investor.
    user_profile = {
        "age": age,
        "income": income,
        "risk_tolerance": risk_tolerance,
        "horizon": horizon,
        "panic_response": panic_response,
        "preferred_categories": preferred_categories,
    }

    # --- 1. DATA-DRIVEN ETF SELECTION (Intra-Category) ---
    daily_returns = price_df.pct_change().dropna()
    chosen_assets = {}
    selection_metrics = {} # To store the "Why" for Member 5 to visualize

    for cat in preferred_categories:
        if cat not in CATEGORY_TICKER_MAP:
            continue
        candidates = [t for t in CATEGORY_TICKER_MAP[cat] if t in daily_returns.columns]
        if not candidates:
            continue

        # `cat_metrics` keeps the legacy keys (Sharpe / Return / Volatility) so
        # `visuals_engine.plot_selection_metrics` keeps working unchanged.
        # `ai_payload` carries a richer, AI-friendly view including expense ratio.
        cat_metrics = {}
        ai_payload = {}
        best_ticker_by_sharpe = None
        best_sharpe = -np.inf

        for t in candidates:
            # Try the unified metrics_engine path first so the AI sees the
            # exact same numbers the dashboard would later report.
            ticker_metrics = None
            if bench_cum is not None:
                try:
                    cum_t = calculate_cumulative_returns(price_df[[t]], {t: 1.0})
                    ticker_metrics = calculate_metrics(cum_t, bench_cum)
                except Exception as exc:  # noqa: BLE001
                    print(f"[allocation_engine] metrics for {t} failed: {exc}")
                    ticker_metrics = None

            if ticker_metrics is not None:
                ann_ret = float(ticker_metrics.get("Portfolio Return", 0.0))
                ann_vol = float(ticker_metrics.get("Portfolio Volatility", 0.0))
                sharpe = float(ticker_metrics.get("Sharpe Ratio", 0.0))
                mdd = float(ticker_metrics.get("Max Drawdown", 0.0))
            else:
                # Lightweight fallback (mean / std on daily returns).
                ann_ret = float(daily_returns[t].mean() * 252)
                ann_vol = float(daily_returns[t].std() * np.sqrt(252))
                sharpe = (ann_ret - RISK_FREE_RATE) / ann_vol if ann_vol > 0 else 0.0
                mdd = 0.0

            expense_ratio = (
                _ETF_UNIVERSE.get(t, {}).get("Expense Ratio")
                if _ETF_UNIVERSE
                else None
            )

            cat_metrics[t] = {
                "Sharpe": round(sharpe, 2),
                "Return": round(ann_ret * 100, 2),
                "Volatility": round(ann_vol * 100, 2),
            }
            ai_payload[t] = {
                "Annualized Return": round(ann_ret, 4),
                "Volatility": round(ann_vol, 4),
                "Sharpe Ratio": round(sharpe, 2),
                "Max Drawdown": round(mdd, 4),
                "Expense Ratio": expense_ratio,
            }

            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_ticker_by_sharpe = t

        if not cat_metrics:
            continue

        # AI tournament: ask AI to pick using metrics + expense ratio +
        # the user's questionnaire (so the choice is tailored, not generic).
        ai_pick = ai_pick_best_in_category(cat, ai_payload, user_profile)
        if ai_pick.get("ticker") in cat_metrics:
            best_ticker = ai_pick["ticker"]
            reasoning = ai_pick.get("reasoning", "")
            source = "AI"
        else:
            best_ticker = best_ticker_by_sharpe
            reasoning = "Selected by highest historical Sharpe Ratio (AI unavailable or invalid response)."
            source = "Sharpe fallback"

        chosen_assets[cat] = best_ticker
        selection_metrics[cat] = {
            "Winner": best_ticker,
            "Competitors": cat_metrics,
            "Reasoning": reasoning,
            "Selected By": source,
        }
                    
    # --- 1.5 CORRELATION PENALTY (Avoid Concentration Risk) ---
    # If two chosen assets are highly correlated (> 0.90), keep the one with
    # the higher Sharpe Ratio. We compare pairs in order of HIGHEST correlation
    # first and skip pairs whose tickers were already dropped, so a ticker that
    # was eliminated earlier can never push another (innocent) ticker out.
    if len(chosen_assets) > 1:
        selected_tickers = list(chosen_assets.values())
        corr_matrix = daily_returns[selected_tickers].corr()

        # Collect every (corr, a, b) above threshold, sorted desc so we
        # resolve the most-similar pairs first.
        candidate_pairs = []
        for i in range(len(selected_tickers)):
            for j in range(i + 1, len(selected_tickers)):
                a, b = selected_tickers[i], selected_tickers[j]
                c = corr_matrix.loc[a, b]
                if c > 0.90:
                    candidate_pairs.append((c, a, b))
        candidate_pairs.sort(key=lambda x: x[0], reverse=True)

        to_drop = set()
        for c, ticker_a, ticker_b in candidate_pairs:
            # Skip pairs where one side was already dropped; we never want a
            # dead ticker to influence further eliminations.
            if ticker_a in to_drop or ticker_b in to_drop:
                continue

            sharpe_a = (
                (daily_returns[ticker_a].mean() * 252 - RISK_FREE_RATE)
                / (daily_returns[ticker_a].std() * np.sqrt(252))
            )
            sharpe_b = (
                (daily_returns[ticker_b].mean() * 252 - RISK_FREE_RATE)
                / (daily_returns[ticker_b].std() * np.sqrt(252))
            )

            loser, winner = (
                (ticker_b, ticker_a) if sharpe_a > sharpe_b else (ticker_a, ticker_b)
            )
            to_drop.add(loser)
            print(
                f"Correlation Flag: Dropped {loser} in favor of {winner} "
                f"(Corr: {c:.2f})"
            )

        chosen_assets = {
            cat: ticker for cat, ticker in chosen_assets.items() if ticker not in to_drop
        }


    # Ensure we actually picked *something*
    if not chosen_assets:
        fallback = {"VOO": 0.60, "BND": 0.40}
        return fallback, selection_metrics, ""

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

    # --- 3. AI-DRIVEN PORTFOLIO ANALYSIS ---
    # Reuse the same user_profile dict that was passed to per-category picks
    # so the qualitative write-up is consistent with the selection rationale.
    try:
        ai_analysis = ai_analyze_portfolio(user_profile, final_weights)
    except Exception as exc:  # noqa: BLE001 — never let AI break the pipeline
        print(f"[allocation_engine] AI portfolio analysis failed: {exc}")
        ai_analysis = ""

    return final_weights, selection_metrics, ai_analysis

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
