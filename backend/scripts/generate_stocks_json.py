"""
Static stock data generator — OFFLINE ONLY.

Generates a deterministic, realistic dataset of daily OHLCV stock data
for all 15 configured NSE symbols, covering Jan 1 2025 → Jan 1 2026.

Usage:
    python scripts/generate_stocks_json.py

Output:
    data/stocks.json

This script is NOT used at runtime. The generated JSON serves as the
single source of truth and is committed to the repository.
"""

import json
import random
import math
from datetime import date, timedelta
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────

SYMBOLS = {
    "TCS.NS":        {"name": "Tata Consultancy Services",  "sector": "IT",        "base": 4100.0},
    "INFY.NS":       {"name": "Infosys",                    "sector": "IT",        "base": 1600.0},
    "RELIANCE.NS":   {"name": "Reliance Industries",        "sector": "Energy",    "base": 2950.0},
    "HDFCBANK.NS":   {"name": "HDFC Bank",                  "sector": "Banking",   "base": 1450.0},
    "ICICIBANK.NS":  {"name": "ICICI Bank",                 "sector": "Banking",   "base": 1080.0},
    "WIPRO.NS":      {"name": "Wipro",                      "sector": "IT",        "base": 480.0},
    "ITC.NS":        {"name": "ITC Limited",                "sector": "FMCG",      "base": 430.0},
    "SBIN.NS":       {"name": "State Bank of India",        "sector": "Banking",   "base": 760.0},
    "BHARTIARTL.NS": {"name": "Bharti Airtel",              "sector": "Telecom",   "base": 1200.0},
    "HINDUNILVR.NS": {"name": "Hindustan Unilever",         "sector": "FMCG",      "base": 2400.0},
    "BAJFINANCE.NS": {"name": "Bajaj Finance",              "sector": "Finance",   "base": 7100.0},
    "MARUTI.NS":     {"name": "Maruti Suzuki",              "sector": "Auto",      "base": 12500.0},
    "LT.NS":         {"name": "Larsen & Toubro",            "sector": "Infra",     "base": 3600.0},
    "AXISBANK.NS":   {"name": "Axis Bank",                  "sector": "Banking",   "base": 1050.0},
    "KOTAKBANK.NS":  {"name": "Kotak Mahindra Bank",        "sector": "Banking",   "base": 1750.0},
}

START_DATE = date(2025, 1, 1)
END_DATE   = date(2026, 1, 1)

# Fixed seed for determinism
RANDOM_SEED = 42


def is_trading_day(d: date) -> bool:
    """Exclude weekends. Indian market holidays are not simulated."""
    return d.weekday() < 5  # Mon–Fri


def generate_trading_dates() -> list[date]:
    """Generate all trading days between START_DATE and END_DATE (exclusive end)."""
    dates = []
    d = START_DATE
    while d < END_DATE:
        if is_trading_day(d):
            dates.append(d)
        d += timedelta(days=1)
    return dates


def generate_symbol_data(symbol: str, base_price: float, dates: list[date], rng: random.Random) -> list[dict]:
    """
    Generate realistic daily OHLCV data using a random walk.

    Model:
      - Daily return ~ N(0.0003, 0.015)   (slight upward drift, ≈1-3% daily range)
      - Open = previous close ± small gap
      - High = max(open, close) × (1 + uniform(0.003, 0.015))
      - Low  = min(open, close) × (1 - uniform(0.003, 0.015))
      - Volume = base_volume × (0.6 + random * 0.8)  (variation around base)
    """
    records = []
    price = base_price
    base_volume = int(base_price * 800)  # rough heuristic

    for i, d in enumerate(dates):
        # Daily return with slight upward bias
        daily_return = rng.gauss(0.0003, 0.015)
        close = price * (1 + daily_return)

        # Open is close ± small overnight gap
        gap = rng.gauss(0, 0.003)
        open_price = price * (1 + gap)

        # High and low ensure enveloping open/close
        day_max = max(open_price, close)
        day_min = min(open_price, close)
        high = day_max * (1 + rng.uniform(0.003, 0.015))
        low  = day_min * (1 - rng.uniform(0.003, 0.015))

        # Volume with natural variation
        vol_mult = 0.6 + rng.random() * 0.8
        volume = int(base_volume * vol_mult)

        records.append({
            "symbol": symbol,
            "date":   d.isoformat(),
            "open":   round(open_price, 2),
            "high":   round(high, 2),
            "low":    round(low, 2),
            "close":  round(close, 2),
            "volume": volume,
        })

        price = close  # carry forward

    return records


def main():
    rng = random.Random(RANDOM_SEED)
    dates = generate_trading_dates()
    print(f"Trading days: {len(dates)}  ({dates[0]} -> {dates[-1]})")

    all_records = []
    for symbol, info in SYMBOLS.items():
        records = generate_symbol_data(symbol, info["base"], dates, rng)
        all_records.extend(records)
        last = records[-1]["close"]
        print(f"  {symbol:18s}  base={info['base']:>10.2f}  final={last:>10.2f}  rows={len(records)}")

    # Write JSON
    out_path = Path(__file__).resolve().parent.parent / "data" / "stocks.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=1)

    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"\nDone! Wrote {len(all_records)} records to {out_path}  ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
