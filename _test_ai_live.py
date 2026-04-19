"""Live AI smoke test: requires HKBU_AI_API_KEY in .env.

Hits the HKBU GenAI endpoint with a tiny ETF-comparison prompt and prints
the parsed result. Use this after setting your API key to confirm the AI
integration works end-to-end before running the full Streamlit app.
"""

from ai import ai_analyze_portfolio, ai_pick_best_in_category, is_available


def main() -> None:
    if not is_available():
        print("HKBU_AI_API_KEY is not set. Edit .env and try again.")
        return

    print("Testing ai_pick_best_in_category ...")
    pick = ai_pick_best_in_category(
        "Broad US Equity",
        {
            "VOO": {
                "Annualized Return": 0.13,
                "Volatility": 0.17,
                "Sharpe Ratio": 0.65,
                "Max Drawdown": -0.24,
                "Expense Ratio": 0.0003,
            },
            "DYNF": {
                "Annualized Return": 0.16,
                "Volatility": 0.21,
                "Sharpe Ratio": 0.66,
                "Max Drawdown": -0.28,
                "Expense Ratio": 0.0030,
            },
        },
    )
    print(f"  -> {pick}\n")

    print("Testing ai_analyze_portfolio ...")
    analysis = ai_analyze_portfolio(
        user_profile={
            "age": 30,
            "income": 75000,
            "risk_tolerance": "Medium",
            "horizon": 20,
            "panic_response": "Do nothing and wait for recovery",
            "preferred_categories": ["Broad US Equity", "Technology", "Treasury Bonds"],
        },
        weights={"VOO": 0.50, "QQQ": 0.30, "TLT": 0.20},
    )
    print("---ANALYSIS---")
    print(analysis or "(empty)")


if __name__ == "__main__":
    main()
