'use client';

/**
 * 决策间隔优化页面
 * 
 * 路径: /admin/ai-cost/optimization
 * 
 * 功能：
 * - 决策间隔成本分析
 * - 智能推荐模式
 * - 一键切换决策间隔
 * - 成本节省预测
 */

import React, { useState, useEffect } from 'react';
import PageHeader from '@/app/components/common/PageHeader';

interface DecisionInterval {
  name: string;
  interval_seconds: number;
  interval_display: string;
  daily_decisions: number;
  daily_cost: number;
  monthly_cost: number;
  savings_pct: number;
  recommended: boolean;
  description: string;
}

export default function OptimizationPage() {
  const [intervals, setIntervals] = useState<DecisionInterval[]>([]);
  const [currentInterval, setCurrentInterval] = useState<number>(600);
  const [loading, setLoading] = useState(true);
  const [changing, setChanging] = useState(false);

  useEffect(() => {
    fetchData();
    fetchCurrentInterval();
  }, []);

  const fetchCurrentInterval = async () => {
    try {
      const res = await fetch('/health');
      const data = await res.json();
      if (data.orchestrator_status?.decision_interval) {
        setCurrentInterval(data.orchestrator_status.decision_interval);
      }
    } catch (error) {
      console.error('获取决策间隔失败:', error);
    }
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/v1/ai-cost/decision-interval-analysis');
      const data = await res.json();
      if (data.success) {
        setIntervals(data.data.intervals);
      }
    } catch (error) {
      console.error('获取数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChangeInterval = async (intervalSeconds: number) => {
    if (!confirm(`确定要切换到 ${intervals.find(i => i.interval_seconds === intervalSeconds)?.name} 模式吗？`)) {
      return;
    }

    try {
      setChanging(true);
      // 使用正确的API路径
      const res = await fetch(`/api/v1/ai/config/decision-interval?interval=${intervalSeconds}`, {
        method: 'PUT',
      });
      
      const data = await res.json();
      if (data.success) {
        alert('✅ 决策间隔切换成功');
        setCurrentInterval(intervalSeconds);
        fetchData();
      } else {
        alert(`❌ 决策间隔切换失败: ${data.message || '未知错误'}`);
      }
    } catch (error) {
      alert(`❌ 决策间隔切换失败: ${error}`);
    } finally {
      setChanging(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  const currentMode = intervals.find(i => i.interval_seconds === currentInterval);
  const recommendedMode = intervals.find(i => i.recommended && i.interval_seconds !== currentInterval);

  return (
    <div className="space-y-6">
      <PageHeader
        icon="⚡"
        title="决策间隔优化"
        description="优化AI决策频率，平衡决策质量和成本"
        color="orange"
      />

      {/* 当前配置 */}
      <div className="bg-gradient-to-r from-blue-50 to-cyan-50 border-2 border-blue-200 rounded-xl p-6">
        <h3 className="text-xl font-bold text-blue-900 mb-4">📌 当前配置</h3>
        {currentMode ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-blue-900">{currentMode.name}</div>
                <div className="text-sm text-blue-700 mt-1">{currentMode.description}</div>
              </div>
              <div className="text-right">
                <div className="text-sm text-blue-600">决策间隔</div>
                <div className="text-3xl font-bold text-blue-900">{currentMode.interval_display}</div>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4 mt-4">
              <div className="bg-white rounded-lg p-3">
                <div className="text-xs text-gray-500">每日决策次数</div>
                <div className="text-lg font-semibold text-gray-900">{currentMode.daily_decisions}</div>
              </div>
              <div className="bg-white rounded-lg p-3">
                <div className="text-xs text-gray-500">月成本</div>
                <div className="text-lg font-semibold text-gray-900">¥{currentMode.monthly_cost.toFixed(0)}</div>
              </div>
              <div className="bg-white rounded-lg p-3">
                <div className="text-xs text-gray-500">节省比例</div>
                <div className="text-lg font-semibold text-green-600">{currentMode.savings_pct}%</div>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-red-600">❌ 未找到当前配置</div>
        )}
      </div>

      {/* 推荐配置 */}
      {recommendedMode && (
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl p-6">
          <h3 className="text-xl font-bold text-green-900 mb-4">💡 推荐配置</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-green-900">{recommendedMode.name}</div>
                <div className="text-sm text-green-700 mt-1">{recommendedMode.description}</div>
              </div>
              <button
                onClick={() => handleChangeInterval(recommendedMode.interval_seconds)}
                disabled={changing}
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-400 font-semibold"
              >
                {changing ? '切换中...' : '一键切换'}
              </button>
            </div>
            <div className="grid grid-cols-3 gap-4 mt-4">
              <div className="bg-white rounded-lg p-3">
                <div className="text-xs text-gray-500">每日决策次数</div>
                <div className="text-lg font-semibold text-gray-900">{recommendedMode.daily_decisions}</div>
              </div>
              <div className="bg-white rounded-lg p-3">
                <div className="text-xs text-gray-500">月成本</div>
                <div className="text-lg font-semibold text-gray-900">¥{recommendedMode.monthly_cost.toFixed(0)}</div>
              </div>
              <div className="bg-white rounded-lg p-3">
                <div className="text-xs text-gray-500">可节省</div>
                <div className="text-lg font-semibold text-green-600">
                  ¥{currentMode ? (currentMode.monthly_cost - recommendedMode.monthly_cost).toFixed(0) : 0}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 所有模式对比 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 决策间隔成本分析</h3>
        
        <div className="space-y-3">
          {intervals.map((interval) => {
            const isCurrent = interval.interval_seconds === currentInterval;
            const isRecommended = interval.recommended;
            
            return (
              <div
                key={interval.interval_seconds}
                className={`border-2 rounded-xl p-4 transition-all ${
                  isCurrent
                    ? 'border-blue-500 bg-blue-50'
                    : isRecommended
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 bg-white'
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-lg font-bold text-gray-900">{interval.name}</span>
                        {isCurrent && (
                          <span className="px-2 py-1 text-xs bg-blue-600 text-white rounded-full">
                            当前
                          </span>
                        )}
                        {isRecommended && !isCurrent && (
                          <span className="px-2 py-1 text-xs bg-green-600 text-white rounded-full">
                            推荐
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-gray-600 mt-1">{interval.description}</div>
                    </div>
                  </div>
                  {!isCurrent && (
                    <button
                      onClick={() => handleChangeInterval(interval.interval_seconds)}
                      disabled={changing}
                      className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors disabled:bg-gray-400 text-sm"
                    >
                      切换
                    </button>
                  )}
                </div>

                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                  <div>
                    <div className="text-xs text-gray-500">决策间隔</div>
                    <div className="text-sm font-semibold text-gray-900">{interval.interval_display}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500">每日决策</div>
                    <div className="text-sm font-semibold text-gray-900">{interval.daily_decisions}次</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500">日成本</div>
                    <div className="text-sm font-semibold text-gray-900">¥{interval.daily_cost.toFixed(2)}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500">月成本</div>
                    <div className="text-sm font-semibold text-gray-900">¥{interval.monthly_cost.toFixed(0)}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500">节省比例</div>
                    <div className="text-sm font-semibold text-green-600">{interval.savings_pct}%</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 优化建议 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">💡 优化建议</h3>
        
        <div className="space-y-3">
          <div className="flex items-start gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="text-blue-600 mt-1">📈</div>
            <div>
              <div className="font-medium text-blue-900">高频交易场景</div>
              <div className="text-sm text-blue-700">
                如果市场波动剧烈，建议使用"实时模式"或"高频模式"，可以更快捕捉交易机会
              </div>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-green-50 border border-green-200 rounded-lg">
            <div className="text-green-600 mt-1">💰</div>
            <div>
              <div className="font-medium text-green-900">成本优先场景</div>
              <div className="text-sm text-green-700">
                如果追求成本节约，建议使用"标准模式"或"经济模式"，可以大幅降低AI调用成本
              </div>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-purple-50 border border-purple-200 rounded-lg">
            <div className="text-purple-600 mt-1">🤖</div>
            <div>
              <div className="font-medium text-purple-900">智能模式</div>
              <div className="text-sm text-purple-700">
                "智能模式"会根据市场波动自动调整决策频率，平衡决策质量和成本
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

