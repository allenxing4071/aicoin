'use client';

import { useEffect, useRef, useState } from 'react';
import { createChart, IChartApi, ISeriesApi } from 'lightweight-charts';
import axios from 'axios';

interface ChartProps {
  symbol: string;
}

export default function TradingChart({ symbol }: ChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // 创建图表
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: '#ffffff' },
        textColor: '#6b7280',
      },
      grid: {
        vertLines: { color: '#e5e7eb' },
        horzLines: { color: '#e5e7eb' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 500,
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#d1d5db',
      },
      timeScale: {
        borderColor: '#d1d5db',
        timeVisible: true,
        secondsVisible: false,
      },
    });

    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#10b981',
      downColor: '#ef4444',
      borderUpColor: '#10b981',
      borderDownColor: '#ef4444',
      wickUpColor: '#10b981',
      wickDownColor: '#ef4444',
    });

    chartRef.current = chart;
    seriesRef.current = candlestickSeries;

    // 加载数据
    loadChartData();

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
  }, [symbol]);

  const loadChartData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`http://localhost:8000/api/v1/market/kline/${symbol}`);
      
      const data = response.data.klines.map((k: any) => ({
        time: Math.floor(new Date(k.timestamp).getTime() / 1000) as any,
        open: parseFloat(k.open),
        high: parseFloat(k.high),
        low: parseFloat(k.low),
        close: parseFloat(k.close),
      }));

      if (seriesRef.current) {
        seriesRef.current.setData(data);
      }
      setLoading(false);
    } catch (error) {
      console.error('Failed to load chart data:', error);
      // 使用模拟数据
      generateMockData();
    }
  };

  const generateMockData = () => {
    const now = Math.floor(Date.now() / 1000);
    const data = [];
    let price = 95000;

    for (let i = 100; i >= 0; i--) {
      const time = (now - i * 3600) as any;
      const change = (Math.random() - 0.5) * 1000;
      const open = price;
      const close = price + change;
      const high = Math.max(open, close) + Math.random() * 500;
      const low = Math.min(open, close) - Math.random() * 500;

      data.push({ time, open, high, low, close });
      price = close;
    }

    if (seriesRef.current) {
      seriesRef.current.setData(data);
    }
    setLoading(false);
  };

  return (
    <div className="relative bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-gray-900">{symbol}</h3>
        <div className="flex space-x-2">
          <button className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200">
            1H
          </button>
          <button className="px-3 py-1 text-sm bg-blue-600 text-white rounded">
            4H
          </button>
          <button className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200">
            1D
          </button>
        </div>
      </div>
      
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-90 z-10">
          <div className="text-gray-600">Loading chart data...</div>
        </div>
      )}
      
      <div ref={chartContainerRef} />
    </div>
  );
}

