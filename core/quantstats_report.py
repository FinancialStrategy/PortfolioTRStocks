# core/quantstats_report.py

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import quantstats as qs


def _to_qs_series(x) -> pd.Series:
    s = pd.Series(x).copy()
    s.index = pd.to_datetime(s.index)
    s = pd.to_numeric(s, errors="coerce").dropna()
    s = s[~s.index.duplicated(keep="last")]
    s = s.sort_index()
    return s


def align_returns_and_benchmark(
    returns: pd.Series,
    benchmark: pd.Series | None = None,
) -> tuple[pd.Series, pd.Series | None]:
    r = _to_qs_series(returns)

    if benchmark is None:
        return r, None

    b = _to_qs_series(benchmark)

    aligned = pd.concat([r.rename("portfolio"), b.rename("benchmark")], axis=1, join="inner").dropna()
    if aligned.empty:
        return r, None

    return aligned["portfolio"], aligned["benchmark"]


def generate_quantstats_metrics(
    returns: pd.Series,
    benchmark: pd.Series | None = None,
    rf: float = 0.0,
    periods_per_year: int = 252,
) -> pd.DataFrame:
    r, b = align_returns_and_benchmark(returns, benchmark)

    metrics = qs.reports.metrics(
        r,
        benchmark=b,
        rf=rf,
        display=False,
        mode="full",
        compounded=True,
        periods_per_year=periods_per_year,
    )

    if isinstance(metrics, pd.DataFrame):
        return metrics.reset_index(drop=False)

    return pd.DataFrame(metrics)


def generate_quantstats_html_report(
    returns: pd.Series,
    benchmark: pd.Series | None = None,
    rf: float = 0.0,
    periods_per_year: int = 252,
    title: str = "QuantStats Report",
) -> str:
    r, b = align_returns_and_benchmark(returns, benchmark)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
        output_path = Path(tmp.name)

    qs.reports.html(
        r,
        benchmark=b,
        rf=rf,
        title=title,
        output=str(output_path),
        compounded=True,
        periods_per_year=periods_per_year,
    )

    html = output_path.read_text(encoding="utf-8", errors="ignore")
    return html


def generate_quantstats_snapshot(
    returns: pd.Series,
    benchmark: pd.Series | None = None,
    rf: float = 0.0,
) -> dict:
    r, b = align_returns_and_benchmark(returns, benchmark)

    snapshot = {
        "Sharpe": qs.stats.sharpe(r, rf=rf),
        "Sortino": qs.stats.sortino(r, rf=rf),
        "Max Drawdown": qs.stats.max_drawdown(r),
        "CAGR": qs.stats.cagr(r),
        "Volatility": qs.stats.volatility(r),
    }

    if b is not None:
        try:
            snapshot["Information Ratio"] = qs.stats.information_ratio(r, b)
        except Exception:
            snapshot["Information Ratio"] = None
        try:
            snapshot["Beta"] = qs.stats.beta(r, b)
        except Exception:
            snapshot["Beta"] = None
        try:
            snapshot["Alpha"] = qs.stats.alpha(r, b)
        except Exception:
            snapshot["Alpha"] = None

    return snapshot
