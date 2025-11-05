#!/usr/bin/env python3
import os
import sys
import io
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
from fredapi import Fred
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "config", "tickers.yml")
OUT_YF = os.path.join(ROOT, "data", "yahoo")
OUT_FRED = os.path.join(ROOT, "data", "fred")

def ensure_dirs():
    os.makedirs(OUT_YF, exist_ok=True)
    os.makedirs(OUT_FRED, exist_ok=True)

def read_config():
    with open(CONFIG, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def merge_write_csv(path: str, df: pd.DataFrame, index_col: str):
    """Append or update CSV without duplicating rows (by index_col)."""
    df = df.dropna()
    df = df.sort_values(index_col)

    if os.path.exists(path):
        try:
            existing = pd.read_csv(path)
            if index_col not in existing.columns:
                # If formats changed, rebuild fully
                existing = pd.DataFrame(columns=df.columns)
        except Exception:
            existing = pd.DataFrame(columns=df.columns)
        merged = pd.concat([existing, df], ignore_index=True)
        merged = merged.drop_duplicates(subset=[index_col], keep="last")
        merged = merged.sort_values(index_col)
    else:
        merged = df

    merged.to_csv(path, index=False)

def fetch_yahoo(tickers, lookback_days=365*5):
    """Fetch Yahoo data; limit to recent lookback for speed in CI."""
    start = (datetime.utcnow() - timedelta(days=lookback_days)).date().isoformat()
    end = datetime.utcnow().date().isoformat()

    for t in tickers:
        print(f"[Yahoo] Fetching {t} ({start}..{end})")
        df = yf.download(t, start=start, end=end, auto_adjust=False, progress=False)
        if df is None or df.empty:
            print(f"[Yahoo] No data for {t}")
            continue

        # Prefer Adj Close, else Close
        col = "Adj Close" if "Adj Close" in df.columns else "Close"
        out = (
            df[[col]]
            .rename(columns={col: "Close"})
            .reset_index()
        )
        # Normalize column names (DatetimeIndex -> Date)
        if "Date" not in out.columns:
            out = out.rename(columns={out.columns[0]: "Date"})
        out["Ticker"] = t
        out["Date"] = pd.to_datetime(out["Date"]).dt.date.astype(str)

        path = os.path.join(OUT_YF, f"{t.replace('^','_')}.csv")
        merge_write_csv(path, out[["Date", "Ticker", "Close"]], index_col="Date")

def fetch_fred(series_ids):
    api_key = os.environ.get("FRED_API_KEY", "")
    if not api_key:
        print("[FRED] WARNING: FRED_API_KEY not set; skipping FRED pulls.")
        return
    fred = Fred(api_key=api_key)
    for sid in series_ids:
        print(f"[FRED] Fetching {sid}")
        s = fred.get_series(sid)
        if s is None or s.empty:
            print(f"[FRED] No data for {sid}")
            continue
        df = pd.DataFrame({"Date": s.index.date.astype(str), sid: s.values})
        path = os.path.join(OUT_FRED, f"{sid}.csv")
        merge_write_csv(path, df[["Date", sid]], index_col="Date")

def main():
    ensure_dirs()
    cfg = read_config()
    yahoo = cfg.get("yahoo", [])
    fred = cfg.get("fred", [])
    fetch_yahoo(yahoo)
    fetch_fred(fred)
    print("[DONE] Data updated.")

if __name__ == "__main__":
    main()
