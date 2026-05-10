export default function LoadingOverlay({
  equity,
  maxTrades
}: {
  equity?: number;
  maxTrades?: number;
}) {
  return (
    <div className="absolute inset-0 bg-black/70 flex items-center justify-center z-50">
      <div className="text-center space-y-2">
        <div className="text-lg font-semibold">Scanning market…</div>
        {equity !== undefined && (
          <div className="text-sm text-gray-400">
            Equity: ${equity.toFixed(2)}
          </div>
        )}
        {maxTrades !== undefined && (
          <div className="text-xs text-gray-500">
            Max trades: {maxTrades}
          </div>
        )}
      </div>
    </div>
  );
}
