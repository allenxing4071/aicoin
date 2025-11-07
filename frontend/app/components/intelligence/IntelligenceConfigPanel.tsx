'use client';

/**
 * 情报系统配置和监控面板
 * 
 * 功能：
 * 1. 显示当前情报配置（数据源、更新频率）
 * 2. 显示数据源状态（活跃、错误、禁用）
 * 3. 显示数据来源URL和抓取路径
 * 4. 实时监控情报收集状态
 * 5. 配置管理（启用/禁用数据源）
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

interface DataSource {
  type: string;
  name: string;
  url: string | null;
  api_key: string | null;
  enabled: boolean;
  update_interval: number;
  description: string;
}

interface DataSourceStatus {
  name: string;
  type: string;
  status: string;
  last_update: string | null;
  last_error: string | null;
  total_calls: number;
  success_rate: number;
  data_source_url: string | null;
  description: string;
}

interface IntelligenceConfig {
  enabled: boolean;
  update_interval: number;
  qwen_model: string;
  data_sources: DataSource[];
  mock_mode: boolean;
}

interface IntelligenceStats {
  total_collections: number;
  successful_collections: number;
  failed_collections: number;
  last_collection_time: string | null;
  last_success_time: string | null;
  last_error: string | null;
}

export default function IntelligenceConfigPanel() {
  const [config, setConfig] = useState<IntelligenceConfig | null>(null);
  const [sourcesStatus, setSourcesStatus] = useState<DataSourceStatus[]>([]);
  const [stats, setStats] = useState<IntelligenceStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [editingSource, setEditingSource] = useState<string | null>(null);
  const [apiKeyInput, setApiKeyInput] = useState<string>('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [newSource, setNewSource] = useState({
    name: '',
    type: 'news' as 'news' | 'whale' | 'onchain' | 'mock',
    url: '',
    api_key: '',
    description: '',
    update_interval: 1800
  });

  // 加载配置和状态
  const loadData = async () => {
    try {
      const [configRes, statusRes, statsRes] = await Promise.all([
        axios.get(`${API_BASE}/admin/intelligence/config`),
        axios.get(`${API_BASE}/admin/intelligence/data-sources/status`),
        axios.get(`${API_BASE}/admin/intelligence/status`)
      ]);

      if (configRes.data.success) {
        setConfig(configRes.data.data);
      }

      setSourcesStatus(statusRes.data);
      
      if (statsRes.data.success) {
        setStats(statsRes.data.data.stats);
      }

      setLoading(false);
    } catch (error) {
      console.error('加载情报配置失败:', error);
      setLoading(false);
    }
  };

  // 切换数据源状态
  const toggleDataSource = async (sourceName: string, enabled: boolean) => {
    setUpdating(true);
    try {
      await axios.post(`${API_BASE}/admin/intelligence/data-sources/${encodeURIComponent(sourceName)}/toggle`, null, {
        params: { enabled }
      });
      
      // 重新加载数据
      await loadData();
      
      alert(`数据源 "${sourceName}" 已${enabled ? '启用' : '禁用'}`);
    } catch (error) {
      console.error('切换数据源失败:', error);
      alert('操作失败');
    } finally {
      setUpdating(false);
    }
  };

  // 保存API Key
  const saveApiKey = async (sourceName: string) => {
    if (!apiKeyInput.trim()) {
      alert('请输入API Key');
      return;
    }

    setUpdating(true);
    try {
      // 获取当前配置
      const configRes = await axios.get(`${API_BASE}/admin/intelligence/config`);
      const currentConfig = configRes.data.data;

      // 更新指定数据源的API Key
      const updatedSources = currentConfig.data_sources.map((source: DataSource) => {
        if (source.name === sourceName) {
          return { ...source, api_key: apiKeyInput };
        }
        return source;
      });

      // 保存配置
      await axios.post(`${API_BASE}/admin/intelligence/config`, {
        ...currentConfig,
        data_sources: updatedSources
      });

      // 重新加载数据
      await loadData();

      alert(`✅ API Key已保存！\n数据源 "${sourceName}" 现在可以使用真实数据了。`);
      setEditingSource(null);
      setApiKeyInput('');
    } catch (error) {
      console.error('保存API Key失败:', error);
      alert('保存失败');
    } finally {
      setUpdating(false);
    }
  };

  // 测试连接
  const testConnection = async (sourceName: string) => {
    setUpdating(true);
    try {
      const response = await axios.post(`${API_BASE}/admin/intelligence/data-sources/${encodeURIComponent(sourceName)}/test-connection`);
      
      if (response.data.success) {
        const data = response.data.data;
        alert(`✅ ${response.data.message}\n\n` +
              `状态: ${data.status}\n` +
              `响应时间: ${data.response_time_ms}ms\n` +
              (data.api_valid !== undefined ? `API有效性: ${data.api_valid ? '有效' : '无效'}\n` : '') +
              (data.content_length !== undefined ? `内容大小: ${data.content_length} bytes\n` : '') +
              (data.sample_data_count !== undefined ? `样本数据: ${data.sample_data_count} 条\n` : '')
        );
      } else {
        alert(`❌ ${response.data.message}\n\n` +
              `状态: ${response.data.data?.status || '未知'}\n` +
              (response.data.data?.error ? `错误: ${response.data.data.error}\n` : '')
        );
      }
    } catch (error: any) {
      console.error('测试连接失败:', error);
      alert(`❌ 测试连接失败\n\n${error.response?.data?.detail || error.message}`);
    } finally {
      setUpdating(false);
    }
  };

  // 添加新数据源
  const addNewSource = async () => {
    if (!newSource.name || !newSource.url) {
      alert('❌ 请填写数据源名称和URL');
      return;
    }

    setUpdating(true);
    try {
      // 获取当前配置
      const configRes = await axios.get(`${API_BASE}/admin/intelligence/config`);
      const currentConfig = configRes.data.data;

      // 检查是否已存在同名数据源
      if (currentConfig.data_sources.some((s: DataSource) => s.name === newSource.name)) {
        alert('❌ 数据源名称已存在，请使用不同的名称');
        setUpdating(false);
        return;
      }

      // 添加新数据源
      const updatedConfig = {
        ...currentConfig,
        data_sources: [
          ...currentConfig.data_sources,
          {
            type: newSource.type,
            name: newSource.name,
            url: newSource.url,
            api_key: newSource.api_key || null,
            enabled: false,
            update_interval: newSource.update_interval,
            description: newSource.description || `${newSource.name} - 自定义数据源`
          }
        ]
      };

      await axios.post(`${API_BASE}/admin/intelligence/config`, updatedConfig);
      
      alert('✅ 数据源添加成功！');
      
      // 重置表单
      setNewSource({
        name: '',
        type: 'news',
        url: '',
        api_key: '',
        description: '',
        update_interval: 1800
      });
      setShowAddForm(false);
      
      // 重新加载数据
      await loadData();
    } catch (error: any) {
      console.error('添加数据源失败:', error);
      alert(`❌ 添加失败：${error.response?.data?.detail || error.message}`);
    } finally {
      setUpdating(false);
    }
  };

  // 删除数据源
  const deleteDataSource = async (sourceName: string) => {
    if (!confirm(`确定要删除数据源 "${sourceName}" 吗？\n\n此操作不可恢复！`)) {
      return;
    }

    setUpdating(true);
    try {
      // 获取当前配置
      const configRes = await axios.get(`${API_BASE}/admin/intelligence/config`);
      const currentConfig = configRes.data.data;

      // 移除指定数据源
      const updatedConfig = {
        ...currentConfig,
        data_sources: currentConfig.data_sources.filter((s: DataSource) => s.name !== sourceName)
      };

      await axios.post(`${API_BASE}/admin/intelligence/config`, updatedConfig);
      
      alert('✅ 数据源删除成功！');
      
      // 重新加载数据
      await loadData();
    } catch (error: any) {
      console.error('删除数据源失败:', error);
      alert(`❌ 删除失败：${error.response?.data?.detail || error.message}`);
    } finally {
      setUpdating(false);
    }
  };

  useEffect(() => {
    loadData();
    
    // 每30秒刷新一次状态
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 系统配置卡片 */}
      <div className="bg-gradient-to-br from-indigo-50 to-purple-50 border border-indigo-200 rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-bold mb-4 bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
          🕵️‍♀️ Qwen情报系统配置
        </h2>
        
        {config && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white/70 rounded-lg p-4">
              <div className="text-sm text-orange-700 mb-1">系统状态</div>
              <div className={`text-2xl font-bold ${config.enabled ? 'text-green-600' : 'text-red-600'}`}>
                {config.enabled ? '✅ 运行中' : '⏸️ 已停止'}
              </div>
            </div>
            
            <div className="bg-white/70 rounded-lg p-4">
              <div className="text-sm text-orange-700 mb-1">更新频率</div>
              <div className="text-2xl font-bold text-indigo-600">
                {Math.floor(config.update_interval / 60)}分钟
              </div>
            </div>
            
            <div className="bg-white/70 rounded-lg p-4">
              <div className="text-sm text-orange-700 mb-1">AI模型</div>
              <div className="text-lg font-bold text-purple-600">
                {config.qwen_model}
              </div>
            </div>
            
            <div className="bg-white/70 rounded-lg p-4">
              <div className="text-sm text-orange-700 mb-1">数据模式</div>
              <div className={`text-lg font-bold ${config.mock_mode ? 'text-orange-600' : 'text-green-600'}`}>
                {config.mock_mode ? '🧪 模拟数据' : '🌐 真实数据'}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 统计信息 */}
      {stats && (
        <div className="bg-gradient-to-br from-blue-50 to-cyan-50 border border-blue-200 rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-bold mb-4 text-gray-800">📊 收集统计</h3>
          
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="bg-white/70 rounded-lg p-3">
              <div className="text-xs text-orange-700 mb-1">总收集次数</div>
              <div className="text-xl font-bold text-blue-600">{stats.total_collections}</div>
            </div>
            
            <div className="bg-white/70 rounded-lg p-3">
              <div className="text-xs text-orange-700 mb-1">成功次数</div>
              <div className="text-xl font-bold text-green-600">{stats.successful_collections}</div>
            </div>
            
            <div className="bg-white/70 rounded-lg p-3">
              <div className="text-xs text-orange-700 mb-1">失败次数</div>
              <div className="text-xl font-bold text-red-600">{stats.failed_collections}</div>
            </div>
            
            <div className="bg-white/70 rounded-lg p-3">
              <div className="text-xs text-orange-700 mb-1">成功率</div>
              <div className="text-xl font-bold text-purple-600">
                {stats.total_collections > 0 
                  ? Math.round((stats.successful_collections / stats.total_collections) * 100) 
                  : 0}%
              </div>
            </div>
            
            <div className="bg-white/70 rounded-lg p-3">
              <div className="text-xs text-orange-700 mb-1">最后收集</div>
              <div className="text-sm font-semibold text-gray-800">
                {stats.last_collection_time 
                  ? new Date(stats.last_collection_time).toLocaleTimeString('zh-CN')
                  : '未知'}
              </div>
            </div>
          </div>
          
          {stats.last_error && (
            <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-3">
              <div className="text-sm text-red-600">
                <strong>最后错误：</strong> {stats.last_error}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 数据源列表 */}
      <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-gray-800">🔌 数据源配置</h3>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:shadow-lg transition-all flex items-center gap-2"
          >
            <span className="text-xl text-white">{showAddForm ? '❌' : '➕'}</span>
            <span className="text-white">{showAddForm ? '取消添加' : '添加数据源'}</span>
          </button>
        </div>

        {/* 添加数据源表单 */}
        {showAddForm && (
          <div className="mb-6 bg-white/90 border-2 border-green-300 rounded-xl p-6 shadow-lg">
            <h4 className="text-md font-bold text-gray-800 mb-4">➕ 添加新数据源</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* 数据源名称 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <span className="text-red-500">*</span> 数据源名称
                </label>
                <input
                  type="text"
                  value={newSource.name}
                  onChange={(e) => setNewSource({...newSource, name: e.target.value})}
                  placeholder="例如: Bloomberg News"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>

              {/* 数据源类型 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <span className="text-red-500">*</span> 数据源类型
                </label>
                <select
                  value={newSource.type}
                  onChange={(e) => setNewSource({...newSource, type: e.target.value as any})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="news">📰 新闻源 (news)</option>
                  <option value="whale">🐋 巨鲸监控 (whale)</option>
                  <option value="onchain">📊 链上数据 (onchain)</option>
                  <option value="mock">🧪 模拟数据 (mock)</option>
                </select>
              </div>

              {/* 数据源URL */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <span className="text-red-500">*</span> 数据源URL
                </label>
                <input
                  type="url"
                  value={newSource.url}
                  onChange={(e) => setNewSource({...newSource, url: e.target.value})}
                  placeholder="例如: https://api.example.com/news"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">
                  支持RSS订阅、REST API等。如果是RSS源，请填写RSS feed的URL。
                </p>
              </div>

              {/* API Key (可选) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  API Key (可选)
                </label>
                <input
                  type="password"
                  value={newSource.api_key}
                  onChange={(e) => setNewSource({...newSource, api_key: e.target.value})}
                  placeholder="如果API需要认证，请填写"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>

              {/* 更新间隔 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  更新间隔 (秒)
                </label>
                <input
                  type="number"
                  value={newSource.update_interval}
                  onChange={(e) => setNewSource({...newSource, update_interval: parseInt(e.target.value) || 1800})}
                  placeholder="1800"
                  min="60"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">
                  建议: 新闻源1800秒(30分钟)，巨鲸600秒(10分钟)
                </p>
              </div>

              {/* 描述 */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  描述 (可选)
                </label>
                <textarea
                  value={newSource.description}
                  onChange={(e) => setNewSource({...newSource, description: e.target.value})}
                  placeholder="简要描述这个数据源的用途..."
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* 操作按钮 */}
            <div className="flex gap-3 mt-6">
              <button
                onClick={addNewSource}
                disabled={updating || !newSource.name || !newSource.url}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-orange-900 rounded-lg hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium"
              >
                {updating ? '添加中...' : '✅ 确认添加'}
              </button>
              <button
                onClick={() => {
                  setShowAddForm(false);
                  setNewSource({
                    name: '',
                    type: 'news',
                    url: '',
                    api_key: '',
                    description: '',
                    update_interval: 1800
                  });
                }}
                className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all font-medium"
              >
                ❌ 取消
              </button>
            </div>

            {/* 提示信息 */}
            <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-3">
              <div className="text-sm text-blue-800">
                <strong>💡 提示：</strong>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li>新闻源通常是RSS feed，无需API Key</li>
                  <li>巨鲸监控和链上数据通常需要API Key</li>
                  <li>添加后默认为禁用状态，需要手动启用</li>
                  <li>建议先测试连接，确认可用后再启用</li>
                </ul>
              </div>
            </div>
          </div>
        )}
        
        <div className="space-y-4">
          {sourcesStatus.map((source) => (
            <div 
              key={source.name}
              className="bg-white/80 border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                    <span className="text-lg font-semibold">{source.name}</span>
                    <span className={`px-2 py-1 text-xs rounded-full font-medium ${
                      source.status === 'active' ? 'bg-green-100 text-green-700' :
                      source.status === 'error' ? 'bg-red-100 text-red-700' :
                      'bg-gray-50 text-gray-700'
                    }`}>
                      {source.status === 'active' ? '✅ 活跃' : 
                       source.status === 'error' ? '❌ 错误' : 
                       '⏸️ 禁用'}
                    </span>
                    <span className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full font-medium">
                      {source.type}
                    </span>
                    {/* API Key配置状态标记 */}
                    {source.type !== 'news' && source.type !== 'mock' && (
                      config?.data_sources.find(s => s.name === source.name)?.api_key ? (
                        <span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full font-medium">
                          🔑 已配置密钥
                        </span>
                      ) : (
                        <span className="px-2 py-1 text-xs bg-orange-100 text-orange-700 rounded-full font-medium animate-pulse">
                          ⚠️ 需要配置API Key
                        </span>
                      )
                    )}
                  </div>
                  
                  <p className="text-sm text-orange-700 mb-2">{source.description}</p>
                  
                  {source.data_source_url && (
                    <div className="mb-2">
                      <span className="text-xs text-gray-500">数据源URL：</span>
                      <code className="text-xs bg-gray-50 px-2 py-1 rounded ml-1">
                        {source.data_source_url}
                      </code>
                    </div>
                  )}
                  
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span>总调用: {source.total_calls}</span>
                    <span>成功率: {source.success_rate.toFixed(1)}%</span>
                    {source.last_update && (
                      <span>最后更新: {new Date(source.last_update).toLocaleString('zh-CN')}</span>
                    )}
                  </div>
                  
                  {source.last_error && (
                    <div className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded">
                      错误: {source.last_error}
                    </div>
                  )}

                  {/* API Key配置区域 */}
                  {source.type !== 'mock' && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      {/* 未配置API Key的警告提示 */}
                      {source.type !== 'news' && !config?.data_sources.find(s => s.name === source.name)?.api_key && editingSource !== source.name && (
                        <div className="mb-3 bg-orange-50 border border-orange-200 rounded-lg p-3">
                          <div className="flex items-start gap-2">
                            <span className="text-orange-600 text-lg">⚠️</span>
                            <div className="flex-1">
                              <p className="text-sm font-medium text-orange-800 mb-1">
                                此数据源需要配置API Key才能使用
                              </p>
                              <p className="text-xs text-orange-600">
                                {source.type === 'whale' && '巨鲸监控服务需要Whale Alert API密钥'}
                                {source.type === 'onchain' && '链上数据服务需要Etherscan或Glassnode API密钥'}
                              </p>
                            </div>
                          </div>
                        </div>
                      )}
                      
                      {editingSource === source.name ? (
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <label className="text-xs font-medium text-gray-700">API Key:</label>
                            {config?.data_sources.find(s => s.name === source.name)?.api_key && (
                              <span className="text-xs text-green-600">✓ 已配置</span>
                            )}
                          </div>
                          <div className="flex gap-2">
                            <input
                              type="password"
                              value={apiKeyInput}
                              onChange={(e) => setApiKeyInput(e.target.value)}
                              placeholder="输入API Key..."
                              className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                            <button
                              onClick={() => saveApiKey(source.name)}
                              disabled={updating}
                              className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50"
                            >
                              保存
                            </button>
                            <button
                              onClick={() => {
                                setEditingSource(null);
                                setApiKeyInput('');
                              }}
                              className="px-4 py-2 bg-gray-200 text-gray-700 text-sm rounded-lg hover:bg-gray-300"
                            >
                              取消
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => {
                              setEditingSource(source.name);
                              setApiKeyInput(config?.data_sources.find(s => s.name === source.name)?.api_key || '');
                            }}
                            className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                          >
                            🔑 配置API Key
                          </button>
                          {config?.data_sources.find(s => s.name === source.name)?.api_key && (
                            <>
                              <span className="text-xs text-orange-700">|</span>
                              <button
                                onClick={() => testConnection(source.name)}
                                disabled={updating}
                                className="text-xs text-green-600 hover:text-green-800 font-medium disabled:opacity-50"
                              >
                                🧪 测试连接
                              </button>
                            </>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
                
                <div className="ml-4 flex flex-col gap-2">
                  <button
                    onClick={() => toggleDataSource(source.name, source.status !== 'active')}
                    disabled={updating}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      source.status === 'active'
                        ? 'bg-red-100 hover:bg-red-200 text-red-700'
                        : 'bg-green-100 hover:bg-green-200 text-green-700'
                    } ${updating ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    {source.status === 'active' ? '禁用' : '启用'}
                  </button>
                  
                  {/* 删除按钮 - 只对非默认数据源显示 */}
                  {!['CoinDesk RSS', 'CoinTelegraph RSS', 'Whale Alert API', 'Etherscan API', 'Glassnode API', '模拟数据源'].includes(source.name) && (
                    <button
                      onClick={() => deleteDataSource(source.name)}
                      disabled={updating}
                      className="px-4 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                      title="删除此数据源"
                    >
                      🗑️ 删除
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 说明文档 */}
      <div className="bg-gradient-to-br from-yellow-50 to-amber-50 border border-yellow-200 rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-bold mb-3 text-gray-800">📖 情报系统说明</h3>
        
        <div className="space-y-3 text-sm text-gray-700">
          <div>
            <strong className="text-amber-700">🔍 数据来源透明化：</strong>
            <p className="ml-4 mt-1">
              所有数据源的URL和抓取路径都已公开显示。您可以看到每个数据源的具体来源、更新频率和运行状态。
            </p>
          </div>
          
          <div>
            <strong className="text-amber-700">🧪 模拟数据 vs 真实数据：</strong>
            <p className="ml-4 mt-1">
              当前系统默认使用<strong>模拟数据</strong>进行测试。要使用真实数据，需要：
              <br />1. 配置相应的API Key（CoinDesk、Whale Alert、Glassnode等）
              <br />2. 启用对应的数据源
              <br />3. 在配置中关闭"模拟模式"
            </p>
          </div>
          
          <div>
            <strong className="text-amber-700">⚙️ 配置方法：</strong>
            <p className="ml-4 mt-1">
              目前配置需要通过API完成。未来版本将提供可视化配置界面。
              <br />API端点: <code className="bg-gray-50 px-1 py-0.5 rounded">POST /api/v1/admin/intelligence/config</code>
            </p>
          </div>
          
          <div>
            <strong className="text-amber-700">📡 数据源类型：</strong>
            <p className="ml-4 mt-1">
              • <strong>news</strong>: 加密货币新闻（CoinDesk、CoinTelegraph）
              <br />• <strong>whale</strong>: 巨鲸交易监控（Whale Alert）
              <br />• <strong>onchain</strong>: 链上数据指标（Etherscan、Glassnode）
              <br />• <strong>mock</strong>: 模拟数据（用于测试和演示）
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

