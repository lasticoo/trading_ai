from src.db.models import TradeProposal

def list_proposals(db):
    return db.query(TradeProposal).filter_by(status="PENDING").all()
