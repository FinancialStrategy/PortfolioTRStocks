# BIST Quant Terminal

Institutional-grade Streamlit analytics platform for Turkish equities.

## Core Features

- Major 25 Turkish Stocks universe
- Mid Cap 20 Turkish Stocks universe
- Benchmark: XU100.IS
- Portfolio optimization
- Black-Litterman views
- Technical analysis engine
- QuantStats reporting
- Regime detection
- Relative risk analytics
- Monte Carlo simulation
- Excel / PDF exports

## Project Structure

- `app.py` : main Streamlit app
- `config.py` : universes and constants
- `theme.py` : institutional UI styling
- `core/` : analytics engines
- `ui/` : sidebar, charts, layout
- `exports/` : downloadable report modules

## Installation

```bash
pip install -r requirements.txt
streamlit run app.py
