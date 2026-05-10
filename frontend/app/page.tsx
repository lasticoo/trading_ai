"use client";

import { useEffect, useState } from "react";
import {
  scanMarket,
  getProposals,
  getAccount,
  acceptProposal,
  rejectProposal
} from "@/lib/api";

import AccountCard from "@/components/AccountCard";
import ProposalCard from "@/components/ProposalCard";
import LoadingOverlay from "@/components/LoadingOverlay";
import {
  getActiveTrades,
  closeTrade
} from "@/lib/api";

import ActiveTradeCard from "@/components/ActiveTradeCard";


export default function Dashboard() {
  const [account, setAccount] = useState<any | null>(null);
  const [proposals, setProposals] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [initialized, setInitialized] = useState(false);
  const [activeTrades, setActiveTrades] = useState<any[]>([]);


  // =========================
  // REFRESH DATA
  // =========================
  async function refresh() {
    try {
      const acc = await getAccount();
      setAccount(acc ?? null);

      const props = await getProposals();
      setProposals(Array.isArray(props) ? props : []);

      setInitialized(true);
    } catch (err) {
      console.error("❌ refresh error:", err);
      setProposals([]);
      setInitialized(true);
    }
    const trades = await getActiveTrades();
  setActiveTrades(Array.isArray(trades) ? trades : []);

  }

  // =========================
  // SCAN MARKET
  // =========================
  async function handleScan() {
    try {
      setLoading(true);
      await scanMarket();
      await refresh();
    } catch (err) {
      console.error("❌ scan failed:", err);
    } finally {
      setLoading(false);
    }
  }

  // =========================
  // INIT
  // =========================
  useEffect(() => {
    refresh();
  }, []);

  if (!initialized) {
    return <LoadingOverlay />;
  }

  return (
    <main className="p-6 space-y-6 relative">
      {loading && (
        <LoadingOverlay
          equity={account?.equity ?? 0}
          maxTrades={account?.max_trades}
        />
      )}

      <AccountCard
        equity={account?.equity ?? 0}
        maxTrades={account?.max_trades}
      />

      <button
        onClick={handleScan}
        disabled={loading}
        className="bg-blue-600 px-4 py-2 rounded text-white disabled:opacity-50"
      >
        {loading ? "Scanning market..." : "Scan Market"}
      </button>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {proposals.length === 0 && (
          <div className="text-gray-400 text-sm">
            No trade proposals available
          </div>
        )}

        {proposals.map((p) => (
          <ProposalCard
            key={p.id}
            proposal={p}
            onAccept={async () => {
              await acceptProposal(p.id);
              refresh();
            }}
            onReject={async () => {
              await rejectProposal(p.id);
              refresh();
            }}
          />
        ))}
      </div>
      {/* ACTIVE TRADES */}
<div className="space-y-3">
  <h2 className="text-lg font-semibold">Active Trades</h2>

  {activeTrades.length === 0 && (
    <div className="text-gray-400 text-sm">
      No active trades
    </div>
  )}

  {activeTrades.map((t) => (
    <ActiveTradeCard
      key={t.id}
      trade={t}
      onClose={async (result) => {
        const rMultiple = result === "TP" ? 2.0 : -1.0;
        await closeTrade(t.id, result, rMultiple);
        refresh();
      }}
    />
  ))}
</div>

    </main>
  );
}
