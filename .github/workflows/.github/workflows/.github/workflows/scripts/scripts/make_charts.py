#!/usr/bin/env python3
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_YF = os.path.join(ROOT, "data", "yahoo")
CHARTS = os.path.join(ROOT, "data", "charts")

def ensure_dirs():
    os.makedirs(CHARTS, exist_ok=True)

def make_chart(csv_path):
    df = pd.read_csv(csv_path)
    if df.empty:
        return
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    ticker = df["Ticker"].iloc[0]
    plt.figure(figsize=(10,4))
    plt.plot(df["Date"], df["Close"])
    plt.title(f"{ticker} — Close")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.tight_layout()
    out = os.path.join(CHARTS, f"{ticker.replace('^','_')}.png")
    plt.savefig(out, dpi=150)
    plt.close()

def main():
    ensure_dirs()
    for fname in os.listdir(DATA_YF):
        if fname.endswith(".csv"):
            make_chart(os.path.join(DATA_YF, fname))
    print("[DONE] Charts updated.")

if __name__ == "__main__":
    main()
