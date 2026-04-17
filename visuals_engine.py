import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Member 5: Visualization & Reporting
# Your job: Turn the math and weights into beautiful charts using Plotly or Matplotlib.

def plot_allocation(weights: dict):
    """
    Takes a dictionary of weights and returns a pie chart figure.
    """
    labels = list(weights.keys())
    values = list(weights.values())
    
    # Professional color palette for different asset classes
    color_map = {
        'SPY': '#1f77b4',      # Blue - US Equities
        'QQQ': '#ff7f0e',      # Orange - Tech/Nasdaq
        'VTI': '#2ca02c',      # Green - Total Market
        'VOO': '#1f77b4',      # Blue - S&P 500
        'VXUS': '#d62728',     # Red - International
        'BND': '#9467bd',      # Purple - Bonds
        'AGG': '#8c564b',      # Brown - Aggregate Bonds
        'VNQ': '#e377c2',      # Pink - Real Estate
        'DBC': '#7f7f7f',      # Gray - Commodities
        'XLK': '#bcbd22',      # Yellow-Green - Technology Sector
        'XLV': '#17becf',      # Cyan - Healthcare
        'XLE': '#ff9896',      # Light Red - Energy
        'XLF': '#c5b0d5',      # Light Purple - Financial
        'XLI': '#c49c94',      # Tan - Industrial
        'XLY': '#f7b6d2',      # Light Pink - Consumer Discretionary
        'XLP': '#c7c7c7',      # Light Gray - Consumer Staples
        'XLRE': '#dbbb13',     # Gold - Real Estate
        'XLU': '#98df8a'       # Light Green - Utilities
    }
    
    # Fallback color palette for unknown tickers (cycling through attractive colors)
    fallback_colors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
        '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B88B', '#AED6F1',
        '#F1948A', '#D7BDE2', '#A9DFBF', '#F9E79F', '#FADBD8'
    ]
    
    # Assign colors to each label
    colors = []
    fallback_index = 0
    for label in labels:
        if label in color_map:
            colors.append(color_map[label])
        else:
            # Cycle through fallback colors for unknown tickers
            colors.append(fallback_colors[fallback_index % len(fallback_colors)])
            fallback_index += 1
    
    # Create custom hover text with formatted percentages
    hover_text = [f"<b>{label}</b><br>Weight: {value*100:.2f}%<br>Allocation: {value:.4f}" 
                  for label, value in zip(labels, values)]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors, line=dict(color='white', width=3)),
        hovertext=hover_text,
        hoverinfo='text',
        textposition='inside',
        textinfo='percent+label',
        textfont=dict(size=12, color='white', family='Arial Black'),
        hovertemplate='%{hovertext}<extra></extra>',
        pull=[0.05] * len(labels)
    )])
    
    fig.update_traces(
        marker=dict(line=dict(color='white', width=2)),
        selector=dict(type='pie')
    )
    
    fig.update_layout(
        title=dict(
            text="<b>Portfolio Allocation</b> - Target Weights",
            font=dict(size=18, color='#2c3e50', family='Arial'),
            x=0.5,
            xanchor='center'
        ),
        font=dict(size=12, family='Arial', color='#2c3e50'),
        showlegend=True,
        margin=dict(t=60, b=10, l=50, r=120),
        paper_bgcolor='rgba(240, 245, 250, 1)',
        plot_bgcolor='rgba(240, 245, 250, 1)',
        height=450,
        hoverlabel=dict(
            bgcolor='#2E86AB',
            font=dict(family='Arial', size=14, color='white'),
            bordercolor='#1a4d7a',
            namelength=-1
        ),
        hovermode='closest',
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#2E86AB',
            borderwidth=1.5,
            font=dict(size=11, family='Arial')
        )
    )
    
    return fig

