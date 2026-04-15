import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Member 5: Visualization & Reporting
# Your job: Turn the math and weights into beautiful charts using Plotly or Matplotlib.

def plot_allocation(weights: dict):
    """
    Takes a dictionary of weights and returns a pie chart figure.
    """
    # MOCK DATA: This is actually a working basic pie chart, but you can make it prettier!
    # Add custom colors, better labels, hover text, etc.
    
    labels = list(weights.keys())
    values = list(weights.values())
    
    fig = px.pie(names=labels, values=values, title="Portfolio Allocation")
    fig.update_traces(textposition='inside', textinfo='percent+label')
    # fig.update_layout(margin=dict(t=30, b=0, l=0, r=0))
    return fig

def plot_performance(portfolio_cumulative: pd.Series, benchmark_cumulative: pd.Series):
    """
    Takes cumulative return series for portfolio and benchmark and plots them on a line chart over time.
    """
    # MOCK DATA: Basic line chart. Improve it by adding shaded areas for drawdowns, better tooltips, etc.
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=portfolio_cumulative.index, 
        y=portfolio_cumulative.values, 
        mode='lines', 
        name='Your Portfolio',
        line=dict(color='blue', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=benchmark_cumulative.index, 
        y=benchmark_cumulative.values, 
        mode='lines', 
        name='Benchmark (SPY)',
        line=dict(color='gray', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title="Historical Cumulative Performance",
        xaxis_title="Date",
        yaxis_title="Cumulative Return ($1 -> $X)",
        template="plotly_white",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    return fig
