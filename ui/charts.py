# ui/charts.py

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


def _layout(fig, title: str, height: int = 420):
    fig.update_layout(
        title=title,
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12),
        margin=dict(l=30, r=20, t=50, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def plot_allocation_bar(allocation_df: pd.DataFrame):
    fig = px.bar(
        allocation_df,
        x="Ticker",
        y="Weight (%)",
        color="Category",
        text="Weight (%)",
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    return _layout(fig, "Portfolio Allocation", 420)


def plot_category_bar(allocation_df: pd.DataFrame):
    cat = allocation_df.groupby("Category", as_index=False)["Weight (%)"].sum()
    fig = px.bar(
        cat.sort_values("Weight (%)", ascending=False),
        x="Category",
        y="Weight (%)",
        text="Weight (%)",
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    return _layout(fig, "Category Allocation", 420)


def plot_cumulative_vs_benchmark(portfolio_returns: pd.Series, benchmark_returns: pd.Series | None):
    fig = go.Figure()

    p = (1 + portfolio_returns).cumprod()
    fig.add_trace(go.Scatter(x=p.index, y=p, mode="lines", name="Portfolio"))

    if benchmark_returns is not None and not benchmark_returns.empty:
        aligned = benchmark_returns.reindex(p.index).dropna()
        p_aligned = p.reindex(aligned.index).dropna()
        b = (1 + aligned).cumprod()
        fig.add_trace(go.Scatter(x=b.index, y=b, mode="lines", name="Benchmark"))
        fig = _layout(fig, "Cumulative Growth vs Benchmark", 420)
        return fig

    return _layout(fig, "Cumulative Growth", 420)


def plot_active_return_panel(portfolio_returns: pd.Series, benchmark_returns: pd.Series | None):
    fig = go.Figure()

    if benchmark_returns is not None and not benchmark_returns.empty:
        aligned = pd.concat([portfolio_returns, benchmark_returns], axis=1).dropna()
        aligned.columns = ["portfolio", "benchmark"]
        active = aligned["portfolio"] - aligned["benchmark"]
        rolling_active = active.rolling(21).sum() * 100
        fig.add_trace(go.Scatter(x=rolling_active.index, y=rolling_active, mode="lines", name="21D Active Return"))
        fig.add_hline(y=0, line_dash="dash")
        return _layout(fig, "Rolling Active Return", 420)

    fig.add_annotation(text="Benchmark unavailable", x=0.5, y=0.5, showarrow=False, xref="paper", yref="paper")
    return _layout(fig, "Rolling Active Return", 420)


def plot_monte_carlo_paths(paths: np.ndarray, initial_investment: float):
    fig = go.Figure()
    if paths.shape[0] > 0:
        idx = np.random.choice(paths.shape[0], min(80, paths.shape[0]), replace=False)
        for i in idx:
            fig.add_trace(go.Scatter(y=paths[i], mode="lines", line=dict(width=0.7), opacity=0.14, showlegend=False))
        fig.add_trace(go.Scatter(y=paths.mean(axis=0), mode="lines", name="Mean Path", line=dict(width=2.8)))
        fig.add_hline(y=initial_investment, line_dash="dash")
    return _layout(fig, "Monte Carlo Paths", 460)


def plot_terminal_distribution(final_values: np.ndarray, initial_investment: float):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=final_values, nbinsx=60, name="Terminal Values"))
    fig.add_vline(x=initial_investment, line_dash="dash", annotation_text="Initial")
    return _layout(fig, "Terminal Value Distribution", 460)


def plot_regime_dashboard(regime_df: pd.DataFrame):
    fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=("Annualized Rolling Return", "Annualized Rolling Volatility"),
        vertical_spacing=0.14,
    )

    if regime_df is not None and not regime_df.empty:
        fig.add_trace(
            go.Scatter(x=regime_df.index, y=regime_df["return_ann"] * 100, mode="lines", name="Return"),
            row=1, col=1,
        )
        fig.add_trace(
            go.Scatter(x=regime_df.index, y=regime_df["vol_ann"] * 100, mode="lines", name="Volatility"),
            row=2, col=1,
        )

    fig.update_layout(
        title="Regime Dashboard",
        height=650,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=20, t=50, b=30),
    )
    return fig


def plot_price_with_ta(df: pd.DataFrame, ticker: str):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close"))
    fig.add_trace(go.Scatter(x=df.index, y=df["sma_short"], mode="lines", name="SMA Short"))
    fig.add_trace(go.Scatter(x=df.index, y=df["sma_medium"], mode="lines", name="SMA Medium"))
    fig.add_trace(go.Scatter(x=df.index, y=df["sma_long"], mode="lines", name="SMA Long"))
    fig.add_trace(go.Scatter(x=df.index, y=df["bb_upper"], mode="lines", name="BB Upper", opacity=0.5))
    fig.add_trace(go.Scatter(x=df.index, y=df["bb_lower"], mode="lines", name="BB Lower", opacity=0.5))
    return _layout(fig, f"{ticker} Price and Trend Structure", 500)


def plot_rsi_macd_panel(df: pd.DataFrame, ticker: str):
    fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=(f"{ticker} RSI", f"{ticker} MACD"),
        vertical_spacing=0.14,
    )

    fig.add_trace(go.Scatter(x=df.index, y=df["rsi"], mode="lines", name="RSI"), row=1, col=1)
    fig.add_hline(y=70, line_dash="dash", row=1, col=1)
    fig.add_hline(y=30, line_dash="dash", row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df["macd_line"], mode="lines", name="MACD"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["signal_line"], mode="lines", name="Signal"), row=2, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df["macd_hist"], name="Histogram"), row=2, col=1)

    fig.update_layout(
        title=f"{ticker} Momentum Panels",
        height=650,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=20, t=50, b=30),
    )
    return fig


def plot_signal_heatmap(signal_df: pd.DataFrame):
    if signal_df.empty:
        return _layout(go.Figure(), "Signal Heatmap", 420)

    heat = signal_df[["Ticker", "Trend Score", "Mean Reversion Score", "Momentum Score", "Composite Score"]].copy()
    heat = heat.set_index("Ticker")

    fig = px.imshow(
        heat,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="Greys",
    )
    return _layout(fig, "Strategy Signal Heatmap", 420)


def plot_relative_tail_panel(rolling_tail_df: pd.DataFrame):
    fig = go.Figure()

    if rolling_tail_df is not None and not rolling_tail_df.empty:
        fig.add_trace(go.Scatter(
            x=rolling_tail_df.index,
            y=rolling_tail_df["rolling_relative_var"] * 100,
            mode="lines",
            name="Relative VaR",
        ))
        fig.add_trace(go.Scatter(
            x=rolling_tail_df.index,
            y=rolling_tail_df["rolling_relative_cvar"] * 100,
            mode="lines",
            name="Relative CVaR",
        ))
        fig.add_trace(go.Scatter(
            x=rolling_tail_df.index,
            y=rolling_tail_df["rolling_relative_es"] * 100,
            mode="lines",
            name="Relative ES",
        ))

    return _layout(fig, "Rolling Relative Tail Risk", 430)
