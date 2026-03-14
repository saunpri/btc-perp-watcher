from __future__ import annotations

from typing import Dict, List
import requests
import pandas as pd

BINANCE_SPOT = "https://api.binance.com/api/v3"
BINANCE_FUTURES = "https://fapi.binance.com/fapi/v1"


def fetch_klines(symbol: str, interval: str, limit: int = 300) -> pd.DataFrame:
    resp = requests.get(
        f"{BINANCE_SPOT}/klines",
        params={"symbol": symbol, "interval": interval, "limit": limit},
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    cols = [
        "open_time", "open", "high", "low", "close", "volume", "close_time",
        "quote_asset_volume", "num_trades", "taker_buy_base_asset_volume",
        "taker_buy_quote_asset_volume", "ignore"
    ]
    df = pd.DataFrame(data, columns=cols)
    for c in ["open", "high", "low", "close", "volume", "quote_asset_volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms", utc=True)
    return df


def fetch_open_interest(symbol: str) -> Dict:
    resp = requests.get(
        f"{BINANCE_FUTURES}/openInterest",
        params={"symbol": symbol},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()


def fetch_funding_history(symbol: str, limit: int = 20) -> List[Dict]:
    resp = requests.get(
        f"{BINANCE_FUTURES}/fundingRate",
        params={"symbol": symbol, "limit": limit},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()
