# app.py

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from config import (
    UNIVERSES,
    DEFAULT_BENCHMARK,
    DEFAULT_NUM_SIMULATIONS,
    DEFAULT_FORECAST_DAYS,
    DEFAULT_RISK_FREE_RATE,
)
from theme import apply_theme, render_hero
from core.data_loader import DataLoader
from core.optimization import PortfolioOptimizer
from core.monte_carlo import MonteCarloEngine
from core.black_litterman import BlackLittermanModel
from core.regime import RegimeDetector
from core.relative_risk import (
    tracking_error,
    information_ratio,
    beta_alpha,
    relative_var_cvar_es,
)
from core.reporting import (
    allocation_table,
    benchmark_probability_table,
    percentile_table,
)
from core.risk import (
    risk_summary_table,
    rolling_relative_tail_metrics,
)
from core.technical_analysis import (
    enrich_technical_indicators,
    technical_signal_score,
    latest_technical_snapshot,
)
from core.strategy_engine import (
    build_strategy_dashboard,
    build_portfolio_strategy_overlay,
)
from core.quantstats_report import (
    generate_quantstats_metrics,
    generate_quantstats_html_report,
    generate_quantstats_snapshot,
)
from core.efficient_frontier import (
    generate_random_frontier,
    generate_benchmark_relative_frontier,
)

from ui.sidebar import render_sidebar
from ui.layout import render_kpi_row, render_section_header
from ui.charts import (
    plot_allocation_bar,
    plot_category_bar,
    plot_monte_carlo_paths,
    plot_terminal_distribution,
    plot_regime_dashboard,
    plot_price_with_ta,
    plot_rsi_macd_panel,
    plot_relative_tail_panel,
    plot_cumulative_vs_benchmark,
    plot_active_return_panel,
    plot_signal_heatmap,
    plot_benchmark_relative_frontier,
    plot_quantstats_snapshot,
)


