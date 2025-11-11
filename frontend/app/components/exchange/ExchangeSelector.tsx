'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = '/api/v1';

interface ExchangeInfo {
  name: string;
  market_type: string;
  is_initialized: boolean;
  supports_spot: boolean;
  supports_futures: boolean;
}

export default function ExchangeSelector() {
  const [activeExchange, setActiveExchange] = useState<ExchangeInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchActiveExchange();
    
    // 每5秒自动刷新一次交易所状态，确保与后台同步
    const interval = setInterval(fetchActiveExchange, 5000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchActiveExchange = async () => {
    try {
      const response = await axios.get(`${API_BASE}/exchanges/active`);
      if (response.data.success) {
        setActiveExchange(response.data.data);
      }
    } catch (error: any) {
      console.error('获取当前交易所失败:', error);
      // 即使API失败,也设置一个默认值,让UI可以正常显示
      setActiveExchange({
        name: 'hyperliquid',
        market_type: 'perpetual',
        is_initialized: false,
        supports_spot: false,
        supports_futures: true
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-full border border-gray-200">
        <div className="w-2 h-2 rounded-full bg-gray-300 animate-pulse"></div>
        <span className="text-sm text-gray-500">加载中...</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      {/* 状态指示器（只读） */}
      <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-full border border-gray-200">
        <div className={`w-2 h-2 rounded-full ${activeExchange?.is_initialized ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></div>
        <span className="text-sm text-gray-700 font-medium">
          {activeExchange?.name === 'binance' ? '币安' : 'Hyperliquid'} 
          {' · '}
          {activeExchange?.market_type === 'spot' ? '现货' : 
           activeExchange?.market_type === 'futures' ? '合约' : '永续'}
        </span>
      </div>

      {/* 刷新按钮 */}
      <button
        onClick={fetchActiveExchange}
        className="p-2 bg-white text-blue-600 rounded-full border border-gray-200 hover:bg-blue-50 hover:border-blue-300 transition-all"
        title="刷新交易所状态"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      </button>
    </div>
  );
}
