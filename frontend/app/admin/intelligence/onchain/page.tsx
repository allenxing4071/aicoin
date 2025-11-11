'use client';

/**
 * 链上数据页面
 * 
 * 路径: /admin/intelligence/onchain
 * 
 * 功能：
 * - 链上指标展示
 * - 数据可视化
 * - 数据源管理
 */

import React, { useState, useEffect } from 'react';
import PageHeader from '@/app/components/common/PageHeader';
import { unifiedDesignSystem, getThemeStyles } from '@/app/admin/unified-design-system';

interface OnChainMetrics {
  exchange_net_flow?: number;
  active_addresses?: number;
  gas_price?: number;
  transaction_volume?: number;
  timestamp?: string;
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

export default function OnChainDataPage() {
  const theme = getThemeStyles('blue');
  const [metrics, setMetrics] = useState<OnChainMetrics[]>([]);
  const [latestMetrics, setLatestMetrics] = useState<OnChainMetrics | null>(null);
  const [sources, setSources] = useState<DataSource[]>([]);
  const [sourceStatuses, setSourceStatuses] = useState<SourceStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState<string | null>(null);
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
      const configRes = await fetch('/api/v1/admin/intelligence/config');
      const configData = await configRes.json();
      if (configData.success && configData.data.data_sources) {
        const onchainSources = configData.data.data_sources.filter(
          (s: DataSource) => s.type === 'onchain'
        );
        setSources(onchainSources);
      }

      // 获取数据源状态
      const statusRes = await fetch('/api/v1/admin/intelligence/data-sources/status');
      const statusData = await statusRes.json();
      if (Array.isArray(statusData)) {
        const onchainStatuses = statusData.filter((s: SourceStatus) => s.type === 'onchain');
        setSourceStatuses(onchainStatuses);
      }

      // 获取链上指标（从情报报告中提取）
      const reportsRes = await fetch('/api/v1/intelligence/reports?limit=20');
      const reportsData = await reportsRes.json();
      if (reportsData.success && reportsData.data) {
        const allMetrics: OnChainMetrics[] = [];
        reportsData.data.forEach((report: any) => {
          if (report.on_chain_metrics) {
            allMetrics.push({
              ...report.on_chain_metrics,
              timestamp: report.timestamp,
            });
          }
        });
        setMetrics(allMetrics);
        if (allMetrics.length > 0) {
          setLatestMetrics(allMetrics[0]);
        }
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
        `/api/v1/admin/intelligence/data-sources/${encodeURIComponent(sourceName)}/toggle?enabled=${!currentEnabled}`,
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
        `/api/v1/admin/intelligence/data-sources/${encodeURIComponent(sourceName)}/test-connection`,
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
      const configRes = await fetch('/api/v1/admin/intelligence/config');
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
      const saveRes = await fetch('/api/v1/admin/intelligence/config', {
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

  const formatNumber = (num: number | undefined) => {
    if (num === undefined) return 'N/A';
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(2)}M`;
    } else if (num >= 1000) {
      return `${(num / 1000).toFixed(2)}K`;
    }
    return num.toFixed(2);
  };

  const getFlowColor = (flow: number | undefined) => {
    if (flow === undefined) return 'text-gray-600';
    if (flow > 0) return 'text-green-600';
    if (flow < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const getFlowIcon = (flow: number | undefined) => {
    if (flow === undefined) return '➖';
    if (flow > 0) return '📈';
    if (flow < 0) return '📉';
    return '➖';
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
        icon="⛓️"
        title="链上数据监控"
        description="监控和分析链上数据指标，洞察市场趋势"
        color="purple"
      />

      {/* 最新指标卡片 */}
      {latestMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 shadow-lg border-2 border-blue-300">
            <div className="text-sm text-gray-500 mb-1">交易所净流入</div>
            <div className={`text-3xl font-bold ${getFlowColor(latestMetrics.exchange_net_flow)}`}>
              {getFlowIcon(latestMetrics.exchange_net_flow)} {formatNumber(latestMetrics.exchange_net_flow)}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {latestMetrics.exchange_net_flow && latestMetrics.exchange_net_flow > 0 ? '资金流入' : '资金流出'}
            </div>
          </div>
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 shadow-lg border-2 border-green-300">
            <div className="text-sm text-gray-500 mb-1">活跃地址数</div>
            <div className="text-3xl font-bold text-green-600">
              {formatNumber(latestMetrics.active_addresses)}
            </div>
          </div>
          <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-6 shadow-lg border-2 border-orange-300">
            <div className="text-sm text-gray-500 mb-1">Gas价格</div>
            <div className="text-3xl font-bold text-orange-600">
              {latestMetrics.gas_price ? `${latestMetrics.gas_price.toFixed(0)} Gwei` : 'N/A'}
            </div>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 shadow-lg border-2 border-purple-300">
            <div className="text-sm text-gray-500 mb-1">交易量</div>
            <div className="text-3xl font-bold text-purple-600">
              {formatNumber(latestMetrics.transaction_volume)}
            </div>
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
                      className="px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700"
                    >
                      🔑 配置Key
                    </button>
                    <button
                      onClick={() => handleTestConnection(source.name)}
                      disabled={testing === source.name || !source.api_key}
                      className="px-3 py-1 text-sm bg-purple-600 text-white rounded hover:bg-purple-700 disabled:bg-gray-400"
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
            <p>暂无链上数据源配置</p>
          </div>
        )}
      </div>

      {/* 历史数据趋势 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 历史数据</h3>
        
        <div className="space-y-3">
          {metrics.slice(0, 10).map((metric, idx) => (
            <div key={idx} className="border-l-4 border-purple-500 pl-4 py-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-gray-900">
                  {metric.timestamp ? new Date(metric.timestamp).toLocaleString('zh-CN') : '未知时间'}
                </span>
              </div>
              <div className="grid grid-cols-4 gap-4 text-sm">
                <div>
                  <div className="text-xs text-gray-500">净流入</div>
                  <div className={`font-semibold ${getFlowColor(metric.exchange_net_flow)}`}>
                    {formatNumber(metric.exchange_net_flow)}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">活跃地址</div>
                  <div className="font-semibold text-gray-900">{formatNumber(metric.active_addresses)}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">Gas价格</div>
                  <div className="font-semibold text-gray-900">
                    {metric.gas_price ? `${metric.gas_price.toFixed(0)} Gwei` : 'N/A'}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">交易量</div>
                  <div className="font-semibold text-gray-900">{formatNumber(metric.transaction_volume)}</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {metrics.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <div className="text-4xl mb-2">⛓️</div>
            <p>暂无链上数据</p>
            <p className="text-sm mt-2">配置并启用链上数据源后将自动收集数据</p>
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
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded p-3 mb-4 text-sm text-blue-800">
              💡 提示: API Key 将安全存储在服务器端
            </div>
            {selectedSource.name.includes('Etherscan') && (
              <div className="bg-green-50 border border-green-200 rounded p-3 mb-4 text-sm text-green-800">
                📝 获取 Etherscan API Key: <a href="https://etherscan.io/myapikey" target="_blank" rel="noopener noreferrer" className="underline">https://etherscan.io/myapikey</a>
              </div>
            )}
            {selectedSource.name.includes('Glassnode') && (
              <div className="bg-green-50 border border-green-200 rounded p-3 mb-4 text-sm text-green-800">
                📝 获取 Glassnode API Key: <a href="https://studio.glassnode.com/settings/api" target="_blank" rel="noopener noreferrer" className="underline">https://studio.glassnode.com/settings/api</a>
              </div>
            )}
            <div className="flex gap-2">
              <button
                onClick={handleSaveApiKey}
                className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
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
