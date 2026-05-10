const API = "http://localhost:8000";

// =========================
// SCAN MARKET
// =========================
export const scanMarket = async () => {
  const r = await fetch(`${API}/scan`, { method: "POST" });
  if (!r.ok) throw new Error("Scan failed");
  return r.json();
};

// =========================
// PROPOSALS
// =========================
export const getProposals = async () => {
  const r = await fetch(`${API}/proposals`);
  if (!r.ok) return [];
  return r.json();
};

export const acceptProposal = async (id: number) => {
  const r = await fetch(`${API}/${id}/accept`, { method: "POST" });
  if (!r.ok) throw new Error("Accept proposal failed");
  return r.json();
};

export const rejectProposal = async (id: number) => {
  const r = await fetch(`${API}/${id}/reject`, { method: "POST" });
  if (!r.ok) throw new Error("Reject proposal failed");
  return r.json();
};

// =========================
// ACCOUNT
// =========================
export const getAccount = async () => {
  const r = await fetch(`${API}/account/`);
  if (!r.ok) throw new Error("Get account failed");
  return r.json();
};

// =========================
// ACTIVE TRADES
// GET /
// =========================
export const getActiveTrades = async () => {
  const r = await fetch(`${API}/`);
  if (!r.ok) return [];
  return r.json();
};

// =========================
// CLOSE TRADE
// POST /{trade_id}/close
// =========================
export const closeTrade = async (
  tradeId: number,
  result: "TP" | "SL",
  r_multiple: number
) => {
  const r = await fetch(`${API}/${tradeId}/close`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      result,
      r_multiple
    })
  });

  if (!r.ok) throw new Error("Close trade failed");
  return r.json();
};
