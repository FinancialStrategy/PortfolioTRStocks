# core/strategy_engine.py

from __future__ import annotations

import numpy as np
import pandas as pd

from core.technical_analysis import enrich_technical_indicators, technical_signal_score


def _latest_signal_snapshot(ohlcv: pd.DataFrame) -> pd.Series:
    df = enrich_technical_indicators(ohlcv)
    df = technical_signal_score(df)
    return df.iloc[-1]


def trend_following_score(snapshot: pd.Series) -> float:
    score = 0.0
    score += 1.0 if snapshot["Close"] > snapshot["sma_short"] else -1.0
    score += 1.0 if snapshot["sma_short"] > snapshot["sma_medium"] else -1.0
    score += 1.0 if snapshot["sma_medium"] > snapshot["sma_long"] else -1.0
    score += 1.0 if snapshot["macd_line"] > snapshot["signal_line"] else -1.0
    return score


def mean_reversion_score(snapshot: pd.Series) -> float:
    score = 0.0
    score += 1.0 if snapshot["rsi"] < 30 else 0.0
    score += -1.0 if snapshot["rsi"] > 70 else 0.0
    score += 1.0 if snapshot["Close"] < snapshot["bb_lower"] else 0.0
    score += -1.0 if snapshot["Close"] > snapshot["bb_upper"] else 0.0
    return score


def momentum_score(snapshot: pd.Series) -> float:
    score = 0.0
    score += 1.0 if snapshot["momentum_20"] > 0 else -1.0
    score += 1.0 if snapshot["roc_12"] > 0 else -1.0
    return score


def build_strategy_dashboard(ohlcv_map: dict[str, pd.DataFrame], tickers: list[str]) -> pd.DataFrame:
    rows = []

    for t in tickers:
        if t not in ohlcv_map:
            continue

        try:
            snap = _latest_signal_snapshot(ohlcv_map[t])

            trend = trend_following_score(snap)
            mr = mean_reversion_score(snap)
            mom = momentum_score(snap)
            composite = snap["signal_score"]

            rows.append(
                {
                    "Ticker": t,
                    "Signal Label": snap["signal_label"],
                    "Trend Score": trend,
                    "Mean Reversion Score": mr,
                    "Momentum Score": mom,
                    "Composite Score": composite,
                    "RSI": snap["rsi"],
                    "MACD Hist": snap["macd_hist"],
                    "Momentum 20D": snap["momentum_20"],
                }
            )
        except Exception:
            continue

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values("Composite Score", ascending=False).reset_index(drop=True)
    return out


def build_portfolio_strategy_overlay(
    ohlcv_map: dict[str, pd.DataFrame],
    tickers: list[str],
    portfolio_weights: np.ndarray,
) -> dict[str, pd.DataFrame]:
    dash = build_strategy_dashboard(ohlcv_map, tickers)

    if dash.empty:
        return {
            "summary_table": pd.DataFrame(),
            "ranking_table": pd.DataFrame(),
        }

    weights_map = pd.Series(portfolio_weights, index=tickers, name="Weight")
    dash["Weight"] = dash["Ticker"].map(weights_map).fillna(0.0)

    dash["Weighted Composite"] = dash["Composite Score"] * dash["Weight"]
    dash["Weighted Trend"] = dash["Trend Score"] * dash["Weight"]
    dash["Weighted Mean Reversion"] = dash["Mean Reversion Score"] * dash["Weight"]
    dash["Weighted Momentum"] = dash["Momentum Score"] * dash["Weight"]

    summary = pd.DataFrame(
        {
            "Metric": [
                "Portfolio Weighted Composite",
                "Portfolio Weighted Trend Score",
                "Portfolio Weighted Mean Reversion Score",
                "Portfolio Weighted Momentum Score",
                "Average RSI",
            ],
            "Value": [
                dash["Weighted Composite"].sum(),
                dash["Weighted Trend"].sum(),
                dash["Weighted Mean Reversion"].sum(),
                dash["Weighted Momentum"].sum(),
                dash["RSI"].mean(),
            ],
        }
    )

    ranking = dash[
        [
            "Ticker",
            "Signal Label",
            "Weight",
            "Composite Score",
            "Trend Score",
            "Mean Reversion Score",
            "Momentum Score",
            "RSI",
            "MACD Hist",
            "Momentum 20D",
        ]
    ].copy()

    ranking = ranking.sort_values("Composite Score", ascending=False).reset_index(drop=True)

    return {
        "summary_table": summary,
        "ranking_table": ranking,
    }
