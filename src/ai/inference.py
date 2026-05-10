import torch
import numpy as np

class TradingAI:
    def __init__(self, model, device="cpu"):
        self.model = model
        self.device = device

    def predict(self, X):
        """
        X shape: (SEQ_LEN, FEATURE_DIM)
        """
        X = torch.tensor(X, dtype=torch.float32)
        X = X.T.unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits = self.model(X)
            probs = torch.sigmoid(logits).cpu().numpy()[0]

        return {
            "long": {
                "tp": float(probs[0]),
                "sl": float(probs[1]),
                "none": float(probs[2]),
            },
            "short": {
                "tp": float(probs[3]),
                "sl": float(probs[4]),
                "none": float(probs[5]),
            },
        }
    def predict_with_probs(self, features):
        """
        Return raw probabilities untuk analisis & debugging
        """
        probs = self.predict(features)  
        # asumsi predict() sudah return dict

        return {
            "long": {
                "tp": float(probs["long"]["tp"]),
                "sl": float(probs["long"]["sl"]),
                "none": float(probs["long"]["none"]),
            },
            "short": {
                "tp": float(probs["short"]["tp"]),
                "sl": float(probs["short"]["sl"]),
                "none": float(probs["short"]["none"]),
            }}
