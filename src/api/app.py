from fastapi import FastAPI
from src.service.trade_proposal import generate_trade_proposal
from src.risk.risk_engine import RiskManager

app = FastAPI()

risk_manager = RiskManager(
    equity_start=25.0,
    equity_current=25.0
)

@app.post("/analyze")
def analyze_market(payload: dict):
    symbol = payload["symbol"]
    price = payload["price"]
    ai_probs = payload["ai_probs"]  # dari AI inference

    proposal = generate_trade_proposal(
        symbol=symbol,
        price=price,
        ai_probs=ai_probs,
        risk_manager=risk_manager
    )

    return proposal or {"message": "NO TRADE"}
