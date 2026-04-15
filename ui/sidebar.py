# ui/sidebar.py

from __future__ import annotations

from datetime import datetime, timedelta

import streamlit as st


def render_sidebar(
    universes: dict,
    default_benchmark: str,
    default_num_simulations: int,
    default_forecast_days: int,
    default_risk_free_rate: float,
) -> dict:
    with st.sidebar:
        st.markdown("## Terminal Controls")

        universe_name = st.selectbox(
            "Investment Universe",
            options=list(universes.keys()),
            index=0,
            key="sb_universe_name",
        )

        benchmark_ticker = st.text_input(
            "Benchmark",
            value=default_benchmark,
            key="sb_benchmark_ticker",
        )

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=5 * 365)

        start_date = st.date_input("Start Date", value=start_date, max_value=end_date, key="sb_start_date")
        end_date = st.date_input("End Date", value=end_date, max_value=end_date, key="sb_end_date")

        st.markdown("---")
        st.markdown("### Portfolio Construction")

        allocation_method = st.radio(
            "Allocation Method",
            options=[
                "Equal Weight",
                "Optimized (Max Sharpe)",
                "Optimized (Min Volatility)",
                "Optimized (Max Return)",
                "Tracking Error Optimization",
                "Custom Weights",
            ],
            index=1,
            key="sb_allocation_method",
        )

        use_black_litterman = st.toggle(
            "Enable Black-Litterman",
            value=False,
            key="sb_use_black_litterman",
        )

        custom_weights = None
        if allocation_method == "Custom Weights":
            tickers = list(universes[universe_name].keys())
            st.caption("Weights should sum approximately to 100%.")
            custom_weights = []
            total = 0.0

            for t in tickers:
                w = st.number_input(
                    f"{t} Weight (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=round(100.0 / len(tickers), 2),
                    step=1.0,
                    key=f"sb_custom_weight_{t}",
                )
                custom_weights.append(w / 100.0)
                total += w

            if abs(total - 100.0) > 0.5:
                st.warning(f"Current custom weight sum: {total:.2f}%")

        st.markdown("---")
        st.markdown("### Quant Settings")

        covariance_method = st.selectbox(
            "Covariance Method",
            options=["Sample", "Ledoit-Wolf"],
            index=1,
            key="sb_cov_method",
        )

        use_log_returns = st.toggle(
            "Use Log Returns",
            value=False,
            key="sb_use_log_returns",
        )

        risk_free_rate = st.number_input(
            "Risk-Free Rate (decimal)",
            min_value=0.0,
            max_value=1.0,
            value=float(default_risk_free_rate),
            step=0.01,
            key="sb_risk_free_rate",
        )

        st.markdown("---")
        st.markdown("### Monte Carlo")

        num_simulations = st.slider(
            "Number of Simulations",
            min_value=1000,
            max_value=50000,
            value=default_num_simulations,
            step=1000,
            key="sb_num_simulations",
        )

        forecast_days = st.slider(
            "Forecast Horizon (Trading Days)",
            min_value=21,
            max_value=756,
            value=default_forecast_days,
            step=21,
            key="sb_forecast_days",
        )

        initial_investment = st.number_input(
            "Initial Investment (TRY)",
            min_value=10000,
            value=1000000,
            step=10000,
            key="sb_initial_investment",
        )

        st.markdown("---")
        run_button = st.button(
            "Run Terminal",
            type="primary",
            use_container_width=True,
            key="sb_run_terminal",
        )

    return {
        "universe_name": universe_name,
        "benchmark_ticker": benchmark_ticker,
        "start_date": start_date,
        "end_date": end_date,
        "allocation_method": allocation_method,
        "use_black_litterman": use_black_litterman,
        "custom_weights": custom_weights,
        "covariance_method": covariance_method,
        "use_log_returns": use_log_returns,
        "risk_free_rate": risk_free_rate,
        "num_simulations": num_simulations,
        "forecast_days": forecast_days,
        "initial_investment": initial_investment,
        "run_button": run_button,
    }
