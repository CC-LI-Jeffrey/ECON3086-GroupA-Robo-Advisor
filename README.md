# ECON3086 - Group A: Robo-Advisor Project

Welcome to the Group A Robo-Advisor project! This document outlines our project structure, workload distribution, and our coding standards.

## 🚀 How to Run the App

1. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

## 👥 Workload Distribution & Modules

We have split the project into 5 modular files. Everyone can work on their file simultaneously because we are using **Mock Data**. Do not change the function names or their expected inputs/outputs (the "Interfaces") without telling the group!

*   **Member 1 (UI/UX) -> `app.py`**
    *   Builds the Streamlit interface.
    *   Calls functions from the other modules to display the final app.
*   **Member 2 (Data) -> `data_engine.py`**
    *   Fetches ETF data from Yahoo Finance (`yfinance`).
    *   Filters the ETF universe based on our criteria.
*   **Member 3 (Math/Quant) -> `metrics_engine.py`**
    *   Calculates financial metrics (Sharpe ratio, max drawdown, annualized returns).
*   **Member 4 (Strategy) -> `allocation_engine.py`**
    *   Uses the user's age, income, and risk tolerance to output a dictionary of ETF weights.
*   **Member 5 (Visuals) -> `visuals_engine.py`**
    *   Uses Plotly/Matplotlib to create interactive charts for the Streamlit app.

## 🤝 The "Contract" (Interfaces)

To work in parallel, we agree on inputs and outputs for our main functions. Each `.py` file currently returns **fake (mock) data**. 
Your job is to replace the fake data inside your assigned file with the *real* calculated data using pandas, numpy, etc.

*   `allocate_portfolio(age, risk_tolerance, income, preferred_categories, horizon, panic_response)` returns a dictionary: `{"VOO": 0.6, "BND": 0.4}`
*   `fetch_etf_data(tickers, period)` returns a `pandas.DataFrame` where columns are tickers and the index is dates.
*   `calculate_metrics(portfolio_cum_returns, benchmark_cum_returns)` returns a dictionary of floats: `{"Annualized Return": 0.08, "Sharpe": 1.2, ...}`

Happy coding!
