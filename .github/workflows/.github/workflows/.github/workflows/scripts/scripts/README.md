# Market Data Pipeline (Yahoo + FRED)

This repository pulls daily market data from **Yahoo Finance** and **FRED**, stores time-series CSVs, and (optionally) renders charts. A GitHub Actions workflow runs this automatically each day.

## What it does
- Fetches daily prices for configured Yahoo tickers → `data/yahoo/<TICKER>.csv`
- Fetches macro series from FRED → `data/fred/<SERIES>.csv`
- Builds simple charts → `data/charts/*.png`
- Commits any changes back to the repository

## Configure
Edit `config/tickers.yml` to add/remove tickers or series.

## Secrets
Create a repo secret named `FRED_API_KEY` with your FRED API key:
- https://fred.stlouisfed.org/docs/api/api_key.html

## Run locally
```bash
pip install -r requirements.txt
python scripts/fetch_market_data.py
python scripts/make_charts.py
