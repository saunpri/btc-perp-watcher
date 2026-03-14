from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from watcher.config import load_config
from watcher.data_sources import fetch_klines, fetch_open_interest, fetch_funding_history
from watcher.ex_bridge import build_ex_bridge
from watcher.indicators import rsi
from watcher.signals import detect_signals
from watcher.state_logic import derive_price_vs_oi, derive_state
from watcher.storage import append_signals, append_state_log, write_json


def latest_csv_row(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows[-1] if rows else None


def build_snapshot(config: Dict[str, Any]) -> Dict[str, Any]:
    symbol_spot = config["symbol_spot"]
    symbol_perp = config["symbol_perp"]
    period = int(config["rsi_period"])
    levels = config["levels"]

    df_15m = fetch_klines(symbol_spot, "15m")
    df_1h = fetch_klines(symbol_spot, "1h")
    df_1d = fetch_klines(symbol_spot, "1d")
    df_1w = fetch_klines(symbol_spot, "1w")

    for df in (df_15m, df_1h, df_1d, df_1w):
        df["rsi"] = rsi(df["close"], period)

    price = float(df_15m["close"].iloc[-1])
    price_prev = float(df_15m["close"].iloc[-2])

    oi_payload = fetch_open_interest(symbol_perp)
    oi_now = float(oi_payload["openInterest"])

    prev_oi_est = oi_now
    funding_hist = fetch_funding_history(symbol_perp, limit=2)
    funding_latest = float(funding_hist[-1]["fundingRate"]) if funding_hist else 0.0

    price_vs_oi = derive_price_vs_oi(price_now=price, price_prev=price_prev, oi_now=oi_now, oi_prev=prev_oi_est)

    metrics = {
        "price": price,
        "rsi_15m": float(df_15m["rsi"].iloc[-1]),
        "rsi_1h": float(df_1h["rsi"].iloc[-1]),
        "rsi_1d": float(df_1d["rsi"].iloc[-1]),
        "rsi_1w": float(df_1w["rsi"].iloc[-1]),
        "funding_latest": funding_latest,
        "open_interest": oi_now,
        "price_vs_oi": price_vs_oi,
    }

    state = derive_state(metrics, levels).as_dict()
    ts = datetime.now(timezone.utc).isoformat()
    return {
        "timestamp_utc": ts,
        "metrics": metrics,
        "state": state,
        "levels": levels,
    }


def main() -> None:
    config = load_config()
    base_dir = Path(__file__).resolve().parent.parent
    output_dir = base_dir / config["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    state_log_path = output_dir / "state_log.csv"
    signal_log_path = output_dir / "signal_log.csv"
    current_state_path = output_dir / "current_state.json"
    ex_bridge_path = output_dir / "ex_bridge.json"

    snapshot = build_snapshot(config)
    row = {
        "timestamp_utc": snapshot["timestamp_utc"],
        **snapshot["metrics"],
        **snapshot["state"],
    }
    prev = latest_csv_row(state_log_path)
    append_state_log(state_log_path, row)
    signals = detect_signals(snapshot, prev)
    append_signals(signal_log_path, signals)

    write_json(current_state_path, snapshot)
    write_json(ex_bridge_path, build_ex_bridge(snapshot))
    print(f"Watcher update complete: {snapshot['timestamp_utc']}")


if __name__ == "__main__":
    main()
