'use client';

import { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import axios from 'axios';

interface TickerData {
  symbol: string;
  price: number;
  change24h: number;
  timestamp?: string;
}

const API_BASE = 'http://localhost:8000/api/v1';

export default function PriceTicker() {
  const [tickers, setTickers] = useState<TickerData[]>([
    { symbol: 'BTC', price: 95000.00, change24h: 2.5 },
    { symbol: 'ETH', price: 3500.00, change24h: 1.8 },
    { symbol: 'SOL', price: 180.00, change24h: -1.2 },
    { symbol: 'BNB', price: 600.00, change24h: 0.5 },
    { symbol: 'DOGE', price: 0.35, change24h: 5.2 },
    { symbol: 'XRP', price: 0.50, change24h: -0.8 },
  ]);

  // 获取真实价格数据
  const fetchRealPrices = async () => {
    try {
      const response = await axios.get(`${API_BASE}/market-data/ticker`);
      if (response.data.success) {
        const realTickers = response.data.data.map((ticker: any) => ({
          symbol: ticker.symbol,
          price: ticker.price,
          change24h: ticker.changePercent || 0,
          timestamp: ticker.timestamp
        }));
        setTickers(realTickers);
      }
    } catch (error) {
      console.error('Failed to fetch real prices:', error);
      // 如果获取失败，使用模拟数据
      setTickers(prev => prev.map(ticker => ({
        ...ticker,
        price: ticker.price * (1 + (Math.random() - 0.5) * 0.002),
        change24h: ticker.change24h + (Math.random() - 0.5) * 0.5,
      })));
    }
  };

  // 实时价格更新
  useEffect(() => {
    // 立即获取一次真实数据
    fetchRealPrices();
    
    // 每5秒更新一次价格
    const interval = setInterval(fetchRealPrices, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-white border-b border-gray-200">
      <div className="flex items-center py-3 px-6 gap-8">
        {tickers.map((ticker, index) => (
          <div key={ticker.symbol} className="flex items-center space-x-3">
            <span className="text-gray-600 font-medium">{ticker.symbol}</span>
            <span className="text-gray-900 font-semibold">
              ${ticker.price.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
              })}
            </span>
            <span className={`flex items-center text-sm ${
              ticker.change24h >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {ticker.change24h >= 0 ? (
                <TrendingUp className="w-3 h-3 mr-1" />
              ) : (
                <TrendingDown className="w-3 h-3 mr-1" />
              )}
              {Math.abs(ticker.change24h).toFixed(2)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
