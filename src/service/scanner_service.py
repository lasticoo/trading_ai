from src.data.binance_symbols import get_all_futures_symbols
from src.data.live_loader import LiveDataLoader
from src.service.trade_proposal import generate_trade_proposal
from src.db.models import TradeProposal, Account
from src.risk.risk_engine import RiskManager

MODEL_PATH = "models/tcn_trading_model.pt"


def _load_ai():
    """Load model jika ada. Return None jika belum ditraining."""
    try:
        from src.ai.inference import TradingAI
        from src.ai.load_model import load_trained_model
        model = load_trained_model(MODEL_PATH)
        return TradingAI(model)
    except FileNotFoundError:
        print(f"[WARN] Model tidak ditemukan di {MODEL_PATH}. Pakai mode dummy.")
        return None
    except Exception as e:
        print(f"[WARN] Gagal load model: {e}. Pakai mode dummy.")
        return None


def _dummy_probs():
    """Probabilitas acak untuk testing tanpa model."""
    import random
    tp = random.uniform(0.3, 0.7)
    sl = random.uniform(0.1, 0.4)
    none_ = max(0, 1 - tp - sl)
    return {
        "long":  {"tp": tp,  "sl": sl,  "none": none_},
        "short": {"tp": sl,  "sl": tp,  "none": none_}
    }


def run_scan(db):
    account = db.query(Account).first()
    if not account:
        from src.service.account_service import get_or_create_account
        account = get_or_create_account(db)

    symbols = get_all_futures_symbols()
    loader  = LiveDataLoader(interval="15m", lookback=150)
    ai      = _load_ai()

    risk_manager = RiskManager(
        equity_start=account.equity,
        equity_current=account.equity
    )

    created = 0

    for symbol in symbols:
        try:
            price, features, atr = loader.load_latest(symbol)

            if features.shape[0] < 20:
                continue

            ai_probs = ai.predict(features) if ai else _dummy_probs()
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

            # Hapus proposal PENDING lama untuk symbol ini
            db.query(TradeProposal).filter(
                TradeProposal.symbol == symbol,
                TradeProposal.status == "PENDING"
            ).delete()

            db.add(TradeProposal(
                symbol=proposal["symbol"],
                side=proposal["side"],
                entry=proposal["entry"],
                sl=proposal["sl"],
                tp=proposal["tp"],
                ev=proposal["ev"],
                status="PENDING"
            ))

            created += 1

        except Exception as e:
            print(f"[SCAN ERROR] {symbol}: {e}")
            continue

    db.commit()
    return {"status": "OK", "created": created, "scanned": len(symbols)}