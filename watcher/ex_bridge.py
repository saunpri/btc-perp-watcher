from __future__ import annotations

from typing import Dict, Any


def build_ex_bridge(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    state = snapshot["state"]
    metrics = snapshot["metrics"]
    levels = snapshot["levels"]
    return {
        "timestamp_utc": snapshot["timestamp_utc"],
        "latest_regime": state["regime"],
        "latest_bias": state["bias"],
        "watcher_verdict": state["watcher_verdict"],
        "challenge_signals": [
            "weekly_rsi_reset_zone" if metrics["rsi_1w"] <= 35 else None,
            "price_at_upside_gate" if metrics["price"] >= levels["upside_gate"] * 0.995 else None,
            "new_longs_chasing" if state["price_vs_oi"] == "price_up_oi_up_new_longs" else None,
        ],
        "supports": {
            "primary": levels["support_primary"],
            "strength_zone_low": levels["strength_zone_low"],
            "strength_zone_high": levels["strength_zone_high"],
            "defense_low": levels["defense_low"],
        },
        "upside_gates": {
            "gate_1": levels["upside_gate"],
            "gate_2": levels["upside_gate_2"],
        },
    }
