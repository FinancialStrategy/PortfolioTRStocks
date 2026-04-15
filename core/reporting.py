# core/reporting.py

from __future__ import annotations

import numpy as np
import pandas as pd


def allocation_table(tickers, weights, universe):
    df = pd.DataFrame(
        {
            "Ticker": tickers,
            "Name": [universe[t]["name"] for t in tickers],
            "Category": [universe[t]["category"] for t in tickers],
            "Segment": [universe[t]["segment"] for t in tickers],
            "Weight (%)": np.asarray(weights) * 100.0,
        }
    )
    return df.sort_values("Weight (%)", ascending=False).reset_index(drop=True)


def benchmark_probability_table(final_values, initial_investment: float):
    final_values = np.asarray(final_values, dtype=float)
    percentiles = [0.00, 0.05, 0.10, 0.15, 0.20]

    rows = []
    for p in percentiles:
        benchmark_final = initial_investment * (1.0 + p)
        prob = (final_values > benchmark_final).mean() * 100.0
        rows.append(
            {
                "Benchmark Assumption": f"{p*100:.0f}%",
                "Benchmark Terminal Value": benchmark_final,
                "Probability Portfolio Beats (%)": prob,
            }
        )

    return pd.DataFrame(rows)


def percentile_table(final_values, initial_investment: float):
    p = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    vals = np.percentile(final_values, p)
    returns = (vals / initial_investment - 1.0) * 100.0

    return pd.DataFrame(
        {
            "Percentile": p,
            "Terminal Value": vals,
            "Return (%)": returns,
        }
    )
