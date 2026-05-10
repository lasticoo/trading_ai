class SingleSymbolAnalyzer:
    def __init__(self, ai, risk_manager, data_loader, rr=2.0):
        self.ai = ai
        self.risk_manager = risk_manager
        self.data_loader = data_loader
        self.rr = rr

    def analyze(self, symbol):
        # ⬇⬇⬇ FIX UTAMA ADA DI SINI
        price, features, atr = self.data_loader.load_latest(symbol)

        # =========================
        # AI INFERENCE
        # =========================
        ai_probs = self.ai.predict(features)

        long_probs = ai_probs["long"]
        short_probs = ai_probs["short"]

        ev_long = long_probs["tp"] * self.rr - long_probs["sl"]
        ev_short = short_probs["tp"] * self.rr - short_probs["sl"]

        if ev_long <= 0 and ev_short <= 0:
            return {
                "symbol": symbol,
                "side": "NO_TRADE",
                "ev": round(max(ev_long, ev_short), 3),
                "probs": ai_probs,
                "approved": False,
                "reason": "EV_TOO_LOW"
            }

        side = "LONG" if ev_long > ev_short else "SHORT"
        ev = max(ev_long, ev_short)

        # =========================
        # RISK ENGINE CHECK
        # =========================
        can_trade, reason = self.risk_manager.can_trade()
        if not can_trade:
            return {
                "symbol": symbol,
                "side": side,
                "ev": round(ev, 3),
                "probs": ai_probs,
                "approved": False,
                "reason": reason
            }

        risk_pct, risk_reason = self.risk_manager.get_effective_risk()
        if risk_pct <= 0:
            return {
                "symbol": symbol,
                "side": side,
                "ev": round(ev, 3),
                "probs": ai_probs,
                "approved": False,
                "reason": risk_reason
            }

        # =========================
        # ATR-BASED TP / SL (INTRADAY)
        # =========================
        sl_dist = 0.5 * atr
        tp_dist = 1.0 * atr

        if side == "LONG":
            sl = price - sl_dist
            tp = price + tp_dist
        else:
            sl = price + sl_dist
            tp = price - tp_dist

        return {
            "symbol": symbol,
            "side": side,
            "entry": round(price, 6),
            "sl": round(sl, 6),
            "tp": round(tp, 6),
            "atr": round(atr, 6),
            "ev": round(ev, 3),
            "probs": ai_probs,
            "approved": True,
            "reason": "APPROVED"
        }