# =========================================================
# Streamlit Page Config
# =========================================================
st.set_page_config(
    page_title="BIST Quant Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# Helpers
# =========================================================
def normalize_weights(weights: np.ndarray) -> np.ndarray:
    weights = np.asarray(weights, dtype=float)

    if len(weights) == 0:
        return weights

    total = weights.sum()
    if total <= 0 or np.isnan(total):
        return np.repeat(1.0 / len(weights), len(weights))

    return weights / total


def get_weights_from_method(
    allocation_method: str,
    selected_tickers: list[str],
    optimizer: PortfolioOptimizer,
    benchmark_series: pd.Series | None,
    custom_weights: list[float] | None,
) -> np.ndarray:
    n = len(selected_tickers)

    if n == 0:
        raise ValueError("No valid tickers remain for allocation.")

    if allocation_method == "Equal Weight":
        return np.repeat(1.0 / n, n)

    if allocation_method == "Optimized (Max Sharpe)":
        return normalize_weights(optimizer.optimize("max_sharpe"))

    if allocation_method == "Optimized (Min Volatility)":
        return normalize_weights(optimizer.optimize("min_volatility"))

    if allocation_method == "Optimized (Max Return)":
        return normalize_weights(optimizer.optimize("max_return"))

    if allocation_method == "Tracking Error Optimization":
        if benchmark_series is None or benchmark_series.empty:
            st.warning("Benchmark data unavailable. Falling back to equal weights.")
            return np.repeat(1.0 / n, n)

        try:
            return normalize_weights(optimizer.optimize_tracking_error(benchmark_series))
        except Exception as e:
            st.warning(
                f"Tracking error optimization failed. Falling back to equal weights. Details: {e}"
            )
            return np.repeat(1.0 / n, n)

    if allocation_method == "Custom Weights":
        if custom_weights is None:
            st.warning("Custom weights unavailable. Falling back to equal weights.")
            return np.repeat(1.0 / n, n)

        w = np.array(custom_weights, dtype=float)
        if len(w) != n:
            st.warning("Custom weights length mismatch. Falling back to equal weights.")
            return np.repeat(1.0 / n, n)

        return normalize_weights(w)

    return np.repeat(1.0 / n, n)


def build_black_litterman_view(
    selected_tickers: list[str],
    optimizer: PortfolioOptimizer,
) -> dict | None:
    if len(selected_tickers) == 0:
        return None

    st.markdown("### Black-Litterman Views")
    st.caption("Absolute and relative tactical views with confidence weighting.")

    num_views = st.slider(
        "Number of Views",
        min_value=1,
        max_value=min(5, len(selected_tickers)),
        value=1,
    )

    market_weights = np.repeat(1.0 / len(selected_tickers), len(selected_tickers))

    model = BlackLittermanModel(
        cov_matrix=optimizer.cov_matrix,
        market_weights=market_weights,
        risk_aversion=2.5,
        tau=0.05,
    )

    P_rows = []
    Q_values = []
    confidences = []

    for i in range(num_views):
        col1, col2, col3 = st.columns(3)

        with col1:
            asset_a = st.selectbox(
                f"Primary Asset {i+1}",
                selected_tickers,
                key=f"bl_asset_a_{i}",
            )

        with col2:
            asset_b = st.selectbox(
                f"Relative Asset {i+1}",
                ["None"] + selected_tickers,
                key=f"bl_asset_b_{i}",
            )

        with col3:
            expected_return = st.slider(
                f"Expected View Return {i+1} (%)",
                min_value=-20.0,
                max_value=20.0,
                value=3.0,
                step=0.5,
                key=f"bl_return_{i}",
            )

        conf = st.slider(
            f"Confidence {i+1}",
            min_value=0.05,
            max_value=0.95,
            value=0.60,
            step=0.05,
            key=f"bl_conf_{i}",
        )

        row = np.zeros(len(selected_tickers))
        row[selected_tickers.index(asset_a)] = 1.0

        if asset_b != "None":
            row[selected_tickers.index(asset_b)] = -1.0

        P_rows.append(row)
        Q_values.append(expected_return / 100.0)
        confidences.append(conf)

    posterior = model.posterior(
        np.array(P_rows, dtype=float),
        np.array(Q_values, dtype=float),
        np.array(confidences, dtype=float),
    )

    posterior_df = (
        posterior["posterior_returns"]
        .rename("Posterior Return")
        .reset_index()
        .rename(columns={"index": "Ticker"})
    )

    st.dataframe(posterior_df, use_container_width=True, hide_index=True)

    return posterior


def extract_metric_value(risk_df: pd.DataFrame, metric_name: str, multiplier: float = 1.0, suffix: str = "") -> str:
    try:
        val = risk_df.loc[risk_df["Metric"] == metric_name, "Value"].iloc[0]
        if pd.isna(val):
            return "N/A"
        return f"{val * multiplier:.2f}{suffix}" if suffix else f"{val:.3f}"
    except Exception:
        return "N/A"


# =========================================================
# Main App
# =========================================================
def main():
    apply_theme()

    render_hero(
        "BIST Quant Terminal",
        "Institutional portfolio construction, technical analysis, strategy intelligence, and benchmark-relative risk analytics for Turkish equities.",
    )

    state = render_sidebar(
        universes=UNIVERSES,
        default_benchmark=DEFAULT_BENCHMARK,
        default_num_simulations=DEFAULT_NUM_SIMULATIONS,
        default_forecast_days=DEFAULT_FORECAST_DAYS,
        default_risk_free_rate=DEFAULT_RISK_FREE_RATE,
    )

    if not state["run_button"]:
        st.info("Universe ve analiz ayarlarını soldan seçip Run Terminal butonuna bas.")
        return

    selected_universe_name = state["universe_name"]
    universe_map = UNIVERSES[selected_universe_name]
    requested_tickers = list(universe_map.keys())

    # -----------------------------------------------------
    # Market Data
    # -----------------------------------------------------
    with st.spinner("BIST verileri indiriliyor ve temizleniyor..."):
        loader = DataLoader(
            tickers=requested_tickers,
            benchmark_ticker=state["benchmark_ticker"],
            start_date=state["start_date"],
            end_date=state["end_date"],
            use_log_returns=state["use_log_returns"],
        )
        market = loader.load_market_data()

    prices = market["prices"]
    returns = market["returns"]
    ohlcv_map = market["ohlcv_map"]
    benchmark_returns = market["benchmark_returns"]
    benchmark_prices = market["benchmark_prices"]
    current_prices = market["current_prices"]
    valid_tickers = market["valid_tickers"]

    if returns.empty or len(valid_tickers) == 0:
        st.error("Temizleme sonrası kullanılabilir getiri serisi kalmadı.")
        st.stop()

    removed = [t for t in requested_tickers if t not in valid_tickers]
    if removed:
        st.warning("Yetersiz coverage nedeniyle çıkarılan hisseler: " + ", ".join(removed))

    # -----------------------------------------------------
    # Optimizer
    # -----------------------------------------------------
    optimizer = PortfolioOptimizer(
        returns=returns,
        risk_free_rate=state["risk_free_rate"],
        covariance_method=state["covariance_method"],
    )

    benchmark_series = None
    if benchmark_returns is not None and not benchmark_returns.empty:
        benchmark_series = benchmark_returns.iloc[:, 0].copy()
        benchmark_series.name = state["benchmark_ticker"]

    weights = get_weights_from_method(
        allocation_method=state["allocation_method"],
        selected_tickers=valid_tickers,
        optimizer=optimizer,
        benchmark_series=benchmark_series,
        custom_weights=state["custom_weights"],
    )

    # -----------------------------------------------------
    # Optional Black-Litterman
    # -----------------------------------------------------
    posterior = None
    if state["use_black_litterman"]:
        posterior = build_black_litterman_view(valid_tickers, optimizer)

    # -----------------------------------------------------
    # Portfolio Objects
    # -----------------------------------------------------
    allocation_df = allocation_table(valid_tickers, weights, universe_map)

    portfolio_returns = returns @ weights
    portfolio_returns.name = "Portfolio"

    risk_df = risk_summary_table(
        portfolio_returns,
        risk_free_rate=state["risk_free_rate"],
        periods_per_year=252,
        confidence=0.95,
    )

    rel_tail_df = pd.DataFrame(columns=["Metric", "Value"])
    rolling_tail_df = pd.DataFrame()
    te = np.nan
    ir = np.nan
    beta = np.nan
    alpha = np.nan

    if benchmark_series is not None and not benchmark_series.empty:
        relative_tail = relative_var_cvar_es(
            portfolio_returns=portfolio_returns,
            benchmark_returns=benchmark_series,
            confidence=0.95,
        )

        rel_tail_df = pd.DataFrame(
            {
                "Metric": [
                    "Relative VaR 95%",
                    "Relative CVaR 95%",
                    "Relative ES 95%",
                ],
                "Value": [
                    relative_tail["relative_var"],
                    relative_tail["relative_cvar"],
                    relative_tail["relative_es"],
                ],
            }
        )

        rolling_tail_df = rolling_relative_tail_metrics(
            portfolio_returns=portfolio_returns,
            benchmark_returns=benchmark_series,
            window=63,
            confidence=0.95,
        )

        te = tracking_error(portfolio_returns, benchmark_series)
        ir = information_ratio(portfolio_returns, benchmark_series)
        beta, alpha = beta_alpha(portfolio_returns, benchmark_series)

    regime_df = RegimeDetector(portfolio_returns, window=63).detect()

    # -----------------------------------------------------
    # Monte Carlo
    # -----------------------------------------------------
    mc_engine = MonteCarloEngine(
        mean_returns=returns.mean(),
        cov_matrix=optimizer.cov_matrix,
        num_simulations=state["num_simulations"],
        forecast_days=state["forecast_days"],
    )
    sim_results = mc_engine.run(weights, state["initial_investment"])

    benchmark_prob_df = benchmark_probability_table(
        sim_results["final_values"],
        state["initial_investment"],
    )

    percentile_df = percentile_table(
        sim_results["final_values"],
        state["initial_investment"],
    )

    # -----------------------------------------------------
    # Frontier + QuantStats
    # -----------------------------------------------------
    frontier_df = generate_random_frontier(
        returns=returns,
        n_points=2500,
        risk_free_rate=state["risk_free_rate"],
    )

    relative_frontier_df = pd.DataFrame()
    if benchmark_series is not None and not benchmark_series.empty:
        relative_frontier_df = generate_benchmark_relative_frontier(
            returns=returns,
            benchmark_returns=benchmark_series,
            n_points=2500,
        )

    qs_snapshot = generate_quantstats_snapshot(
        returns=portfolio_returns,
        benchmark=benchmark_series,
        rf=0.0,
    )

    # -----------------------------------------------------
    # KPI Row
    # -----------------------------------------------------
    render_kpi_row(
        {
            "Annual Return": (
                extract_metric_value(risk_df, "Annual Return", multiplier=100, suffix="%"),
                "Geometric annualized return",
            ),
            "Annual Volatility": (
                extract_metric_value(risk_df, "Annual Volatility", multiplier=100, suffix="%"),
                "Realized annualized volatility",
            ),
            "Sharpe Ratio": (
                extract_metric_value(risk_df, "Sharpe Ratio"),
                "Risk-adjusted performance",
            ),
            "Tracking Error": (
                f"{te * 100:.2f}%" if pd.notna(te) else "N/A",
                f"Relative to {state['benchmark_ticker']}",
            ),
            "Info Ratio": (
                f"{ir:.3f}" if pd.notna(ir) else "N/A",
                "Active return efficiency",
            ),
            "Expected Terminal": (
                f"{sim_results['expected_value']:,.0f} TRY",
                "Monte Carlo expected terminal wealth",
            ),
        }
    )

    # -----------------------------------------------------
    # Tabs
    # -----------------------------------------------------
    tabs = st.tabs(
        [
            "Executive Summary",
            "Technical Analysis",
            "Strategy Lab",
            "Monte Carlo",
            "Relative Risk",
            "QuantStats Report",
        ]
    )

    # =====================================================
    # Tab 1: Executive Summary
    # =====================================================
    with tabs[0]:
        render_section_header(
            "Executive Summary",
            "Allocation, risk, cumulative performance and benchmark-relative overview.",
        )

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(plot_allocation_bar(allocation_df), use_container_width=True)
        with c2:
            st.plotly_chart(plot_category_bar(allocation_df), use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            st.plotly_chart(
                plot_cumulative_vs_benchmark(portfolio_returns, benchmark_series),
                use_container_width=True,
            )
        with c4:
            st.plotly_chart(
                plot_active_return_panel(portfolio_returns, benchmark_series),
                use_container_width=True,
            )

        st.markdown("### Allocation Table")
        st.dataframe(allocation_df, use_container_width=True, hide_index=True)

        st.markdown("### Risk Summary")
        st.dataframe(risk_df, use_container_width=True, hide_index=True)

        if not rel_tail_df.empty:
            st.markdown("### Relative Tail Risk")
            st.dataframe(rel_tail_df, use_container_width=True, hide_index=True)

        if not relative_frontier_df.empty:
            st.markdown("### Benchmark-Relative Efficient Frontier")
            st.plotly_chart(
                plot_benchmark_relative_frontier(relative_frontier_df),
                use_container_width=True,
            )

    # =====================================================
    # Tab 2: Technical Analysis
    # =====================================================
    with tabs[1]:
        render_section_header(
            "Technical Analysis",
            "RSI, MACD, Bollinger Bands, trend structure, and cross-sectional signal map.",
        )

        ta_ticker = st.selectbox("Select Ticker", valid_tickers, key="ta_ticker_select")

        ta_raw = ohlcv_map[ta_ticker].copy()
        ta_df = enrich_technical_indicators(ta_raw)
        ta_df = technical_signal_score(ta_df)
        ta_last = latest_technical_snapshot(ta_df)

        render_kpi_row(
            {
                "Signal": (str(ta_last["signal_label"]), "Composite technical label"),
                "RSI": (f"{ta_last['rsi']:.2f}", "Relative Strength Index"),
                "MACD Hist": (f"{ta_last['macd_hist']:.4f}", "MACD histogram"),
                "ATR": (f"{ta_last['atr']:.4f}", "Average true range"),
                "Momentum 20D": (f"{ta_last['momentum_20'] * 100:.2f}%", "20-day momentum"),
                "ROC 12": (f"{ta_last['roc_12']:.2f}", "Rate of change"),
            }
        )

        st.plotly_chart(plot_price_with_ta(ta_df, ta_ticker), use_container_width=True)
        st.plotly_chart(plot_rsi_macd_panel(ta_df, ta_ticker), use_container_width=True)

        signal_heatmap_df = build_strategy_dashboard(ohlcv_map, valid_tickers)

        st.markdown("### Cross-Sectional Signal Dashboard")
        st.dataframe(signal_heatmap_df, use_container_width=True, hide_index=True)

        st.plotly_chart(plot_signal_heatmap(signal_heatmap_df), use_container_width=True)

    # =====================================================
    # Tab 3: Strategy Lab
    # =====================================================
    with tabs[2]:
        render_section_header(
            "Strategy Lab",
            "Trend-following, mean reversion, momentum, and tactical overlay intelligence.",
        )

        strategy_outputs = build_portfolio_strategy_overlay(
            ohlcv_map=ohlcv_map,
            tickers=valid_tickers,
            portfolio_weights=weights,
        )

        st.markdown("### Portfolio Strategy Dashboard")
        st.dataframe(
            strategy_outputs["summary_table"],
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("### Signal Ranking")
        st.dataframe(
            strategy_outputs["ranking_table"],
            use_container_width=True,
            hide_index=True,
        )

        if posterior is not None:
            st.markdown("### Black-Litterman Posterior")
            posterior_df = (
                posterior["posterior_returns"]
                .rename("Posterior Return")
                .reset_index()
                .rename(columns={"index": "Ticker"})
            )
            st.dataframe(posterior_df, use_container_width=True, hide_index=True)

    # =====================================================
    # Tab 4: Monte Carlo
    # =====================================================
    with tabs[3]:
        render_section_header(
            "Monte Carlo",
            "Distribution, path analysis, benchmark outperformance probabilities, and terminal percentiles.",
        )

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(
                plot_monte_carlo_paths(
                    sim_results["portfolio_values"],
                    state["initial_investment"],
                ),
                use_container_width=True,
            )
        with c2:
            st.plotly_chart(
                plot_terminal_distribution(
                    sim_results["final_values"],
                    state["initial_investment"],
                ),
                use_container_width=True,
            )

        st.markdown("### Benchmark Outperformance Probabilities")
        st.dataframe(benchmark_prob_df, use_container_width=True, hide_index=True)

        st.markdown("### Terminal Percentiles")
        st.dataframe(percentile_df, use_container_width=True, hide_index=True)

    # =====================================================
    # Tab 5: Relative Risk
    # =====================================================
    with tabs[4]:
        render_section_header(
            "Relative Risk",
            "Tracking error, alpha/beta, rolling active tail risk, and regime analysis.",
        )

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Tracking Error", f"{te * 100:.2f}%" if pd.notna(te) else "N/A")
        with k2:
            st.metric("Information Ratio", f"{ir:.3f}" if pd.notna(ir) else "N/A")
        with k3:
            st.metric("Beta", f"{beta:.3f}" if pd.notna(beta) else "N/A")
        with k4:
            st.metric("Alpha", f"{alpha * 100:.2f}%" if pd.notna(alpha) else "N/A")

        if not rolling_tail_df.empty:
            st.plotly_chart(
                plot_relative_tail_panel(rolling_tail_df),
                use_container_width=True,
            )

        st.plotly_chart(
            plot_regime_dashboard(regime_df),
            use_container_width=True,
        )

        if not rel_tail_df.empty:
            st.markdown("### Relative Tail Risk Table")
            st.dataframe(rel_tail_df, use_container_width=True, hide_index=True)

    # =====================================================
    # Tab 6: QuantStats Report
    # =====================================================
    with tabs[5]:
        render_section_header(
            "QuantStats Report",
            "Quantitative performance reporting, tear sheet metrics, and benchmark-relative diagnostic layer.",
        )

        qs_metrics = generate_quantstats_metrics(
            returns=portfolio_returns,
            benchmark=benchmark_series,
            rf=0.0,
            periods_per_year=252,
        )

        st.plotly_chart(
            plot_quantstats_snapshot(qs_snapshot),
            use_container_width=True,
        )

        st.markdown("### QuantStats Metrics")
        st.dataframe(qs_metrics, use_container_width=True, hide_index=True)

        if not relative_frontier_df.empty:
            st.markdown("### Benchmark-Relative Efficient Frontier")
            st.plotly_chart(
                plot_benchmark_relative_frontier(relative_frontier_df),
                use_container_width=True,
            )

        if st.toggle("Render Full QuantStats HTML Tear Sheet", value=False):
            try:
                qs_html = generate_quantstats_html_report(
                    returns=portfolio_returns,
                    benchmark=benchmark_series,
                    rf=0.0,
                    periods_per_year=252,
                    title=f"{selected_universe_name} vs {state['benchmark_ticker']}",
                )
                components.html(qs_html, height=1200, scrolling=True)
            except Exception as e:
                st.warning(f"QuantStats HTML render failed: {e}")

    st.markdown("---")
    st.caption(
        "This platform uses Yahoo Finance data and model-based analytics. Outputs are analytical in nature and do not constitute investment advice."
    )


if __name__ == "__main__":
    main()
