'use client';

import { useEffect, useState, useRef } from 'react';
import { createChart, IChartApi, ISeriesApi, LineStyle } from 'lightweight-charts';

interface Model {
  name: string;
  value: number;
  change: number;
  color: string;
  icon?: string;
}

interface EquityCurveMultiProps {
  models: Model[];
}

export default function EquityCurveMulti({ models }: EquityCurveMultiProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRefs = useRef<Map<string, ISeriesApi<'Line'>>>(new Map());

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // 创建图表
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: '#0a0b0d' },
        textColor: '#9ca3af',
      },
      grid: {
        vertLines: { color: '#1f2937', style: LineStyle.Dotted },
        horzLines: { color: '#1f2937', style: LineStyle.Dotted },
      },
      width: chartContainerRef.current.clientWidth,
      height: chartContainerRef.current.clientHeight,
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#2e3748',
        scaleMargins: {
          top: 0.1,
          bottom: 0.1,
        },
      },
      timeScale: {
        borderColor: '#2e3748',
        timeVisible: true,
        secondsVisible: false,
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
      });
      seriesRefs.current.set(model.name, series);
    });

    // 生成模拟数据
    generateMockData();

    // 响应式调整
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
          height: chartContainerRef.current.clientHeight,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    // 实时更新
    const interval = setInterval(() => {
      updateData();
    }, 3000);

    return () => {
      window.removeEventListener('resize', handleResize);
      clearInterval(interval);
      chart.remove();
    };
  }, []);

  const generateMockData = () => {
    const now = Math.floor(Date.now() / 1000);
    const pointsCount = 100;

    models.forEach((model) => {
      const data = [];
      let value = 10000;
      const trend = (model.change / 100) * 100; // 转换为基点

      for (let i = pointsCount; i >= 0; i--) {
        const time = (now - i * 3600 * 4) as any;
        const volatility = (Math.random() - 0.5) * 200;
        const trendValue = (trend / pointsCount) * (pointsCount - i);
        value = 10000 + trendValue + (Math.random() - 0.48) * 500;
        
        data.push({
          time,
          value: Math.max(4000, value),
        });
      }

      const series = seriesRefs.current.get(model.name);
      if (series) {
        series.setData(data);
      }
    });
  };

  const updateData = () => {
    const now = Math.floor(Date.now() / 1000) as any;

    models.forEach((model) => {
      const series = seriesRefs.current.get(model.name);
      if (series) {
        const change = (Math.random() - 0.48) * 50;
        series.update({
          time: now,
          value: model.value + change,
        });
      }
    });
  };

  return (
    <div className="relative w-full h-full bg-[#0a0b0d] rounded-lg">
      <div ref={chartContainerRef} className="w-full h-full" />
    </div>
  );
}

