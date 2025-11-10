'use client';

/**
 * AI平台调用统计页面
 * 
 * 路径: /admin/ai-platforms/stats
 * 
 * 功能：
 * - 按时间维度统计调用量
 * - 按模型分组统计
 * - 调用趋势图表
 * - 峰值时段分析
 */

import React, { useState, useEffect } from 'react';
import PageHeader from '@/app/components/common/PageHeader';
import { unifiedDesignSystem, getThemeStyles } from '@/app/admin/unified-design-system';
import { StatCardGrid, StatCard } from '@/app/components/common/Cards';

interface PlatformStats {
  id: number;
  name: string;
  provider: string;
  total_calls: number;
  successful_calls: number;
  failed_calls: number;
  success_rate: number;
  avg_response_time: number | null;
  total_cost?: number;
}

interface HourlyStats {
  hour: string;
  calls: number;
  successful: number;
  failed: number;
  cost: number;
}

export default function StatsPage() {
  const [platforms, setPlatforms] = useState<PlatformStats[]>([]);
  const [hourlyStats, setHourlyStats] = useState<HourlyStats[]>([]);
  const [peakHour, setPeakHour] = useState<HourlyStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState<'today' | 'week' | 'month'>('today');
  
  // 使用统一的靛蓝色主题
  const theme = getThemeStyles('indigo');

  useEffect(() => {
    fetchData();
    fetchHourlyData();
  }, [timeRange]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const res = await fetch(`http://localhost:8000/api/v1/ai-platforms/stats?time_range=${timeRange}`);
      const data = await res.json();
      if (data.success && data.data) {
        setPlatforms(data.data.platforms);
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchHourlyData = async () => {
    try {
      // 只在今日和本周模式下获取小时统计
      if (timeRange === 'month') {
        setHourlyStats([]);
        setPeakHour(null);
        return;
      }
      
      const res = await fetch(`http://localhost:8000/api/v1/ai-platforms/hourly-stats?time_range=${timeRange}`);
      const data = await res.json();
      if (data.success && data.data) {
        setHourlyStats(data.data.hourly_stats || []);
        setPeakHour(data.data.peak_hour || null);
      }
    } catch (error) {
      console.error('Failed to fetch hourly data:', error);
    }
  };

  const totalCalls = platforms.reduce((sum, p) => sum + p.total_calls, 0);
  const totalSuccessful = platforms.reduce((sum, p) => sum + p.successful_calls, 0);
  const totalFailed = platforms.reduce((sum, p) => sum + p.failed_calls, 0);
  const overallSuccessRate = totalCalls > 0 ? (totalSuccessful / totalCalls) * 100 : 0;

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
            <div className={unifiedDesignSystem.pageHeader.icon}>📊</div>
            <div className={unifiedDesignSystem.pageHeader.titleWrapper}>
              <h1 className={unifiedDesignSystem.pageHeader.title}>调用统计</h1>
              <p className={unifiedDesignSystem.pageHeader.description}>
                AI平台调用量统计和趋势分析
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 时间范围选择 */}
      <div className="flex gap-2">
        <button
          onClick={() => setTimeRange('today')}
          className={`${unifiedDesignSystem.button.small} ${
            timeRange === 'today'
              ? 'bg-gradient-to-r from-indigo-500 to-indigo-600 text-white shadow-lg'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          今日
        </button>
        <button
          onClick={() => setTimeRange('week')}
          className={`${unifiedDesignSystem.button.small} ${
            timeRange === 'week'
              ? 'bg-gradient-to-r from-indigo-500 to-indigo-600 text-white shadow-lg'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          本周
        </button>
        <button
          onClick={() => setTimeRange('month')}
          className={`${unifiedDesignSystem.button.small} ${
            timeRange === 'month'
              ? 'bg-gradient-to-r from-indigo-500 to-indigo-600 text-white shadow-lg'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          本月
        </button>
      </div>

      {/* 总体统计 */}
      <div className={unifiedDesignSystem.grid.cols4}>
        <div className={`${unifiedDesignSystem.statCard.container} ${theme.statCardBackground}`}>
          <div className={unifiedDesignSystem.statCard.label}>总调用次数</div>
          <div className={`${unifiedDesignSystem.statCard.value} ${theme.statCardValue}`}>
            {totalCalls.toLocaleString()}
          </div>
        </div>
        <div className={`${unifiedDesignSystem.statCard.container} ${unifiedDesignSystem.statCard.backgrounds.green}`}>
          <div className={unifiedDesignSystem.statCard.label}>成功调用</div>
          <div className={`${unifiedDesignSystem.statCard.value} ${unifiedDesignSystem.statCard.valueColors.green}`}>
            {totalSuccessful.toLocaleString()}
          </div>
        </div>
        <div className={`${unifiedDesignSystem.statCard.container} ${unifiedDesignSystem.statCard.backgrounds.red}`}>
          <div className={unifiedDesignSystem.statCard.label}>失败调用</div>
          <div className={`${unifiedDesignSystem.statCard.value} ${unifiedDesignSystem.statCard.valueColors.red}`}>
            {totalFailed.toLocaleString()}
          </div>
        </div>
        <div className={`${unifiedDesignSystem.statCard.container} ${unifiedDesignSystem.statCard.backgrounds.purple}`}>
          <div className={unifiedDesignSystem.statCard.label}>整体成功率</div>
          <div className={`${unifiedDesignSystem.statCard.value} ${unifiedDesignSystem.statCard.valueColors.purple}`}>
            {overallSuccessRate.toFixed(1)}%
          </div>
        </div>
      </div>

      {/* 各平台调用统计 */}
      <div className={`${unifiedDesignSystem.listCard.container} ${theme.listCardBorder}`}>
        <h3 className={`${unifiedDesignSystem.listCard.title} mb-4`}>📈 各平台调用统计</h3>
        
        <div className="space-y-4">
          {platforms.map((platform) => (
            <div key={platform.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h4 className="font-semibold text-gray-900">{platform.name}</h4>
                  <p className="text-sm text-gray-500">{platform.provider}</p>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-500">成功率</div>
                  <div className={`text-2xl font-bold ${
                    platform.success_rate >= 95 ? 'text-green-600' :
                    platform.success_rate >= 80 ? 'text-yellow-600' :
                    'text-red-600'
                  }`}>
                    {platform.success_rate.toFixed(1)}%
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <div className="text-xs text-gray-500">总调用</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {platform.total_calls.toLocaleString()}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">成功</div>
                  <div className="text-lg font-semibold text-green-600">
                    {platform.successful_calls.toLocaleString()}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">失败</div>
                  <div className="text-lg font-semibold text-red-600">
                    {platform.failed_calls.toLocaleString()}
                  </div>
                </div>
              </div>

              {/* 调用量占比 */}
              <div className="mt-3">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-xs text-gray-500">调用量占比</span>
                  <span className="text-xs font-medium text-gray-700">
                    {totalCalls > 0 ? ((platform.total_calls / totalCalls) * 100).toFixed(1) : 0}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="h-2 bg-blue-500 rounded-full transition-all"
                    style={{
                      width: `${totalCalls > 0 ? (platform.total_calls / totalCalls) * 100 : 0}%`,
                    }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 峰值时段分析 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">⏰ 峰值时段分析</h3>
        
        {timeRange === 'month' ? (
          <div className="text-center py-12 text-gray-500">
            <div className="text-4xl mb-2">📊</div>
            <p>月度数据量较大，暂不显示小时统计</p>
            <p className="text-sm mt-2">请切换到"今日"或"本周"查看峰值时段</p>
          </div>
        ) : hourlyStats.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <div className="text-4xl mb-2">📊</div>
            <p>暂无小时统计数据</p>
            <p className="text-sm mt-2">请等待系统收集调用数据</p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* 峰值时段高亮 */}
            {peakHour && (
              <div className="bg-gradient-to-r from-orange-50 to-red-50 border-2 border-orange-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm text-orange-600 font-medium">🔥 峰值时段</div>
                    <div className="text-2xl font-bold text-orange-900 mt-1">
                      {new Date(peakHour.hour).toLocaleString('zh-CN', { 
                        month: 'short', 
                        day: 'numeric', 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-orange-600">调用次数</div>
                    <div className="text-3xl font-bold text-orange-900">{peakHour.calls}</div>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-3 mt-3">
                  <div>
                    <div className="text-xs text-orange-600">成功</div>
                    <div className="text-lg font-semibold text-green-600">{peakHour.successful}</div>
                  </div>
                  <div>
                    <div className="text-xs text-orange-600">失败</div>
                    <div className="text-lg font-semibold text-red-600">{peakHour.failed}</div>
                  </div>
                  <div>
                    <div className="text-xs text-orange-600">成本</div>
                    <div className="text-lg font-semibold text-gray-900">¥{peakHour.cost}</div>
                  </div>
                </div>
              </div>
            )}

            {/* 小时统计列表 */}
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {hourlyStats.map((stat, index) => {
                const maxCalls = Math.max(...hourlyStats.map(s => s.calls));
                const percentage = maxCalls > 0 ? (stat.calls / maxCalls) * 100 : 0;
                const isPeak = peakHour && stat.hour === peakHour.hour;
                
                return (
                  <div
                    key={index}
                    className={`border rounded-lg p-3 transition-all ${
                      isPeak ? 'border-orange-300 bg-orange-50' : 'border-gray-200 bg-white'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {isPeak && <span className="text-orange-500">🔥</span>}
                        <span className="font-medium text-gray-900">
                          {new Date(stat.hour).toLocaleString('zh-CN', { 
                            month: 'short', 
                            day: 'numeric', 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })}
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-sm">
                        <span className="text-gray-600">
                          调用: <span className="font-semibold text-blue-600">{stat.calls}</span>
                        </span>
                        <span className="text-gray-600">
                          成功: <span className="font-semibold text-green-600">{stat.successful}</span>
                        </span>
                        <span className="text-gray-600">
                          失败: <span className="font-semibold text-red-600">{stat.failed}</span>
                        </span>
                        <span className="text-gray-600">
                          成本: <span className="font-semibold text-gray-900">¥{stat.cost}</span>
                        </span>
                      </div>
                    </div>
                    {/* 调用量可视化 */}
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all ${
                          isPeak ? 'bg-orange-500' : 'bg-blue-500'
                        }`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

