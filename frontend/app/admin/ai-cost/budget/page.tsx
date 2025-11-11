'use client';

/**
 * AI成本预算设置页面
 * 
 * 路径: /admin/ai-cost/budget
 * 
 * 功能：
 * - 设置月度总预算
 * - 按模型设置预算
 * - 预算告警阈值
 * - 超预算通知
 */

import React, { useState, useEffect } from 'react';
import PageHeader from '@/app/components/common/PageHeader';
import { unifiedDesignSystem, getThemeStyles } from '@/app/admin/unified-design-system';
import { StatCardGrid, StatCard } from '@/app/components/common/Cards';

interface ModelBudget {
  model_name: string;
  display_name: string;
  provider: string;
  current_month_cost: number;
  monthly_budget: number;
  remaining_budget: number;
  usage_percentage: number;
}

export default function BudgetSettingsPage() {
  const [models, setModels] = useState<ModelBudget[]>([]);
  const [totalBudget, setTotalBudget] = useState<number>(1000);
  const [alertThreshold, setAlertThreshold] = useState<number>(80);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savingModel, setSavingModel] = useState<string | null>(null);
  
  // 使用统一的橙色主题
  const theme = getThemeStyles('orange');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/v1/intelligence/budget/summary');
      const data = await res.json();
      if (data.success && data.data) {
        setModels(data.data.platforms.map((p: any) => ({
          model_name: p.provider,
          display_name: p.name,
          provider: p.provider,
          current_month_cost: p.current_cost,
          monthly_budget: p.monthly_budget || 0,
          remaining_budget: (p.monthly_budget || 0) - p.current_cost,
          usage_percentage: p.usage_percentage || 0,
        })));
        
        // 设置总预算
        if (data.data.total_budget > 0) {
          setTotalBudget(data.data.total_budget);
        }
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveBudget = async (modelName: string, budget: number) => {
    try {
      setSaving(true);
      setSavingModel(modelName);
      
      // 验证预算值
      if (budget < 0) {
        alert('❌ 预算不能为负数');
        return;
      }
      
      // 找到对应的平台ID
      const model = models.find(m => m.model_name === modelName);
      if (!model) {
        alert('❌ 未找到对应平台');
        return;
      }
      
      // 从API获取平台列表找到ID
      const platformsRes = await fetch('/api/v1/intelligence/platforms');
      const platformsData = await platformsRes.json();
      const platform = platformsData.platforms?.find((p: any) => p.provider === modelName);
      
      if (!platform) {
        alert('❌ 未找到对应平台');
        return;
      }
      
      
      const res = await fetch(`/api/v1/intelligence/platforms/${platform.id}/budget`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          monthly_budget: budget,
          alert_threshold: alertThreshold 
        }),
      });
      
      const data = await res.json();
      if (data.success) {
        
        // 立即更新本地状态，不需要等待fetchData
        setModels(prevModels => 
          prevModels.map(m => 
            m.model_name === modelName 
              ? {
                  ...m,
                  monthly_budget: budget,
                  remaining_budget: budget - m.current_month_cost,
                  usage_percentage: budget > 0 ? (m.current_month_cost / budget) * 100 : 0,
                }
              : m
          )
        );
        
        // 显示一个简短的成功提示
        const toast = document.createElement('div');
        toast.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in';
        toast.textContent = `✅ ${model.display_name} 预算已保存: ¥${budget}`;
        document.body.appendChild(toast);
        setTimeout(() => {
          toast.style.opacity = '0';
          toast.style.transition = 'opacity 0.3s';
          setTimeout(() => toast.remove(), 300);
        }, 2000);
        
        // 后台静默刷新完整数据
        fetchData();
      } else {
        alert('❌ 预算设置失败');
      }
    } catch (error) {
      console.error('预算设置失败:', error);
      alert(`❌ 预算设置失败: ${error}`);
    } finally {
      setSaving(false);
      setSavingModel(null);
    }
  };

  const totalUsed = models.reduce((sum, m) => sum + m.current_month_cost, 0);
  const totalBudgetUsage = totalBudget > 0 ? (totalUsed / totalBudget) * 100 : 0;

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
        title="预算设置"
        description="设置AI模型月度预算和告警阈值"
        color="green"
      />

      {/* 总预算设置 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 总预算设置</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              月度总预算（¥）
            </label>
            <input
              type="number"
              value={totalBudget}
              onChange={(e) => setTotalBudget(Number(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="1000"
              min="0"
              step="10"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              告警阈值（%）
            </label>
            <input
              type="number"
              value={alertThreshold}
              onChange={(e) => setAlertThreshold(Number(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
              placeholder="80"
              min="0"
              max="100"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={() => {
                // TODO: 实现全局预算设置API
                alert(`总预算设置: ¥${totalBudget}\n告警阈值: ${alertThreshold}%\n\n功能即将上线！`);
              }}
              disabled={saving}
              className="w-full px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-400"
            >
              保存设置
            </button>
          </div>
        </div>

        {/* 总预算使用情况 */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">本月总使用</span>
            <span className="text-sm font-semibold text-gray-900">
              ¥{totalUsed.toFixed(2)} / ¥{totalBudget.toFixed(2)}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all ${
                totalBudgetUsage >= 100
                  ? 'bg-red-500'
                  : totalBudgetUsage >= alertThreshold
                  ? 'bg-yellow-500'
                  : 'bg-green-500'
              }`}
              style={{ width: `${Math.min(totalBudgetUsage, 100)}%` }}
            />
          </div>
          <div className="flex justify-between items-center mt-2">
            <span className="text-xs text-gray-500">
              {totalBudgetUsage >= alertThreshold && totalBudgetUsage < 100 && '⚠️ 接近预算上限'}
              {totalBudgetUsage >= 100 && '🚨 已超出预算'}
            </span>
            <span className="text-xs font-medium text-gray-700">
              {totalBudgetUsage.toFixed(1)}%
            </span>
          </div>
        </div>
      </div>

      {/* 各模型预算设置 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🎯 各模型预算</h3>
        
        <div className="space-y-4">
          {models.map((model) => (
            <div key={model.model_name} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h4 className="font-semibold text-gray-900">{model.display_name}</h4>
                  <p className="text-sm text-gray-500">{model.provider}</p>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-500">本月使用</div>
                  <div className="text-lg font-semibold text-gray-900">
                    ¥{model.current_month_cost.toFixed(2)}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    月度预算（¥）
                    {savingModel === model.model_name && (
                      <span className="ml-2 text-xs text-blue-600">💾 保存中...</span>
                    )}
                  </label>
                  <div className="relative">
                    <input
                      type="number"
                      defaultValue={model.monthly_budget}
                      onBlur={(e) => {
                        const budget = Number(e.target.value);
                        if (budget !== model.monthly_budget && !isNaN(budget)) {
                          handleSaveBudget(model.model_name, budget);
                        }
                      }}
                      disabled={savingModel === model.model_name}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                      placeholder="0"
                      min="0"
                      step="1"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    剩余预算（¥）
                  </label>
                  <div className="px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-700 font-medium">
                    {model.monthly_budget > 0
                      ? `¥${(model.monthly_budget - model.current_month_cost).toFixed(2)}`
                      : <span className="text-gray-400">未设置</span>}
                  </div>
                </div>
              </div>

              {/* 预算使用进度条 */}
              {model.monthly_budget > 0 && (
                <div className="mt-3">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-xs text-gray-500">预算使用率</span>
                    <span className="text-xs font-medium text-gray-700">
                      {((model.current_month_cost / model.monthly_budget) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${
                        model.current_month_cost >= model.monthly_budget
                          ? 'bg-red-500'
                          : model.current_month_cost >= model.monthly_budget * (alertThreshold / 100)
                          ? 'bg-yellow-500'
                          : 'bg-blue-500'
                      }`}
                      style={{
                        width: `${Math.min((model.current_month_cost / model.monthly_budget) * 100, 100)}%`,
                      }}
                    />
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* 预算告警规则 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🔔 告警规则</h3>
        
        <div className="space-y-3">
          <div className="flex items-start gap-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="text-yellow-600 mt-1">⚠️</div>
            <div>
              <div className="font-medium text-yellow-900">预算告警</div>
              <div className="text-sm text-yellow-700">
                当使用率达到 {alertThreshold}% 时发送告警通知
              </div>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-red-50 border border-red-200 rounded-lg">
            <div className="text-red-600 mt-1">🚨</div>
            <div>
              <div className="font-medium text-red-900">超预算告警</div>
              <div className="text-sm text-red-700">
                当使用率达到 100% 时发送紧急告警并自动禁用模型
              </div>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="text-blue-600 mt-1">📊</div>
            <div>
              <div className="font-medium text-blue-900">每日报告</div>
              <div className="text-sm text-blue-700">
                每天发送预算使用情况报告到管理员邮箱
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

