'use client';

import { useState, useEffect } from 'react';
import { tradingApi, marketApi } from '@/lib/api';

interface TradingDashboardProps {
  agentId: string;
}

export default function TradingDashboard({ agentId }: TradingDashboardProps) {
  const [balance, setBalance] = useState<{
    balance: number;
    positions: Array<{
      ticker: string;
      quantity: number;
      average_cost: number;
      current_value?: number;
      unrealized_pnl?: number;
    }>;
    total_value: number;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Order form state
  const [orderTicker, setOrderTicker] = useState('');
  const [orderQuantity, setOrderQuantity] = useState('');
  const [orderType, setOrderType] = useState<'buy' | 'sell'>('buy');
  const [submitting, setSubmitting] = useState(false);
  const [orderResult, setOrderResult] = useState<string | null>(null);

  useEffect(() => {
    fetchBalance();
  }, [agentId]);

  const fetchBalance = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await tradingApi.getBalance(agentId);
      setBalance(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch balance');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!orderTicker || !orderQuantity) return;

    setSubmitting(true);
    setOrderResult(null);

    try {
      const result = await tradingApi.createOrder({
        agent_id: agentId,
        ticker: orderTicker.toUpperCase(),
        order_type: orderType,
        quantity: parseFloat(orderQuantity),
      });
      setOrderResult(`${orderType.toUpperCase()} order executed: ${result.quantity} shares of ${result.ticker} at $${result.price.toFixed(2)}`);
      setOrderTicker('');
      setOrderQuantity('');
      fetchBalance(); // Refresh balance
    } catch (err) {
      setOrderResult(`Error: ${err instanceof Error ? err.message : 'Order failed'}`);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div className="h-8 bg-gray-200 rounded w-1/3 mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6 border border-red-200">
        <div className="text-red-500">{error}</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Account Summary */}
      <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
        <h2 className="text-xl font-bold mb-4">Trading Account</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-gray-500">Cash Balance</div>
            <div className="text-2xl font-bold text-green-600">
              ${balance?.balance.toFixed(2)}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Total Value</div>
            <div className="text-2xl font-bold text-blue-600">
              ${balance?.total_value.toFixed(2)}
            </div>
          </div>
        </div>
      </div>

      {/* Positions */}
      <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
        <h2 className="text-xl font-bold mb-4">Positions</h2>
        {balance?.positions && balance.positions.length > 0 ? (
          <div className="space-y-2">
            {balance.positions.map((pos) => (
              <div key={pos.ticker} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <div>
                  <span className="font-bold">{pos.ticker}</span>
                  <span className="text-gray-500 ml-2">{pos.quantity} shares</span>
                </div>
                <div className="text-right">
                  <div className="font-bold">${(pos.current_value ?? 0).toFixed(2)}</div>
                  <div className={`text-sm ${(pos.unrealized_pnl ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {(pos.unrealized_pnl ?? 0) >= 0 ? '+' : ''}{(pos.unrealized_pnl ?? 0).toFixed(2)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-gray-500 text-center py-4">No positions</div>
        )}
      </div>

      {/* Order Form */}
      <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
        <h2 className="text-xl font-bold mb-4">Place Order</h2>
        <form onSubmit={handleSubmitOrder} className="space-y-4">
          <div className="flex gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">Ticker</label>
              <input
                type="text"
                value={orderTicker}
                onChange={(e) => setOrderTicker(e.target.value.toUpperCase())}
                placeholder="AAPL"
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                required
              />
            </div>
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
              <input
                type="number"
                value={orderQuantity}
                onChange={(e) => setOrderQuantity(e.target.value)}
                placeholder="10"
                min="1"
                step="1"
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                required
              />
            </div>
          </div>
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={submitting}
              onClick={() => setOrderType('buy')}
              className={`flex-1 py-2 px-4 rounded-md font-medium ${
                orderType === 'buy'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-200 text-gray-700'
              } hover:bg-green-700 disabled:opacity-50`}
            >
              Buy
            </button>
            <button
              type="submit"
              disabled={submitting}
              onClick={() => setOrderType('sell')}
              className={`flex-1 py-2 px-4 rounded-md font-medium ${
                orderType === 'sell'
                  ? 'bg-red-600 text-white'
                  : 'bg-gray-200 text-gray-700'
              } hover:bg-red-700 disabled:opacity-50`}
            >
              Sell
            </button>
          </div>
        </form>

        {orderResult && (
          <div className={`mt-4 p-3 rounded ${orderResult.startsWith('Error') ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
            {orderResult}
          </div>
        )}
      </div>
    </div>
  );
}
