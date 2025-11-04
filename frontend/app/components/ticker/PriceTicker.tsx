'use client';

import { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import axios from 'axios';
import CoinIcon from '../common/CoinIcon';

interface TickerData {
  symbol: string;
  price: number;
  change24h: number;
  timestamp?: string;
}

const API_BASE = 'http://localhost:8000/api/v1';

export default function PriceTicker() {
  const [tickers, setTickers] = useState<TickerData[]>([]);
  const [mounted, setMounted] = useState(false);
  const [loading, setLoading] = useState(true);

  // 获取真实价格数据
  const fetchRealPrices = async () => {
    try {
      const response = await axios.get(`${API_BASE}/market/tickers`);
      if (response.data && Array.isArray(response.data)) {
        const realTickers = response.data
          .filter((ticker: any) => ticker && ticker.symbol && parseFloat(ticker.price || 0) > 0)  // 过滤无效数据和价格为0的
          .map((ticker: any) => ({
            symbol: ticker.symbol,
            price: parseFloat(ticker.price || 0),
            change24h: parseFloat(ticker.change_24h || 0),
            timestamp: ticker.timestamp
          }));
        
        if (realTickers.length > 0) {
          setTickers(realTickers);
          setLoading(false);
        } else {
          console.warn('No valid tickers with price > 0');
        }
      }
    } catch (error) {
      console.error('Failed to fetch real prices:', error);
      // 获取失败时不改变loading状态，保持之前的数据
    }
  };

  // 实时价格更新
  useEffect(() => {
    setMounted(true);
    // 立即获取一次真实数据
    fetchRealPrices();
    
    // 每5秒更新一次价格
    const interval = setInterval(fetchRealPrices, 5000);

    return () => clearInterval(interval);
  }, []);

  // 防止hydration错误
  if (!mounted) {
    return (
      <div className="bg-white border-b border-gray-200">
        <div className="flex items-center py-3 px-6 gap-8">
          <span className="text-gray-500 text-sm">加载市场数据中...</span>
        </div>
      </div>
    );
  }

  // 显示加载状态
  if (loading || tickers.length === 0) {
    return (
      <div className="bg-white border-b border-gray-200">
        <div className="flex items-center py-3 px-6 gap-8">
          <span className="text-gray-500 text-sm animate-pulse">加载市场数据中...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border-b border-gray-200">
      <div className="flex items-center py-3 px-6 gap-8">
        {tickers.map((ticker, index) => (
          <div key={ticker.symbol} className="flex items-center space-x-2">
            <CoinIcon symbol={ticker.symbol} size={20} />
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
