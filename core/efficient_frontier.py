# core/efficient_frontier.py

from __future__ import annotations

import numpy as np
import pandas as pd


TRADING_DAYS = 252


def portfolio_return_vol(
    mean_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    weights: np.ndarray,
) -> tuple[float, float]:
    w = np.asarray(weights, dtype=float)
    daily_ret = float(np.dot(mean_returns.values, w))
    ann_ret = (1.0 + daily_ret) ** TRADING_DAYS - 1.0
    ann_vol = float(np.sqrt(w.T @ (cov_matrix.values * TRADING_DAYS) @ w))
    return ann_ret, ann_vol


def generate_random_frontier(
    returns: pd.DataFrame,
    n_points: int = 3000,
    risk_free_rate: float = 0.0,
) -> pd.DataFrame:
    mean_returns = returns.mean()
    cov_matrix = returns.cov()

    rows = []
    n_assets = returns.shape[1]

    for _ in range(n_points):
        w = np.random.random(n_assets)
        w = w / w.sum()

        ann_ret, ann_vol = portfolio_return_vol(mean_returns, cov_matrix, w)
        sharpe = (ann_ret - risk_free_rate) / ann_vol if ann_vol > 0 else np.nan

        rows.append(
            {
                "return": ann_ret,
                "volatility": ann_vol,
                "sharpe": sharpe,
                "weights": w,
            }
        )

    return pd.DataFrame(rows)


def generate_benchmark_relative_frontier(
    returns: pd.DataFrame,
    benchmark_returns: pd.Series,
    n_points: int = 3000,
) -> pd.DataFrame:
    aligned = pd.concat([returns, benchmark_returns.rename("benchmark")], axis=1, join="inner").dropna()
    if aligned.empty:
        return pd.DataFrame()

    asset_returns = aligned[returns.columns]
    benchmark = aligned["benchmark"]

    rows = []
    n_assets = asset_returns.shape[1]

    for _ in range(n_points):
        w = np.random.random(n_assets)
        w = w / w.sum()

        portfolio = asset_returns @ w
        active = portfolio - benchmark

        active_ret = active.mean() * TRADING_DAYS
        te = active.std(ddof=1) * np.sqrt(TRADING_DAYS)
        info_ratio = active_ret / te if te > 0 else np.nan

        rows.append(
            {
                "active_return": active_ret,
                "tracking_error": te,
                "information_ratio": info_ratio,
                "weights": w,
            }
        )

    return pd.DataFrame(rows)
