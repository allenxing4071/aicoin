'use client';

/**
 * 情报系统监控页面
 * 
 * 路径: /admin/intelligence/monitoring
 * 
 * 功能：
 * - 系统健康状态
 * - 性能指标统计
 * - 四层存储监控
 * - 多平台协调监控
 */

import React, { useState, useEffect } from 'react';
import PageHeader from '@/app/components/common/PageHeader';
import { getThemeStyles } from '@/app/admin/unified-design-system';
import { StatCardGrid, StatCard } from '@/app/components/common/Cards';

interface SystemHealth {
  overall_status: string;
  components: {
    l1_cache: { status: string; latency_ms?: number; has_data?: boolean };
    l2_analyzer: { status: string; source_count?: number };
    l3_store: { status: string };
    l4_vector: { status: string };
    multi_platform: { status: string };
  };
}

interface SystemMetrics {
  collection_metrics: {
    total_collections: number;
    successful_collections: number;
    success_rate: number;
    avg_collection_time_seconds: number;
  };
  cache_metrics: {
    cache_hits: number;
    cache_misses: number;
    cache_hit_rate: number;
  };
  platform_metrics: {
    total_platform_calls: number;
    successful_calls: number;
    platform_success_rate: number;
  };
  storage_metrics: {
    l1_cache_writes: number;
    l2_analyses_completed: number;
    l3_store_writes: number;
    l4_vectorizations: number;
  };
}

