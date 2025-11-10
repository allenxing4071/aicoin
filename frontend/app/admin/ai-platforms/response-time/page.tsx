'use client';

/**
 * AI平台响应时间分析页面
 * 
 * 路径: /admin/ai-platforms/response-time
 * 
 * 功能：
 * - 平均响应时间
 * - P50/P95/P99延迟
 * - 响应时间趋势
 * - 慢查询分析
 */

import React, { useState, useEffect } from 'react';
import PageHeader from '@/app/components/common/PageHeader';
import { unifiedDesignSystem, getThemeStyles } from '@/app/admin/unified-design-system';
import { StatCardGrid, StatCard } from '@/app/components/common/Cards';

interface PlatformResponseTime {
  id: number;
  name: string;
  provider: string;
  platform_type: string;
  avg_response_time: number | null;
  total_calls: number;
  performance_level: string;
}

export default function ResponseTimePage() {
  const [platforms, setPlatforms] = useState<PlatformResponseTime[]>([]);
  const [loading, setLoading] = useState(true);
  const [percentileData, setPercentileData] = useState<any>(null);
  const [trendData, setTrendData] = useState<any>(null);
  const [timeRange, setTimeRange] = useState('week');
  
  // 使用统一的靛蓝色主题
  const theme = getThemeStyles('indigo');

  useEffect(() => {
    fetchData();
    fetchPercentileData();
    fetchTrendData();
  }, [timeRange]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const res = await fetch('http://localhost:8000/api/v1/intelligence/platforms');
      const data = await res.json();
      if (data.platforms) {
        setPlatforms(data.platforms.map((p: any) => {
          const avgTime = p.performance?.avg_response_time || 0;
          let performanceLevel = '未知';
          if (avgTime > 0) {
            if (avgTime < 500) performanceLevel = '优秀';
            else if (avgTime < 1000) performanceLevel = '良好';
            else if (avgTime < 2000) performanceLevel = '一般';
            else if (avgTime < 5000) performanceLevel = '较慢';
            else performanceLevel = '很慢';
          }
          
          return {
            id: p.id,
            name: p.name,
            provider: p.provider,
            platform_type: p.platform_type,
            avg_response_time: p.performance?.avg_response_time,
            total_calls: p.performance?.total_calls || 0,
            performance_level: performanceLevel,
          };
        }).sort((a: any, b: any) => {
          if (a.avg_response_time === null) return 1;
          if (b.avg_response_time === null) return -1;
          return a.avg_response_time - b.avg_response_time;
        }));
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPercentileData = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/ai-platforms/response-time-percentiles?time_range=${timeRange}`);
      const data = await res.json();
      if (data.success) {
        setPercentileData(data.data);
      }
    } catch (error) {
      console.error('Failed to fetch percentile data:', error);
    }
  };

  const fetchTrendData = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/ai-platforms/response-time-trend?time_range=${timeRange}`);
      const data = await res.json();
      if (data.success) {
        setTrendData(data.data);
      }
    } catch (error) {
      console.error('Failed to fetch trend data:', error);
    }
  };

  const getPerformanceColor = (level: string) => {
    switch (level) {
      case '优秀': return { text: 'text-green-600', bg: 'bg-green-100', border: 'border-green-500' };
      case '良好': return { text: 'text-blue-600', bg: 'bg-blue-100', border: 'border-blue-500' };
      case '一般': return { text: 'text-yellow-600', bg: 'bg-yellow-100', border: 'border-yellow-500' };
      case '较慢': return { text: 'text-orange-600', bg: 'bg-orange-100', border: 'border-orange-500' };
      case '很慢': return { text: 'text-red-600', bg: 'bg-red-100', border: 'border-red-500' };
      default: return { text: 'text-gray-600', bg: 'bg-gray-100', border: 'border-gray-500' };
    }
  };

  const avgResponseTime = platforms.filter(p => p.avg_response_time !== null)
    .reduce((sum, p) => sum + (p.avg_response_time || 0), 0) / 
    platforms.filter(p => p.avg_response_time !== null).length || 0;

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
        icon="⚡"
        title="响应时间分析"
        description="AI平台响应时间和性能分析"
        color="purple"
      />

      {/* 总体统计 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 shadow-lg border-2 border-purple-300">
          <div className="text-sm text-gray-500 mb-1">平均响应时间</div>
          <div className="text-3xl font-bold text-purple-600">
            {avgResponseTime > 0 ? `${avgResponseTime.toFixed(0)}ms` : 'N/A'}
          </div>
        </div>
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 shadow-lg border-2 border-green-300">
          <div className="text-sm text-gray-500 mb-1">最快平台</div>
          <div className="text-lg font-bold text-green-600">
            {platforms[0]?.avg_response_time !== null 
              ? `${platforms[0]?.name} (${platforms[0]?.avg_response_time?.toFixed(0)}ms)`
              : 'N/A'}
          </div>
        </div>
        <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-xl p-6 shadow-lg border-2 border-red-300">
          <div className="text-sm text-gray-500 mb-1">最慢平台</div>
          <div className="text-lg font-bold text-red-600">
            {platforms.filter(p => p.avg_response_time !== null).slice(-1)[0]?.avg_response_time !== null
              ? `${platforms.filter(p => p.avg_response_time !== null).slice(-1)[0]?.name} (${platforms.filter(p => p.avg_response_time !== null).slice(-1)[0]?.avg_response_time?.toFixed(0)}ms)`
              : 'N/A'}
          </div>
        </div>
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 shadow-lg border-2 border-blue-300">
          <div className="text-sm text-gray-500 mb-1">监控平台数</div>
          <div className="text-3xl font-bold text-blue-600">
            {platforms.filter(p => p.avg_response_time !== null).length}
          </div>
        </div>
      </div>

      {/* 响应时间排行 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">⚡ 响应时间排行</h3>
        
        <div className="space-y-3">
          {platforms.map((platform, index) => {
            const colors = getPerformanceColor(platform.performance_level);
            
            return (
              <div
                key={platform.id}
                className={`border-2 rounded-lg p-4 ${colors.border}`}
              >
                <div className="flex items-center gap-4">
                  {/* 排名 */}
                  <div className={`text-2xl font-bold ${
                    index === 0 ? 'text-green-500' :
                    index === 1 ? 'text-blue-500' :
                    index === 2 ? 'text-yellow-500' :
                    'text-gray-400'
                  }`}>
                    #{index + 1}
                  </div>

                  {/* 平台信息 */}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="font-semibold text-gray-900">{platform.name}</h4>
                      <span className="text-xs text-gray-500">
                        {platform.provider} • {platform.platform_type}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors.bg} ${colors.text}`}>
                        {platform.performance_level}
                      </span>
                    </div>
                    
                    <div className="text-sm text-gray-600">
                      总调用次数: {platform.total_calls.toLocaleString()}
                    </div>
                  </div>

                  {/* 响应时间 */}
                  <div className="text-right">
                    <div className="text-sm text-gray-500 mb-1">平均响应时间</div>
                    <div className={`text-3xl font-bold ${colors.text}`}>
                      {platform.avg_response_time !== null 
                        ? `${platform.avg_response_time.toFixed(0)}ms`
                        : 'N/A'}
                    </div>
                  </div>
                </div>

                {/* 响应时间可视化 */}
                {platform.avg_response_time !== null && (
                  <div className="mt-3">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all ${
                          platform.avg_response_time < 500 ? 'bg-green-500' :
                          platform.avg_response_time < 1000 ? 'bg-blue-500' :
                          platform.avg_response_time < 2000 ? 'bg-yellow-500' :
                          platform.avg_response_time < 5000 ? 'bg-orange-500' :
                          'bg-red-500'
                        }`}
                        style={{
                          width: `${Math.min((platform.avg_response_time / 5000) * 100, 100)}%`,
                        }}
                      />
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* 性能标准说明 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📋 性能标准</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
            <div className="font-semibold text-green-900 mb-1">优秀</div>
            <div className="text-sm text-green-700">&lt; 500ms</div>
          </div>
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="font-semibold text-blue-900 mb-1">良好</div>
            <div className="text-sm text-blue-700">500-1000ms</div>
          </div>
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="font-semibold text-yellow-900 mb-1">一般</div>
            <div className="text-sm text-yellow-700">1-2秒</div>
          </div>
          <div className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
            <div className="font-semibold text-orange-900 mb-1">较慢</div>
            <div className="text-sm text-orange-700">2-5秒</div>
          </div>
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
            <div className="font-semibold text-red-900 mb-1">很慢</div>
            <div className="text-sm text-red-700">&gt; 5秒</div>
          </div>
        </div>
      </div>

      {/* P50/P95/P99延迟分析 */}
      <div className="bg-white rounded-xl shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">📊 延迟分位数分析</h3>
          <select 
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
          >
            <option value="today">今日</option>
            <option value="week">本周</option>
            <option value="month">本月</option>
          </select>
        </div>
        
        {percentileData && percentileData.platforms && percentileData.platforms.length > 0 ? (
          <div className="space-y-4">
            {percentileData.platforms.map((platform: any) => (
              <div key={platform.platform_id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h4 className="font-semibold text-gray-900">{platform.platform_name}</h4>
                    <div className="text-sm text-gray-500 mt-1">
                      样本数: {platform.sample_count} 次调用
                    </div>
                  </div>
                </div>
                
                {/* 分位数统计 */}
                <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <div className="text-xs text-gray-500 mb-1">最小值</div>
                    <div className="text-lg font-bold text-gray-700">
                      {platform.min.toFixed(0)}ms
                    </div>
                  </div>
                  <div className="bg-green-50 p-3 rounded-lg">
                    <div className="text-xs text-green-600 font-medium mb-1">P50 (中位数)</div>
                    <div className="text-lg font-bold text-green-700">
                      {platform.p50.toFixed(0)}ms
                    </div>
                  </div>
                  <div className="bg-blue-50 p-3 rounded-lg">
                    <div className="text-xs text-blue-600 font-medium mb-1">平均值</div>
                    <div className="text-lg font-bold text-blue-700">
                      {platform.avg.toFixed(0)}ms
                    </div>
                  </div>
                  <div className="bg-yellow-50 p-3 rounded-lg">
                    <div className="text-xs text-yellow-600 font-medium mb-1">P95</div>
                    <div className="text-lg font-bold text-yellow-700">
                      {platform.p95.toFixed(0)}ms
                    </div>
                  </div>
                  <div className="bg-orange-50 p-3 rounded-lg">
                    <div className="text-xs text-orange-600 font-medium mb-1">P99</div>
                    <div className="text-lg font-bold text-orange-700">
                      {platform.p99.toFixed(0)}ms
                    </div>
                  </div>
                  <div className="bg-red-50 p-3 rounded-lg">
                    <div className="text-xs text-red-600 font-medium mb-1">最大值</div>
                    <div className="text-lg font-bold text-red-700">
                      {platform.max.toFixed(0)}ms
                    </div>
                  </div>
                </div>
                
                {/* 可视化进度条 */}
                <div className="mt-4 space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500 w-16">P50:</span>
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-green-500 h-2 rounded-full"
                        style={{ width: `${Math.min((platform.p50 / platform.max) * 100, 100)}%` }}
                      />
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500 w-16">P95:</span>
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-yellow-500 h-2 rounded-full"
                        style={{ width: `${Math.min((platform.p95 / platform.max) * 100, 100)}%` }}
                      />
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500 w-16">P99:</span>
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-orange-500 h-2 rounded-full"
                        style={{ width: `${Math.min((platform.p99 / platform.max) * 100, 100)}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {percentileData.note && (
              <div className="text-xs text-gray-500 text-center mt-4">
                💡 {percentileData.note}
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
      
      {/* 响应时间趋势 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📈 响应时间趋势</h3>
        
        {trendData && trendData.platforms && trendData.platforms.length > 0 ? (
          <div className="space-y-6">
            {trendData.platforms.map((platform: any) => (
              <div key={platform.platform_id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h4 className="font-semibold text-gray-900">{platform.platform_name}</h4>
                    <div className="text-sm text-gray-500 mt-1">
                      平均响应时间: <span className="font-medium text-purple-600">{platform.overall_avg.toFixed(0)}ms</span>
                    </div>
                  </div>
                </div>
                
                {/* 趋势图 */}
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
                              point.avg_response_time < 300 ? 'bg-green-500' :
                              point.avg_response_time < 400 ? 'bg-blue-500' :
                              point.avg_response_time < 500 ? 'bg-yellow-500' :
                              'bg-red-500'
                            }`}
                            style={{ width: `${Math.min((point.avg_response_time / 1000) * 100, 100)}%` }}
                          />
                          <span className="absolute inset-0 flex items-center justify-center text-xs font-medium text-gray-700">
                            {point.avg_response_time.toFixed(0)}ms
                          </span>
                        </div>
                      </div>
                      <div className="text-xs text-gray-500 w-16 text-right">
                        {point.call_count} 次
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
            
            {trendData.note && (
              <div className="text-xs text-gray-500 text-center mt-4">
                💡 {trendData.note}
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
    </div>
  );
}

