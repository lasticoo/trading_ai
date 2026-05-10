from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.api.deps import get_db
from src.service.scanner_service import run_scan

router = APIRouter(tags=["default"])

@router.post("/scan")
def scan_market(db: Session = Depends(get_db)):
    return run_scan(db)
