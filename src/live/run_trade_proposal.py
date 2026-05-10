import time
from copy import deepcopy

from src.ai.load_model import load_trained_model
from src.ai.inference import TradingAI
from src.scanner.multi_symbol_scanner import scan_symbols
from src.service.trade_proposal import generate_trade_proposal
from src.risk.risk_engine import RiskManager
from src.db.db import log_trade_proposal
from src.data.binance_symbols import get_all_futures_symbols

# =========================
# CONFIG
# =========================
MODEL_PATH = "models/tcn_trading_model.pt"
SCAN_INTERVAL_SEC = 1 * 1   # 15 menit
TOP_N = 5                     # ambil 5 EV terbaik

# =========================
# INIT MODEL
# =========================
model = load_trained_model(MODEL_PATH)
ai = TradingAI(model)

# =========================
# INIT RISK (GLOBAL STATE)
# =========================
base_risk_manager = RiskManager(
    equity_start=25.0,
    equity_current=15.0
)

# =========================
# LOAD SYMBOLS
# =========================
symbols = get_all_futures_symbols()

print("🚀 LIVE Multi-Symbol Trade Proposal Service started")
print(f"📊 Loaded {len(symbols)} Binance Futures symbols")

# =========================
# MAIN LOOP
# =========================
while True:
    try:
        print("\n🔍 Scanning market...")

        # =========================
        # 1️⃣ SCAN MARKET
        # =========================
        candidates = scan_symbols(
            symbols,
            ai,
            top_n=TOP_N
        )

        if not candidates:
            print("❌ No valid setup found in this cycle")
            time.sleep(SCAN_INTERVAL_SEC)
            continue

        # =========================
        # 2️⃣ GENERATE PROPOSALS
        # =========================
        for c in candidates:
            # ⚠️ clone risk manager (preview only)
            rm = deepcopy(base_risk_manager)

            proposal = generate_trade_proposal(
            symbol=c["symbol"],
            price=c["price"],
            ai_probs=c["ai_probs"],
            ohlcv_df=c["ohlcv_df"],   # 🔑 WAJIB
            risk_manager=rm
        )


            if proposal is None:
                continue

            if not proposal.get("approved", False):
                continue

            # =========================
            # 3️⃣ LOG & DISPLAY
            # =========================
            log_trade_proposal(proposal)

            print("\n📦 TRADE PROPOSAL")
            print(f"symbol : {proposal['symbol']}")
            print(f"side   : {proposal['side']}")
            print(f"EV     : {proposal['ev']}")
            print(f"entry  : {proposal['entry']}")
            print(f"sl     : {proposal['sl']}")
            print(f"tp     : {proposal['tp']}")
            print(f"risk   : {proposal['risk']}")
            print("-" * 40)

        # =========================
        # 4️⃣ WAIT NEXT CANDLE
        # =========================
        time.sleep(SCAN_INTERVAL_SEC)

    except Exception as e:
        print("⚠️ ERROR:", repr(e))
        time.sleep(60)
