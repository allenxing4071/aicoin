'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import PageHeader from '../../components/common/PageHeader';

const API_BASE = '/api/v1';

interface Exchange {
  id: number;
  name: string;
  display_name: string;
  is_active: boolean;
  market_type: string;
  testnet: boolean;
  created_at: string;
  updated_at: string;
}

interface ExchangeInfo {
  name: string;
  market_type: string;
  is_initialized: boolean;
  supports_spot: boolean;
  supports_futures: boolean;
}

export default function ExchangesPage() {
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const [supportedExchanges, setSupportedExchanges] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'list' | 'supported'>('list');
  const [activeExchange, setActiveExchange] = useState<ExchangeInfo | null>(null);
  const [switching, setSwitching] = useState(false);

  useEffect(() => {
    fetchExchanges();
    fetchSupportedExchanges();
    fetchActiveExchange();
    
    // 每5秒自动刷新交易所状态
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
    }
  };

  const fetchExchanges = async () => {
    try {
      const response = await axios.get(`${API_BASE}/exchanges`);
      if (response.data.success) {
        setExchanges(response.data.data);
      }
    } catch (error) {
      console.error('获取交易所列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSupportedExchanges = async () => {
    try {
      const response = await axios.get(`${API_BASE}/exchanges/supported`);
      if (response.data.success) {
        setSupportedExchanges(response.data.data);
      }
    } catch (error) {
      console.error('获取支持的交易所失败:', error);
    }
  };

  const handleReload = async () => {
    try {
      const response = await axios.post(`${API_BASE}/exchanges/reload`);
      if (response.data.success) {
        alert('✅ 重新加载成功!');
        fetchExchanges();
      }
    } catch (error: any) {
      alert(`❌ 重新加载失败: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`确定要删除交易所配置"${name}"吗?`)) {
      return;
    }

    try {
      const response = await axios.delete(`${API_BASE}/exchanges/${id}`);
      if (response.data.success) {
        alert('✅ 删除成功!');
        fetchExchanges();
      }
    } catch (error: any) {
      alert(`❌ 删除失败: ${error.response?.data?.detail || error.message}`);
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
        `${API_BASE}/exchanges/switch?exchange_name=${exchange}&market_type=${targetMarket}`
      );
      
      if (response.data.success) {
        await fetchActiveExchange();
        await fetchExchanges();
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

  return (
    <div className="space-y-6">
      {/* 页面标题 - 统一风格 */}
      <PageHeader
        icon="🔄"
        title="交易所管理"
        description="管理和切换不同的交易所"
        color="blue"
        actions={
          <button
            onClick={handleReload}
            className="px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-xl transition-all shadow-sm hover:shadow-md flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            重新加载适配器
          </button>
        }
      />

      {/* 当前交易所选择器 - 后台完整版 */}
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

      {/* 标签切换 */}
      <div className="flex gap-2 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('list')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'list'
              ? 'text-blue-600 border-b-2 border-blue-400'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          配置列表
        </button>
        <button
          onClick={() => setActiveTab('supported')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'supported'
              ? 'text-blue-600 border-b-2 border-blue-400'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          支持的交易所
        </button>
      </div>

      {/* 配置列表 */}
      {activeTab === 'list' && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl overflow-hidden">
          {loading ? (
            <div className="p-8 text-center text-gray-600">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
              加载中...
            </div>
          ) : exchanges.length === 0 ? (
            <div className="p-8 text-center text-gray-600">
              暂无交易所配置
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-white/50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                      交易所
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                      市场类型
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                      状态
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                      环境
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                      创建时间
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                      操作
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {exchanges.map((exchange) => (
                    <tr key={exchange.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <span className="text-2xl">
                            {exchange.name === 'binance' ? '🟡' : '🔷'}
                          </span>
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {exchange.display_name}
                            </div>
                            <div className="text-xs text-gray-600">
                              {exchange.name}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 py-1 text-xs font-medium bg-gray-50 text-gray-700 rounded">
                          {exchange.market_type}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {exchange.is_active ? (
                          <span className="px-2 py-1 text-xs font-medium bg-green-50 text-green-600 rounded flex items-center gap-1 w-fit">
                            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                            激活中
                          </span>
                        ) : (
                          <span className="px-2 py-1 text-xs font-medium bg-gray-50 text-gray-600 rounded">
                            未激活
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                        {exchange.testnet ? '测试网' : '主网'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {new Date(exchange.created_at).toLocaleString('zh-CN')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {!exchange.is_active && (
                          <button
                            onClick={() => handleDelete(exchange.id, exchange.display_name)}
                            className="text-red-600 hover:text-red-300 transition-colors"
                          >
                            删除
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* 支持的交易所 */}
      {activeTab === 'supported' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {supportedExchanges.map((exchange) => (
            <div
              key={exchange.name}
              className="bg-white backdrop-blur-sm rounded-xl p-6 border border-gray-200"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <span className="text-4xl">
                    {exchange.name === 'binance' ? '🟡' : '🔷'}
                  </span>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">
                      {exchange.display_name}
                    </h3>
                    <p className="text-sm text-gray-600">{exchange.name}</p>
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">现货交易</span>
                  <span className={exchange.supports_spot ? 'text-green-600' : 'text-red-600'}>
                    {exchange.supports_spot ? '✓ 支持' : '✗ 不支持'}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">合约交易</span>
                  <span className={exchange.supports_futures ? 'text-green-600' : 'text-red-600'}>
                    {exchange.supports_futures ? '✓ 支持' : '✗ 不支持'}
                  </span>
                </div>
              </div>

              {exchange.name === 'binance' && (
                <div className="mt-4 p-3 bg-yellow-50 border border-yellow-300 rounded-xl">
                  <p className="text-sm text-yellow-800 font-medium">
                    ⚠️ 需要配置 BINANCE_API_KEY 和 BINANCE_API_SECRET
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

