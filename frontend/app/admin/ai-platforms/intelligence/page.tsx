'use client';

/**
 * 情报模型配置页面
 * 
 * 路径: /admin/ai-platforms/intelligence
 * 
 * 功能：
 * - 显示所有Qwen系列情报模型（通义千问、腾讯混元、火山引擎、百度文心）
 * - 配置API密钥、Base URL
 * - 启用/禁用开关
 * - 健康检查
 * - 调用统计
 */

import React, { useState, useEffect } from 'react';
import PageHeader from '@/app/components/common/PageHeader';
import { unifiedDesignSystem, getThemeStyles } from '@/app/admin/unified-design-system';
import { StatCardGrid, StatCard } from '@/app/components/common/Cards';

interface IntelligencePlatform {
  id: number;
  name: string;
  provider: string;
  platform_type: string;
  base_url: string;
  enabled: boolean;
  config_json: {
    model_name?: string;
    description?: string;
    input_price_per_million?: number;
    output_price_per_million?: number;
  };
  performance: {
    total_calls: number;
    successful_calls: number;
    failed_calls: number;
    success_rate: number;
    avg_response_time: number | null;
    total_cost: number;
  };
  health: {
    last_check: string | null;
    status: string | null;
  };
  created_at: string;
  updated_at: string;
}

