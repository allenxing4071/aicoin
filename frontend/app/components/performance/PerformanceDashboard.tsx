'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import MetricCard from './MetricCard';
import RiskGauge from './RiskGauge';
import { PerformanceSkeleton } from '../common/LoadingSkeleton';

const API_BASE = 'http://localhost:8000/api/v1';

interface PerformanceMetrics {
  returns: {
    total_return: number;
    annual_return: number;
    daily_return: number;
    mtd_return: number;
    ytd_return: number;
  };
  risk: {
    max_drawdown: number;
    current_drawdown: number;
    annual_volatility: number;
    downside_volatility: number;
    sharpe_ratio: number;
    sortino_ratio: number;
  };
  ratios: {
    sharpe_ratio: number;
    sortino_ratio: number;
    calmar_ratio: number;
    information_ratio: number;
    omega_ratio: number;
  };
  win_rate: {
    overall: number;
    long: number;
    short: number;
    total_trades: number;
    winning_trades: number;
    losing_trades: number;
  };
  efficiency: {
    expectancy: number;
    kelly_criterion: number;
    trades_per_day: number;
    capital_turnover: number;
    profit_factor: number;
  };
}

export default function PerformanceDashboard() {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [period, setPeriod] = useState(30);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 60000); // 每分钟刷新
    return () => clearInterval(interval);
  }, [period]);

  const fetchMetrics = async () => {
    try {
      setError(null);
      const res = await axios.get(`${API_BASE}/performance/metrics`, {
        params: { period_days: period },
        timeout: 10000 // 10秒超时
      });
      setMetrics(res.data);
      setLoading(false);
      setRetryCount(0);
    } catch (error: any) {
      console.error('❌ Failed to fetch performance metrics:', error);
      console.error('❌ Error type:', error.code);
      console.error('❌ Error message:', error.message);
      
      // 设置错误信息
      if (error.code === 'ECONNABORTED') {
        setError('请求超时，API响应过慢');
      } else if (error.code === 'ERR_NETWORK') {
        setError('网络错误，无法连接到服务器');
      } else {
        setError('加载失败：' + (error.message || '未知错误'));
      }
      
      // 自动重试机制
      if (retryCount < 3) {
        setTimeout(() => {
          setRetryCount(retryCount + 1);
          fetchMetrics();
        }, 2000);
      } else {
        setLoading(false);
      }
    }
  };

  if (loading) {
    return (
      <div className="space-y-4 p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl">
        <div className="bg-gradient-to-br from-white to-purple-50/30 border border-purple-200 rounded-xl p-4 shadow-md">
          <div className="text-center">
            <div className="text-lg mb-2 animate-pulse">📊</div>
            <div className="text-sm text-gray-600">
              加载性能数据中...
              {retryCount > 0 && <span className="text-orange-600 font-semibold"> (重试 {retryCount}/3)</span>}
            </div>
          </div>
        </div>
        <PerformanceSkeleton />
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className="p-4 bg-gradient-to-br from-red-50 to-orange-50 border border-red-200 rounded-xl shadow-lg">
        <div className="flex items-center justify-between">
          <div className="text-sm text-red-600 font-semibold">
            ⚠️ {error || '加载性能数据失败'}
          </div>
          <button
            onClick={() => {
              setRetryCount(0);
              setLoading(true);
              fetchMetrics();
            }}
            className="px-3 py-1 text-xs font-bold bg-red-600 text-white rounded-lg hover:bg-red-700 shadow-md transition-all"
          >
            重试
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4 p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl">
      {/* 期间选择器 */}
      <div className="bg-gradient-to-br from-white to-purple-50/30 border border-purple-200 rounded-xl p-4 shadow-lg">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent flex items-center">
            <span className="text-xl mr-2">📈</span>
            性能概览
          </h3>
          <div className="flex space-x-2">
            {[7, 30, 90].map((days) => (
              <button
                key={days}
                onClick={() => setPeriod(days)}
                className={`px-3 py-1 text-xs font-bold rounded-lg transition-all ${
                  period === days
                    ? 'bg-purple-600 text-white shadow-md'
                    : 'bg-white text-gray-600 hover:bg-purple-50'
                }`}
              >
                {days}天
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 收益指标 */}
      <div className="grid grid-cols-3 gap-3">
        <MetricCard
          title="总收益"
          value={`${metrics.returns.total_return.toFixed(2)}%`}
          change={metrics.returns.daily_return}
          trend={metrics.returns.total_return >= 0 ? 'up' : 'down'}
        />
        <MetricCard
          title="年化收益"
          value={`${metrics.returns.annual_return.toFixed(2)}%`}
          change={metrics.returns.mtd_return}
          trend={metrics.returns.annual_return >= 0 ? 'up' : 'down'}
        />
        <MetricCard
          title="日收益"
          value={`${metrics.returns.daily_return.toFixed(2)}%`}
          change={metrics.returns.daily_return}
          trend={metrics.returns.daily_return >= 0 ? 'up' : 'down'}
        />
      </div>

      {/* 风险仪表盘 */}
      <div className="grid grid-cols-3 gap-3">
        <RiskGauge
          title="最大回撤"
          value={metrics.risk.max_drawdown}
          max={10}
          unit="%"
          thresholds={{ warning: 5, danger: 8 }}
        />
        <RiskGauge
          title="夏普比率"
          value={metrics.risk.sharpe_ratio}
          max={3}
          unit=""
          thresholds={{ warning: 0.5, danger: 0 }}
          inverted={true}
        />
        <RiskGauge
          title="波动率"
          value={metrics.risk.annual_volatility}
          max={50}
          unit="%"
          thresholds={{ warning: 20, danger: 35 }}
        />
      </div>

      {/* 胜率与交易统计 */}
      <div className="bg-gradient-to-br from-white to-purple-50/30 border border-purple-200 rounded-xl shadow-lg">
        <div className="px-4 py-3 border-b border-purple-200 bg-gradient-to-r from-purple-100/50 to-pink-100/50 rounded-t-xl">
          <h3 className="text-sm font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent flex items-center">
            <span className="text-xl mr-2">📊</span>
            交易统计
          </h3>
        </div>
        <div className="p-3 grid grid-cols-2 gap-3">
          <div>
            <div className="text-xs text-gray-600 mb-1">胜率</div>
            <div className="flex items-baseline space-x-2">
              <div className={`text-2xl font-bold ${
                metrics.win_rate.overall >= 50 ? 'text-green-600' :
                metrics.win_rate.overall >= 30 ? 'text-yellow-600' :
                'text-red-600'
              }`}>
                {metrics.win_rate.overall.toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500">
                ({metrics.win_rate.winning_trades}胜 / {metrics.win_rate.losing_trades}负)
              </div>
            </div>
            <div className="mt-2 flex space-x-4 text-xs">
              <div>
                <span className="text-gray-600">做多: </span>
                <span className="font-mono">{metrics.win_rate.long.toFixed(1)}%</span>
              </div>
              <div>
                <span className="text-gray-600">做空: </span>
                <span className="font-mono">{metrics.win_rate.short.toFixed(1)}%</span>
              </div>
            </div>
          </div>

          <div>
            <div className="text-xs text-gray-600 mb-1">总交易数</div>
            <div className="text-2xl font-bold text-gray-900">
              {metrics.win_rate.total_trades}
            </div>
            <div className="mt-2 text-xs text-gray-600">
              平均: {metrics.efficiency.trades_per_day.toFixed(1)} 笔/天
            </div>
          </div>
        </div>
      </div>

      {/* 风险调整收益比率 */}
      <div className="bg-white border border-gray-200">
        <div className="px-3 py-2 border-b border-gray-200 bg-gray-50">
          <h3 className="text-xs font-bold text-gray-900">风险调整收益</h3>
        </div>
        <div className="p-3 grid grid-cols-3 gap-3 text-xs">
          <div>
            <div className="text-gray-600 mb-1">夏普比率</div>
            <div className={`text-lg font-bold ${
              metrics.ratios.sharpe_ratio >= 1 ? 'text-green-600' :
              metrics.ratios.sharpe_ratio >= 0.5 ? 'text-yellow-600' :
              'text-red-600'
            }`}>
              {metrics.ratios.sharpe_ratio.toFixed(2)}
            </div>
          </div>
          <div>
            <div className="text-gray-600 mb-1">索提诺比率</div>
            <div className={`text-lg font-bold ${
              metrics.ratios.sortino_ratio >= 1 ? 'text-green-600' :
              metrics.ratios.sortino_ratio >= 0.5 ? 'text-yellow-600' :
              'text-red-600'
            }`}>
              {metrics.ratios.sortino_ratio.toFixed(2)}
            </div>
          </div>
          <div>
            <div className="text-gray-600 mb-1">卡玛比率</div>
            <div className={`text-lg font-bold ${
              metrics.ratios.calmar_ratio >= 1 ? 'text-green-600' :
              metrics.ratios.calmar_ratio >= 0 ? 'text-yellow-600' :
              'text-red-600'
            }`}>
              {metrics.ratios.calmar_ratio.toFixed(2)}
            </div>
          </div>
        </div>
      </div>

      {/* 效率指标 */}
      <div className="bg-white border border-gray-200">
        <div className="px-3 py-2 border-b border-gray-200 bg-gray-50">
          <h3 className="text-xs font-bold text-gray-900">效率指标</h3>
        </div>
        <div className="p-3 grid grid-cols-2 gap-3 text-xs">
          <div className="flex justify-between">
            <span className="text-gray-600">期望值:</span>
            <span className="font-mono font-semibold">${metrics.efficiency.expectancy.toFixed(2)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">凯利准则:</span>
            <span className="font-mono font-semibold">{metrics.efficiency.kelly_criterion.toFixed(2)}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">资金周转率:</span>
            <span className="font-mono font-semibold">{metrics.efficiency.capital_turnover.toFixed(2)}x</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">盈利因子:</span>
            <span className="font-mono font-semibold">{metrics.efficiency.profit_factor.toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

