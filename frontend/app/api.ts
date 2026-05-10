const API_BASE = "http://localhost:8000";

export async function scanMarket() {
  return fetch(`${API_BASE}/scan`, { method: "POST" }).then(r => r.json());
}

export async function getProposals() {
  return fetch(`${API_BASE}/proposals`).then(r => r.json());
}

export async function rejectProposal(id: number) {
  return fetch(`${API_BASE}/proposals/${id}/reject`, { method: "POST" });
}

export async function acceptProposal(id: number) {
  return fetch(`${API_BASE}/trades/accept`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ proposal_id: id })
  });
}

export async function getAccount() {
  return fetch(`${API_BASE}/account`).then(r => r.json());
}

export async function applyResult(r_multiple: number, risk_pct: number) {
  return fetch(`${API_BASE}/account/apply-result`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ r_multiple, risk_pct })
  }).then(r => r.json());
}
  
// =========================
// ACTIVE TRADES
// =========================
export const getActiveTrades = async () => {
  const r = await fetch(`${API_BASE}/`);
  if (!r.ok) return [];
  return r.json();
};

// =========================
// CLOSE TRADE
// =========================
export const closeTrade = async (
  tradeId: number,
  result: "TP" | "SL",
  r_multiple: number
) => {
  const r = await fetch(`${API_BASE}/${tradeId}/close`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ result, r_multiple })
  });

  if (!r.ok) throw new Error("Close trade failed");
  return r.json();
};
