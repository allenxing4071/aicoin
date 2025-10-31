'use client';

import { useEffect, useRef, useState } from 'react';
import { createChart, ColorType, IChartApi, ISeriesApi } from 'lightweight-charts';

interface LightweightChartProps {
  symbol?: string;
  data?: Array<{
    time: number;
    open: number;
    high: number;
    low: number;
    close: number;
    volume?: number;
  }>;
}

export default function LightweightChart({ symbol = 'BTC-PERP', data }: LightweightChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // 创建图表
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#ffffff' },
        textColor: '#333',
      },
      width: chartContainerRef.current.clientWidth,
      height: 400,
      grid: {
        vertLines: { color: '#f0f0f0' },
        horzLines: { color: '#f0f0f0' },
      },
      crosshair: {
        mode: 1, // Normal crosshair
      },
      rightPriceScale: {
        borderColor: '#e0e0e0',
      },
      timeScale: {
        borderColor: '#e0e0e0',
        timeVisible: true,
        secondsVisible: false,
      },
    });

    chartRef.current = chart;

    // 添加K线系列
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });

    candlestickSeriesRef.current = candlestickSeries;

    // 生成模拟K线数据 (如果没有提供真实数据)
    if (!data || data.length === 0) {
      const mockData = generateMockCandleData();
      candlestickSeries.setData(mockData);
    } else {
      candlestickSeries.setData(data);
    }

    // 自适应宽度
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    // 清理
    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
      }
    };
  }, []);

  // 当数据更新时更新图表
  useEffect(() => {
    if (candlestickSeriesRef.current && data && data.length > 0) {
      candlestickSeriesRef.current.setData(data);
    }
  }, [data]);

  return (
    <div className="w-full h-full">
      <div className="px-4 py-2 border-b border-gray-200 flex items-center justify-between">
        <div className="text-sm font-bold text-gray-900">{symbol}</div>
        <div className="flex space-x-2">
          <button className="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded">1分</button>
          <button className="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded">5分</button>
          <button className="px-2 py-1 text-xs bg-gray-900 text-white rounded">15分</button>
          <button className="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded">1小时</button>
          <button className="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded">1天</button>
        </div>
      </div>
      <div ref={chartContainerRef} className="w-full" />
    </div>
  );
}

// 生成模拟K线数据
function generateMockCandleData() {
  const data = [];
  const basePrice = 95000;
  let currentPrice = basePrice;
  const now = Math.floor(Date.now() / 1000);

  for (let i = 100; i >= 0; i--) {
    const time = now - i * 15 * 60; // 15分钟K线
    const change = (Math.random() - 0.5) * 1000;
    currentPrice += change;

    const open = currentPrice;
    const close = currentPrice + (Math.random() - 0.5) * 500;
    const high = Math.max(open, close) + Math.random() * 200;
    const low = Math.min(open, close) - Math.random() * 200;

    data.push({
      time: time as any,
      open: open,
      high: high,
      low: low,
      close: close,
    });

    currentPrice = close;
  }

  return data;
}

