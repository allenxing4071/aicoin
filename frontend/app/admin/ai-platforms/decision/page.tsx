'use client';

/**
 * 决策模型配置页面
 * 
 * 路径: /admin/ai-platforms/decision
 * 
 * 功能：
 * - 显示DeepSeek决策模型配置
 * - API密钥管理
 * - 模型参数设置
 * - 决策历史记录
 */

import React, { useState, useEffect } from 'react';
import PageHeader from '@/app/components/common/PageHeader';
import { unifiedDesignSystem, getThemeStyles } from '@/app/admin/unified-design-system';
import { StatCardGrid, StatCard } from '@/app/components/common/Cards';

interface DecisionPlatform {
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

export default function DecisionModelsPage() {
  const [platforms, setPlatforms] = useState<DecisionPlatform[]>([]);
  const [loading, setLoading] = useState(true);
  
  // 使用统一的蓝色主题
  const theme = getThemeStyles('blue');

  useEffect(() => {
    fetchPlatforms();
  }, []);

  const fetchPlatforms = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/v1/intelligence/platforms');
      const data = await res.json();
      // API返回格式: {platforms: [...], total: number}
      if (data.platforms) {
        // 只显示决策模型（DeepSeek）
        const decisionPlatforms = data.platforms.filter(
          (p: DecisionPlatform) => p.provider === 'deepseek'
        );
        setPlatforms(decisionPlatforms);
      }
    } catch (error) {
      console.error('Failed to fetch platforms:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleEnabled = async (id: number, enabled: boolean) => {
    try {
      const res = await fetch(`/api/v1/intelligence/platforms/${id}`, {
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
      const res = await fetch(`/api/v1/intelligence/platforms/${id}/health`, {
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
            <div className={unifiedDesignSystem.pageHeader.icon}>🎯</div>
            <div className={unifiedDesignSystem.pageHeader.titleWrapper}>
              <h1 className={unifiedDesignSystem.pageHeader.title}>决策模型配置</h1>
              <p className={unifiedDesignSystem.pageHeader.description}>
                管理DeepSeek交易决策模型配置和性能监控
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 统计卡片 */}
      <StatCardGrid columns={4}>
        <StatCard 
          label="启用平台" 
          value={platforms.filter(p => p.enabled).length}
          color="blue"
        />
        <StatCard 
          label="总决策次数" 
          value={platforms.reduce((sum, p) => sum + p.performance.total_calls, 0).toLocaleString()}
          color="green"
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
          color="purple"
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
                <div className={unifiedDesignSystem.listCard.icon}>🎯</div>
                <div className={unifiedDesignSystem.listCard.titleWrapper}>
                  <h3 className={unifiedDesignSystem.listCard.title}>{platform.name}</h3>
                  <p className={unifiedDesignSystem.listCard.subtitle}>
                    {platform.provider} • {platform.platform_type}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={platform.enabled ? unifiedDesignSystem.badge.success : unifiedDesignSystem.badge.default}
                >
                  {platform.enabled ? '✓ 已启用' : '✗ 已禁用'}
                </span>
              </div>
            </div>

            {/* 统计信息 */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
              <div>
                <div className="text-xs text-gray-500">总决策</div>
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
            </div>
          </div>
        ))}
      </div>

      {platforms.length === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 text-center">
          <div className="text-4xl mb-2">⚠️</div>
          <h3 className="text-lg font-semibold text-yellow-900 mb-2">暂无决策模型</h3>
          <p className="text-sm text-yellow-700">
            请先在数据库中配置DeepSeek决策平台
          </p>
        </div>
      )}
    </div>
  );
}

