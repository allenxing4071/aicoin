'use client';

/**
 * 成本趋势图表组件
 * 使用 lightweight-charts 展示每日成本变化
 */

import React, { useEffect, useRef, useState } from 'react';
import { createChart, IChartApi, ISeriesApi, ColorType } from 'lightweight-charts';

interface DailyData {
  date: string;
  total_cost: number;
  total_calls: number;
  successful_calls: number;
  failed_calls: number;
}

interface CostTrendData {
  days: number;
  start_time: string;
  end_time: string;
  daily_trend: DailyData[];
  summary: {
    total_cost: number;
    avg_daily_cost: number;
    max_daily_cost: number;
    min_daily_cost: number;
  };
}

export default function CostTrendChart() {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const areaSeriesRef = useRef<ISeriesApi<'Area'> | null>(null);
  
  const [loading, setLoading] = useState(true);
  const [trendData, setTrendData] = useState<CostTrendData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000); // 每分钟刷新
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!chartContainerRef.current || !trendData || trendData.daily_trend.length === 0) return;

    // 创建图表
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#ffffff' },
        textColor: '#6b7280',
      },
      grid: {
        vertLines: { color: '#f3f4f6' },
        horzLines: { color: '#f3f4f6' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 250,
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#e5e7eb',
      },
      timeScale: {
        borderColor: '#e5e7eb',
        timeVisible: true,
        secondsVisible: false,
      },
    });

    // 创建面积图系列
    const areaSeries = chart.addAreaSeries({
      topColor: 'rgba(34, 197, 94, 0.4)',
      bottomColor: 'rgba(34, 197, 94, 0.0)',
      lineColor: 'rgba(34, 197, 94, 1)',
      lineWidth: 2,
      priceFormat: {
        type: 'custom',
        formatter: (price: number) => `¥${price.toFixed(2)}`,
      },
    });

    // 转换数据格式 - 使用 YYYY-MM-DD 格式作为时间轴
    const chartData = trendData.daily_trend.map((d) => ({
      time: d.date.split('T')[0], // 使用 YYYY-MM-DD 格式
      value: d.total_cost,
    }));

    areaSeries.setData(chartData);
    
    // 自动适应可见范围
    chart.timeScale().fitContent();

    chartRef.current = chart;
    areaSeriesRef.current = areaSeries;

    // 响应式调整
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [trendData]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/v1/ai-platforms/cost-trend-daily?days=7');
      const result = await response.json();
      
      if (result.success && result.data) {
        setTrendData(result.data);
      } else {
        setError('获取数据失败');
      }
    } catch (err) {
      console.error('Failed to fetch cost trend:', err);
      setError('网络错误');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !trendData) {
    return (
      <div className="text-center py-12 text-gray-500">
        <div className="text-2xl mb-2">⏳</div>
        <p>加载中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12 text-red-500">
        <div className="text-2xl mb-2">❌</div>
        <p>{error}</p>
      </div>
    );
  }

  if (!trendData || trendData.daily_trend.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <div className="text-4xl mb-2">📊</div>
        <p>暂无数据</p>
        <p className="text-sm mt-2">请等待AI平台产生调用数据</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* 统计概览 */}
      <div className="grid grid-cols-4 gap-3 mb-4">
        <div className="text-center">
          <div className="text-xs text-gray-500">总成本</div>
          <div className="text-lg font-bold text-green-600">
            ¥{trendData.summary.total_cost.toFixed(2)}
          </div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-500">日均成本</div>
          <div className="text-lg font-bold text-blue-600">
            ¥{trendData.summary.avg_daily_cost.toFixed(2)}
          </div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-500">最高</div>
          <div className="text-lg font-bold text-orange-600">
            ¥{trendData.summary.max_daily_cost.toFixed(2)}
          </div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-500">最低</div>
          <div className="text-lg font-bold text-gray-600">
            ¥{trendData.summary.min_daily_cost.toFixed(2)}
          </div>
        </div>
      </div>

      {/* 图表 */}
      <div ref={chartContainerRef} className="w-full" />

      {/* 提示信息 */}
      <div className="text-xs text-gray-500 text-center">
        💡 展示最近 {trendData.days} 天的成本趋势
      </div>
    </div>
  );
}

