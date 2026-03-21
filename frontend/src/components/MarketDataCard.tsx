'use client';

interface MarketDataQuote {
  ticker: string;
  name: string;
  price: number;
  change?: number;
  changePercent?: number;
}

interface MarketDataCardProps {
  ticker: string;
  data?: MarketDataQuote | null;
  onSelect?: (ticker: string) => void;
  compact?: boolean;
}

export default function MarketDataCard({ ticker, data, onSelect, compact = false }: MarketDataCardProps) {
  const isPositive = (data?.changePercent ?? 0) >= 0;

  // Stable skeleton - prevents layout shift
  if (!data) {
    return (
      <div className={`bg-white rounded-lg border border-gray-200 ${compact ? 'p-2' : 'p-4'} animate-pulse`}>
        <div className="flex justify-between items-start mb-2">
          <div>
            <div className="h-4 bg-gray-200 rounded w-16 mb-1"></div>
            <div className="h-3 bg-gray-100 rounded w-24"></div>
          </div>
          <div className="h-5 bg-gray-100 rounded w-10"></div>
        </div>
        <div className="h-6 bg-gray-200 rounded w-20"></div>
      </div>
    );
  }

  return (
    <div
      className={`bg-white rounded-lg border border-gray-200 hover:border-blue-400 transition-all cursor-pointer ${
        isPositive ? 'hover:shadow-green-50' : 'hover:shadow-red-50'
      } ${compact ? 'p-2' : 'p-4'}`}
      onClick={() => onSelect?.(ticker)}
    >
      <div className="flex justify-between items-start mb-1">
        <div>
          <span className={`font-bold ${compact ? 'text-sm' : 'text-base'}`}>{data.ticker}</span>
          <span className={`text-gray-400 ml-1 ${compact ? 'text-xs' : 'text-sm'}`}>
            {data.name.length > 12 ? data.name.slice(0, 12) + '...' : data.name}
          </span>
        </div>
        {!compact && data.changePercent !== undefined && (
          <span className={`text-xs px-1.5 py-0.5 rounded ${
            isPositive ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
          }`}>
            {isPositive ? '+' : ''}{data.changePercent?.toFixed(1)}%
          </span>
        )}
      </div>
      <div className={`font-bold ${compact ? 'text-base' : 'text-xl'}`}>
        ${data.price?.toFixed(2) ?? 'N/A'}
      </div>
      {compact && data.changePercent !== undefined && (
        <div className={`text-xs ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
          {isPositive ? '+' : ''}{data.changePercent?.toFixed(1)}%
        </div>
      )}
    </div>
  );
}