export default function IntelligenceModelsPage() {
  const [platforms, setPlatforms] = useState<IntelligencePlatform[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingPlatform, setEditingPlatform] = useState<IntelligencePlatform | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    provider: '',
    base_url: '',
    api_key: '',
    model_name: '',
    description: '',
    input_price_per_million: 0,
    output_price_per_million: 0,
  });
  
  // 使用统一的紫色主题
  const theme = getThemeStyles('purple');

  useEffect(() => {
    fetchPlatforms();
  }, []);

  const fetchPlatforms = async () => {
    try {
      setLoading(true);
      const res = await fetch('http://localhost:8000/api/v1/intelligence/platforms');
      const data = await res.json();
      // API返回格式: {platforms: [...], total: number}
      if (data.platforms) {
        // 只显示情报模型（非DeepSeek）
        const intelligencePlatforms = data.platforms.filter(
          (p: IntelligencePlatform) => p.provider !== 'deepseek'
        );
        setPlatforms(intelligencePlatforms);
      }
    } catch (error) {
      console.error('Failed to fetch platforms:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleEnabled = async (id: number, enabled: boolean) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/intelligence/platforms/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled }),
      });
      if (res.ok) {
        fetchPlatforms();
      }
    } catch (error) {
      console.error('Failed to toggle platform:', error);
    }
  };

  const handleHealthCheck = async (id: number) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/intelligence/platforms/${id}/health`, {
        method: 'POST',
      });
      const data = await res.json();
      if (data.success) {
        alert(`✅ 健康检查成功\n响应时间: ${data.response_time}ms`);
        fetchPlatforms();
      } else {
        alert(`❌ 健康检查失败: ${data.message}`);
      }
    } catch (error) {
      alert(`❌ 健康检查失败: ${error}`);
    }
  };

  const handleAdd = () => {
    setEditingPlatform(null);
    setFormData({
      name: '',
      provider: '',
      base_url: '',
      api_key: '',
      model_name: '',
      description: '',
      input_price_per_million: 0,
      output_price_per_million: 0,
    });
    setShowModal(true);
  };

  const handleEdit = (platform: IntelligencePlatform) => {
    setEditingPlatform(platform);
    setFormData({
      name: platform.name,
      provider: platform.provider,
      base_url: platform.base_url,
      api_key: '',
      model_name: platform.config_json?.model_name || '',
      description: platform.config_json?.description || '',
      input_price_per_million: platform.config_json?.input_price_per_million || 0,
      output_price_per_million: platform.config_json?.output_price_per_million || 0,
    });
    setShowModal(true);
  };

  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`确定要删除 ${name} 吗？`)) return;
    
    try {
      const res = await fetch(`http://localhost:8000/api/v1/intelligence/platforms/${id}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        alert('✅ 删除成功');
        fetchPlatforms();
      } else {
        alert('❌ 删除失败');
      }
    } catch (error) {
      alert(`❌ 删除失败: ${error}`);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const payload = {
      name: formData.name,
      provider: formData.provider,
      platform_type: 'intelligence',
      base_url: formData.base_url,
      api_key: formData.api_key || undefined,
      enabled: true,
      config_json: {
        model_name: formData.model_name,
        description: formData.description,
        input_price_per_million: formData.input_price_per_million,
        output_price_per_million: formData.output_price_per_million,
      },
    };

    try {
      const url = editingPlatform
        ? `http://localhost:8000/api/v1/intelligence/platforms/${editingPlatform.id}`
        : 'http://localhost:8000/api/v1/intelligence/platforms';
      
      const res = await fetch(url, {
        method: editingPlatform ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        alert(editingPlatform ? '✅ 更新成功' : '✅ 添加成功');
        setShowModal(false);
        fetchPlatforms();
      } else {
        const error = await res.json();
        alert(`❌ ${editingPlatform ? '更新' : '添加'}失败: ${error.detail || '未知错误'}`);
      }
    } catch (error) {
      alert(`❌ ${editingPlatform ? '更新' : '添加'}失败: ${error}`);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  return (
    <div className={unifiedDesignSystem.page.container}>
      {/* 页头 */}
      <div className={theme.pageHeader}>
        <div className={unifiedDesignSystem.pageHeader.content}>
          <div className={unifiedDesignSystem.pageHeader.titleSection}>
            <div className={unifiedDesignSystem.pageHeader.icon}>🕵️</div>
            <div className={unifiedDesignSystem.pageHeader.titleWrapper}>
              <h1 className={unifiedDesignSystem.pageHeader.title}>情报模型配置</h1>
              <p className={unifiedDesignSystem.pageHeader.description}>
                管理Qwen系列情报收集模型（通义千问、腾讯混元、火山引擎、百度文心）
              </p>
            </div>
          </div>
          <button
            onClick={handleAdd}
            className={`${theme.button} flex items-center gap-2`}
          >
            <span className="text-xl">+</span>
            添加平台
          </button>
        </div>
      </div>

      {/* 统计卡片 */}
      <StatCardGrid columns={4}>
        <StatCard 
          label="启用平台" 
          value={platforms.filter(p => p.enabled).length}
          color="purple"
        />
        <StatCard 
          label="总调用次数" 
          value={platforms.reduce((sum, p) => sum + p.performance.total_calls, 0).toLocaleString()}
          color="blue"
        />
        <StatCard 
          label="成功率" 
          value={`${platforms.reduce((sum, p) => sum + p.performance.total_calls, 0) > 0
            ? (
                (platforms.reduce((sum, p) => sum + p.performance.successful_calls, 0) /
                  platforms.reduce((sum, p) => sum + p.performance.total_calls, 0)) *
                100
              ).toFixed(1)
            : 0}%`}
          color="green"
        />
        <StatCard 
          label="总成本" 
          value={`¥${platforms.reduce((sum, p) => sum + p.performance.total_cost, 0).toFixed(2)}`}
          color="orange"
        />
      </StatCardGrid>

      {/* 平台列表 */}
      <div className="space-y-4">
        {platforms.map((platform) => (
          <div
            key={platform.id}
            className={`${unifiedDesignSystem.listCard.container} ${theme.listCardBorder}`}
          >
            <div className={unifiedDesignSystem.listCard.header}>
              <div className={unifiedDesignSystem.listCard.titleSection}>
                <div className={unifiedDesignSystem.listCard.icon}>🕵️</div>
                <div className={unifiedDesignSystem.listCard.titleWrapper}>
                  <h3 className={unifiedDesignSystem.listCard.title}>{platform.name}</h3>
                  <p className={unifiedDesignSystem.listCard.subtitle}>
                    {platform.provider} • {platform.platform_type}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`px-3 py-1 text-xs rounded-full font-medium ${
                    platform.enabled
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  {platform.enabled ? '✓ 已启用' : '✗ 已禁用'}
                </span>
              </div>
            </div>

            {/* 统计信息 */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
              <div>
                <div className="text-xs text-gray-500">总调用</div>
                <div className="text-lg font-semibold text-gray-900">
                  {platform.performance.total_calls.toLocaleString()}
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500">成功</div>
                <div className="text-lg font-semibold text-green-600">
                  {platform.performance.successful_calls.toLocaleString()}
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500">失败</div>
                <div className="text-lg font-semibold text-red-600">
                  {platform.performance.failed_calls.toLocaleString()}
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500">成功率</div>
                <div className="text-lg font-semibold text-blue-600">
                  {platform.performance.total_calls > 0
                    ? ((platform.performance.successful_calls / platform.performance.total_calls) * 100).toFixed(1)
                    : 0}
                  %
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500">平均响应</div>
                <div className="text-lg font-semibold text-purple-600">
                  {platform.performance.avg_response_time ? `${platform.performance.avg_response_time.toFixed(0)}ms` : 'N/A'}
                </div>
              </div>
            </div>

            {/* Base URL */}
            <div className="mb-4">
              <div className="text-xs text-gray-500 mb-1">Base URL</div>
              <div className="text-sm text-gray-700 font-mono bg-gray-50 px-3 py-2 rounded">
                {platform.base_url}
              </div>
            </div>

            {/* 最后健康检查 */}
            {platform.health.last_check && (
              <div className="mb-4">
                <div className="text-xs text-gray-500 mb-1">最后健康检查</div>
                <div className="text-sm text-gray-700">
                  {new Date(platform.health.last_check).toLocaleString('zh-CN')}
                </div>
              </div>
            )}

            {/* 操作按钮 */}
            <div className="flex gap-2">
              <button
                onClick={() => handleToggleEnabled(platform.id, !platform.enabled)}
                className={`${unifiedDesignSystem.button.small} ${
                  platform.enabled
                    ? 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    : 'bg-gradient-to-r from-green-500 to-green-600 text-white hover:shadow-lg'
                }`}
              >
                {platform.enabled ? '禁用' : '启用'}
              </button>
              <button
                onClick={() => handleHealthCheck(platform.id)}
                className={`${unifiedDesignSystem.button.small} bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:shadow-lg`}
              >
                健康检查
              </button>
              <button
                onClick={() => handleEdit(platform)}
                className={`${unifiedDesignSystem.button.small} bg-gradient-to-r from-yellow-500 to-yellow-600 text-white hover:shadow-lg`}
              >
                编辑
              </button>
              <button
                onClick={() => handleDelete(platform.id, platform.name)}
                className={`${unifiedDesignSystem.button.small} bg-gradient-to-r from-red-500 to-red-600 text-white hover:shadow-lg`}
              >
                删除
              </button>
            </div>
          </div>
        ))}
      </div>

      {platforms.length === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 text-center">
          <div className="text-4xl mb-2">⚠️</div>
          <h3 className="text-lg font-semibold text-yellow-900 mb-2">暂无情报模型</h3>
          <p className="text-sm text-yellow-700">
            点击右上角"添加平台"按钮开始配置情报平台（Qwen系列）
          </p>
        </div>
      )}

      {/* 添加/编辑模态框 */}
      {showModal && (
        <div className={unifiedDesignSystem.modal.overlay}>
          <div className={unifiedDesignSystem.modal.container}>
            <div className={unifiedDesignSystem.modal.header}>
              <h2 className={unifiedDesignSystem.modal.title}>
                {editingPlatform ? '编辑平台' : '添加平台'}
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className={unifiedDesignSystem.modal.closeButton}
              >
                ×
              </button>
            </div>

            <form onSubmit={handleSubmit} className={unifiedDesignSystem.modal.content}>
              {/* 基本信息 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  平台名称 <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="例如: 腾讯混元 (Qwen搜索)"
                  className={`w-full ${theme.input}`}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  提供商 <span className="text-red-500">*</span>
                </label>
                <select
                  required
                  value={formData.provider}
                  onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
                  className={`w-full ${theme.input}`}
                >
                  <option value="">请选择提供商</option>
                  <option value="tencent">腾讯云 (Tencent)</option>
                  <option value="volcano">火山引擎 (Volcano)</option>
                  <option value="baidu">百度云 (Baidu)</option>
                  <option value="qwen">通义千问 (Qwen)</option>
                  <option value="other">其他</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Base URL <span className="text-red-500">*</span>
                </label>
                <input
                  type="url"
                  required
                  value={formData.base_url}
                  onChange={(e) => setFormData({ ...formData, base_url: e.target.value })}
                  placeholder="https://api.example.com/v1"
                  className={`w-full ${theme.input} font-mono text-sm`}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  API Key {editingPlatform && <span className="text-gray-500 text-xs">(留空则不修改)</span>}
                </label>
                <input
                  type="password"
                  value={formData.api_key}
                  onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                  placeholder="sk-..."
                  className={`w-full ${theme.input} font-mono text-sm`}
                />
              </div>

              {/* 模型配置 */}
              <div className="border-t pt-4">
                <h3 className="text-sm font-semibold text-gray-900 mb-3">模型配置</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      模型名称
                    </label>
                    <input
                      type="text"
                      value={formData.model_name}
                      onChange={(e) => setFormData({ ...formData, model_name: e.target.value })}
                      placeholder="例如: hunyuan-lite"
                      className={`w-full ${theme.input}`}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      描述
                    </label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      placeholder="模型的简要描述..."
                      rows={2}
                      className={`w-full ${theme.input}`}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        输入价格 (元/百万tokens)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={formData.input_price_per_million}
                        onChange={(e) => setFormData({ ...formData, input_price_per_million: parseFloat(e.target.value) || 0 })}
                        className={`w-full ${theme.input}`}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        输出价格 (元/百万tokens)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={formData.output_price_per_million}
                        onChange={(e) => setFormData({ ...formData, output_price_per_million: parseFloat(e.target.value) || 0 })}
                        className={`w-full ${theme.input}`}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* 提交按钮 */}
              <div className={unifiedDesignSystem.modal.footer}>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className={unifiedDesignSystem.button.secondary}
                >
                  取消
                </button>
                <button
                  type="submit"
                  className={theme.button}
                >
                  {editingPlatform ? '保存修改' : '添加平台'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

