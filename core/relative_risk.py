# core/relative_risk.py

from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def _to_series(x, name: str = "value") -> pd.Series:
    if isinstance(x, pd.Series):
        s = x.copy()
    elif isinstance(x, pd.DataFrame):
        if x.shape[1] != 1:
            raise ValueError(f"{name} DataFrame must have exactly one column.")
        s = x.iloc[:, 0].copy()
    else:
        s = pd.Series(x, name=name)

    s = pd.to_numeric(s, errors="coerce")
    s = s.replace([np.inf, -np.inf], np.nan).dropna()
    s.name = name
    return s


def _align_series(
    portfolio_returns,
    benchmark_returns,
    portfolio_name: str = "portfolio",
    benchmark_name: str = "benchmark",
) -> pd.DataFrame:
    p = _to_series(portfolio_returns, portfolio_name)
    b = _to_series(benchmark_returns, benchmark_name)

    aligned = pd.concat([p, b], axis=1, join="inner").dropna()
    aligned.columns = [portfolio_name, benchmark_name]
    return aligned


def safe_divide(a: float, b: float) -> float:
    try:
        if b is None or pd.isna(b) or b == 0:
            return np.nan
    except Exception:
        return np.nan
    return a / b


def active_return_series(
    portfolio_returns,
    benchmark_returns,
) -> pd.Series:
    aligned = _align_series(portfolio_returns, benchmark_returns)

    if aligned.empty:
        return pd.Series(dtype=float, name="active_return")

    active = aligned["portfolio"] - aligned["benchmark"]
    active.name = "active_return"
    return active


def tracking_error(
    portfolio_returns,
    benchmark_returns,
    periods_per_year: int = TRADING_DAYS,
) -> float:
    active = active_return_series(portfolio_returns, benchmark_returns)
    if active.empty:
        return np.nan
    return active.std(ddof=1) * np.sqrt(periods_per_year)


def information_ratio(
    portfolio_returns,
    benchmark_returns,
    periods_per_year: int = TRADING_DAYS,
) -> float:
    active = active_return_series(portfolio_returns, benchmark_returns)
    if active.empty:
        return np.nan

    te = active.std(ddof=1) * np.sqrt(periods_per_year)
    active_ann = active.mean() * periods_per_year
    return safe_divide(active_ann, te)


def beta_alpha(
    portfolio_returns,
    benchmark_returns,
    periods_per_year: int = TRADING_DAYS,
):
    aligned = _align_series(portfolio_returns, benchmark_returns)

    if aligned.empty:
        return np.nan, np.nan

    p = aligned["portfolio"]
    b = aligned["benchmark"]

    var_b = b.var()
    if pd.isna(var_b) or var_b == 0:
        return np.nan, np.nan

    beta = p.cov(b) / var_b
    alpha = (p.mean() - beta * b.mean()) * periods_per_year
    return beta, alpha


def _historical_var_cvar(
    returns,
    confidence: float = 0.95,
):
    r = _to_series(returns, "returns")
    if r.empty:
        return np.nan, np.nan

    q = r.quantile(1.0 - confidence)
    tail = r[r <= q]
    cvar = tail.mean() if len(tail) > 0 else q
    return q, cvar


def relative_var_cvar_es(
    portfolio_returns,
    benchmark_returns,
    confidence: float = 0.95,
):
    active = active_return_series(
        portfolio_returns=portfolio_returns,
        benchmark_returns=benchmark_returns,
    )

    if active.empty:
        return {
            "relative_var": np.nan,
            "relative_cvar": np.nan,
            "relative_es": np.nan,
        }

    rel_var, rel_cvar = _historical_var_cvar(active, confidence=confidence)

    return {
        "relative_var": rel_var,
        "relative_cvar": rel_cvar,
        "relative_es": rel_cvar,
    }
