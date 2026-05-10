// === PROPOSAL DARI AI ===
export interface TradeProposal {
  id: number;
  symbol: string;
  side: "LONG" | "SHORT";
  entry: number;
  sl: number;
  tp: number;
  ev: number;
  status: "PENDING" | "REJECTED" | "ACCEPTED";
  created_at: string;
}

// === TRADE YANG SEDANG BERJALAN ===
export interface ActiveTrade {
  id: number;
  symbol: string;
  side: "LONG" | "SHORT";
  entry: number;
  sl: number;
  tp: number;
  risk_pct: number;
  created_at: string;
}
