from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.api.deps import get_db
from src.service.account_service import (
    get_account_state,
    update_equity,
    apply_trade_result
)

router = APIRouter(prefix="/account", tags=["account"])


class ApplyResultRequest(BaseModel):
    r_multiple: float
    risk_pct: float


@router.get("/")
def get_account(db: Session = Depends(get_db)):
    return get_account_state(db)


@router.post("/update")
def set_equity(equity: float, db: Session = Depends(get_db)):
    return update_equity(db, equity)


@router.post("/apply-result")
def apply_result(
    payload: ApplyResultRequest,
    db: Session = Depends(get_db)
):
    return apply_trade_result(db, payload.r_multiple, payload.risk_pct)