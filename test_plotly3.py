import pandas as pd
import plotly.express as px

data = {
    "Category": ["Broad US Equity", "Broad US Equity", "Broad US Equity", "Technology", "Technology"],
    "Ticker": ["DYNF", "VUG", "SPYG", "SMH", "FTEC"],
    "Is_Winner": ["Loser", "Winner", "Loser", "Winner", "Loser"],
    "Sharpe Ratio": [0.5, 0.6, 0.4, 0.7, 0.65],
    "Annualized Return %": [10, 12, 9, 8, 7],
    "Annualized Volatility %": [15, 16, 14, 12, 11]
}
df = pd.DataFrame(data)

fig = px.bar(
    df, 
    x="Ticker", 
    y="Sharpe Ratio", 
    color="Is_Winner",
    facet_col="Category",
    color_discrete_map={"Winner": "#2ca02c", "Loser": "#7f7f7f"},
    text="Ticker",
    title="<b>ETF Selection Tournament (Highest Sharpe Ratio Wins)</b>"
)

fig.update_traces(textposition='auto', textangle=-90)
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
fig.update_xaxes(matches=None, showticklabels=False, title="")
fig.update_yaxes(showgrid=True, gridcolor='rgba(128,128,128,0.2)')

fig.update_layout(
    title=dict(font=dict(size=18, family='Arial'), x=0.5),
    font=dict(size=12, family='Arial'),
    legend_title="Status",
    xaxis_title="Selected Categories",
    height=400,
    margin=dict(t=50, b=50, l=10, r=10)
)
print("Title in top dict:", fig.layout.title.text)
import json
print(json.dumps([a.to_plotly_json() for a in fig.layout.annotations], indent=2))
fig.write_html("test3.html")
