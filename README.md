# Asset Allocation Backtester

Advisor-focused MVP to compare portfolio allocation strategies using sample annual return series.

## Features
- Multi-strategy allocation comparison
- Portfolio growth path chart
- Metrics: total return, CAGR, volatility, Sharpe ratio, max drawdown
- Interactive Streamlit controls for strategy weights

## Setup
```bash
git clone https://github.com/john-stromberg/asset-allocation-backtester.git
cd asset-allocation-backtester
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure
- `app.py` - Streamlit UI
- `calculators/backtest.py` - backtest and risk metric logic
- `data/sample_returns.py` - sample annual return inputs

## Notes
This MVP uses embedded sample data and is intended for workflow prototyping.
