'use client';

import { useEffect, useRef } from 'react';
import { createChart, IChartApi, ISeriesApi, LineStyle } from 'lightweight-charts';

interface Model {
  name: string;
  value: number;
  change: number;
  color: string;
  icon?: string;
}

interface MultiModelChartProps {
  models: Model[];
  timeRange?: 'all' | '72h';
}

export default function MultiModelChart({ models, timeRange = 'all' }: MultiModelChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRefs = useRef<Map<string, ISeriesApi<'Line'>>>(new Map());

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // 创建图表
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: '#ffffff' },
        textColor: '#6b7280',
      },
      grid: {
        vertLines: { color: '#e5e7eb', style: LineStyle.Solid },
        horzLines: { color: '#e5e7eb', style: LineStyle.Solid },
      },
      width: chartContainerRef.current.clientWidth,
      height: chartContainerRef.current.clientHeight - 20,
      crosshair: {
        mode: 1,
        vertLine: {
          color: '#4b5563',
          width: 1,
          style: LineStyle.Dashed,
        },
        horzLine: {
          color: '#4b5563',
          width: 1,
          style: LineStyle.Dashed,
        },
      },
      rightPriceScale: {
        borderColor: '#1f2937',
        scaleMargins: {
          top: 0.05,
          bottom: 0.05,
        },
      },
      timeScale: {
        borderColor: '#1f2937',
        timeVisible: true,
        secondsVisible: false,
        fixLeftEdge: true,
        fixRightEdge: true,
      },
    });

    chartRef.current = chart;

    // 为每个模型创建线条
    models.forEach((model) => {
      const series = chart.addLineSeries({
        color: model.color,
        lineWidth: 2,
        title: model.name,
        priceLineVisible: false,
        lastValueVisible: true,
      });
      seriesRefs.current.set(model.name, series);
    });

    // 生成历史数据
    generateHistoricalData();

    // 响应式调整
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
          height: chartContainerRef.current.clientHeight - 20,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    // 实时更新
    const interval = setInterval(() => {
      updateData();
    }, 5000);

    return () => {
      window.removeEventListener('resize', handleResize);
      clearInterval(interval);
      chart.remove();
    };
  }, [models]);

  const generateHistoricalData = () => {
    const now = Math.floor(Date.now() / 1000);
    const daysBack = timeRange === '72h' ? 3 : 15; // 72小时 或 15天历史
    const pointsPerDay = 24; // 每小时一个点
    const totalPoints = daysBack * pointsPerDay;

    models.forEach((model) => {
      const data = [];
      const startValue = 10000;
      const endValue = model.value;
      const totalChange = endValue - startValue;

      for (let i = 0; i < totalPoints; i++) {
        const time = (now - (totalPoints - i) * 3600) as any;
        
        // 使用趋势 + 随机波动
        const progress = i / totalPoints;
        const trendValue = startValue + (totalChange * progress);
        const volatility = 200 * Math.sin(i / 10); // 周期性波动
        const randomNoise = (Math.random() - 0.5) * 300;
        
        let value = trendValue + volatility + randomNoise;
        
        // 确保在合理范围内
        value = Math.max(4000, Math.min(16000, value));
        
        data.push({
          time,
          value,
        });
      }

      const series = seriesRefs.current.get(model.name);
      if (series) {
        series.setData(data);
      }
    });

    // 自动调整可见范围
    if (chartRef.current) {
      chartRef.current.timeScale().fitContent();
    }
  };

  const updateData = () => {
    const now = Math.floor(Date.now() / 1000) as any;

    models.forEach((model) => {
      const series = seriesRefs.current.get(model.name);
      if (series) {
        // 小幅随机波动
        const change = (Math.random() - 0.48) * 100;
        const newValue = Math.max(4000, Math.min(16000, model.value + change));
        
        series.update({
          time: now,
          value: newValue,
        });
      }
    });
  };

  return (
    <div className="relative w-full h-full bg-[#0a0b0d]">
      <div ref={chartContainerRef} className="w-full h-full" />
    </div>
  );
}

