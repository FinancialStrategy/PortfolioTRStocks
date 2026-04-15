# core/quantstats_report.py

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import quantstats as qs


def prepare_quantstats_series(returns: pd.Series) -> pd.Series:
    series = pd.Series(returns).dropna().copy()
    series.index = pd.to_datetime(series.index)
    return series


def generate_quantstats_metrics(
    returns: pd.Series,
    benchmark: pd.Series | None = None,
    rf: float = 0.0,
    periods_per_year: int = 252,
) -> pd.DataFrame:
    r = prepare_quantstats_series(returns)

    if benchmark is not None:
        b = prepare_quantstats_series(benchmark)
        b = b.reindex(r.index).dropna()
        r = r.reindex(b.index).dropna()
    else:
        b = None

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
    r = prepare_quantstats_series(returns)

    if benchmark is not None:
        b = prepare_quantstats_series(benchmark)
        b = b.reindex(r.index).dropna()
        r = r.reindex(b.index).dropna()
    else:
        b = None

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
