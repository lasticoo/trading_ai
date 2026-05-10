from src.ai.load_model import load_trained_model
from src.ai.inference import TradingAI
from src.risk.risk_engine import RiskManager
from src.service.single_symbol_analyzer import SingleSymbolAnalyzer
from src.data.live_loader import LiveDataLoader

MODEL_PATH = "models/tcn_trading_model.pt"

model = load_trained_model(MODEL_PATH)
ai = TradingAI(model)

risk_manager = RiskManager(
    equity_start=25.0,
    equity_current=25.0
)

data_loader = LiveDataLoader(interval="15m")

analyzer = SingleSymbolAnalyzer(ai, risk_manager, data_loader)

symbol = input("Masukkan symbol (contoh ETHUSDT): ").strip().upper()

result = analyzer.analyze(symbol)

print("\n📊 ANALYSIS RESULT")
print("Symbol :", result["symbol"])
print("Side   :", result["side"])
print("EV     :", result["ev"])
print("Probabilities:")
for k, v in result["probs"][result["side"].lower()].items():
    print(f"  {k}: {v:.2f}")

print("Decision:", "APPROVED ✅" if result["approved"] else "REJECTED ❌")
print("Reason  :", result["reason"])