export default function IntelligenceMonitoringPage() {
  const theme = getThemeStyles('blue');
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // 每30秒刷新
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // 获取健康状态
      const healthRes = await fetch('/api/v1/intelligence/storage/system/health');
      const healthData = await healthRes.json();
      if (healthData.success) {
        setHealth(healthData.data);
      }
      
      // 获取性能指标
      const metricsRes = await fetch('/api/v1/intelligence/storage/system/metrics');
      const metricsData = await metricsRes.json();
      if (metricsData.success) {
        setMetrics(metricsData.data);
      }

      setLastUpdate(new Date().toLocaleString('zh-CN'));
    } catch (error) {
      console.error('Failed to fetch monitoring data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600';
      case 'degraded': return 'text-yellow-600';
      case 'unhealthy': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusBgColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-50 border-green-200';
      case 'degraded': return 'bg-yellow-50 border-yellow-200';
      case 'unhealthy': return 'bg-red-50 border-red-200';
      default: return 'bg-gray-50 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return '✓';
      case 'degraded': return '⚠';
      case 'unhealthy': return '✗';
      default: return '?';
    }
  };

  if (loading && !health && !metrics) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="情报系统监控"
        description="实时监控情报系统健康状态和性能指标"
        icon="📊"
      />

      {/* 页头控制栏 */}
      <div className="bg-white rounded-xl shadow p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={fetchData}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              🔄 刷新数据
            </button>
            <span className="text-sm text-gray-500">
              自动刷新: 每30秒
            </span>
          </div>
          <div className="text-sm text-gray-500">
            最后更新: {lastUpdate}
          </div>
        </div>
      </div>

      {/* 总体状态 */}
      <div className={`bg-white rounded-xl shadow p-6 border-l-4 ${
        health?.overall_status === 'healthy' ? 'border-green-500' :
        health?.overall_status === 'degraded' ? 'border-yellow-500' :
        'border-red-500'
      }`}>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">系统总体状态</h2>
            <p className="text-sm text-gray-600">
              {health?.overall_status === 'healthy' ? '所有组件运行正常' :
               health?.overall_status === 'degraded' ? '部分组件存在问题' :
               '系统存在严重问题'}
            </p>
          </div>
          <div className={`text-4xl font-bold ${getStatusColor(health?.overall_status || 'unknown')}`}>
            {getStatusIcon(health?.overall_status || 'unknown')} {health?.overall_status?.toUpperCase()}
          </div>
        </div>
      </div>

      {/* 组件健康状态 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">组件健康状态</h3>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {health?.components && Object.entries(health.components).map(([name, component]) => (
            <div key={name} className={`border rounded-lg p-4 ${getStatusBgColor(component.status)}`}>
              <div className="text-sm text-gray-600 mb-2 font-medium">
                {name === 'l1_cache' ? 'L1 缓存' :
                 name === 'l2_analyzer' ? 'L2 分析' :
                 name === 'l3_store' ? 'L3 存储' :
                 name === 'l4_vector' ? 'L4 向量' :
                 name === 'multi_platform' ? '多平台' : name.toUpperCase()}
              </div>
              <div className={`text-2xl font-bold ${getStatusColor(component.status)} mb-2`}>
                {getStatusIcon(component.status)}
              </div>
              <div className="text-xs text-gray-600">
                {component.status}
              </div>
              {component.latency_ms && (
                <div className="text-xs text-gray-500 mt-1">
                  延迟: {component.latency_ms.toFixed(1)}ms
                </div>
              )}
              {component.source_count !== undefined && (
                <div className="text-xs text-gray-500 mt-1">
                  源: {component.source_count}个
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* 性能指标 */}
      {metrics && (
        <>
          {/* 情报收集指标 */}
          <div className="bg-white rounded-xl shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 情报收集指标</h3>
            <StatCardGrid>
              <StatCard
                title="总收集次数"
                value={metrics.collection_metrics.total_collections}
                subtitle="次"
                theme={theme}
              />
              <StatCard
                title="成功收集"
                value={metrics.collection_metrics.successful_collections}
                subtitle="次"
                theme={theme}
              />
              <StatCard
                title="成功率"
                value={`${(metrics.collection_metrics.success_rate * 100).toFixed(1)}%`}
                subtitle={`${metrics.collection_metrics.successful_collections}/${metrics.collection_metrics.total_collections}`}
                theme={theme}
              />
              <StatCard
                title="平均耗时"
                value={`${metrics.collection_metrics.avg_collection_time_seconds.toFixed(1)}s`}
                subtitle="每次收集"
                theme={theme}
              />
            </StatCardGrid>
          </div>

          {/* 缓存性能 */}
          <div className="bg-white rounded-xl shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">⚡ 缓存性能</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="border rounded-lg p-4">
                <div className="text-sm text-gray-600 mb-2">缓存命中率</div>
                <div className="text-3xl font-bold text-green-600 mb-2">
                  {(metrics.cache_metrics.cache_hit_rate * 100).toFixed(1)}%
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-green-500"
                    style={{ width: `${metrics.cache_metrics.cache_hit_rate * 100}%` }}
                  />
                </div>
              </div>
              <div className="border rounded-lg p-4">
                <div className="text-sm text-gray-600 mb-2">缓存命中</div>
                <div className="text-3xl font-bold text-blue-600">
                  {metrics.cache_metrics.cache_hits}
                </div>
                <div className="text-xs text-gray-500">次</div>
              </div>
              <div className="border rounded-lg p-4">
                <div className="text-sm text-gray-600 mb-2">缓存未命中</div>
                <div className="text-3xl font-bold text-orange-600">
                  {metrics.cache_metrics.cache_misses}
                </div>
                <div className="text-xs text-gray-500">次</div>
              </div>
            </div>
          </div>

          {/* 平台调用统计 */}
          <div className="bg-white rounded-xl shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">🔄 平台调用统计</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="border rounded-lg p-4">
                <div className="text-sm text-gray-600 mb-2">总调用次数</div>
                <div className="text-3xl font-bold text-blue-600">
                  {metrics.platform_metrics.total_platform_calls}
                </div>
                <div className="text-xs text-gray-500">次</div>
              </div>
              <div className="border rounded-lg p-4">
                <div className="text-sm text-gray-600 mb-2">成功调用</div>
                <div className="text-3xl font-bold text-green-600">
                  {metrics.platform_metrics.successful_calls}
                </div>
                <div className="text-xs text-gray-500">次</div>
              </div>
              <div className="border rounded-lg p-4">
                <div className="text-sm text-gray-600 mb-2">成功率</div>
                <div className="text-3xl font-bold text-green-600 mb-2">
                  {(metrics.platform_metrics.platform_success_rate * 100).toFixed(1)}%
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-green-500"
                    style={{ width: `${metrics.platform_metrics.platform_success_rate * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* 存储层统计 */}
          <div className="bg-white rounded-xl shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">💾 存储层统计</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="border border-pink-200 rounded-lg p-4 bg-pink-50">
                <div className="text-sm text-gray-600 mb-2">L1 缓存写入</div>
                <div className="text-3xl font-bold text-pink-600">
                  {metrics.storage_metrics.l1_cache_writes}
                </div>
                <div className="text-xs text-gray-500">次</div>
              </div>
              <div className="border border-blue-200 rounded-lg p-4 bg-blue-50">
                <div className="text-sm text-gray-600 mb-2">L2 分析完成</div>
                <div className="text-3xl font-bold text-blue-600">
                  {metrics.storage_metrics.l2_analyses_completed}
                </div>
                <div className="text-xs text-gray-500">次</div>
              </div>
              <div className="border border-green-200 rounded-lg p-4 bg-green-50">
                <div className="text-sm text-gray-600 mb-2">L3 存储写入</div>
                <div className="text-3xl font-bold text-green-600">
                  {metrics.storage_metrics.l3_store_writes}
                </div>
                <div className="text-xs text-gray-500">次</div>
              </div>
              <div className="border border-purple-200 rounded-lg p-4 bg-purple-50">
                <div className="text-sm text-gray-600 mb-2">L4 向量化</div>
                <div className="text-3xl font-bold text-purple-600">
                  {metrics.storage_metrics.l4_vectorizations}
                </div>
                <div className="text-xs text-gray-500">次</div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* 说明信息 */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">
          💡 关于情报系统监控
        </h3>
        <div className="space-y-2 text-sm text-blue-800">
          <p>
            <strong>系统健康状态</strong>: 实时监控L1-L4各层存储和多平台协调器的运行状态。
          </p>
          <p>
            <strong>性能指标</strong>: 统计情报收集、缓存命中、平台调用和存储操作的性能数据。
          </p>
          <p>
            <strong>自动刷新</strong>: 页面每30秒自动刷新一次，确保数据实时性。
          </p>
          <p className="mt-3 pt-3 border-t border-blue-300">
            <strong>健康状态说明</strong>: 
            <span className="text-green-600 font-medium"> ✓ Healthy</span> = 正常运行 | 
            <span className="text-yellow-600 font-medium"> ⚠ Degraded</span> = 部分异常 | 
            <span className="text-red-600 font-medium"> ✗ Unhealthy</span> = 严重问题
          </p>
        </div>
      </div>
    </div>
  );
}

