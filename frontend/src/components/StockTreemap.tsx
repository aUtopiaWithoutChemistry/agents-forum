'use client';

import { useState, useEffect } from 'react';
import { Treemap, Tooltip, ResponsiveContainer } from 'recharts';
import { marketApi } from '@/lib/api';

// Top S&P 500 stocks by approximate weight
const SP500_STOCKS = [
  { ticker: 'AAPL', name: 'Apple', weight: 7.5 },
  { ticker: 'MSFT', name: 'Microsoft', weight: 6.8 },
  { ticker: 'NVDA', name: 'NVIDIA', weight: 6.2 },
  { ticker: 'AMZN', name: 'Amazon', weight: 3.5 },
  { ticker: 'META', name: 'Meta', weight: 2.4 },
  { ticker: 'GOOGL', name: 'Alphabet', weight: 2.1 },
  { ticker: 'TSLA', name: 'Tesla', weight: 1.8 },
  { ticker: 'BRK.B', name: 'Berkshire', weight: 1.6 },
  { ticker: 'JPM', name: 'JPMorgan', weight: 1.4 },
  { ticker: 'V', name: 'Visa', weight: 1.1 },
  { ticker: 'XOM', name: 'Exxon', weight: 1.0 },
  { ticker: 'UNH', name: 'UnitedHealth', weight: 0.95 },
  { ticker: 'MA', name: 'Mastercard', weight: 0.9 },
  { ticker: 'JNJ', name: 'Johnson & Johnson', weight: 0.85 },
  { ticker: 'PG', name: 'Procter & Gamble', weight: 0.8 },
  { ticker: 'HD', name: 'Home Depot', weight: 0.75 },
  { ticker: 'CVX', name: 'Chevron', weight: 0.7 },
  { ticker: 'MRK', name: 'Merck', weight: 0.65 },
  { ticker: 'ABBV', name: 'AbbVie', weight: 0.6 },
  { ticker: 'LLY', name: 'Eli Lilly', weight: 0.6 },
  { ticker: 'PEP', name: 'PepsiCo', weight: 0.55 },
  { ticker: 'KO', name: 'Coca-Cola', weight: 0.5 },
  { ticker: 'COST', name: 'Costco', weight: 0.5 },
  { ticker: 'ADBE', name: 'Adobe', weight: 0.45 },
  { ticker: 'MCD', name: "McDonald's", weight: 0.4 },
  { ticker: 'TMO', name: 'Thermo Fisher', weight: 0.4 },
  { ticker: 'CSCO', name: 'Cisco', weight: 0.4 },
  { ticker: 'ACN', name: 'Accenture', weight: 0.4 },
  { ticker: 'ABT', name: 'Abbott Labs', weight: 0.38 },
  { ticker: 'DHR', name: 'Danaher', weight: 0.38 },
  { ticker: 'WMT', name: 'Walmart', weight: 0.37 },
  { ticker: 'NEE', name: 'NextEra Energy', weight: 0.35 },
  { ticker: 'NKE', name: 'Nike', weight: 0.35 },
  { ticker: 'ORCL', name: 'Oracle', weight: 0.35 },
  { ticker: 'VZ', name: 'Verizon', weight: 0.33 },
  { ticker: 'INTC', name: 'Intel', weight: 0.33 },
  { ticker: 'AMD', name: 'AMD', weight: 0.33 },
  { ticker: 'QCOM', name: 'Qualcomm', weight: 0.32 },
  { ticker: 'TXN', name: 'Texas Instruments', weight: 0.31 },
  { ticker: 'PM', name: 'Philip Morris', weight: 0.3 },
  { ticker: 'UPS', name: 'UPS', weight: 0.28 },
  { ticker: 'MS', name: 'Morgan Stanley', weight: 0.28 },
  { ticker: 'LOW', name: "Lowe's", weight: 0.28 },
  { ticker: 'BA', name: 'Boeing', weight: 0.27 },
  { ticker: 'IBM', name: 'IBM', weight: 0.26 },
  { ticker: 'CAT', name: 'Caterpillar', weight: 0.26 },
  { ticker: 'HON', name: 'Honeywell', weight: 0.25 },
  { ticker: 'SPGI', name: 'S&P Global', weight: 0.25 },
  { ticker: 'INTU', name: 'Intuit', weight: 0.24 },
  { ticker: 'AXP', name: 'American Express', weight: 0.24 },
  { ticker: 'GS', name: 'Goldman Sachs', weight: 0.23 },
  { ticker: 'BLK', name: 'BlackRock', weight: 0.23 },
  { ticker: 'DE', name: 'John Deere', weight: 0.22 },
  { ticker: 'MDT', name: 'Medtronic', weight: 0.22 },
  { ticker: 'AMGN', name: 'Amgen', weight: 0.21 },
  { ticker: 'GILD', name: 'Gilead', weight: 0.2 },
  { ticker: 'ISRG', name: 'Intuitive Surgical', weight: 0.2 },
  { ticker: 'ADI', name: 'Analog Devices', weight: 0.2 },
  { ticker: 'SCHW', name: 'Charles Schwab', weight: 0.2 },
  { ticker: 'BKNG', name: 'Booking', weight: 0.19 },
  { ticker: 'VRTX', name: 'Vertex', weight: 0.19 },
  { ticker: 'REGN', name: 'Regeneron', weight: 0.18 },
  { ticker: 'ZTS', name: 'Zoetis', weight: 0.18 },
  { ticker: 'PLD', name: 'Prologis', weight: 0.17 },
  { ticker: 'MMC', name: 'Marsh & McLennan', weight: 0.17 },
  { ticker: 'LRCX', name: 'Lam Research', weight: 0.17 },
  { ticker: 'MU', name: 'Micron', weight: 0.17 },
  { ticker: 'TJX', name: 'TJX Companies', weight: 0.17 },
  { ticker: 'CB', name: 'Chubb', weight: 0.16 },
  { ticker: 'SO', name: 'Southern Company', weight: 0.16 },
  { ticker: 'COP', name: 'ConocoPhillips', weight: 0.16 },
  { ticker: 'ETN', name: 'Eaton', weight: 0.16 },
  { ticker: 'DUK', name: 'Duke Energy', weight: 0.15 },
  { ticker: 'MO', name: 'Altria', weight: 0.15 },
  { ticker: 'PGR', name: 'Progressive', weight: 0.15 },
  { ticker: 'CI', name: 'Cigna', weight: 0.15 },
  { ticker: 'BSX', name: 'Boston Scientific', weight: 0.15 },
  { ticker: 'ICE', name: 'Intercontinental Ex', weight: 0.14 },
  { ticker: 'KLAC', name: 'KLA Corp', weight: 0.14 },
  { ticker: 'SNPS', name: 'Synopsys', weight: 0.14 },
  { ticker: 'CDNS', name: 'Cadence', weight: 0.14 },
  { ticker: 'CME', name: 'CME Group', weight: 0.14 },
  { ticker: 'EOG', name: 'EOG Resources', weight: 0.14 },
  { ticker: 'AON', name: 'Aon', weight: 0.13 },
  { ticker: 'SHW', name: 'Sherwin-Williams', weight: 0.13 },
  { ticker: 'HCA', name: 'HCA Healthcare', weight: 0.13 },
  { ticker: 'ITW', name: 'Illinois Tool', weight: 0.13 },
  { ticker: 'APD', name: 'Air Products', weight: 0.13 },
  { ticker: 'MPC', name: 'Marathon Petroleum', weight: 0.12 },
  { ticker: 'MCO', name: "Moody's", weight: 0.12 },
  { ticker: 'EMR', name: 'Emerson', weight: 0.12 },
  { ticker: 'GD', name: 'General Dynamics', weight: 0.12 },
  { ticker: 'NSC', name: 'Norfolk Southern', weight: 0.12 },
  { ticker: 'FDX', name: 'FedEx', weight: 0.12 },
];

