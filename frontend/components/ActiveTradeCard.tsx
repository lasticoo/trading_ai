import { ActiveTrade } from "@/types/trading";

export default function ActiveTradeCard({
  trade,
  onClose
}: {
  trade: ActiveTrade;
  onClose: (result: "TP" | "SL") => void;
}) {
  return (
    <div className="bg-gray-800 p-4 rounded-xl space-y-2">
      <div className="font-semibold">{trade.symbol}</div>

      <div className="text-sm text-gray-400">
        {trade.side} | Entry {trade.entry}
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => onClose("TP")}
          className="bg-green-600 px-3 py-1 rounded"
        >
          TP
        </button>
        <button
          onClick={() => onClose("SL")}
          className="bg-red-600 px-3 py-1 rounded"
        >
          SL
        </button>
      </div>
    </div>
  );
}
