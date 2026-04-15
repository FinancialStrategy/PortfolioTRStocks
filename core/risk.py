# core/risk.py

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import norm


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


def _align_two_series(
    left,
    right,
    left_name: str = "left",
    right_name: str = "right",
) -> pd.DataFrame:
    s_left = _to_series(left, left_name)
    s_right = _to_series(right, right_name)
    aligned = pd.concat([s_left, s_right], axis=1, join="inner").dropna()
    aligned.columns = [left_name, right_name]
    return aligned


def safe_divide(a: float, b: float) -> float:
    try:
        if b is None or pd.isna(b) or b == 0:
            return np.nan
    except Exception:
        return np.nan
    return a / b


def annualized_return(returns, periods_per_year: int = TRADING_DAYS) -> float:
    r = _to_series(returns, "returns")
    if r.empty:
        return np.nan

    growth = (1.0 + r).prod()
    n = len(r)
    if n == 0 or growth <= 0:
        return np.nan

    return growth ** (periods_per_year / n) - 1.0


def annualized_volatility(returns, periods_per_year: int = TRADING_DAYS) -> float:
    r = _to_series(returns, "returns")
    if r.empty:
        return np.nan
    return r.std(ddof=1) * np.sqrt(periods_per_year)


def downside_volatility(
    returns,
    mar_daily: float = 0.0,
    periods_per_year: int = TRADING_DAYS,
) -> float:
    r = _to_series(returns, "returns")
    if r.empty:
        return np.nan

    downside = np.minimum(r - mar_daily, 0.0)
    return np.sqrt(np.mean(downside ** 2)) * np.sqrt(periods_per_year)


def cumulative_wealth_index(returns, initial_value: float = 1.0) -> pd.Series:
    r = _to_series(returns, "returns")
    if r.empty:
        return pd.Series(dtype=float)
    wealth = initial_value * (1.0 + r).cumprod()
    wealth.name = "wealth"
    return wealth


def drawdown_series(returns) -> pd.Series:
    wealth = cumulative_wealth_index(returns, initial_value=1.0)
    if wealth.empty:
        return pd.Series(dtype=float)
    running_max = wealth.cummax()
    dd = wealth / running_max - 1.0
    dd.name = "drawdown"
    return dd


def maximum_drawdown(returns) -> float:
    dd = drawdown_series(returns)
    if dd.empty:
        return np.nan
    return dd.min()


def sharpe_ratio(
    returns,
    risk_free_rate: float = 0.0,
    periods_per_year: int = TRADING_DAYS,
) -> float:
    ann_ret = annualized_return(returns, periods_per_year)
    ann_vol = annualized_volatility(returns, periods_per_year)
    return safe_divide(ann_ret - risk_free_rate, ann_vol)


def sortino_ratio(
    returns,
    risk_free_rate: float = 0.0,
    periods_per_year: int = TRADING_DAYS,
) -> float:
    ann_ret = annualized_return(returns, periods_per_year)
    dvol = downside_volatility(
        returns,
        mar_daily=risk_free_rate / periods_per_year,
        periods_per_year=periods_per_year,
    )
    return safe_divide(ann_ret - risk_free_rate, dvol)


def calmar_ratio(
    returns,
    periods_per_year: int = TRADING_DAYS,
) -> float:
    ann_ret = annualized_return(returns, periods_per_year)
    mdd = maximum_drawdown(returns)
    return safe_divide(ann_ret, abs(mdd))


