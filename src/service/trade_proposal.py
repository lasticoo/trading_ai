from datetime import datetime
from src.risk.risk_engine import calculate_position
import numpy as np

RR = 2.0

# SL / TP RANGE (DIKUNCI)
SL_MIN = 0.012
SL_MAX = 0.015
TP_MIN = 0.024
TP_MAX = 0.03
ATR_MULT = 1.3


def clamp(x, lo, hi):
    return max(lo, min(x, hi))


def compute_atr(df, period=14):
    high = df["high"]
    low = df["low"]
    close = df["close"]
    prev_close = close.shift(1)

    tr = np.maximum(
        high - low,
        np.maximum(abs(high - prev_close), abs(low - prev_close))
    )

    return tr.rolling(period).mean().iloc[-1]


def generate_trade_proposal(
    symbol,
    price,
    ai_probs,
    risk_manager,
    ohlcv_df
):
    # =========================
    # 1️⃣ EV
    # =========================
    ev_long = ai_probs["long"]["tp"] * RR - ai_probs["long"]["sl"]
    ev_short = ai_probs["short"]["tp"] * RR - ai_probs["short"]["sl"]

    if ev_long <= 0.4 and ev_short <= 0.4:
        return None

    if ev_long >= ev_short:
        side = "LONG"
        ev = ev_long
    else:
        side = "SHORT"
        ev = ev_short

    # =========================
    # 2️⃣ ATR → SL / TP %
    # =========================
    atr = compute_atr(ohlcv_df)
    atr_pct = atr / price

    raw_sl_pct = atr_pct * ATR_MULT
    sl_pct = clamp(raw_sl_pct, SL_MIN, SL_MAX)
    tp_pct = clamp(sl_pct * RR, TP_MIN, TP_MAX)

    if side == "LONG":
        stop_price = price * (1 - sl_pct)
        tp_price = price * (1 + tp_pct)
    else:
        stop_price = price * (1 + sl_pct)
        tp_price = price * (1 - tp_pct)

    # =========================
    # 3️⃣ RISK ENGINE (SINGLE SOURCE)
    # =========================
    allowed, risk_info, phase, reason = risk_manager.assess_trade(
        ev=ev,
        entry_price=price,
        stop_price=stop_price
    )

    if not allowed:
        return None

    # =========================
    # 4️⃣ FINAL SNAPSHOT
    # =========================
    return {
        "symbol": symbol,
        "side": side,
        "entry": round(price, 6),
        "sl": round(stop_price, 6),
        "tp": round(tp_price, 6),
        "sl_pct": round(sl_pct * 100, 2),
        "tp_pct": round(tp_pct * 100, 2),
        "ev": round(ev, 3),

        "allowed": True,
        "approved": True,
        "reason": reason,

        "risk": risk_info,
        "phase": phase,
        "probs": ai_probs,

        "timestamp": datetime.utcnow().isoformat()
    }


