from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, Any, List

STATE_LOG_FIELDS = [
    "timestamp_utc", "price", "rsi_15m", "rsi_1h", "rsi_1d", "rsi_1w",
    "funding_latest", "open_interest", "price_vs_oi", "regime", "bias",
    "breakout_risk", "flush_risk", "support_state", "watcher_verdict"
]

SIGNAL_LOG_FIELDS = ["timestamp_utc", "signal_type", "signal_text"]


def ensure_csv(path: Path, fields: List[str]) -> None:
    if not path.exists():
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()


def append_state_log(path: Path, row: Dict[str, Any]) -> None:
    ensure_csv(path, STATE_LOG_FIELDS)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=STATE_LOG_FIELDS)
        writer.writerow({k: row.get(k) for k in STATE_LOG_FIELDS})


def append_signals(path: Path, signals: List[Dict[str, Any]]) -> None:
    ensure_csv(path, SIGNAL_LOG_FIELDS)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SIGNAL_LOG_FIELDS)
        for row in signals:
            writer.writerow({k: row.get(k) for k in SIGNAL_LOG_FIELDS})


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
