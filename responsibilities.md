# Group A Responsibilities

This document defines the clear roles and coding responsibilities for each of our 5 team members. Everyone must write code, and work can proceed in parallel because we have defined clear inputs and outputs (interfaces) for each module.

---

### 👤 Member 1: Front-End & App Architecture (`app.py`)
**Role:** UI/UX Developer
**Responsibilities:**
- Build the main Streamlit application layout.
- Create the user questionnaire on the sidebar (Age, Income, Risk Tolerance, Preferred ETF Categories).
- Import the functions from the other 4 members and pass the user's inputs through the pipeline.
- Ensure the app is responsive, handles errors gracefully (e.g., if a user submits without selecting categories), and presents the final dashboard logically.

### 👤 Member 2: Data Pipeline & Universe (`data_engine.py`)
**Role:** Data Engineer
**Responsibilities:**
- Define the static ETF universe with metadata (Ticker, Category, Expense Ratio).
- Use `yfinance` (or another API) to fetch historical daily price data for selected ETFs and the benchmark.
- Data cleaning: Handle missing values, align dates, and calculate adjusted close prices.
- Ensure the output format is returned as a clean `pandas.DataFrame` for the Quant and Strategy engines to use.

### 👤 Member 3: Backtesting & Metrics (`metrics_engine.py`)
**Role:** Quantitative Analyst
**Responsibilities:**
- Write mathematical functions to process the daily price time-series.
- Calculate daily and cumulative returns.
- Compute core financial metrics used in modern portfolio theory:
  - Annualized Return
  - Annualized Volatility
  - Sharpe Ratio (assuming a standard risk-free rate)
  - Maximum Drawdown
  can be more indicator

### 👤 Member 4: Strategy & Allocation (`allocation_engine.py`)
**Role:** Portfolio Strategist
**Responsibilities:**
- Translate the qualitative user profile (Age, Risk, Income, Preferences) into a quantitative asset allocation.
- Write the decision tree or optimization logic that filters the ETF universe based on the user's `preferred_categories`.
- Apply rules of thumb (like `110 - age` for equities) adjusted by their risk tolerance.
- Return the final target weights for the portfolio (must sum exactly to 1.0 or 100%).

### 👤 Member 5: Visualization & Reporting (`visuals_engine.py`)
**Role:** Data Visualization Analyst
**Responsibilities:**
- Build interactive, beautiful charts using libraries like `plotly` or `matplotlib`.
- Create a pie or donut chart to represent the final Target Allocation weights.
- Create a time-series line chart comparing the simulated historical growth of the recommended portfolio vs. the benchmark (e.g., S&P 500).
- Customize charts with proper tooltips, legends, colors, and formatting so they look professional on the Streamlit dashboard.
