# Member 4: Portfolio Allocation Logic
# Your job: Write the logic that translates a user's profile into specific ETF weights.

def allocate_portfolio(age: int, risk_tolerance: str, income: float, preferred_categories: list, horizon: int, panic_response: str) -> dict:
    """
    Takes user inputs (including preferred ETF categories) and returns a dictionary of ETF tickers and their decimal weights.
    Weights MUST sum to 1.0.
    """
    # MOCK DATA: Replace with real business logic!
    # Hint: Use the "110-age" rule for equities, and adjust based on risk_tolerance.
    
    if risk_tolerance == "Low":
        # Safe dummy portfolio
        return {
            "VOO": 0.20,
            "AGG": 0.70,
            "GLD": 0.10
        }
    elif risk_tolerance == "Medium":
        # Balanced dummy portfolio
        return {
            "VOO": 0.60,
            "AGG": 0.30,
            "VNQ": 0.10
        }
    else:  # High
        # Aggressive dummy portfolio
        return {
            "VOO": 0.85,
            "AGG": 0.05,
            "VNQ": 0.10
        }