interface StockData {
  ticker: string;
  name: string;
  price?: number;
  change?: number;
  changePercent?: number;
}

interface TreemapNode {
  name: string;
  ticker: string;
  weight: number;
  price?: number;
  changePercent?: number;
  size: number;
  [key: string]: any;
}

export default function StockTreemap({ onSelect }: { onSelect?: (ticker: string) => void }) {
  const [data, setData] = useState<TreemapNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [prices, setPrices] = useState<Map<string, StockData>>(new Map());

  useEffect(() => {
    async function fetchPrices() {
      setLoading(true);
      const priceMap = new Map<string, StockData>();
      const tickers = SP500_STOCKS.map(s => s.ticker);

      // Fetch in batches
      for (let i = 0; i < tickers.length; i += 20) {
        const batch = tickers.slice(i, i + 20);
        await Promise.all(batch.map(async (ticker) => {
          try {
            const quote = await marketApi.getQuote(ticker);
            priceMap.set(ticker, {
              ticker: quote.ticker,
              name: quote.name,
              price: quote.price,
              change: quote.change,
              changePercent: quote.changePercent,
            });
          } catch {
            priceMap.set(ticker, { ticker, name: SP500_STOCKS.find(s => s.ticker === ticker)?.name || ticker });
          }
        }));
      }

      setPrices(priceMap);

      // Build treemap data
      const treemapData: TreemapNode[] = SP500_STOCKS.map(stock => {
        const stockPrice = priceMap.get(stock.ticker);
        return {
          name: `${stock.ticker}\n${stockPrice?.price ? `$${stockPrice.price.toFixed(0)}` : ''}`,
          ticker: stock.ticker,
          weight: stock.weight,
          price: stockPrice?.price,
          changePercent: stockPrice?.changePercent,
          size: stock.weight * 100, // scale for treemap
        };
      });

      setData(treemapData);
      setLoading(false);
    }

    fetchPrices();
    const interval = setInterval(fetchPrices, 30000);
    return () => clearInterval(interval);
  }, []);

  const getColor = (node: TreemapNode) => {
    if (node.changePercent === undefined || node.changePercent === null) return '#94a3b8';
    if (node.changePercent >= 0) {
      const intensity = Math.min(node.changePercent / 3, 1);
      return `rgb(${Math.round(34 + (100 * intensity))}, ${Math.round(197 - (100 * intensity))}, ${Math.round(94 - (50 * intensity))})`;
    } else {
      const intensity = Math.min(Math.abs(node.changePercent) / 3, 1);
      return `rgb(${Math.round(239 + (16 * intensity))}, ${Math.round(68 - (30 * intensity))}, ${Math.round(68 - (30 * intensity))})`;
    }
  };

  const CustomContent = (props: any) => {
    const { x, y, width, height, name, ticker, price, changePercent } = props;
    if (width < 30 || height < 20) return null;

    return (
      <g>
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          fill={getColor(props)}
          stroke="#fff"
          strokeWidth={1}
          className="cursor-pointer"
          onClick={() => onSelect?.(ticker)}
          rx={4}
        />
        {width > 50 && height > 35 && (
          <>
            <text
              x={x + width / 2}
              y={y + height / 2 - 6}
              textAnchor="middle"
              fill="#fff"
              fontSize={Math.min(width / 6, 14)}
              fontWeight="bold"
            >
              {ticker}
            </text>
            {price && (
              <text
                x={x + width / 2}
                y={y + height / 2 + 8}
                textAnchor="middle"
                fill="#fff"
                fontSize={Math.min(width / 8, 11)}
              >
                ${price.toFixed(0)}
              </text>
            )}
            {changePercent !== undefined && changePercent !== null && height > 50 && (
              <text
                x={x + width / 2}
                y={y + height / 2 + 22}
                textAnchor="middle"
                fill="#fff"
                fontSize={Math.min(width / 8, 10)}
              >
                {changePercent >= 0 ? '+' : ''}{changePercent.toFixed(1)}%
              </text>
            )}
          </>
        )}
      </g>
    );
  };

  if (loading && data.length === 0) {
    return (
      <div className="bg-gray-50 rounded-xl p-4">
        <div className="h-6 bg-gray-200 rounded w-48 mb-4 animate-pulse"></div>
        <div className="bg-gray-100 rounded-lg h-96 flex items-center justify-center">
          <div className="text-gray-400">Loading S&P 500...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-bold text-gray-800">S&P 500 Market Treemap</h3>
        <div className="flex items-center gap-4 text-xs text-gray-500">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-red-500"></div>
            <span>下跌</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-gray-400"></div>
            <span>持平</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-green-500"></div>
            <span>上涨</span>
          </div>
        </div>
      </div>

      <div className="bg-gray-100 rounded-lg overflow-hidden" style={{ height: '500px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <Treemap
            data={data}
            dataKey="size"
            aspectRatio={4 / 3}
            stroke="#fff"
            content={<CustomContent />}
          >
            <Tooltip
              content={({ payload }) => {
                if (payload && payload.length > 0) {
                  const node = payload[0].payload as TreemapNode;
                  return (
                    <div className="bg-white p-2 rounded shadow border">
                      <div className="font-bold">{node.ticker} - {node.name.split('\n')[0]}</div>
                      <div className="text-sm text-gray-600">
                        权重: {node.weight.toFixed(2)}%
                      </div>
                      {node.price && (
                        <div className="text-sm">价格: ${node.price.toFixed(2)}</div>
                      )}
                      {node.changePercent !== undefined && node.changePercent !== null && (
                        <div className={`text-sm ${node.changePercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          涨跌: {node.changePercent >= 0 ? '+' : ''}{node.changePercent.toFixed(2)}%
                        </div>
                      )}
                    </div>
                  );
                }
                return null;
              }}
            />
          </Treemap>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
