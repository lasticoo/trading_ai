import { TradeProposal } from "@/types/trading";

export default function ProposalCard({
  proposal,
  onAccept,
  onReject
}: {
  proposal: TradeProposal;
  onAccept: () => void;
  onReject: () => void;
}) {
  return (
    <div className="bg-gray-800 p-4 rounded-xl space-y-2">
      <div className="flex justify-between">
        <span className="font-semibold">{proposal.symbol}</span>
        <span
          className={
            proposal.side === "LONG"
              ? "text-green-400"
              : "text-red-400"
          }
        >
          {proposal.side}
        </span>
      </div>

      <div className="text-sm text-gray-400">
        Entry: {proposal.entry} | SL: {proposal.sl} | TP: {proposal.tp}
      </div>

      <div className="text-sm">EV: {proposal.ev}</div>

      <div className="flex gap-2">
        <button
          onClick={onAccept}
          className="bg-green-600 px-3 py-1 rounded"
        >
          ACCEPT
        </button>
        <button
          onClick={onReject}
          className="bg-red-600 px-3 py-1 rounded"
        >
          REJECT
        </button>
      </div>
    </div>
  );
}
