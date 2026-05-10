from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.api.deps import get_db
from src.db.models import ActiveTrade, TradeProposal, TradeHistory

router = APIRouter(tags=["default"])

# =========================
# GET ACTIVE TRADES
# (Swagger: GET /)
# =========================
@router.get("/")
def get_active_trades(db: Session = Depends(get_db)):
    return db.query(ActiveTrade).all()


# =========================
# ACCEPT PROPOSAL
# (Swagger: POST /{proposal_id}/accept)
# =========================
@router.post("/{proposal_id}/accept")
def accept_proposal(proposal_id: int, db: Session = Depends(get_db)):
    proposal = db.query(TradeProposal).get(proposal_id)
    if not proposal:
        return {"error": "Proposal not found"}

    trade = ActiveTrade(
        symbol=proposal.symbol,
        side=proposal.side,
        entry=proposal.entry,
        sl=proposal.sl,
        tp=proposal.tp,
        risk_pct=1.5
    )

    db.add(trade)
    proposal.status = "ACCEPTED"
    db.commit()

    return {"status": "ACCEPTED", "trade_id": trade.id}


# =========================
# REJECT PROPOSAL
# (Swagger: POST /{proposal_id}/reject)
# =========================
@router.post("/{proposal_id}/reject")
def reject_proposal(proposal_id: int, db: Session = Depends(get_db)):
    proposal = db.query(TradeProposal).get(proposal_id)
    if not proposal:
        return {"error": "Proposal not found"}

    proposal.status = "REJECTED"
    db.commit()

    return {"status": "REJECTED"}


# =========================
# CLOSE TRADE
# (Swagger: POST /{trade_id}/close)
# =========================
@router.post("/{trade_id}/close")
def close_trade(trade_id: int, result: str, r_multiple: float, db: Session = Depends(get_db)):
    trade = db.query(ActiveTrade).get(trade_id)
    if not trade:
        return {"error": "Trade not found"}

    history = TradeHistory(
        symbol=trade.symbol,
        side=trade.side,
        result=result,
        r_multiple=r_multiple
    )

    db.add(history)
    db.delete(trade)
    db.commit()

    return {"status": "CLOSED"}
