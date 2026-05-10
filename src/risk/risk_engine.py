from dataclasses import dataclass
from datetime import datetime, timedelta

# =========================
# GLOBAL HARD RULES
# =========================
MAX_TRADES_PER_DAY = 5
MAX_LOSS_PER_DAY = 2
COOLDOWN_MINUTES = 30

# =========================
# PHASE DEFINITIONS
# =========================
PHASES = {
    1: {"min": 0,   "max": 200},
    2: {"min": 200, "max": 800},
    3: {"min": 800, "max": float("inf")}
}

# =========================
# PHASE CONFIG
# =========================
PHASE_CONFIG = {
    1: {
        "base_risk": 0.015,
        "dd_limit": 0.30,
        "dd_reduce_risk": 0.01
    },
    2: {
        "base_risk": 0.01,
        "dd_limit": 0.25,
        "pause_below": 160
    },
    3: {
        "base_risk": 0.0075,
        "dd_limit": 0.20,
        "dd_soft": 0.15,
        "dd_reduce_risk": 0.005
    }
}

# =========================
# UTIL
# =========================
def detect_phase(equity: float):
    for phase, r in PHASES.items():
        if r["min"] <= equity < r["max"]:
            return phase
    return 3


def calculate_position(
    equity,
    entry_price,
    stop_price,
    risk_pct,
    leverage=10
):
    sl_pct = abs(entry_price - stop_price) / entry_price
    sl_pct = max(sl_pct, 0.001)

    risk_amount = equity * risk_pct
    notional = risk_amount / sl_pct
    qty = notional / entry_price
    margin = notional / leverage

    return {
        "risk_pct": round(risk_pct * 100, 2),
        "risk_$": round(risk_amount, 2),
        "qty": round(qty, 4),
        "margin": round(margin, 2),
        "leverage": leverage
    }


# =========================
# DAILY RISK MANAGER
# =========================
@dataclass
class RiskManager:
    equity_start: float
    equity_current: float

    phase: int = 1
    phase_peak: float = None

    trades_today: int = 0
    losses_today: int = 0
    last_trade_time: datetime = None
    trading_enabled: bool = True

    def __post_init__(self):
        self.phase = detect_phase(self.equity_current)
        self.phase_peak = self.equity_current

    def update_phase(self):
        new_phase = detect_phase(self.equity_current)
        if new_phase != self.phase:
            self.phase = new_phase
            self.phase_peak = self.equity_current

    def can_trade(self):
        if not self.trading_enabled:
            return False, "TRADING_DISABLED"

        if self.trades_today >= MAX_TRADES_PER_DAY:
            return False, "MAX_TRADES_REACHED"

        if self.losses_today >= MAX_LOSS_PER_DAY:
            self.trading_enabled = False
            return False, "DAILY_STOP_HIT"

        if self.last_trade_time:
            if datetime.utcnow() < self.last_trade_time + timedelta(minutes=COOLDOWN_MINUTES):
                return False, "COOLDOWN"

        return True, "OK"

    def get_effective_risk(self):
        cfg = PHASE_CONFIG[self.phase]
        risk = cfg["base_risk"]

        dd = (self.phase_peak - self.equity_current) / self.phase_peak

        if self.phase == 1 and dd > cfg["dd_limit"]:
            risk = cfg["dd_reduce_risk"]

        if self.phase == 2 and self.equity_current < cfg["pause_below"]:
            self.trading_enabled = False
            return 0, "PHASE2_PAUSE"

        if self.phase == 3:
            if dd > cfg["dd_soft"]:
                risk = cfg["dd_reduce_risk"]
            if dd > cfg["dd_limit"]:
                self.trading_enabled = False
                return 0, "PHASE3_MAX_DD"

        return risk, "OK"

    # =========================
    # SINGLE PUBLIC API
    # =========================
    def assess_trade(self, ev, entry_price, stop_price):
        allowed, reason = self.can_trade()
        if not allowed:
            return False, None, self.phase, reason

        if ev < 0.4:
            return False, None, self.phase, "EV_TOO_LOW"

        risk_pct, risk_reason = self.get_effective_risk()
        if risk_pct <= 0:
            return False, None, self.phase, risk_reason

        pos = calculate_position(
            equity=self.equity_current,
            entry_price=entry_price,
            stop_price=stop_price,
            risk_pct=risk_pct
        )

        return True, pos, self.phase, "APPROVED"
