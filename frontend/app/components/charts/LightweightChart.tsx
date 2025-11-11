'use client';

import { useEffect, useRef, useState } from 'react';
import { createChart, ColorType, IChartApi, ISeriesApi } from 'lightweight-charts';
import axios from 'axios';

const API_BASE = '/api/v1';

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

    // 创建图表 - 完全匹配nof1.ai样式
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#ffffff' },
        textColor: '#1a1a1a',
        fontSize: 12,
      },
      width: chartContainerRef.current.clientWidth,
      height: 400,
      grid: {
        vertLines: { 
          color: '#e0e0e0',
          style: 0, // Solid line
          visible: true,
        },
        horzLines: { 
          color: '#e0e0e0',
          style: 0, // Solid line  
          visible: true,
        },
      },
      crosshair: {
        mode: 1, // Normal crosshair
        vertLine: {
          color: '#9B7DFF',
          width: 1,
          style: 3, // Dashed
          labelBackgroundColor: '#9B7DFF',
        },
        horzLine: {
          color: '#9B7DFF',
          width: 1,
          style: 3, // Dashed
          labelBackgroundColor: '#9B7DFF',
        },
      },
      leftPriceScale: {
        visible: true,
        borderVisible: true,
        borderColor: '#2B2B43',
        scaleMargins: {
          top: 0.1,
          bottom: 0.1,
        },
        autoScale: true,
        invertScale: true, // 反转Y轴：上大下小
      },
      rightPriceScale: {
        visible: false, // 隐藏右侧，只显示左侧
      },
      timeScale: {
        borderVisible: true,
        borderColor: '#2B2B43',
        timeVisible: true,
        secondsVisible: false,
        rightOffset: 5,
        barSpacing: 10,
        fixLeftEdge: false,
        fixRightEdge: false,
      },
      localization: {
        timeFormatter: (timestamp: number) => {
          const date = new Date(timestamp * 1000);
          const month = String(date.getMonth() + 1).padStart(2, '0');
          const day = String(date.getDate()).padStart(2, '0');
          const hours = String(date.getHours()).padStart(2, '0');
          const minutes = String(date.getMinutes()).padStart(2, '0');
          return `${month}-${day} ${hours}:${minutes}`;
        },
      },
    });

    chartRef.current = chart;

    // 添加K线系列 - 匹配nof1.ai样式
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
      priceScaleId: '', // 空字符串 = 左侧价格轴
    });

    candlestickSeriesRef.current = candlestickSeries;

    // 获取K线数据 (如果没有提供真实数据)
    if (!data || data.length === 0) {
      fetchKlineData(symbol).then(klineData => {
        if (klineData && klineData.length > 0) {
          candlestickSeries.setData(klineData as any);
        } else {
          const mockData = generateMockCandleData();
          candlestickSeries.setData(mockData as any);
        }
      });
    } else {
      candlestickSeries.setData(data as any);
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
      candlestickSeriesRef.current.setData(data as any);
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

// 获取真实K线数据
async function fetchKlineData(symbol: string) {
  try {
    const response = await axios.get(`${API_BASE}/market/kline/${symbol}`, {
      params: { interval: '15m', limit: 100 }
    });
    if (response.data && Array.isArray(response.data)) {
      return response.data.map((k: any) => ({
        time: k.timestamp,
        open: parseFloat(k.open),
        high: parseFloat(k.high),
        low: parseFloat(k.low),
        close: parseFloat(k.close),
      }));
    }
  } catch (error) {
    console.error('Failed to fetch kline data:', error);
  }
  return null;
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

