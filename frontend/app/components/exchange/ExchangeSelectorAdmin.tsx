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

export default function ExchangeSelectorAdmin() {
  const [activeExchange, setActiveExchange] = useState<ExchangeInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [switching, setSwitching] = useState(false);

  useEffect(() => {
    fetchActiveExchange();
    
    // 每5秒自动刷新一次交易所状态
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

  const handleSwitchExchange = async (exchange: string, market: string) => {
    setSwitching(true);
    try {
      let targetMarket = market;
      
      if (!targetMarket || targetMarket === 'unknown' || targetMarket === 'undefined') {
        targetMarket = exchange === 'hyperliquid' ? 'perpetual' : 'spot';
      }
      
      if (exchange === 'hyperliquid') {
        targetMarket = 'perpetual';
      }
      
      console.log(`切换交易所: ${exchange}, 市场类型: ${targetMarket}`);
      
      const response = await axios.post(
        `${API_BASE}/exchanges/switch-exchange?exchange_name=${exchange}&market_type=${targetMarket}`
      );
      
      if (response.data.success) {
        await fetchActiveExchange();
        alert('✅ 切换成功!');
        window.location.reload();
      }
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || '切换失败';
      alert(`❌ ${errorMsg}`);
      console.error('切换交易所失败:', error);
    } finally {
      setSwitching(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center gap-3">
        <div className="animate-pulse flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-full">
          <div className="w-2 h-2 rounded-full bg-gray-300"></div>
          <span className="text-sm text-gray-500">加载中...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-3">
      {/* 状态指示器 */}
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
        disabled={switching}
        className="p-2 bg-white text-blue-600 rounded-full border border-gray-200 hover:bg-blue-50 hover:border-blue-300 transition-all disabled:opacity-50"
        title="刷新交易所状态"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      </button>

      {/* 切换中提示 */}
      {switching && (
        <div className="px-3 py-2 bg-blue-50 border border-blue-200 rounded-full text-sm text-blue-700 flex items-center gap-2">
          <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          切换中...
        </div>
      )}
    </div>
  );
}

