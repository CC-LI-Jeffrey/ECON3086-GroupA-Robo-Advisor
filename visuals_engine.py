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
        textfont=dict(size=18, color='white', family='Arial Black'),
        hovertemplate='%{hovertext}<extra></extra>',
        pull=[0.05] * len(labels),
        hole=0,
        sort=False
    )])

    fig.update_traces(
        marker=dict(line=dict(color='white', width=2)),
        selector=dict(type='pie')
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation='v',
            font=dict(size=16, color='white', family='Arial'),
            x=1.05,
            y=0.5,
            xanchor='left',
            yanchor='middle',
            bgcolor='rgba(0,0,0,0)'
        ),
        margin=dict(t=40, b=40, l=40, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=600,
        width=600
    )

    return fig
    
def plot_selection_metrics(selection_metrics: dict):
    """
    Takes the output from the allocate_portfolio tournament and returns a bar chart 
    showing why the winning ETF was chosen over its peers.
    """
    if not selection_metrics:
        # Return an empty dummy figure if no metrics provided
        return go.Figure()

    # Flatten the nested dictionary into a list of rows for better Pandas ingestion
    rows = []
    for cat, data in selection_metrics.items():
        winner = data['Winner']
        for ticker, stats in data['Competitors'].items():
            rows.append({
                "Category": cat,
                "Ticker": ticker,
                "Is_Winner": "Winner" if ticker == winner else "Loser",
                "Sharpe Ratio": stats["Sharpe"],
                "Annualized Return %": stats["Return"],
                "Annualized Volatility %": stats["Volatility"]
            })
            
    df = pd.DataFrame(rows)
    
    # We only want to plot categories that had actual competition (more than 1 ETF)
    competition_cats = df.groupby('Category').filter(lambda x: len(x) > 1)
    
    if competition_cats.empty:
        # If all chosen categories only had 1 candidate, don't show the chart
        fig = go.Figure()
        fig.update_layout(
            title="No competitive categories selected (Each had only 1 candidate ETF available).",
            paper_bgcolor='rgba(240, 245, 250, 1)'
        )
        return fig

    # Sort the data so winners are easy to spot and categories are grouped
    competition_cats = competition_cats.sort_values(by=['Category', 'Sharpe Ratio'], ascending=[True, False])

    # Plot the Sharpe Ratios grouped by Category and split by Ticker
    fig = px.bar(
        competition_cats, 
        x="Ticker", 
        y="Sharpe Ratio", 
        color="Is_Winner",
        facet_col="Category",
        color_discrete_map={"Winner": "#2ca02c", "Loser": "#7f7f7f"}, # Green for winner, Gray for loser
        text="Ticker", # Show the ticker name on the bar
        hover_data=["Annualized Return %", "Annualized Volatility %"],
        title="<b>ETF Selection Tournament (Highest Sharpe Ratio Wins)</b>"
    )
    
    # Text appearance and X-axis configuration for facets
    fig.update_traces(textposition='auto', textangle=-90)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1])) # Removes 'Category=' from the subplot titles
    fig.update_xaxes(matches=None, showticklabels=False, title=None) # Removes the redundant ticker labels on X axis
    fig.update_yaxes(showgrid=True, gridcolor='rgba(128,128,128,0.2)') # Add subtle grid lines for readability
    
    fig.update_layout(
        title=dict(
            text="<b>ETF Selection Tournament (Highest Sharpe Ratio)</b>", 
            font=dict(size=20, family='Arial'), 
            x=0.5,
            y=0.95, # Push title up
            xanchor='center',
            yanchor='top'
        ),
        font=dict(size=12, family='Arial'),
        legend_title="Status",
        paper_bgcolor='rgba(0,0,0,0)', # Transparent to adapt to Streamlit dark/light mode
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent to adapt to Streamlit dark/light mode
        yaxis_title="Historical Sharpe Ratio (Higher is Better)",
        height=450, # Give it a bit more room to breathe
        margin=dict(t=100, b=20, l=10, r=10), # Extra top margin for sub-titles
        legend=dict(
            xanchor="left",
            yanchor="top",
            y=1.0,
            x=1.02,
            font=dict(size=11, family='Arial')
        )
    )

    return fig

def plot_performance(portfolio_cumulative: pd.Series, benchmark_cumulative: pd.Series, benchmark_name: str = 'S&P 500'):
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
        name=f'Benchmark ({benchmark_name})',
        line=dict(color='#A23B72', width=2.5, dash='dash'),
        customdata=benchmark_returns_series.values,
        hovertemplate=f'<b>Benchmark ({benchmark_name})</b><br>Value: $''%{y:.2f}<br>Return: %{customdata:.2f}%<extra></extra>'
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
