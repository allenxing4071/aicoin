'use client';

import { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, Clock } from 'lucide-react';
import axios from 'axios';

interface Trade {
  id: number;
  symbol: string;
  side: 'BUY' | 'SELL';
  price: number;
  size: number;
  pnl: number;
  timestamp: string;
  confidence: number;
}

export default function TradeList() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadTrades();
    const interval = setInterval(loadTrades, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadTrades = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/v1/trading/trades');
      if (response.data && response.data.trades) {
        setTrades(response.data.trades.slice(0, 10));
      }
    } catch (error) {
      console.error('Failed to load trades:', error);
      generateMockTrades();
    } finally {
      setLoading(false);
    }
  };

  const generateMockTrades = () => {
    const mockTrades: Trade[] = [
      {
        id: 1,
        symbol: 'BTC-PERP',
        side: 'BUY',
        price: 94233.50,
        size: 0.12,
        pnl: 245.80,
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        confidence: 0.75
      },
      {
        id: 2,
        symbol: 'ETH-PERP',
        side: 'SELL',
        price: 3456.20,
        size: 2.5,
        pnl: -123.45,
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        confidence: 0.65
      },
      {
        id: 3,
        symbol: 'SOL-PERP',
        side: 'BUY',
        price: 178.50,
        size: 15.0,
        pnl: 567.30,
        timestamp: new Date(Date.now() - 10800000).toISOString(),
        confidence: 0.80
      }
    ];
    setTrades(mockTrades);
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) return `${diffDays}天前`;
    if (diffHours > 0) return `${diffHours}小时前`;
    if (diffMins > 0) return `${diffMins}分钟前`;
    return '刚刚';
  };

  return (
    <div className="bg-[#0a0b0d] rounded-lg border border-gray-800">
      <div className="p-4 border-b border-gray-800">
        <h3 className="text-lg font-bold text-white">完成的交易</h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-xs text-gray-400 border-b border-gray-800">
              <th className="text-left p-3">时间</th>
              <th className="text-left p-3">交易对</th>
              <th className="text-left p-3">方向</th>
              <th className="text-right p-3">价格</th>
              <th className="text-right p-3">数量</th>
              <th className="text-right p-3">盈亏</th>
              <th className="text-right p-3">信心度</th>
            </tr>
          </thead>
          <tbody>
            {trades.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-8 text-gray-500">
                  {loading ? '加载中...' : '暂无交易记录'}
                </td>
              </tr>
            ) : (
              trades.map((trade) => (
                <tr key={trade.id} className="border-b border-gray-800 hover:bg-gray-900/50">
                  <td className="p-3">
                    <div className="flex items-center space-x-1 text-sm text-gray-400">
                      <Clock className="w-3 h-3" />
                      <span>{formatTime(trade.timestamp)}</span>
                    </div>
                  </td>
                  <td className="p-3">
                    <span className="text-sm font-medium text-white">{trade.symbol}</span>
                  </td>
                  <td className="p-3">
                    <div className={`flex items-center space-x-1 w-fit px-2 py-1 rounded ${
                      trade.side === 'BUY' ? 'bg-green-400/10 text-green-400' : 'bg-red-400/10 text-red-400'
                    }`}>
                      {trade.side === 'BUY' ? (
                        <TrendingUp className="w-3 h-3" />
                      ) : (
                        <TrendingDown className="w-3 h-3" />
                      )}
                      <span className="text-xs font-semibold">{trade.side}</span>
                    </div>
                  </td>
                  <td className="p-3 text-right">
                    <span className="text-sm text-white">${trade.price.toLocaleString()}</span>
                  </td>
                  <td className="p-3 text-right">
                    <span className="text-sm text-gray-300">{trade.size}</span>
                  </td>
                  <td className="p-3 text-right">
                    <span className={`text-sm font-semibold ${
                      trade.pnl >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                    </span>
                  </td>
                  <td className="p-3 text-right">
                    <span className="text-sm text-yellow-400">
                      {(trade.confidence * 100).toFixed(0)}%
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