def historical_var_cvar(
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


def historical_expected_shortfall(
    returns,
    confidence: float = 0.95,
) -> float:
    _, cvar = historical_var_cvar(returns, confidence=confidence)
    return cvar


def parametric_var(
    returns,
    confidence: float = 0.95,
) -> float:
    r = _to_series(returns, "returns")
    if r.empty:
        return np.nan
    mu = r.mean()
    sigma = r.std(ddof=1)
    z = norm.ppf(1.0 - confidence)
    return mu + z * sigma


def relative_active_return_series(
    portfolio_returns,
    benchmark_returns,
) -> pd.Series:
    aligned = _align_two_series(
        portfolio_returns,
        benchmark_returns,
        left_name="portfolio",
        right_name="benchmark",
    )
    if aligned.empty:
        return pd.Series(dtype=float, name="active_return")

    active = aligned["portfolio"] - aligned["benchmark"]
    active.name = "active_return"
    return active


def rolling_relative_tail_metrics(
    portfolio_returns,
    benchmark_returns,
    window: int = 63,
    confidence: float = 0.95,
) -> pd.DataFrame:
    active = relative_active_return_series(portfolio_returns, benchmark_returns)

    if active.empty or len(active) < window:
        return pd.DataFrame(
            columns=[
                "rolling_relative_var",
                "rolling_relative_cvar",
                "rolling_relative_es",
            ]
        )

    rows = []
    idx = []

    for i in range(window, len(active) + 1):
        sample = active.iloc[i - window:i]
        var_, cvar_ = historical_var_cvar(sample, confidence=confidence)

        rows.append(
            {
                "rolling_relative_var": var_,
                "rolling_relative_cvar": cvar_,
                "rolling_relative_es": cvar_,
            }
        )
        idx.append(active.index[i - 1])

    return pd.DataFrame(rows, index=idx)


def distribution_statistics(returns) -> dict:
    r = _to_series(returns, "returns")
    if r.empty:
        return {
            "mean_periodic": np.nan,
            "median_periodic": np.nan,
            "std_periodic": np.nan,
            "skewness": np.nan,
            "kurtosis": np.nan,
            "min_periodic": np.nan,
            "max_periodic": np.nan,
        }

    return {
        "mean_periodic": r.mean(),
        "median_periodic": r.median(),
        "std_periodic": r.std(ddof=1),
        "skewness": r.skew(),
        "kurtosis": r.kurt(),
        "min_periodic": r.min(),
        "max_periodic": r.max(),
    }


def risk_summary_table(
    returns,
    risk_free_rate: float = 0.0,
    periods_per_year: int = TRADING_DAYS,
    confidence: float = 0.95,
) -> pd.DataFrame:
    r = _to_series(returns, "returns")

    if r.empty:
        return pd.DataFrame(
            {
                "Metric": [
                    "Annual Return",
                    "Annual Volatility",
                    "Sharpe Ratio",
                    "Sortino Ratio",
                    "Calmar Ratio",
                    "Maximum Drawdown",
                    "Historical VaR 95%",
                    "Historical CVaR 95%",
                    "Historical ES 95%",
                    "Parametric VaR 95%",
                ],
                "Value": [np.nan] * 10,
            }
        )

    hist_var, hist_cvar = historical_var_cvar(r, confidence=confidence)
    hist_es = historical_expected_shortfall(r, confidence=confidence)
    gauss_var = parametric_var(r, confidence=confidence)

    out = pd.DataFrame(
        {
            "Metric": [
                "Annual Return",
                "Annual Volatility",
                "Sharpe Ratio",
                "Sortino Ratio",
                "Calmar Ratio",
                "Maximum Drawdown",
                f"Historical VaR {int(confidence*100)}%",
                f"Historical CVaR {int(confidence*100)}%",
                f"Historical ES {int(confidence*100)}%",
                f"Parametric VaR {int(confidence*100)}%",
            ],
            "Value": [
                annualized_return(r, periods_per_year),
                annualized_volatility(r, periods_per_year),
                sharpe_ratio(r, risk_free_rate, periods_per_year),
                sortino_ratio(r, risk_free_rate, periods_per_year),
                calmar_ratio(r, periods_per_year),
                maximum_drawdown(r),
                hist_var,
                hist_cvar,
                hist_es,
                gauss_var,
            ],
        }
    )
    return out
