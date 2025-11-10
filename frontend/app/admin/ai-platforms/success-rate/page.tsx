'use client';

/**
 * AI平台成功率分析页面
 * 
 * 路径: /admin/ai-platforms/success-rate
 * 
 * 功能：
 * - 各模型成功率对比
 * - 失败原因分析
 * - 重试次数统计
 * - 稳定性评分
 */

import React, { useState, useEffect } from 'react';
import PageHeader from '@/app/components/common/PageHeader';
import { unifiedDesignSystem, getThemeStyles } from '@/app/admin/unified-design-system';
import { StatCardGrid, StatCard } from '@/app/components/common/Cards';

interface PlatformSuccessRate {
  id: number;
  name: string;
  provider: string;
  platform_type: string;
  total_calls: number;
  successful_calls: number;
  failed_calls: number;
  success_rate: number;
  stability_score: number;
}

export default function SuccessRatePage() {
  const [platforms, setPlatforms] = useState<PlatformSuccessRate[]>([]);
  const [loading, setLoading] = useState(true);
  const [failureData, setFailureData] = useState<any>(null);
  const [trendData, setTrendData] = useState<any>(null);
  const [timeRange, setTimeRange] = useState('week');
  
  // 使用统一的靛蓝色主题
  const theme = getThemeStyles('indigo');

  useEffect(() => {
    fetchData();
    fetchFailureData();
    fetchTrendData();
  }, [timeRange]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const res = await fetch('http://localhost:8000/api/v1/intelligence/platforms');
      const data = await res.json();
      if (data.platforms) {
        setPlatforms(data.platforms.map((p: any) => ({
          id: p.id,
          name: p.name,
          provider: p.provider,
          platform_type: p.platform_type,
          total_calls: p.performance?.total_calls || 0,
          successful_calls: p.performance?.successful_calls || 0,
          failed_calls: p.performance?.failed_calls || 0,
          // 将0-1的小数转换为0-100的百分比
          success_rate: (p.performance?.success_rate || 0) * 100,
          stability_score: (p.performance?.success_rate || 0) * 100,
        })).sort((a: any, b: any) => b.success_rate - a.success_rate));
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFailureData = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/ai-platforms/failure-analysis?time_range=${timeRange}`);
      const data = await res.json();
      if (data.success) {
        setFailureData(data.data);
      }
    } catch (error) {
      console.error('Failed to fetch failure data:', error);
    }
  };

  const fetchTrendData = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/ai-platforms/stability-trend?time_range=${timeRange}`);
      const data = await res.json();
      if (data.success) {
        setTrendData(data.data);
      }
    } catch (error) {
      console.error('Failed to fetch trend data:', error);
    }
  };

  const getStabilityLevel = (score: number) => {
    if (score >= 99) return { label: '优秀', color: 'text-green-600', bgColor: 'bg-green-100' };
    if (score >= 95) return { label: '良好', color: 'text-blue-600', bgColor: 'bg-blue-100' };
    if (score >= 90) return { label: '一般', color: 'text-yellow-600', bgColor: 'bg-yellow-100' };
    if (score >= 80) return { label: '较差', color: 'text-orange-600', bgColor: 'bg-orange-100' };
    return { label: '很差', color: 'text-red-600', bgColor: 'bg-red-100' };
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
        icon="✅"
        title="成功率分析"
        description="AI平台调用成功率和稳定性分析"
        color="green"
      />

      {/* 成功率排行榜 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🏆 成功率排行榜</h3>
        
        <div className="space-y-3">
          {platforms.map((platform, index) => {
            const stability = getStabilityLevel(platform.stability_score);
            
            return (
              <div
                key={platform.id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center gap-4">
                  {/* 排名 */}
                  <div className={`text-3xl font-bold ${
                    index === 0 ? 'text-yellow-500' :
                    index === 1 ? 'text-gray-400' :
                    index === 2 ? 'text-orange-400' :
                    'text-gray-300'
                  }`}>
                    #{index + 1}
                  </div>

                  {/* 平台信息 */}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-semibold text-gray-900">{platform.name}</h4>
                      <span className="text-xs text-gray-500">
                        {platform.provider} • {platform.platform_type}
                      </span>
                    </div>
                    
                    {/* 统计数据 */}
                    <div className="grid grid-cols-4 gap-3 text-sm">
                      <div>
                        <span className="text-gray-500">总调用: </span>
                        <span className="font-semibold text-gray-900">
                          {platform.total_calls.toLocaleString()}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">成功: </span>
                        <span className="font-semibold text-green-600">
                          {platform.successful_calls.toLocaleString()}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">失败: </span>
                        <span className="font-semibold text-red-600">
                          {platform.failed_calls.toLocaleString()}
                        </span>
                      </div>
                      <div>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${stability.bgColor} ${stability.color}`}>
                          {stability.label}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* 成功率 */}
                  <div className="text-right">
                    <div className="text-sm text-gray-500 mb-1">成功率</div>
                    <div className={`text-3xl font-bold ${
                      platform.success_rate >= 99 ? 'text-green-600' :
                      platform.success_rate >= 95 ? 'text-blue-600' :
                      platform.success_rate >= 90 ? 'text-yellow-600' :
                      platform.success_rate >= 80 ? 'text-orange-600' :
                      'text-red-600'
                    }`}>
                      {platform.success_rate.toFixed(2)}%
                    </div>
                  </div>
                </div>

                {/* 成功率进度条 */}
                <div className="mt-3">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${
                        platform.success_rate >= 99 ? 'bg-green-500' :
                        platform.success_rate >= 95 ? 'bg-blue-500' :
                        platform.success_rate >= 90 ? 'bg-yellow-500' :
                        platform.success_rate >= 80 ? 'bg-orange-500' :
                        'bg-red-500'
                      }`}
                      style={{ width: `${platform.success_rate}%` }}
                    />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 失败原因分析 */}
      <div className="bg-white rounded-xl shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">🔍 失败原因分析</h3>
          <select 
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
          >
            <option value="today">今日</option>
            <option value="week">本周</option>
            <option value="month">本月</option>
            <option value="all">全部</option>
          </select>
        </div>
        
        {failureData ? (
          <div className="space-y-4">
            {/* 总体统计 */}
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-red-600 font-medium">总失败次数</div>
                  <div className="text-3xl font-bold text-red-700 mt-1">
                    {failureData.total_failures?.toLocaleString() || 0}
                  </div>
                </div>
                <div className="text-4xl">❌</div>
              </div>
            </div>

            {/* 失败原因分类 */}
            {failureData.overall_categories && failureData.overall_categories.length > 0 ? (
              <div className="grid grid-cols-2 gap-4">
                {failureData.overall_categories.map((cat: any, idx: number) => (
                  <div key={idx} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900">{cat.category}</span>
                      <span className="text-sm text-gray-500">{cat.percentage}%</span>
                    </div>
                    <div className="text-2xl font-bold text-red-600 mb-2">
                      {cat.count}
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-red-500 h-2 rounded-full"
                        style={{ width: `${cat.percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>暂无失败记录</p>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <div className="animate-spin text-4xl mb-2">⏳</div>
            <p>加载中...</p>
          </div>
        )}
      </div>

      {/* 稳定性趋势 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📈 稳定性趋势</h3>
        
        {trendData && trendData.platforms && trendData.platforms.length > 0 ? (
          <div className="space-y-6">
            {trendData.platforms.map((platform: any) => (
              <div key={platform.platform_id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h4 className="font-semibold text-gray-900">{platform.platform_name}</h4>
                    <div className="text-sm text-gray-500 mt-1">
                      平均成功率: <span className="font-medium text-blue-600">{platform.avg_success_rate}%</span>
                      {' '} | 稳定性评分: <span className="font-medium text-green-600">{platform.stability_score}</span>
                    </div>
                  </div>
                </div>
                
                {/* 趋势图（简化版 - 使用进度条） */}
                <div className="space-y-2">
                  {platform.data_points && platform.data_points.slice(-7).map((point: any, idx: number) => (
                    <div key={idx} className="flex items-center gap-3">
                      <div className="text-xs text-gray-500 w-32">
                        {new Date(point.timestamp).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit' })}
                      </div>
                      <div className="flex-1">
                        <div className="w-full bg-gray-200 rounded-full h-4 relative">
                          <div 
                            className={`h-4 rounded-full transition-all ${
                              point.success_rate >= 95 ? 'bg-green-500' :
                              point.success_rate >= 90 ? 'bg-blue-500' :
                              point.success_rate >= 80 ? 'bg-yellow-500' :
                              'bg-red-500'
                            }`}
                            style={{ width: `${point.success_rate}%` }}
                          />
                          <span className="absolute inset-0 flex items-center justify-center text-xs font-medium text-gray-700">
                            {point.success_rate.toFixed(1)}%
                          </span>
                        </div>
                      </div>
                      <div className="text-xs text-gray-500 w-16 text-right">
                        {point.total_calls} 次
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <div className="animate-spin text-4xl mb-2">⏳</div>
            <p>加载中...</p>
          </div>
        )}
      </div>
    </div>
  );
}

