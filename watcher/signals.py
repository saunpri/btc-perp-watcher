from __future__ import annotations

from typing import Dict, Any, List


def detect_signals(snapshot: Dict[str, Any], prev_row: Dict[str, Any] | None) -> List[Dict[str, Any]]:
    ts = snapshot["timestamp_utc"]
    metrics = snapshot["metrics"]
    state = snapshot["state"]
    levels = snapshot["levels"]
    signals: List[Dict[str, Any]] = []

    price = metrics["price"]

    if price >= levels["upside_gate"]:
        signals.append({"timestamp_utc": ts, "signal_type": "upside_gate_test", "signal_text": f"Price reached or exceeded upside gate {levels['upside_gate']}"})
    if price < levels["support_primary"]:
        signals.append({"timestamp_utc": ts, "signal_type": "primary_support_lost", "signal_text": f"Price traded below primary support {levels['support_primary']}"})
    if metrics["rsi_1w"] <= 35:
        signals.append({"timestamp_utc": ts, "signal_type": "weekly_rsi_reset_zone", "signal_text": f"Weekly RSI entered reset zone at {metrics['rsi_1w']:.2f}"})

    if prev_row:
        prev_regime = prev_row.get("regime")
        if prev_regime and prev_regime != state["regime"]:
            signals.append({"timestamp_utc": ts, "signal_type": "regime_change", "signal_text": f"Regime changed from {prev_regime} to {state['regime']}"})

    deduped = []
    seen = set()
    for s in signals:
        key = (s["signal_type"], s["signal_text"])
        if key not in seen:
            seen.add(key)
            deduped.append(s)
    return deduped
