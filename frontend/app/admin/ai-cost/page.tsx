'use client';

/**
 * AI成本管理 - 总览仪表盘
 * 
 * 路径: /admin/ai-cost
 * 
 * 功能：
 * - 显示关键成本指标
 * - 显示成本分布和趋势
 * - 提供快捷操作入口
 * - 显示预算告警
 */

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import PageHeader from '@/app/components/common/PageHeader';
import { unifiedDesignSystem, getThemeStyles } from '@/app/admin/unified-design-system';
import { StatCardGrid, StatCard } from '@/app/components/common/Cards';
import CostTrendChart from '@/app/components/charts/CostTrendChart';

interface PlatformCost {
  id: number;
  name: string;
  provider: string;
  total_cost: number;
  current_month_cost: number;
  monthly_budget: number;
  usage_percentage: number;
}

interface CostSummary {
  total_cost: number;
  month_cost: number;
  today_cost: number;
  avg_daily_cost: number;
  total_budget: number;
  budget_usage: number;
}

export default function AICostOverviewPage() {
  const [platforms, setPlatforms] = useState<PlatformCost[]>([]);
  const [summary, setSummary] = useState<CostSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [alerts, setAlerts] = useState<string[]>([]);
  
  // 使用统一的橙色主题
  const theme = getThemeStyles('orange');

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // 每30秒刷新
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // 使用stats API获取全部数据 (含真实调用记录)
      const res = await fetch('/api/v1/ai-platforms/stats?time_range=all');
      const data = await res.json();
      
      if (data.success && data.data) {
        // 转换数据格式
        const platformCosts = data.data.platforms.map((p: any) => ({
          id: p.id,
          name: p.name,
          provider: p.provider,
          total_cost: p.total_cost,
          current_month_cost: p.total_cost, // 暂用总成本代替月度成本
          monthly_budget: 0, // TODO: 需要从platform配置获取
          usage_percentage: 0,
          today_cost: 0 // TODO: 需要单独查询今日成本
        }));
        
        setPlatforms(platformCosts);
        
        // 设置汇总数据
        setSummary({
          total_cost: data.data.summary.total_cost,
          month_cost: data.data.summary.total_cost, 
          today_cost: 0, // TODO: 需要单独查询
          avg_daily_cost: data.data.summary.total_cost / new Date().getDate(),
          total_budget: 0,
          budget_usage: 0
        });
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
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
    <div className="space-y-6">
      <PageHeader
        icon="💰"
        title="AI成本管理 - 总览"
        description="实时监控所有AI平台的成本和使用情况"
        color="green"
      />

      {/* 关键指标卡片 */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-6 shadow-lg border-2 border-gray-300">
            <div className="text-sm text-gray-500 mb-1">总成本</div>
            <div className="text-3xl font-bold text-gray-900">
              ¥{summary.total_cost.toFixed(2)}
            </div>
            <div className="text-xs text-gray-500 mt-1">累计花费</div>
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 shadow-lg border-2 border-blue-300">
            <div className="text-sm text-gray-500 mb-1">本月成本</div>
            <div className="text-3xl font-bold text-blue-600">
              ¥{summary.month_cost.toFixed(2)}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              预算使用率: {summary.budget_usage.toFixed(1)}%
            </div>
          </div>

          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 shadow-lg border-2 border-green-300">
            <div className="text-sm text-gray-500 mb-1">今日成本</div>
            <div className="text-3xl font-bold text-green-600">
              ¥{summary.today_cost.toFixed(2)}
            </div>
            <div className="text-xs text-gray-500 mt-1">今日累计</div>
          </div>

          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 shadow-lg border-2 border-purple-300">
            <div className="text-sm text-gray-500 mb-1">平均每日</div>
            <div className="text-3xl font-bold text-purple-600">
              ¥{summary.avg_daily_cost.toFixed(2)}
            </div>
            <div className="text-xs text-gray-500 mt-1">本月平均</div>
          </div>
        </div>
      )}

      {/* 预算告警 */}
      {alerts.length > 0 && (
        <div className="bg-yellow-50 border-2 border-yellow-200 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-yellow-900 mb-3">⚠️ 预算告警</h3>
          <div className="space-y-2">
            {alerts.map((alert, index) => (
              <div key={index} className="flex items-center gap-2 text-yellow-800">
                <span className="text-sm">{alert}</span>
              </div>
            ))}
          </div>
          <Link
            href="/admin/ai-cost/budget"
            className="inline-block mt-4 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors text-sm font-medium"
          >
            前往预算设置 →
          </Link>
        </div>
      )}

      {/* 成本分布 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 按平台分布 */}
        <div className="bg-white rounded-xl shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 成本分布（按平台）</h3>
          
          <div className="space-y-3">
            {platforms.map((platform) => {
              const percentage = summary && summary.month_cost > 0
                ? (platform.current_month_cost / summary.month_cost) * 100
                : 0;
              
              return (
                <div key={platform.id}>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm font-medium text-gray-700">{platform.name}</span>
                    <span className="text-sm font-semibold text-gray-900">
                      ¥{platform.current_month_cost.toFixed(2)} ({percentage.toFixed(1)}%)
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="h-2 bg-blue-500 rounded-full transition-all"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* 成本趋势 */}
        <div className="bg-white rounded-xl shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📈 成本趋势（最近7天）</h3>
          <CostTrendChart />
        </div>
      </div>

      {/* 快捷操作 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🚀 快捷操作</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link
            href="/admin/ai-cost/budget"
            className="flex flex-col items-center justify-center p-6 border-2 border-green-200 bg-green-50 rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="text-4xl mb-2">🎯</div>
            <h4 className="font-semibold text-green-900 mb-1">设置预算</h4>
            <p className="text-sm text-green-700 text-center">管理月度预算和告警</p>
          </Link>

          <Link
            href="/admin/ai-cost/optimization"
            className="flex flex-col items-center justify-center p-6 border-2 border-orange-200 bg-orange-50 rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="text-4xl mb-2">⚡</div>
            <h4 className="font-semibold text-orange-900 mb-1">优化间隔</h4>
            <p className="text-sm text-orange-700 text-center">调整决策频率节省成本</p>
          </Link>

          <Link
            href="/admin/ai-platforms/stats"
            className="flex flex-col items-center justify-center p-6 border-2 border-blue-200 bg-blue-50 rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="text-4xl mb-2">📊</div>
            <h4 className="font-semibold text-blue-900 mb-1">调用统计</h4>
            <p className="text-sm text-blue-700 text-center">查看详细调用数据</p>
          </Link>

          <Link
            href="/admin/ai-platforms/success-rate"
            className="flex flex-col items-center justify-center p-6 border-2 border-purple-200 bg-purple-50 rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="text-4xl mb-2">📈</div>
            <h4 className="font-semibold text-purple-900 mb-1">成功率分析</h4>
            <p className="text-sm text-purple-700 text-center">分析平台成功率</p>
          </Link>
        </div>
      </div>

      {/* 各平台详细信息 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">💳 各平台详情</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">平台</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">本月成本</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">月度预算</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">使用率</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">状态</th>
              </tr>
            </thead>
            <tbody>
              {platforms.map((platform) => (
                <tr key={platform.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <div className="font-medium text-gray-900">{platform.name}</div>
                    <div className="text-sm text-gray-500">{platform.provider}</div>
                  </td>
                  <td className="text-right py-3 px-4 font-semibold text-gray-900">
                    ¥{platform.current_month_cost.toFixed(2)}
                  </td>
                  <td className="text-right py-3 px-4 text-gray-700">
                    {platform.monthly_budget > 0 ? `¥${platform.monthly_budget.toFixed(2)}` : '未设置'}
                  </td>
                  <td className="text-right py-3 px-4">
                    {platform.monthly_budget > 0 ? (
                      <span className={`font-semibold ${
                        platform.usage_percentage >= 100 ? 'text-red-600' :
                        platform.usage_percentage >= 80 ? 'text-yellow-600' :
                        'text-green-600'
                      }`}>
                        {platform.usage_percentage.toFixed(1)}%
                      </span>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                  <td className="text-right py-3 px-4">
                    {platform.monthly_budget > 0 && platform.usage_percentage >= 100 ? (
                      <span className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded-full">
                        超预算
                      </span>
                    ) : platform.monthly_budget > 0 && platform.usage_percentage >= 80 ? (
                      <span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-700 rounded-full">
                        接近上限
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full">
                        正常
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
