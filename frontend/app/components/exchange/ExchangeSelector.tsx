'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

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
  const [switching, setSwitching] = useState(false);

  useEffect(() => {
    fetchActiveExchange();
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

  const handleSwitchExchange = async (exchange: string, market: string) => {
    setSwitching(true);
    try {
      const response = await axios.post(
        `${API_BASE}/exchanges/switch?exchange_name=${exchange}&market_type=${market}`
      );
      
      if (response.data.success) {
        // 刷新当前交易所信息
        await fetchActiveExchange();
        alert('✅ 切换成功!');
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
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-5">
        <div className="animate-pulse flex items-center gap-4">
          <div className="h-4 bg-blue-200 rounded w-24"></div>
          <div className="h-9 bg-blue-200 rounded w-36"></div>
          <div className="h-9 bg-blue-200 rounded w-36"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-xl p-5">
      <div className="flex flex-wrap items-center gap-4">
        {/* 交易所选择 */}
        <div className="flex items-center gap-3">
          <label className="text-sm text-blue-900 font-semibold">交易所:</label>
          <select
            value={activeExchange?.name || 'hyperliquid'}
            onChange={(e) => handleSwitchExchange(e.target.value, activeExchange?.market_type || 'perpetual')}
            disabled={switching}
            className="px-4 py-2 bg-white text-blue-900 rounded-xl border border-blue-300 hover:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-sm"
          >
            <option value="hyperliquid">🔷 Hyperliquid</option>
            <option value="binance">🟡 Binance</option>
          </select>
        </div>

        {/* 市场类型选择 */}
        <div className="flex items-center gap-3">
          <label className="text-sm text-blue-900 font-semibold">市场:</label>
          <select
            value={activeExchange?.market_type || 'perpetual'}
            onChange={(e) => handleSwitchExchange(activeExchange?.name || 'hyperliquid', e.target.value)}
            disabled={switching}
            className="px-4 py-2 bg-white text-blue-900 rounded-xl border border-blue-300 hover:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-sm"
          >
            {/* 现货 */}
            {(activeExchange?.supports_spot || !activeExchange) && (
              <option value="spot">💰 现货 (Spot)</option>
            )}
            {/* 合约/期货 */}
            {(activeExchange?.supports_futures || !activeExchange) && (
              <>
                <option value="futures">📈 合约 (Futures)</option>
                <option value="perpetual">♾️ 永续 (Perpetual)</option>
              </>
            )}
            {/* 如果什么都不支持,显示默认选项 */}
            {activeExchange && !activeExchange.supports_spot && !activeExchange.supports_futures && (
              <option value="perpetual">♾️ 永续 (Perpetual)</option>
            )}
          </select>
        </div>

        {/* 状态指示器 */}
        <div className="flex items-center gap-2 ml-auto px-3 py-2 bg-white rounded-xl border border-blue-200">
          <div className={`w-2 h-2 rounded-full ${activeExchange?.is_initialized ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></div>
          <span className="text-sm text-blue-900 font-medium">
            {activeExchange?.name === 'binance' ? '币安' : 'Hyperliquid'} 
            {' • '}
            {activeExchange?.market_type === 'spot' ? '现货' : 
             activeExchange?.market_type === 'futures' ? '合约' : '永续'}
          </span>
        </div>

        {/* 重新加载按钮 */}
        <button
          onClick={fetchActiveExchange}
          disabled={switching}
          className="p-2.5 bg-white hover:bg-blue-100 text-blue-600 rounded-xl border border-blue-200 transition-all disabled:opacity-50 shadow-sm"
          title="刷新"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>

      {/* 切换中提示 */}
      {switching && (
        <div className="mt-3 px-3 py-2 bg-blue-100 border border-blue-300 rounded-xl text-sm text-blue-800 flex items-center gap-2">
          <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          正在切换交易所...
        </div>
      )}
    </div>
  );
}

