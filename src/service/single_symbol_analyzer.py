from src.service.trade_proposal import generate_trade_proposal

class SingleSymbolAnalyzer:
    def __init__(self, ai, risk_manager, data_loader):
        self.ai = ai
        self.risk_manager = risk_manager
        self.data_loader = data_loader

    def analyze(self, symbol: str):
        # ambil harga & feature terbaru
        price, features, atr = self.data_loader.load_latest(symbol)

        # probabilitas mentah dari model
        probs = self.ai.predict_with_probs(features)

        # buat proposal
        proposal = generate_trade_proposal(
            symbol=symbol,
            price=price,
            ai_probs=probs,
            risk_manager=self.risk_manager
        )

        return proposal
