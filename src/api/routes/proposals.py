from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.db.models import TradeProposal, ActiveTrade, Account

router = APIRouter()


@router.get("/proposals")
def list_proposals(db: Session = Depends(get_db)):
    return db.query(TradeProposal).filter_by(status="PENDING").all()


@router.post("/{proposal_id}/accept")
def accept_proposal(proposal_id: int, db: Session = Depends(get_db)):
    proposal = db.query(TradeProposal).get(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    if proposal.status != "PENDING":
        raise HTTPException(status_code=400, detail="Proposal sudah diproses")

    account = db.query(Account).first()
    active_count = db.query(ActiveTrade).count()

    if active_count >= account.max_trades:
        raise HTTPException(status_code=400, detail="Batas max trade aktif tercapai")

    active = ActiveTrade(
        symbol=proposal.symbol,
        side=proposal.side,
        entry=proposal.entry,
        sl=proposal.sl,
        tp=proposal.tp,
        risk_pct=1.5
    )

    proposal.status = "ACCEPTED"
    db.add(active)
    db.commit()
    db.refresh(active)

    return {"status": "ACCEPTED", "active_trade_id": active.id}


@router.post("/{proposal_id}/reject")
def reject_proposal(proposal_id: int, db: Session = Depends(get_db)):
    proposal = db.query(TradeProposal).get(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    proposal.status = "REJECTED"
    db.commit()

    return {"status": "REJECTED", "id": proposal_id}