from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class WatcherState:
    regime: str
    bias: str
    price_vs_oi: str
    breakout_risk: str
    flush_risk: str
    support_state: str
    watcher_verdict: str

    def as_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


def derive_price_vs_oi(price_now: float, price_prev: float, oi_now: float, oi_prev: float) -> str:
    price_up = price_now > price_prev
    oi_up = oi_now > oi_prev
    if price_up and oi_up:
        return "price_up_oi_up_new_longs"
    if price_up and not oi_up:
        return "price_up_oi_down_short_covering"
    if (not price_up) and oi_up:
        return "price_down_oi_up_new_shorts"
    return "price_down_oi_down_long_unwind"


def derive_state(metrics: Dict[str, Any], levels: Dict[str, float]) -> WatcherState:
    price = metrics["price"]
    rsi_15m = metrics["rsi_15m"]
    rsi_1d = metrics["rsi_1d"]
    rsi_1w = metrics["rsi_1w"]
    funding = metrics["funding_latest"]
    price_vs_oi = metrics["price_vs_oi"]

    if price >= levels["upside_gate"]:
        regime = "breakout_test"
    elif price >= levels["strength_zone_low"]:
        regime = "bullish_compression"
    elif price >= levels["support_primary"]:
        regime = "constructive_retest"
    elif price >= levels["defense_low"]:
        regime = "support_failure_risk"
    else:
        regime = "bearish_continuation_risk"

    if price >= levels["strength_zone_low"] and rsi_15m >= 55:
        bias = "bullish"
    elif price >= levels["support_primary"] and rsi_1d >= 50:
        bias = "neutral_bullish"
    elif rsi_1w <= 35 and rsi_1d < 50:
        bias = "reset_zone"
    else:
        bias = "neutral"

    breakout_risk = "high" if price >= levels["upside_gate"] * 0.995 else "medium" if price >= levels["strength_zone_low"] else "low"
    flush_risk = "high" if price < levels["support_primary"] or (rsi_15m < 45 and price < levels["strength_zone_low"]) else "medium"

    if price >= levels["strength_zone_low"] and price <= levels["strength_zone_high"]:
        support_state = "holding_strength_zone"
    elif price >= levels["support_primary"]:
        support_state = "holding_primary_support"
    elif price >= levels["defense_low"]:
        support_state = "above_last_defense"
    else:
        support_state = "below_defense"

    if bias == "bullish" and regime in {"bullish_compression", "breakout_test"}:
        verdict = "constructive under resistance; favor long only on acceptance"
    elif bias == "reset_zone":
        verdict = "weekly damage unresolved; bounce may still be relief inside a larger reset"
    elif regime == "support_failure_risk":
        verdict = "structure weakening; watch for deeper rotation"
    else:
        verdict = "balanced; wait for confirmation at key levels"

    if funding > 0.0005:
        verdict += "; positive funding indicates perp longs paying"
    if price_vs_oi == "price_up_oi_up_new_longs":
        verdict += "; bounce is being chased by new longs"

    return WatcherState(
        regime=regime,
        bias=bias,
        price_vs_oi=price_vs_oi,
        breakout_risk=breakout_risk,
        flush_risk=flush_risk,
        support_state=support_state,
        watcher_verdict=verdict,
    )
