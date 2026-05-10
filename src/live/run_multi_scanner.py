from src.ai.load_model import load_trained_model
from src.ai.inference import TradingAI
from src.scanner.multi_symbol_scanner import scan_symbols
from src.service.trade_proposal import generate_trade_proposal
from src.risk.risk_engine import RiskManager
from src.data.binance_symbols import get_all_futures_symbols

MODEL_PATH = "models/tcn_trading_model.pt"

print("\n🔍 MULTI-SYMBOL SCANNER (BINANCE FUTURES)\n")

symbols = get_all_futures_symbols()
print(f"Loaded {len(symbols)} futures symbols")

model = load_trained_model(MODEL_PATH)
ai = TradingAI(model)

risk_manager = RiskManager(
    equity_start=25.0,
    equity_current=25.0
)

candidates = scan_symbols(symbols, ai, top_n=10)

if not candidates:
    print("❌ NO VALID SETUP FOUND")
else:
    for c in candidates:
        proposal = generate_trade_proposal(
        symbol=c["symbol"],
        price=c["price"],
        ai_probs=c["ai_probs"],
        ohlcv_df=c["ohlcv_df"],   # 🔑 WAJIB
        risk_manager=risk_manager
        )


        probs = proposal["probs"][proposal["side"].lower()]

        print(
            f"{proposal['symbol']:10s} | "
            f"{proposal['side']:5s} | "
            f"EV: {proposal['ev']:+.3f} | "
            f"pTP: {probs['tp']:.2f} "
            f"pSL: {probs['sl']:.2f} "
            f"pNONE: {probs['none']:.2f} | "
            f"{'✅ APPROVED' if proposal['approved'] else '❌ REJECTED'}"
        )
