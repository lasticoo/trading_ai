from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from src.db.database import Base

class Account(Base):
    __tablename__ = "account"
    id = Column(Integer, primary_key=True)
    equity = Column(Float, default=24.0)
    max_trades = Column(Integer, default=5)
    updated_at = Column(DateTime, default=datetime.utcnow)


class TradeProposal(Base):
    __tablename__ = "trade_proposals"
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    side = Column(String)
    entry = Column(Float)
    sl = Column(Float)
    tp = Column(Float)
    ev = Column(Float)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)

class ActiveTrade(Base):
    __tablename__ = "active_trades"
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    side = Column(String)
    entry = Column(Float)
    sl = Column(Float)
    tp = Column(Float)
    risk_pct = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class TradeHistory(Base):
    __tablename__ = "trade_history"
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    side = Column(String)
    result = Column(String)  # TP / SL
    r_multiple = Column(Float)
    closed_at = Column(DateTime, default=datetime.utcnow)
