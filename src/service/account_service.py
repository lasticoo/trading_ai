from src.db.models import Account
from datetime import datetime

# =========================
# CONFIG (SINGLE SOURCE)
# =========================
DEFAULT_EQUITY = 25.0

# =========================
# INIT ACCOUNT (ONCE)
# =========================
def get_or_create_account(db):
    account = db.query(Account).first()
    if not account:
        account = Account(
            equity=DEFAULT_EQUITY,
            max_trades=5,
            updated_at=datetime.utcnow()
        )
        db.add(account)
        db.commit()
        db.refresh(account)
    return account


# =========================
# GET ACCOUNT STATE
# =========================
def get_account_state(db):
    account = get_or_create_account(db)
    return {
        "equity": round(account.equity, 2),
        "max_trades": account.max_trades,
        "updated_at": account.updated_at.isoformat()
    }


# =========================
# UPDATE EQUITY (MANUAL / ADMIN)
# =========================
def update_equity(db, new_equity: float):
    account = get_or_create_account(db)
    account.equity = float(new_equity)
    account.updated_at = datetime.utcnow()
    db.commit()

    return {
        "equity": round(account.equity, 2),
        "updated_at": account.updated_at.isoformat()
    }


# =========================
# APPLY TRADE RESULT (CORE LOGIC)
# =========================
def apply_trade_result(db, r_multiple: float, risk_pct: float):
    """
    r_multiple:
        +2.0  -> TP
        -1.0  -> SL

    risk_pct:
        0.015 -> 1.5%
        0.01  -> 1%
    """
    account = get_or_create_account(db)

    # ✅ R-based PnL (BENAR)
    pnl = account.equity * (risk_pct * r_multiple)
    account.equity += pnl
    account.updated_at = datetime.utcnow()

    db.commit()

    return {
        "new_equity": round(account.equity, 2),
        "pnl": round(pnl, 2),
        "r_multiple": r_multiple,
        "risk_pct": risk_pct
    }
