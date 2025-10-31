'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import MetricCard from './MetricCard';
import RiskGauge from './RiskGauge';

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
  const [period, setPeriod] = useState(30);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 60000); // 每分钟刷新
    return () => clearInterval(interval);
  }, [period]);

  const fetchMetrics = async () => {
    try {
      console.log('🔍 Fetching performance metrics for period:', period);
      const res = await axios.get(`${API_BASE}/performance/metrics`, {
        params: { period_days: period }
      });
      console.log('✅ Performance API response:', res.data);
      setMetrics(res.data);
      setLoading(false);
    } catch (error) {
      console.error('❌ Failed to fetch performance metrics:', error);
      console.error('Error details:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white border border-gray-200 p-4">
        <div className="text-sm text-gray-500">加载性能数据中...</div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="bg-white border border-gray-200 p-4">
        <div className="text-sm text-red-600">加载性能数据失败</div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* 期间选择器 */}
      <div className="bg-white border border-gray-200 p-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold text-gray-900">PERFORMANCE OVERVIEW</h3>
          <div className="flex space-x-2">
            {[7, 30, 90].map((days) => (
              <button
                key={days}
                onClick={() => setPeriod(days)}
                className={`px-3 py-1 text-xs font-bold rounded ${
                  period === days
                    ? 'bg-gray-900 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {days}D
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 收益指标 */}
      <div className="grid grid-cols-3 gap-3">
        <MetricCard
          title="Total Return"
          value={`${metrics.returns.total_return.toFixed(2)}%`}
          change={metrics.returns.daily_return}
          trend={metrics.returns.total_return >= 0 ? 'up' : 'down'}
        />
        <MetricCard
          title="Annual Return"
          value={`${metrics.returns.annual_return.toFixed(2)}%`}
          change={metrics.returns.mtd_return}
          trend={metrics.returns.annual_return >= 0 ? 'up' : 'down'}
        />
        <MetricCard
          title="Daily Return"
          value={`${metrics.returns.daily_return.toFixed(2)}%`}
          change={metrics.returns.daily_return}
          trend={metrics.returns.daily_return >= 0 ? 'up' : 'down'}
        />
      </div>

      {/* 风险仪表盘 */}
      <div className="grid grid-cols-3 gap-3">
        <RiskGauge
          title="Max Drawdown"
          value={metrics.risk.max_drawdown}
          max={10}
          unit="%"
          thresholds={{ warning: 5, danger: 8 }}
        />
        <RiskGauge
          title="Sharpe Ratio"
          value={metrics.risk.sharpe_ratio}
          max={3}
          unit=""
          thresholds={{ warning: 0.5, danger: 0 }}
          inverted={true}
        />
        <RiskGauge
          title="Volatility"
          value={metrics.risk.annual_volatility}
          max={50}
          unit="%"
          thresholds={{ warning: 20, danger: 35 }}
        />
      </div>

      {/* 胜率与交易统计 */}
      <div className="bg-white border border-gray-200">
        <div className="px-3 py-2 border-b border-gray-200 bg-gray-50">
          <h3 className="text-xs font-bold text-gray-900">TRADING STATISTICS</h3>
        </div>
        <div className="p-3 grid grid-cols-2 gap-3">
          <div>
            <div className="text-xs text-gray-600 mb-1">Win Rate</div>
            <div className="flex items-baseline space-x-2">
              <div className={`text-2xl font-bold ${
                metrics.win_rate.overall >= 50 ? 'text-green-600' :
                metrics.win_rate.overall >= 30 ? 'text-yellow-600' :
                'text-red-600'
              }`}>
                {metrics.win_rate.overall.toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500">
                ({metrics.win_rate.winning_trades}W / {metrics.win_rate.losing_trades}L)
              </div>
            </div>
            <div className="mt-2 flex space-x-4 text-xs">
              <div>
                <span className="text-gray-600">Long: </span>
                <span className="font-mono">{metrics.win_rate.long.toFixed(1)}%</span>
              </div>
              <div>
                <span className="text-gray-600">Short: </span>
                <span className="font-mono">{metrics.win_rate.short.toFixed(1)}%</span>
              </div>
            </div>
          </div>

          <div>
            <div className="text-xs text-gray-600 mb-1">Total Trades</div>
            <div className="text-2xl font-bold text-gray-900">
              {metrics.win_rate.total_trades}
            </div>
            <div className="mt-2 text-xs text-gray-600">
              Avg: {metrics.efficiency.trades_per_day.toFixed(1)} per day
            </div>
          </div>
        </div>
      </div>

      {/* 风险调整收益比率 */}
      <div className="bg-white border border-gray-200">
        <div className="px-3 py-2 border-b border-gray-200 bg-gray-50">
          <h3 className="text-xs font-bold text-gray-900">RISK-ADJUSTED RETURNS</h3>
        </div>
        <div className="p-3 grid grid-cols-3 gap-3 text-xs">
          <div>
            <div className="text-gray-600 mb-1">Sharpe Ratio</div>
            <div className={`text-lg font-bold ${
              metrics.ratios.sharpe_ratio >= 1 ? 'text-green-600' :
              metrics.ratios.sharpe_ratio >= 0.5 ? 'text-yellow-600' :
              'text-red-600'
            }`}>
              {metrics.ratios.sharpe_ratio.toFixed(2)}
            </div>
          </div>
          <div>
            <div className="text-gray-600 mb-1">Sortino Ratio</div>
            <div className={`text-lg font-bold ${
              metrics.ratios.sortino_ratio >= 1 ? 'text-green-600' :
              metrics.ratios.sortino_ratio >= 0.5 ? 'text-yellow-600' :
              'text-red-600'
            }`}>
              {metrics.ratios.sortino_ratio.toFixed(2)}
            </div>
          </div>
          <div>
            <div className="text-gray-600 mb-1">Calmar Ratio</div>
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
          <h3 className="text-xs font-bold text-gray-900">EFFICIENCY METRICS</h3>
        </div>
        <div className="p-3 grid grid-cols-2 gap-3 text-xs">
          <div className="flex justify-between">
            <span className="text-gray-600">Expectancy:</span>
            <span className="font-mono font-semibold">${metrics.efficiency.expectancy.toFixed(2)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Kelly Criterion:</span>
            <span className="font-mono font-semibold">{metrics.efficiency.kelly_criterion.toFixed(2)}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Capital Turnover:</span>
            <span className="font-mono font-semibold">{metrics.efficiency.capital_turnover.toFixed(2)}x</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Profit Factor:</span>
            <span className="font-mono font-semibold">{metrics.efficiency.profit_factor.toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

