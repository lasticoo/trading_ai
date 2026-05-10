from src.data.binance_symbols import get_all_futures_symbols
from src.data.live_loader import LiveDataLoader
from src.service.trade_proposal import generate_trade_proposal
from src.db.models import TradeProposal, Account
from src.risk.risk_engine import RiskManager
from src.ai.inference import TradingAI
from src.ai.load_model import load_trained_model

MODEL_PATH = "models/tcn_trading_model.pt"

def run_scan(db):
    # =========================
    # 0️⃣ ACCOUNT STATE (SINGLE SOURCE OF TRUTH)
    # =========================
    account = db.query(Account).first()
    if not account:
        raise Exception("Account not initialized")

    # =========================
    # 1️⃣ INIT CORE COMPONENTS
    # =========================
    symbols = get_all_futures_symbols()
    loader = LiveDataLoader(interval="15m", lookback=150)

    model = load_trained_model(MODEL_PATH)
    ai = TradingAI(model)

    # ✅ FIX UTAMA ADA DI SINI
    risk_manager = RiskManager(
        equity_start=account.equity,
        equity_current=account.equity
    )

    created = 0

    # =========================
    # 2️⃣ SCAN LOOP
    # =========================
    for symbol in symbols:
        try:
            # =========================
            # LOAD LIVE DATA
            # =========================
            price, features, atr = loader.load_latest(symbol)

            if features.shape[0] < 50:
                continue

            # =========================
            # AI INFERENCE
            # =========================
            ai_probs = ai.predict(features)
            if not ai_probs:
                continue

            # =========================
            # TRADE DECISION
            # =========================
            ohlcv_df = loader.fetch_klines(symbol)

            proposal = generate_trade_proposal(
                symbol=symbol,
                price=price,
                ai_probs=ai_probs,
                risk_manager=risk_manager,
                ohlcv_df=ohlcv_df
            )

            if proposal is None:
                continue

            # =========================
            # SAVE SNAPSHOT (DB)
            # =========================
            db.add(
                TradeProposal(
                    symbol=proposal["symbol"],
                    side=proposal["side"],
                    entry=proposal["entry"],
                    sl=proposal["sl"],
                    tp=proposal["tp"],
                    ev=proposal["ev"],
                    status="PENDING",
                    meta=proposal
                )
            )

            created += 1

        except Exception as e:
            print(f"[SCAN ERROR] {symbol}: {e}")
            continue

    db.commit()

    return {
        "status": "OK",
        "created": created
    }
