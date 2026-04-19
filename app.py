import streamlit as st

from allocation_engine import CATEGORY_TICKER_MAP, allocate_portfolio
from data_engine import fetch_etf_data
from metrics_engine import calculate_cumulative_returns, calculate_metrics
from visuals_engine import plot_allocation, plot_performance, plot_selection_metrics

# Member 1: User Interface & App Architecture
# Builds the Streamlit interface and orchestrates the other engines.

st.set_page_config(page_title="Group A Robo-Advisor", layout="wide")

st.title("📈 Robo-Advisor: Smart Portfolio Allocation")
st.markdown("Welcome! Please fill out your profile below to get a recommended ETF portfolio.")


# --- Cached wrappers ---
# Both yfinance and the AI endpoint are slow + rate-limited. We cache results
# so repeated button presses with the same inputs are instantaneous and we
# avoid burning extra API tokens.

@st.cache_data(ttl=3600, show_spinner=False)
def cached_fetch_etf_data(tickers_tuple: tuple, period: str):
    """Cache yfinance downloads for one hour, keyed by the (sorted) ticker tuple."""
    return fetch_etf_data(list(tickers_tuple), period)


@st.cache_data(ttl=3600, show_spinner=False)
def cached_allocate_portfolio(
    age: int,
    risk_tolerance: str,
    income: float,
    preferred_categories_tuple: tuple,
    horizon: int,
    panic_response: str,
    historical_prices,
):
    """Cache the full allocation (including AI calls) per unique input set."""
    return allocate_portfolio(
        age,
        risk_tolerance,
        income,
        list(preferred_categories_tuple),
        horizon,
        panic_response,
        historical_prices,
    )


def _projected_future_value(
    initial: float, monthly_contribution: float, annual_return: float, years: int
) -> float:
    """Future value with monthly contributions invested at `annual_return` (annual compound).

    Simplification: monthly contributions are summed into a yearly PMT and
    treated as an ordinary annuity, which is accurate enough for a dashboard
    projection and keeps the formula transparent for non-finance users.
    """
    pmt_yearly = monthly_contribution * 12
    fv_initial = initial * (1 + annual_return) ** years
    if annual_return == 0:
        fv_contributions = pmt_yearly * years
    else:
        fv_contributions = pmt_yearly * (((1 + annual_return) ** years - 1) / annual_return)
    return fv_initial + fv_contributions


# --- 1. USER QUESTIONNAIRE ---
st.sidebar.header("User Profile")
age = st.sidebar.slider("Age", min_value=18, max_value=100, value=30)
income = st.sidebar.number_input("Annual Income ($)", min_value=0, value=75000, step=5000)

st.sidebar.header("Financial Context")
init_investment = st.sidebar.number_input("Initial Investment ($)", min_value=1000, value=10000, step=1000)
monthly_add = st.sidebar.number_input("Monthly Contribution ($)", min_value=0, value=500, step=100)

st.sidebar.header("Risk & Goals")
horizon = st.sidebar.slider("Investment Horizon (Years)", 1, 40, 20)

risk_tolerance = st.sidebar.selectbox(
    "Risk Tolerance",
    ["Low", "Medium", "High"],
    index=1,
    help="Think about your financial flexibility and obligations."
)
st.sidebar.caption(
    "🎯 **Guide:**\n"
    "- **Low:** Heavy obligations (e.g., paying a mortgage, children's tuition, tight budget). Cannot afford significant capital loss.\n"
    "- **Medium:** Stable income and manageable debt. Comfortable with standard market fluctuations.\n"
    "- **High:** High disposable income, few dependents. Willing to endure large drops for maximum long-term growth."
)

panic_response = st.sidebar.radio(
    "If your portfolio dropped 20% in one month, what would you do?",
    ["Sell everything to protect what's left", "Do nothing and wait for recovery", "See it as a discount and buy more"]
)

preferred_categories = st.sidebar.multiselect(
    "Preferred ETF Categories",
    [
        "Broad US Equity", "International Equity", "Global Equity", "Small/Mid Cap Equity",
        "Growth Equity", "Value & Dividends", "Technology", "Healthcare", "Financials",
        "Energy", "Industrials", "Real Estate", "Treasury Bonds",
        "Corporate & Broad Bonds", "Commodities", "Crypto"
    ],
    default=["Broad US Equity", "Technology"]
)

