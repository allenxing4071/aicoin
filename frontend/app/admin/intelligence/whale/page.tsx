'use client';

/**
 * 巨鲸监控页面
 * 
 * 路径: /admin/intelligence/whale
 * 
 * 功能：
 * - 巨鲸活动列表
 * - 实时监控
 * - 统计分析
 * - 告警设置
 */

import React, { useState, useEffect } from 'react';
import PageHeader from '@/app/components/common/PageHeader';
import { unifiedDesignSystem, getThemeStyles } from '@/app/admin/unified-design-system';

interface WhaleSignal {
  symbol: string;
  action: string;
  amount_usd: number;
  address: string;
  timestamp: string;
  exchange: string;
}

interface DataSource {
  type: string;
  name: string;
  url: string | null;
  api_key: string | null;
  enabled: boolean;
  update_interval: number;
  description: string;
}

interface SourceStatus {
  name: string;
  type: string;
  status: string;
  last_update: string | null;
  last_error: string | null;
  total_calls: number;
  success_rate: number;
}

export default function WhaleMonitoringPage() {
  const theme = getThemeStyles('blue');
  const [whaleSignals, setWhaleSignals] = useState<WhaleSignal[]>([]);
  const [sources, setSources] = useState<DataSource[]>([]);
  const [sourceStatuses, setSourceStatuses] = useState<SourceStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState<string | null>(null);
  const [stats, setStats] = useState<any>(null);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [selectedSource, setSelectedSource] = useState<DataSource | null>(null);
  const [apiKeyInput, setApiKeyInput] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // 获取数据源配置
      const configRes = await fetch('http://localhost:8000/api/v1/admin/intelligence/config');
      const configData = await configRes.json();
      if (configData.success && configData.data.data_sources) {
        const whaleSources = configData.data.data_sources.filter(
          (s: DataSource) => s.type === 'whale'
        );
        setSources(whaleSources);
      }

      // 获取数据源状态
      const statusRes = await fetch('http://localhost:8000/api/v1/admin/intelligence/data-sources/status');
      const statusData = await statusRes.json();
      if (Array.isArray(statusData)) {
        const whaleStatuses = statusData.filter((s: SourceStatus) => s.type === 'whale');
        setSourceStatuses(whaleStatuses);
      }

      // 获取巨鲸活动（从情报报告中提取）
      const reportsRes = await fetch('http://localhost:8000/api/v1/intelligence/reports?limit=20');
      const reportsData = await reportsRes.json();
      if (reportsData.success && reportsData.data) {
        const allSignals: WhaleSignal[] = [];
        reportsData.data.forEach((report: any) => {
          if (report.whale_signals && Array.isArray(report.whale_signals)) {
            allSignals.push(...report.whale_signals);
          }
        });
        setWhaleSignals(allSignals.slice(0, 50)); // 显示最新50条

        // 计算统计数据
        const buySignals = allSignals.filter(s => s.action === 'buy');
        const sellSignals = allSignals.filter(s => s.action === 'sell');
        const totalVolume = allSignals.reduce((sum, s) => sum + (s.amount_usd || 0), 0);
        
        setStats({
          total: allSignals.length,
          buy: buySignals.length,
          sell: sellSignals.length,
          volume: totalVolume,
        });
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleSource = async (sourceName: string, currentEnabled: boolean) => {
    try {
      const res = await fetch(
        `http://localhost:8000/api/v1/admin/intelligence/data-sources/${encodeURIComponent(sourceName)}/toggle?enabled=${!currentEnabled}`,
        { method: 'POST' }
      );
      const data = await res.json();
      if (data.success) {
        alert(`✅ 数据源已${!currentEnabled ? '启用' : '禁用'}`);
        fetchData();
      } else {
        alert(`❌ 操作失败: ${data.message}`);
      }
    } catch (error) {
      alert(`❌ 操作失败: ${error}`);
    }
  };

  const handleTestConnection = async (sourceName: string) => {
    try {
      setTesting(sourceName);
      const res = await fetch(
        `http://localhost:8000/api/v1/admin/intelligence/data-sources/${encodeURIComponent(sourceName)}/test-connection`,
        { method: 'POST' }
      );
      const data = await res.json();
      
      if (data.success) {
        alert(`✅ 连接成功！\n响应时间: ${data.data.response_time_ms}ms\nAPI有效: ${data.data.api_valid ? '是' : '否'}`);
      } else {
        alert(`❌ 连接失败: ${data.message}`);
      }
    } catch (error) {
      alert(`❌ 测试失败: ${error}`);
    } finally {
      setTesting(null);
    }
  };

  const handleConfigApiKey = (source: DataSource) => {
    setSelectedSource(source);
    setApiKeyInput(source.api_key || '');
    setShowConfigModal(true);
  };

  const handleSaveApiKey = async () => {
    if (!selectedSource) return;
    
    try {
      // 获取完整配置
      const configRes = await fetch('http://localhost:8000/api/v1/admin/intelligence/config');
      const configData = await configRes.json();
      
      if (!configData.success) {
        alert('❌ 获取配置失败');
        return;
      }

      // 更新API Key
      const updatedSources = configData.data.data_sources.map((s: DataSource) => {
        if (s.name === selectedSource.name) {
          return { ...s, api_key: apiKeyInput };
        }
        return s;
      });

      // 保存配置
      const saveRes = await fetch('http://localhost:8000/api/v1/admin/intelligence/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...configData.data,
          data_sources: updatedSources,
        }),
      });

      const saveData = await saveRes.json();
      if (saveData.success) {
        alert('✅ API Key 保存成功');
        setShowConfigModal(false);
        fetchData();
      } else {
        alert(`❌ 保存失败: ${saveData.message}`);
      }
    } catch (error) {
      alert(`❌ 保存失败: ${error}`);
    }
  };

  const getActionColor = (action: string) => {
    if (action === 'buy') return 'bg-green-100 text-green-800';
    if (action === 'sell') return 'bg-red-100 text-red-800';
    return 'bg-blue-100 text-blue-800';
  };

  const getActionIcon = (action: string) => {
    if (action === 'buy') return '🟢';
    if (action === 'sell') return '🔴';
    return '🔄';
  };

  const formatAmount = (amount: number) => {
    if (amount >= 1000000) {
      return `$${(amount / 1000000).toFixed(2)}M`;
    } else if (amount >= 1000) {
      return `$${(amount / 1000).toFixed(2)}K`;
    }
    return `$${amount.toFixed(2)}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        icon="🐋"
        title="巨鲸监控"
        description="监控大额交易和巨鲸活动，捕捉市场动向"
        color="blue"
      />

      {/* 统计卡片 */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 shadow-lg border-2 border-blue-300">
            <div className="text-sm text-gray-500 mb-1">总活动数</div>
            <div className="text-3xl font-bold text-blue-600">{stats.total}</div>
          </div>
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 shadow-lg border-2 border-green-300">
            <div className="text-sm text-gray-500 mb-1">买入信号</div>
            <div className="text-3xl font-bold text-green-600">{stats.buy}</div>
            <div className="text-xs text-gray-500 mt-1">
              占比: {stats.total > 0 ? ((stats.buy / stats.total) * 100).toFixed(1) : 0}%
            </div>
          </div>
          <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-xl p-6 shadow-lg border-2 border-red-300">
            <div className="text-sm text-gray-500 mb-1">卖出信号</div>
            <div className="text-3xl font-bold text-red-600">{stats.sell}</div>
            <div className="text-xs text-gray-500 mt-1">
              占比: {stats.total > 0 ? ((stats.sell / stats.total) * 100).toFixed(1) : 0}%
            </div>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 shadow-lg border-2 border-purple-300">
            <div className="text-sm text-gray-500 mb-1">总交易量</div>
            <div className="text-3xl font-bold text-purple-600">{formatAmount(stats.volume)}</div>
          </div>
        </div>
      )}

      {/* 数据源配置 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">⚙️ 数据源配置</h3>
        
        <div className="space-y-3">
          {sources.map((source, idx) => {
            const status = sourceStatuses.find(s => s.name === source.name);
            return (
              <div key={idx} className={`${unifiedDesignSystem.listCard.container} ${theme.listCardBorder}`}>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-semibold text-gray-900">{source.name}</h4>
                      <span
                        className={`px-3 py-1 text-xs rounded-full font-medium ${
                          source.enabled
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-600'
                        }`}
                      >
                        {source.enabled ? '✓ 启用' : '✗ 禁用'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{source.description}</p>
                    <p className="text-xs text-gray-500">更新间隔: {source.update_interval / 60}分钟</p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleConfigApiKey(source)}
                      className="px-3 py-1 text-sm bg-purple-600 text-white rounded hover:bg-purple-700"
                    >
                      🔑 配置Key
                    </button>
                    <button
                      onClick={() => handleTestConnection(source.name)}
                      disabled={testing === source.name || !source.api_key}
                      className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
                    >
                      {testing === source.name ? '测试中...' : '测试连接'}
                    </button>
                    <button
                      onClick={() => handleToggleSource(source.name, source.enabled)}
                      className={`px-3 py-1 text-sm rounded ${
                        source.enabled
                          ? 'bg-gray-600 text-white hover:bg-gray-700'
                          : 'bg-green-600 text-white hover:bg-green-700'
                      }`}
                    >
                      {source.enabled ? '禁用' : '启用'}
                    </button>
                  </div>
                </div>

                {!source.api_key && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded p-3 text-sm text-yellow-800">
                    ⚠️ 需要配置 API Key 才能使用此数据源
                  </div>
                )}

                {status && source.api_key && (
                  <div className="grid grid-cols-3 gap-4 pt-3 border-t border-gray-200">
                    <div>
                      <div className="text-xs text-gray-500">总调用</div>
                      <div className="text-sm font-semibold text-gray-900">{status.total_calls}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">成功率</div>
                      <div className="text-sm font-semibold text-green-600">{status.success_rate.toFixed(1)}%</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">最后更新</div>
                      <div className="text-sm font-semibold text-gray-900">
                        {status.last_update
                          ? new Date(status.last_update).toLocaleString('zh-CN', {
                              month: '2-digit',
                              day: '2-digit',
                              hour: '2-digit',
                              minute: '2-digit',
                            })
                          : '未更新'}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {sources.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <p>暂无巨鲸监控数据源配置</p>
          </div>
        )}
      </div>

      {/* 巨鲸活动列表 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🐋 巨鲸活动</h3>
        
        <div className="space-y-3">
          {whaleSignals.map((signal, idx) => (
            <div key={idx} className="border-l-4 border-blue-500 pl-4 py-3 hover:bg-gray-50 transition-colors">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-3">
                  <span className={`px-3 py-1 text-xs rounded-full font-medium ${getActionColor(signal.action)}`}>
                    {getActionIcon(signal.action)} {signal.action.toUpperCase()}
                  </span>
                  <span className="font-semibold text-gray-900">{signal.symbol}</span>
                  <span className="text-lg font-bold text-purple-600">{formatAmount(signal.amount_usd)}</span>
                </div>
                <span className="text-xs text-gray-500">
                  {new Date(signal.timestamp).toLocaleString('zh-CN')}
                </span>
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span>交易所: {signal.exchange || '未知'}</span>
                <span className="font-mono text-xs">
                  地址: {signal.address ? `${signal.address.slice(0, 6)}...${signal.address.slice(-4)}` : '未知'}
                </span>
              </div>
            </div>
          ))}
        </div>

        {whaleSignals.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <div className="text-4xl mb-2">🐋</div>
            <p>暂无巨鲸活动数据</p>
            <p className="text-sm mt-2">配置并启用 Whale Alert API 后将自动收集数据</p>
          </div>
        )}
      </div>

      {/* API Key配置模态框 */}
      {showConfigModal && selectedSource && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">🔑 配置 API Key</h3>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                数据源: {selectedSource.name}
              </label>
              <p className="text-xs text-gray-500 mb-3">{selectedSource.description}</p>
              <input
                type="password"
                value={apiKeyInput}
                onChange={(e) => setApiKeyInput(e.target.value)}
                placeholder="请输入 API Key"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              />
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded p-3 mb-4 text-sm text-blue-800">
              💡 提示: API Key 将安全存储在服务器端
            </div>
            {selectedSource.name.includes('Whale Alert') && (
              <div className="bg-green-50 border border-green-200 rounded p-3 mb-4 text-sm text-green-800">
                📝 获取 Whale Alert API Key: <a href="https://whale-alert.io/signup" target="_blank" rel="noopener noreferrer" className="underline">https://whale-alert.io/signup</a>
              </div>
            )}
            <div className="flex gap-2">
              <button
                onClick={handleSaveApiKey}
                className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
              >
                保存
              </button>
              <button
                onClick={() => setShowConfigModal(false)}
                className="flex-1 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
