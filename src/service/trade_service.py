from src.db.models import TradeProposal, ActiveTrade, TradeHistory, Account

MAX_ACTIVE = 5

def approve_trade(db, proposal_id):
    active_count = db.query(ActiveTrade).count()
    if active_count >= MAX_ACTIVE:
        raise Exception("MAX ACTIVE TRADES")

    proposal = db.query(TradeProposal).get(proposal_id)
    proposal.status = "TAKEN"

    trade = ActiveTrade(
        symbol=proposal.symbol,
        side=proposal.side,
        entry=proposal.entry,
        sl=proposal.sl,
        tp=proposal.tp,
        risk_pct=1.5
    )

    db.add(trade)
    db.commit()
    return trade

def close_trade(db, trade_id, result, r_multiple):
    trade = db.query(ActiveTrade).get(trade_id)
    history = TradeHistory(
        symbol=trade.symbol,
        side=trade.side,
        result=result,
        r_multiple=r_multiple
    )

    account = db.query(Account).first()
    account.equity += account.equity * (r_multiple * 0.01)

    db.add(history)
    db.delete(trade)
    db.commit()
