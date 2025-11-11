"use client";

import { useState, useEffect } from "react";
import PageHeader from '../../components/common/PageHeader';

interface ModelPerf {
  accuracy: number;
  profit_rate: number;
  avg_response_time: number;
  total_decisions: number;
  total_trades: number;
  total_pnl: number;
}

interface PerformanceData {
  trained_70b: ModelPerf;
  default_api: ModelPerf;
  current_strategy: string;
  recommendation: string;
}

export default function ModelPerformancePage() {
  const [perfData, setPerfData] = useState<PerformanceData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPerformance();
    // 每30秒刷新一次
    const interval = setInterval(fetchPerformance, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchPerformance = async () => {
    try {
      const response = await fetch("/api/v1/decision/performance");
      const data = await response.json();
      setPerfData(data);
    } catch (error) {
      console.error("获取性能数据失败:", error);
    } finally {
      setLoading(false);
    }
  };

  const changeStrategy = async (strategy: string) => {
    try {
      await fetch("/api/v1/decision/strategy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ strategy })
      });
      fetchPerformance();
    } catch (error) {
      console.error("切换策略失败:", error);
    }
  };

  if (loading || !perfData) {
    return <div className="p-6">加载中...</div>;
  }

  const { trained_70b, default_api, current_strategy, recommendation } = perfData;

  return (
    <div className="space-y-6">
      <PageHeader
        icon="📈"
        title="模型性能监控"
        description="监控AI模型的性能指标和准确率"
        color="cyan"
      />

      {/* 当前策略 */}
      <div className="bg-blue-50 p-4 rounded-xl border border-blue-200">
        <h2 className="font-semibold mb-2">当前路由策略</h2>
        <select
          value={current_strategy}
          onChange={(e) => changeStrategy(e.target.value)}
          className="px-3 py-2 border rounded bg-white"
        >
          <option value="adaptive">🤖 自适应（推荐）</option>
          <option value="single_best">⭐ 单模型（选最优）</option>
          <option value="ab_testing">📊 AB测试（轮流用）</option>
          <option value="ensemble_voting">🗳️ 双模型投票</option>
          <option value="scenario_based">🎯 场景分配</option>
        </select>
        <p className="text-sm text-gray-600 mt-2">
          💡 系统建议: {recommendation}
        </p>
      </div>

      {/* 性能对比 */}
      <div className="grid grid-cols-2 gap-6">
        {/* 训练好的70B */}
        <div className="bg-white p-6 rounded-xl shadow border border-gray-200">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span>🧠</span>
            <span>训练好的70B模型</span>
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">决策准确率</span>
              <span className="font-semibold text-green-600">
                {(trained_70b.accuracy * 100).toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">交易盈利率</span>
              <span className="font-semibold text-green-600">
                {(trained_70b.profit_rate * 100).toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">平均响应时间</span>
              <span className="font-semibold">
                {trained_70b.avg_response_time.toFixed(2)}s
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">总决策次数</span>
              <span className="font-semibold">
                {trained_70b.total_decisions}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">总交易次数</span>
              <span className="font-semibold">
                {trained_70b.total_trades}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">累计盈亏</span>
              <span className={`font-semibold ${
                trained_70b.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                ${trained_70b.total_pnl.toFixed(2)}
              </span>
            </div>
          </div>
        </div>

        {/* 默认API */}
        <div className="bg-white p-6 rounded-xl shadow border border-gray-200">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span>⚡</span>
            <span>默认DeepSeek API</span>
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">决策准确率</span>
              <span className="font-semibold text-blue-600">
                {(default_api.accuracy * 100).toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">交易盈利率</span>
              <span className="font-semibold text-blue-600">
                {(default_api.profit_rate * 100).toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">平均响应时间</span>
              <span className="font-semibold">
                {default_api.avg_response_time.toFixed(2)}s
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">总决策次数</span>
              <span className="font-semibold">
                {default_api.total_decisions}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">总交易次数</span>
              <span className="font-semibold">
                {default_api.total_trades}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">累计盈亏</span>
              <span className={`font-semibold ${
                default_api.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                ${default_api.total_pnl.toFixed(2)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 对比说明 */}
      <div className="bg-yellow-50 p-4 rounded-xl border border-yellow-200">
        <h3 className="font-semibold mb-2">📊 性能对比说明</h3>
        <ul className="text-sm text-gray-700 space-y-1">
          <li>• 准确率和盈利率越高越好</li>
          <li>• 响应时间越短越好（但不应牺牲准确率）</li>
          <li>• 系统会根据实际效果自动调整使用策略</li>
          <li>• 70B模型未训练或不可用时，将自动降级到默认API</li>
        </ul>
      </div>
    </div>
  );
}

