# EquityResearchTool (Large-Scale)

A GenAI-powered equity research framework that automates financial analysis, screening, backtesting, and report generation.

## Features
- Risk/return metrics (vol, Sharpe, beta, drawdowns)
- Fundamentals (margins, ROE/ROA, leverage)
- Screening module (e.g., top ROE stocks in S&P500)
- Backtesting (buy & hold, volatility targeting)
- Report generation (Markdown + JSON)
- Optional LLM insights (OpenAI)
- Unit tests for core modules

## Usage
```bash
# Run single analysis
python main.py --tickers AAPL MSFT --benchmark SPY --start 2020-01-01 --end 2025-01-01

# Screener (Top 10 ROE in S&P500)
python main.py --screener sp500 --metric ROE --top 10

# Backtest AAPL vs SPY
python main.py --backtest AAPL --benchmark SPY
```

## Install Locally
```bash
pip install -e .
```