if st.sidebar.button("Generate Portfolio"):
    st.divider()

    # --- INPUT VALIDATION ---
    if len(preferred_categories) == 0:
        st.error("⚠️ Please select at least one Preferred ETF Category in the sidebar to proceed.")
        st.stop()

    # --- 2. FETCH CANDIDATE DATA ---
    candidate_tickers = []
    for cat in preferred_categories:
        if cat in CATEGORY_TICKER_MAP:
            candidate_tickers.extend(CATEGORY_TICKER_MAP[cat])

    # Always include the benchmark and the safety-net tickers used by the
    # allocation engine. Sort+dedupe so the cache key is stable regardless of
    # the order categories were selected in.
    fetch_tickers = tuple(sorted(set(candidate_tickers + ["^SPX", "VOO", "BND"])))

    with st.spinner("Analyzing historical market data and consulting the AI advisor..."):
        historical_prices = cached_fetch_etf_data(fetch_tickers, "5y")

        # --- 3. ALLOCATE (Selection & Optimization, with AI commentary) ---
        weights, selection_metrics, ai_analysis = cached_allocate_portfolio(
            age,
            risk_tolerance,
            income,
            tuple(preferred_categories),
            horizon,
            panic_response,
            historical_prices,
        )

    st.subheader("1. Recommended Allocation")

    st.markdown("### The ETF Selection Tournament")
    st.markdown(
        "For each category, we score every candidate ETF on its 5-year "
        "risk-adjusted return (Sharpe Ratio), volatility, max drawdown, and "
        "expense ratio, then ask the AI to pick the ETF that best fits **your** "
        "profile (age, risk tolerance, horizon, panic response). If the AI is "
        "unavailable, we fall back to the highest historical Sharpe Ratio."
    )

    st.plotly_chart(plot_selection_metrics(selection_metrics), use_container_width=True)

    # Per-category AI reasoning. Each entry is tagged with whether the
    # winner came from the AI or the Sharpe fallback so the user can audit.
    ai_reasoning_rows = [
        (cat, info.get("Winner"), info.get("Selected By", ""), info.get("Reasoning", ""))
        for cat, info in selection_metrics.items()
        if info.get("Reasoning")
    ]
    if ai_reasoning_rows:
        with st.expander("🤖 Why each ETF was picked for your profile", expanded=False):
            for cat, winner, source, reasoning in ai_reasoning_rows:
                tag = f" *(via {source})*" if source else ""
                st.markdown(f"- **{cat} → `{winner}`**{tag}: {reasoning}")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.write("Target Weights:")
        for ticker, weight in weights.items():
            st.write(f"**{ticker}:** {weight*100:.1f}%")

    with col2:
        fig_pie = plot_allocation(weights)
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- 4. CALCULATE METRICS FOR DISPLAY ---
    st.subheader("2. Historical Backtest & Metrics")

    port_prices = historical_prices[list(weights.keys())]
    bench_prices = historical_prices[["^SPX"]]

    port_cum_returns = calculate_cumulative_returns(port_prices, weights)
    bench_cum_returns = calculate_cumulative_returns(bench_prices, {"^SPX": 1.0})
    metrics = calculate_metrics(port_cum_returns, bench_cum_returns)

    # Future-value projection now respects the user's monthly contribution
    # via the ordinary-annuity formula in `_projected_future_value`.
    future_val = _projected_future_value(
        initial=init_investment,
        monthly_contribution=monthly_add,
        annual_return=metrics['Portfolio Return'],
        years=horizon,
    )

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Projected Value", f"${future_val:,.0f}", f"In {horizon} yrs (incl. ${monthly_add}/mo)")
    m_col2.metric(
        "Annualized Return",
        f"{metrics['Portfolio Return']*100:.2f}%",
        f"vs {metrics['Benchmark Return']*100:.2f}% Bench",
    )
    m_col3.metric("Sharpe Ratio", f"{metrics['Sharpe Ratio']:.2f}")
    m_col4.metric("Max Drawdown", f"{metrics['Max Drawdown']*100:.2f}%")

    # --- 5. DISPLAY CHARTS ---
    fig_line = plot_performance(port_cum_returns, bench_cum_returns, benchmark_name="S&P 500")
    st.plotly_chart(fig_line, use_container_width=True)

    # --- 6. AI PORTFOLIO ANALYSIS ---
    # Hidden silently when the AI is unavailable so the dashboard still works
    # without an API key configured.
    if ai_analysis:
        st.subheader("3. 🤖 AI Portfolio Analysis")
        st.markdown(ai_analysis)

else:
    st.info("👈 Please enter your details on the sidebar and click 'Generate Portfolio'.")
