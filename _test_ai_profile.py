"""Verify the AI tailors per-category picks to the user's questionnaire.

We feed the SAME candidate metrics to ai_pick_best_in_category twice with
two opposite user profiles (Conservative vs Aggressive) and print which
ticker / reason the AI returns. If the integration works as intended, the
two profiles should plausibly choose differently — or at least cite the
profile in the reasoning.
"""

from ai import ai_pick_best_in_category, is_available


CANDIDATES = {
    # Stable, low-fee blue chip
    "VOO": {
        "Annualized Return": 0.13,
        "Volatility": 0.17,
        "Sharpe Ratio": 0.65,
        "Max Drawdown": -0.24,
        "Expense Ratio": 0.0003,
    },
    # Higher returns, but pricier and deeper drawdowns
    "DYNF": {
        "Annualized Return": 0.18,
        "Volatility": 0.22,
        "Sharpe Ratio": 0.72,
        "Max Drawdown": -0.31,
        "Expense Ratio": 0.0030,
    },
    # Lowest vol & drawdown, modest return
    "RSP": {
        "Annualized Return": 0.10,
        "Volatility": 0.14,
        "Sharpe Ratio": 0.57,
        "Max Drawdown": -0.18,
        "Expense Ratio": 0.0020,
    },
}

CONSERVATIVE = {
    "age": 60,
    "income": 50000,
    "risk_tolerance": "Low",
    "horizon": 5,
    "panic_response": "Sell everything to protect what's left",
    "preferred_categories": ["Broad US Equity"],
}

AGGRESSIVE = {
    "age": 25,
    "income": 120000,
    "risk_tolerance": "High",
    "horizon": 30,
    "panic_response": "See it as a discount and buy more",
    "preferred_categories": ["Broad US Equity"],
}


def main() -> None:
    if not is_available():
        print("HKBU_AI_API_KEY not set. Cannot run live profile test.")
        return

    for label, profile in [("CONSERVATIVE", CONSERVATIVE), ("AGGRESSIVE", AGGRESSIVE)]:
        print(f"\n=== {label} user ===")
        print(f"profile = {profile}")
        result = ai_pick_best_in_category("Broad US Equity", CANDIDATES, profile)
        print(f"  AI picked: {result.get('ticker')}")
        print(f"  Reason   : {result.get('reasoning')}")


if __name__ == "__main__":
    main()
