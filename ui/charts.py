# ui/charts.py

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def _apply_layout(fig, title: str, height: int = 440):
    fig.update_layout(
        title=title,
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12),
        margin=dict(l=30, r=20, t=55, b=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
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
    return _apply_layout(fig, "Portfolio Allocation", 430)


def plot_category_bar(allocation_df: pd.DataFrame):
    cat = allocation_df.groupby("Category", as_index=False)["Weight (%)"].sum()
    fig = px.bar(
        cat.sort_values("Weight (%)", ascending=False),
        x="Category",
        y="Weight (%)",
        text="Weight (%)",
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    return _apply_layout(fig, "Category Allocation", 430)


def plot_cumulative_vs_benchmark(portfolio_returns: pd.Series, benchmark_returns: pd.Series | None):
    fig = go.Figure()

    p = (1 + portfolio_returns).cumprod()
    fig.add_trace(go.Scatter(x=p.index, y=p, mode="lines", name="Portfolio", line=dict(width=2.4)))

    if benchmark_returns is not None and not benchmark_returns.empty:
        aligned = pd.concat([portfolio_returns.rename("p"), benchmark_returns.rename("b")], axis=1).dropna()
        if not aligned.empty:
            p2 = (1 + aligned["p"]).cumprod()
            b2 = (1 + aligned["b"]).cumprod()

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=p2.index, y=p2, mode="lines", name="Portfolio", line=dict(width=2.6)))
            fig.add_trace(go.Scatter(x=b2.index, y=b2, mode="lines", name="Benchmark", line=dict(width=2.0)))
            return _apply_layout(fig, "Cumulative Growth vs Benchmark", 430)

    return _apply_layout(fig, "Cumulative Growth", 430)


def plot_active_return_panel(portfolio_returns: pd.Series, benchmark_returns: pd.Series | None):
    fig = go.Figure()

    if benchmark_returns is not None and not benchmark_returns.empty:
        aligned = pd.concat([portfolio_returns.rename("p"), benchmark_returns.rename("b")], axis=1).dropna()
        if not aligned.empty:
            active = aligned["p"] - aligned["b"]
            rolling_active = active.rolling(21).sum() * 100
            fig.add_trace(go.Scatter(x=rolling_active.index, y=rolling_active, mode="lines", name="21D Active Return"))
            fig.add_hline(y=0, line_dash="dash")
            return _apply_layout(fig, "Rolling Active Return", 430)

    fig.add_annotation(text="Benchmark unavailable", x=0.5, y=0.5, showarrow=False, xref="paper", yref="paper")
    return _apply_layout(fig, "Rolling Active Return", 430)


def plot_monte_carlo_paths(paths: np.ndarray, initial_investment: float):
    fig = go.Figure()

    if paths.shape[0] > 0:
        idx = np.random.choice(paths.shape[0], min(80, paths.shape[0]), replace=False)
        for i in idx:
            fig.add_trace(
                go.Scatter(
                    y=paths[i],
                    mode="lines",
                    line=dict(width=0.7),
                    opacity=0.10,
                    showlegend=False,
                )
            )
        fig.add_trace(go.Scatter(y=paths.mean(axis=0), mode="lines", name="Mean Path", line=dict(width=2.8)))
        fig.add_hline(y=initial_investment, line_dash="dash")

    return _apply_layout(fig, "Monte Carlo Paths", 470)


def plot_terminal_distribution(final_values: np.ndarray, initial_investment: float):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=final_values, nbinsx=60, name="Terminal Values"))
    fig.add_vline(x=initial_investment, line_dash="dash", annotation_text="Initial")
    return _apply_layout(fig, "Terminal Value Distribution", 470)


def plot_regime_dashboard(regime_df: pd.DataFrame):
    fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=("Annualized Rolling Return", "Annualized Rolling Volatility"),
        vertical_spacing=0.13,
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
        margin=dict(l=30, r=20, t=55, b=30),
    )
    return fig


def plot_price_with_ta(df: pd.DataFrame, ticker: str):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close", line=dict(width=2.4)))
    fig.add_trace(go.Scatter(x=df.index, y=df["sma_short"], mode="lines", name="SMA Short"))
    fig.add_trace(go.Scatter(x=df.index, y=df["sma_medium"], mode="lines", name="SMA Medium"))
    fig.add_trace(go.Scatter(x=df.index, y=df["sma_long"], mode="lines", name="SMA Long"))
    fig.add_trace(go.Scatter(x=df.index, y=df["bb_upper"], mode="lines", name="BB Upper", opacity=0.45))
    fig.add_trace(go.Scatter(x=df.index, y=df["bb_lower"], mode="lines", name="BB Lower", opacity=0.45))

    return _apply_layout(fig, f"{ticker} Price, Trend and Volatility Bands", 520)


def plot_rsi_macd_panel(df: pd.DataFrame, ticker: str):
    fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=(f"{ticker} RSI", f"{ticker} MACD"),
        vertical_spacing=0.13,
    )

    fig.add_trace(go.Scatter(x=df.index, y=df["rsi"], mode="lines", name="RSI"), row=1, col=1)
    fig.add_hline(y=70, line_dash="dash", row=1, col=1)
    fig.add_hline(y=30, line_dash="dash", row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df["macd_line"], mode="lines", name="MACD"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["signal_line"], mode="lines", name="Signal"), row=2, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df["macd_hist"], name="Histogram"), row=2, col=1)

    fig.update_layout(
        title=f"{ticker} RSI & MACD Panel",
        height=670,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=20, t=55, b=30),
    )
    return fig


def plot_signal_heatmap(signal_df: pd.DataFrame):
    if signal_df.empty:
        return _apply_layout(go.Figure(), "Signal Heatmap", 430)

    heat = signal_df[
        ["Ticker", "Trend Score", "Mean Reversion Score", "Momentum Score", "Composite Score"]
    ].copy()
    heat = heat.set_index("Ticker")

    fig = px.imshow(
        heat,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="Greys",
    )
    return _apply_layout(fig, "Strategy Signal Heatmap", 430)


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

    return _apply_layout(fig, "Rolling Relative Tail Risk", 440)


def plot_benchmark_relative_frontier(frontier_df: pd.DataFrame):
    if frontier_df is None or frontier_df.empty:
        return _apply_layout(go.Figure(), "Benchmark-Relative Efficient Frontier", 480)

    fig = px.scatter(
        frontier_df,
        x="tracking_error",
        y="active_return",
        color="information_ratio",
        color_continuous_scale="Greys",
    )

    fig.update_traces(marker=dict(size=6, opacity=0.60))
    return _apply_layout(fig, "Benchmark-Relative Efficient Frontier", 500)


def plot_quantstats_snapshot(snapshot: dict):
    labels = list(snapshot.keys())
    values = [snapshot[k] if snapshot[k] is not None else np.nan for k in labels]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=values))
    return _apply_layout(fig, "QuantStats Snapshot", 420)
