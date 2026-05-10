export default function AccountCard({
  equity,
  maxTrades
}: {
  equity: number;
  maxTrades?: number;
}) {
  return (
    <div className="bg-gray-900 p-4 rounded-xl space-y-1">
      <div className="text-gray-400 text-sm">Account Equity</div>
      <div className="text-2xl font-bold">${equity.toFixed(2)}</div>

      {maxTrades !== undefined && (
        <div className="text-xs text-gray-500">
          Max trades: {maxTrades}
        </div>
      )}
    </div>
  );
}