def plot_performance(portfolio_cumulative: pd.Series, benchmark_cumulative: pd.Series):
    """
    Takes cumulative return series for portfolio and benchmark and plots them on a line chart over time.
    Enhanced with drawdown visualization and professional styling.
    """
    fig = go.Figure()
    
    # Calculate running maximum for drawdown visualization
    running_max = portfolio_cumulative.cummax()
    drawdown = (portfolio_cumulative - running_max) / running_max
    
    # Calculate returns for each point in the series (not just the final value)
    portfolio_returns_series = (portfolio_cumulative - 1) * 100
    benchmark_returns_series = (benchmark_cumulative - 1) * 100
    
    # Add shaded area for drawdowns (when portfolio is below its running maximum)
    fig.add_trace(go.Scatter(
        x=portfolio_cumulative.index,
        y=running_max,
        fill=None,
        mode='lines',
        line=dict(color='rgba(0,0,0,0)'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=portfolio_cumulative.index,
        y=portfolio_cumulative,
        fill='tonexty',
        mode='lines',
        name='Drawdown Period',
        line=dict(color='rgba(0,0,0,0)'),
        fillcolor='rgba(220, 53, 69, 0.15)',
        showlegend=True,
        hoverinfo='skip'
    ))
    
    # Portfolio performance line
    fig.add_trace(go.Scatter(
        x=portfolio_cumulative.index, 
        y=portfolio_cumulative.values,
        mode='lines',
        name='Your Portfolio',
        line=dict(color='#2E86AB', width=3),
        customdata=portfolio_returns_series.values,
        hovertemplate='<b>Portfolio</b><br>Value: $%{y:.2f}<br>Return: %{customdata:.2f}%<extra></extra>',
        fill='tozeroy',
        fillcolor='rgba(46, 134, 171, 0.1)'
    ))
    
    # Benchmark performance line
    fig.add_trace(go.Scatter(
        x=benchmark_cumulative.index, 
        y=benchmark_cumulative.values,
        mode='lines',
        name='Benchmark (SPY)',
        line=dict(color='#A23B72', width=2.5, dash='dash'),
        customdata=benchmark_returns_series.values,
        hovertemplate='<b>Benchmark (SPY)</b><br>Value: $%{y:.2f}<br>Return: %{customdata:.2f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='<b>Historical Cumulative Performance</b><br><sub>Portfolio vs Benchmark Comparison</sub>',
            font=dict(size=18, color='#2c3e50', family='Arial'),
            x=0.5,
            xanchor='center'
        ),
        xaxis_title="<b>Date</b>",
        yaxis_title="<b>Cumulative Return ($1 → $X)</b>",
        template="plotly_white",
        font=dict(size=12, family='Arial', color='#2c3e50'),
        legend=dict(
            yanchor="bottom",
            y=1.06,
            xanchor="right", 
            x=1.0,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#2E86AB',
            borderwidth=1.5,
            font=dict(size=11, family='Arial', color='#2c3e50')
        ),
        hovermode='x unified',
        plot_bgcolor='rgba(240, 245, 250, 0.5)',
        paper_bgcolor='rgba(250, 250, 250, 1)',
        xaxis_gridcolor='rgba(200, 200, 200, 0.2)',
        yaxis_gridcolor='rgba(200, 200, 200, 0.2)',
        margin=dict(t=130, b=60, l=80, r=30),
        height=600,
        # Add range slider for better interactivity
        xaxis=dict(
            rangeslider=dict(visible=False),
            type='date'
        )
    )
    
    # Add annotations for final values
    final_portfolio_value = portfolio_cumulative.iloc[-1]
    final_benchmark_value = benchmark_cumulative.iloc[-1]
    
    fig.add_annotation(
        x=portfolio_cumulative.index[-1],
        y=final_portfolio_value,
        text=f'${final_portfolio_value:.2f}',
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor='#2E86AB',
        ax=40,
        ay=-20,
        bgcolor='rgba(46, 134, 171, 0.9)',
        font=dict(color='white', size=11),
        bordercolor='#2E86AB',
        borderwidth=1
    )
    
    return fig
