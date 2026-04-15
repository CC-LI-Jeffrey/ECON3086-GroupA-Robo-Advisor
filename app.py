import streamlit as st
from allocation_engine import allocate_portfolio
from data_engine import get_etf_universe, fetch_etf_data
from metrics_engine import calculate_metrics, calculate_cumulative_returns
from visuals_engine import plot_allocation, plot_performance

# Member 1: User Interface & App Architecture
# Your job: Build a beautiful Streamlit app that collects user data and displays the results.

st.set_page_config(page_title="Group A Robo-Advisor", layout="wide")

st.title("📈 Robo-Advisor: Smart Portfolio Allocation")
st.markdown("Welcome! Please fill out your profile below to get a recommended ETF portfolio.")

# --- 1. USER QUESTIONNAIRE ---
st.sidebar.header("User Profile")
age = st.sidebar.slider("Age", min_value=18, max_value=100, value=30)
income = st.sidebar.number_input("Annual Income ($)", min_value=0, value=75000, step=5000)
risk_tolerance = st.sidebar.selectbox("Risk Tolerance", ["Low", "Medium", "High"], index=1)
preferred_categories = st.sidebar.multiselect(
    "Preferred ETF Categories", 
    ["Technology", "Healthcare", "Real Estate", "Bonds", "Commodities", "Broad Market"],
    default=["Broad Market", "Technology"]
)

if st.sidebar.button("Generate Portfolio"):
    st.divider()

    # --- 2. GET ALLOCATION ---
    # Call Member 4's function
    weights = allocate_portfolio(age, risk_tolerance, income, preferred_categories)
    
    st.subheader("1. Recommended Allocation")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("Target Weights:")
        for ticker, weight in weights.items():
            st.write(f"**{ticker}:** {weight*100:.1f}%")
            
    with col2:
        # Call Member 5's pie chart
        fig_pie = plot_allocation(weights)
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- 3. FETCH DATA & GET METRICS ---
    st.subheader("2. Historical Backtest & Metrics")
    
    # Call Member 2's data functions
    tickers = list(weights.keys())
    historical_prices = fetch_etf_data(tickers, "5y")
    benchmark_prices = fetch_etf_data(["SPY"], "5y") # Assuming SPY is benchmark
    
    # Call Member 3's metric functions
    port_cum_returns = calculate_cumulative_returns(historical_prices, weights)
    bench_cum_returns = calculate_cumulative_returns(benchmark_prices, {"SPY": 1.0})
    metrics = calculate_metrics(port_cum_returns, bench_cum_returns)
    
    # Display Metrics
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Annualized Return", f"{metrics['Portfolio Return']*100:.2f}%", f"vs {metrics['Benchmark Return']*100:.2f}% Bench")
    m_col2.metric("Portfolio Volatility", f"{metrics['Portfolio Volatility']*100:.2f}%")
    m_col3.metric("Sharpe Ratio", f"{metrics['Sharpe Ratio']:.2f}")
    m_col4.metric("Max Drawdown", f"{metrics['Max Drawdown']*100:.2f}%")

    # --- 4. DISPLAY CHARTS ---
    # Call Member 5's line chart
    fig_line = plot_performance(port_cum_returns, bench_cum_returns)
    st.plotly_chart(fig_line, use_container_width=True)

else:
    st.info("👈 Please enter your details on the sidebar and click 'Generate Portfolio'.")
