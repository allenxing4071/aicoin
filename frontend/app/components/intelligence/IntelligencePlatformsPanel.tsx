"use client";

/**
 * 云平台管理面板组件 (卡片展开式布局)
 * 
 * 功能:
 * - 显示已配置的云平台列表
 * - 卡片式展开显示详细信息
 * - 启用/禁用平台
 * - 添加新的云平台
 */

import { useState, useEffect } from "react";

interface CloudPlatform {
  id: number;
  name: string;
  provider: string;
  platform_type: string;
  enabled: boolean;
  base_url: string;
  performance: {
    total_calls: number;
    success_rate: number;
    avg_response_time: number | null;
    total_cost: number;
  };
  health: {
    status: string | null;
    last_check: string | null;
  };
}

interface IntelligenceConfig {
  enabled: boolean;
  update_interval: number;
  qwen_model: string;
  mock_mode: boolean;
  data_sources: Array<{
    type: string;
    name: string;
    url: string;
    api_key: string | null;
    enabled: boolean;
    update_interval: number;
    description: string;
  }>;
}

interface IntelligenceStats {
  total_collections: number;
  successful_collections: number;
  failed_collections: number;
  last_collection_time: string | null;
  last_success_time: string | null;
  last_error: string | null;
}

export default function IntelligencePlatformsPanel() {
  const [platforms, setPlatforms] = useState<CloudPlatform[]>([]);
  const [config, setConfig] = useState<IntelligenceConfig | null>(null);
  const [stats, setStats] = useState<IntelligenceStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [reloading, setReloading] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    provider: "qwen",
    platform_type: "qwen_search",
    api_key: "",
    base_url: "",
    enabled: true
  });

  useEffect(() => {
    fetchPlatforms();
    fetchConfig();
    fetchStats();
    
    // 每30秒刷新一次
    const interval = setInterval(() => {
      fetchPlatforms();
      fetchConfig();
      fetchStats();
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchPlatforms = async () => {
    try {
      setError(null);
      
      // 添加超时控制（增加到30秒，给后端足够的初始化时间）
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30秒超时
      
      const response = await fetch("/api/v1/intelligence/platforms", {
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setPlatforms(data.platforms || []);
    } catch (error: any) {
      console.error("❌ 获取平台列表失败:", error);
      if (error.name === 'AbortError') {
        setError("请求超时（30秒），后端服务可能正在启动中，请稍后刷新页面重试");
      } else {
        setError(error.message || "获取平台列表失败");
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchConfig = async () => {
    try {
      const response = await fetch("/api/v1/admin/intelligence/config");
      if (response.ok) {
        const data = await response.json();
        setConfig(data.data);
      }
    } catch (error) {
      console.error("获取配置失败:", error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch("/api/v1/admin/intelligence/status");
      if (response.ok) {
        const data = await response.json();
        setStats(data.data.stats);
      }
    } catch (error) {
      console.error("获取统计失败:", error);
    }
  };

  const togglePlatform = async (id: number, enabled: boolean) => {
    setUpdating(true);
    try {
      await fetch(`/api/v1/intelligence/platforms/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled })
      });
      fetchPlatforms();
      alert(`平台已${enabled ? '启用' : '禁用'}`);
    } catch (error) {
      console.error("切换平台状态失败:", error);
      alert("操作失败");
    } finally {
      setUpdating(false);
    }
  };

  const handleAddPlatform = async () => {
    if (!formData.name || !formData.base_url) {
      alert("请填写必填字段:平台名称和Base URL");
      return;
    }

    setUpdating(true);
    try {
      const response = await fetch("/api/v1/intelligence/platforms", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        setShowAddForm(false);
        setFormData({
          name: "",
          provider: "qwen",
          platform_type: "qwen_search",
          api_key: "",
          base_url: "",
          enabled: true
        });
        fetchPlatforms();
        alert("✅ 平台添加成功! 正在重新加载配置...");
        
        // 自动重新加载平台配置
        await handleReloadPlatforms();
      } else {
        const error = await response.json();
        alert(`❌ 添加失败: ${error.detail || "未知错误"}`);
      }
    } catch (error) {
      console.error("添加平台失败:", error);
      alert("添加平台失败,请检查网络连接");
    } finally {
      setUpdating(false);
    }
  };

  const handleReloadPlatforms = async () => {
    setReloading(true);
    try {
      const response = await fetch("/api/v1/intelligence/platforms/reload", {
        method: "POST"
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          alert(`✅ ${data.message}`);
          fetchPlatforms();
        } else {
          alert(`⚠️ ${data.message}`);
        }
      } else {
        alert("❌ 重新加载失败");
      }
    } catch (error) {
      console.error("重新加载平台失败:", error);
      alert("重新加载失败,请检查后端服务");
    } finally {
      setReloading(false);
    }
  };

  const getProviderIcon = (provider: string) => {
    const icons: Record<string, string> = {
      baidu: "🟦",
      tencent: "🟩",
      volcano: "🟧",
      aws: "🟨",
      qwen: "🟪"
    };
    return icons[provider] || "⚪";
  };

  const getPlatformTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      qwen_search: "Qwen Search (搜索增强)",
      qwen_deep: "Qwen Deep (深度推理)",
      free: "免费API"
    };
    return labels[type] || type;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mx-auto mb-4"></div>
          <p className="text-gray-600">加载云平台配置...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
        <div className="text-red-600 mb-2">❌ 加载失败</div>
        <div className="text-sm text-red-500 mb-4">{error}</div>
        <button
          onClick={fetchPlatforms}
          className="px-4 py-2 bg-red-100 text-red-900 rounded-lg hover:bg-red-200 transition-colors"
        >
          重试
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Qwen情报系统配置 */}
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

      {/* 收集统计 */}
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

      {/* 云平台配置卡片 */}
      <div className="bg-gradient-to-br from-orange-50 to-amber-50 border border-orange-200 rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-gray-800">☁️ 云平台管理</h3>
          <div className="flex gap-2">
            <button
              onClick={handleReloadPlatforms}
              disabled={reloading || updating}
              className="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:shadow-lg transition-all flex items-center gap-2 disabled:opacity-50"
              title="重新加载平台配置（无需重启服务）"
            >
              <span className="text-xl text-white">{reloading ? '⏳' : '🔄'}</span>
              <span className="text-white">{reloading ? '加载中...' : '重新加载'}</span>
            </button>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            disabled={updating}
            className="px-4 py-2 bg-gradient-to-r from-orange-600 to-amber-600 text-white rounded-lg hover:shadow-lg transition-all flex items-center gap-2 disabled:opacity-50"
          >
            <span className="text-xl text-white">{showAddForm ? '❌' : '➕'}</span>
            <span className="text-white">{showAddForm ? '取消添加' : '添加平台'}</span>
          </button>
          </div>
        </div>

        {/* 添加平台表单 */}
        {showAddForm && (
          <div className="mb-6 bg-white/90 border-2 border-orange-300 rounded-xl p-6 shadow-lg">
            <h4 className="text-md font-bold text-gray-800 mb-4">➕ 添加云平台</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* 平台名称 */}
              <div>
                <label className="block text-sm font-medium text-orange-900 mb-2">
                  <span className="text-red-500">*</span> 平台名称
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  placeholder="例如: Qwen主平台"
                  className="w-full px-3 py-2 border border-orange-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                />
              </div>

              {/* 服务商 */}
              <div>
                <label className="block text-sm font-medium text-orange-900 mb-2">
                  服务商
                </label>
                <select
                  value={formData.provider}
                  onChange={(e) => setFormData({...formData, provider: e.target.value})}
                  className="w-full px-3 py-2 border border-orange-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                >
                  <option value="qwen">🟪 Qwen (阿里云)</option>
                  <option value="baidu">🟦 百度千帆</option>
                  <option value="tencent">🟩 腾讯混元</option>
                  <option value="volcano">🟧 火山引擎</option>
                  <option value="aws">🟨 AWS Bedrock</option>
                </select>
              </div>

              {/* 平台类型 */}
              <div>
                <label className="block text-sm font-medium text-orange-900 mb-2">
                  平台类型
                </label>
                <select
                  value={formData.platform_type}
                  onChange={(e) => setFormData({...formData, platform_type: e.target.value})}
                  className="w-full px-3 py-2 border border-orange-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                >
                  <option value="qwen_search">Qwen Search (搜索增强)</option>
                  <option value="qwen_deep">Qwen Deep (深度推理)</option>
                  <option value="free">免费API</option>
                </select>
              </div>

              {/* Base URL */}
              <div>
                <label className="block text-sm font-medium text-orange-900 mb-2">
                  <span className="text-red-500">*</span> Base URL
                </label>
                <input
                  type="text"
                  value={formData.base_url}
                  onChange={(e) => setFormData({...formData, base_url: e.target.value})}
                  placeholder="https://api.example.com/v1"
                  className="w-full px-3 py-2 border border-orange-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                />
              </div>

              {/* API Key */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-orange-900 mb-2">
                  API Key (可选)
                </label>
                <input
                  type="password"
                  value={formData.api_key}
                  onChange={(e) => setFormData({...formData, api_key: e.target.value})}
                  placeholder="留空表示不需要认证"
                  className="w-full px-3 py-2 border border-orange-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                />
              </div>

              {/* 是否启用 */}
              <div className="md:col-span-2 flex items-center gap-2">
                <input
                  type="checkbox"
                  id="enabled"
                  checked={formData.enabled}
                  onChange={(e) => setFormData({...formData, enabled: e.target.checked})}
                  className="w-4 h-4 text-orange-600 border-orange-300 rounded focus:ring-orange-500"
                />
                <label htmlFor="enabled" className="text-sm font-medium text-orange-900">
                  添加后立即启用
                </label>
              </div>
            </div>

            {/* 提示信息 */}
            <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-xs text-blue-800">
                💡 <strong>提示:</strong> 新闻源通常支持RSS feed,无需API Key。巨鲸监控和链上数据需要API认证。 建议先添加测试平台进行连接测试。
              </p>
            </div>

            {/* 操作按钮 */}
            <div className="flex gap-3 mt-6">
              <button
                onClick={handleAddPlatform}
                disabled={updating || !formData.name || !formData.base_url}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-orange-600 to-amber-600 text-white rounded-lg hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium"
              >
                {updating ? '添加中...' : '✅ 确认添加'}
              </button>
              <button
                onClick={() => {
                  setShowAddForm(false);
                  setFormData({
                    name: "",
                    provider: "qwen",
                    platform_type: "qwen_search",
                    api_key: "",
                    base_url: "",
                    enabled: true
                  });
                }}
                className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all font-medium"
              >
                ✖️ 取消
              </button>
            </div>
          </div>
        )}

        {/* 平台列表 */}
        <div className="space-y-3">
          {platforms.length === 0 ? (
            <div className="bg-white/70 rounded-lg p-8 text-center">
              <div className="text-4xl mb-3">☁️</div>
              <p className="text-gray-600 mb-2">暂无云平台配置</p>
              <p className="text-sm text-gray-500">
                点击"添加平台"按钮配置第一个云平台,<br/>
                支持AWS、Qwen等多种云平台API
              </p>
            </div>
          ) : (
            platforms.map((platform) => (
              <div
                key={platform.id}
                className="bg-white/70 rounded-lg border border-orange-200 p-4 hover:shadow-md transition-all"
              >
                <div className="flex items-center justify-between">
                  {/* 左侧信息 */}
                  <div className="flex items-center gap-4 flex-1">
                    <div className="text-3xl">{getProviderIcon(platform.provider)}</div>
                    
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-bold text-gray-900">{platform.name}</h4>
                        <span className={`px-2 py-0.5 text-xs rounded ${
                          platform.enabled
                            ? "bg-green-100 text-green-800"
                            : "bg-gray-100 text-gray-600"
                        }`}>
                          {platform.enabled ? "启用" : "禁用"}
                        </span>
                      </div>
                      
                      <div className="text-sm text-gray-600 space-y-1">
                        <div>
                          <span className="font-medium">类型:</span> {getPlatformTypeLabel(platform.platform_type)}
                        </div>
                        <div className="flex items-center gap-4">
                          <span>
                            <span className="font-medium">调用:</span> {platform.performance.total_calls}
                          </span>
                          <span>
                            <span className="font-medium">成功率:</span> {(platform.performance.success_rate * 100).toFixed(1)}%
                          </span>
                          {platform.performance.avg_response_time && (
                            <span>
                              <span className="font-medium">响应:</span> {platform.performance.avg_response_time.toFixed(2)}s
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-gray-500">
                          {platform.base_url}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* 右侧操作 */}
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => togglePlatform(platform.id, !platform.enabled)}
                      disabled={updating}
                      className={`px-4 py-2 rounded-lg font-medium transition-all ${
                        platform.enabled
                          ? "bg-gray-200 text-gray-700 hover:bg-gray-300"
                          : "bg-gradient-to-r from-green-600 to-emerald-600 text-white hover:shadow-lg"
                      } disabled:opacity-50`}
                    >
                      {platform.enabled ? '停用' : '启用'}
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* 云平台管理说明 */}
      <div className="bg-gradient-to-br from-yellow-50 to-amber-50 border border-yellow-300 rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
          <span>📖</span>
          <span>云平台管理说明</span>
        </h3>

        <div className="space-y-4">
          {/* 工作原理 */}
          <div>
            <div className="flex items-start gap-2 mb-2">
              <span className="text-xl">🔄</span>
              <div className="flex-1">
                <h4 className="font-bold text-gray-900 mb-1">工作原理：</h4>
                <p className="text-sm text-gray-700 leading-relaxed">
                  系统采用<strong>多云平台并行分析</strong>架构，同时调用多个AI云平台对相同数据进行分析，
                  通过<strong>交叉验证</strong>提升情报准确性。类似"专家会诊"机制，多个AI同时分析，取得共识的信息置信度更高。
                </p>
              </div>
            </div>
          </div>

          {/* 数据流程 */}
          <div>
            <div className="flex items-start gap-2 mb-2">
              <span className="text-xl">📊</span>
              <div className="flex-1">
                <h4 className="font-bold text-gray-900 mb-1">数据流程：</h4>
                <div className="text-sm text-gray-700 space-y-1">
                  <p><strong>1. 数据收集</strong> → RSS新闻源定期抓取最新资讯（30分钟/次）</p>
                  <p><strong>2. 并行分析</strong> → 多个云平台同时分析相同数据</p>
                  <p><strong>3. 交叉验证</strong> → 对比各平台结果，计算置信度</p>
                  <p><strong>4. 生成报告</strong> → 输出综合情报报告（准确率85%+）</p>
                </div>
              </div>
            </div>
          </div>

          {/* 平台配置 */}
          <div>
            <div className="flex items-start gap-2 mb-2">
              <span className="text-xl">⚙️</span>
              <div className="flex-1">
                <h4 className="font-bold text-gray-900 mb-1">配置要求：</h4>
                <div className="text-sm text-gray-700 space-y-1">
                  <p>• <strong>推荐配置</strong>：至少3个云平台（提升准确率至85%+）</p>
                  <p>• <strong>最低配置</strong>：1个云平台（基础功能可用，准确率70%）</p>
                  <p>• <strong>API密钥</strong>：需要在各云平台官网申请API Key</p>
                  <p>• <strong>成本控制</strong>：可监控各平台调用次数和费用</p>
                </div>
              </div>
            </div>
          </div>

          {/* 注意事项 */}
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
            <div className="flex items-start gap-2">
              <span className="text-orange-600 text-lg">⚠️</span>
              <div className="flex-1">
                <p className="text-sm font-medium text-orange-800 mb-1">
                  重要提示
                </p>
                <ul className="text-xs text-orange-700 space-y-1 list-disc list-inside">
                  <li>云平台配置需要重启后端服务才能生效</li>
                  <li>建议先在测试环境验证API Key的有效性</li>
                  <li>多平台并行会增加API调用成本，请注意费用控制</li>
                  <li>可以随时启用/禁用单个平台，无需删除配置</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
