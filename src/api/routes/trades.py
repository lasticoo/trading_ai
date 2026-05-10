from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.api.deps import get_db
from src.db.models import ActiveTrade, TradeHistory

router = APIRouter(tags=["trades"])


class CloseTradeRequest(BaseModel):
    result: str        # "TP" atau "SL"
    r_multiple: float  # +2.0 untuk TP, -1.0 untuk SL


@router.get("/")
def get_active_trades(db: Session = Depends(get_db)):
    return db.query(ActiveTrade).all()


@router.post("/{trade_id}/close")
def close_trade(
    trade_id: int,
    payload: CloseTradeRequest,
    db: Session = Depends(get_db)
):
    trade = db.query(ActiveTrade).get(trade_id)
    if not trade:
        raise HTTPException(status_code=404, detail="Trade tidak ditemukan")

    history = TradeHistory(
        symbol=trade.symbol,
        side=trade.side,
        result=payload.result,
        r_multiple=payload.r_multiple
    )

    db.add(history)
    db.delete(trade)
    db.commit()

    return {"status": "CLOSED", "result": payload.result}