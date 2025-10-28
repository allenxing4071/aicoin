'use client';

import { useEffect, useRef, useState } from 'react';
import { createChart, IChartApi, ISeriesApi, LineStyle } from 'lightweight-charts';
import axios from 'axios';

interface Model {
  name: string;
  slug: string;
  value: number;
  change: number;
  color: string;
  icon?: string;
}

interface MultiModelChartProps {
  models: Model[];
  timeRange?: 'all' | '72h';
}

const API_BASE = 'http://localhost:8000/api/v1';

export default function MultiModelChart({ models, timeRange = 'all' }: MultiModelChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRefs = useRef<Map<string, ISeriesApi<'Line'>>>(new Map());
  const [accountHistory, setAccountHistory] = useState<any[]>([]);

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
      seriesRefs.current.set(model.slug, series);
    });

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

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [models]);

  // 获取账户历史数据
  useEffect(() => {
    const fetchAccountHistory = async () => {
      try {
        const response = await axios.get(`${API_BASE}/trading/account/history`);
        if (response.data && response.data.length > 0) {
          setAccountHistory(response.data);
          updateChartData(response.data);
        } else {
          // 如果没有历史数据，生成初始数据点
          generateInitialData();
        }
      } catch (error) {
        console.log('Failed to fetch account history, using initial data');
        generateInitialData();
      }
    };

    fetchAccountHistory();

    // 每10秒更新一次
    const interval = setInterval(fetchAccountHistory, 10000);

    return () => clearInterval(interval);
  }, [models, timeRange]);

  const generateInitialData = () => {
    const now = Math.floor(Date.now() / 1000);
    
    models.forEach((model) => {
      const series = seriesRefs.current.get(model.slug);
      if (series) {
        // 为每个AI生成初始资金点 ($100)
        const initialData = [
          {
            time: now as any,
            value: 100, // 初始资金 $100
          }
        ];
        series.setData(initialData);
      }
    });

    if (chartRef.current) {
      chartRef.current.timeScale().fitContent();
    }
  };

  const updateChartData = (history: any[]) => {
    if (!history || history.length === 0) return;

    // 按模型分组数据
    const dataByModel = new Map<string, any[]>();
    
    models.forEach((model) => {
      dataByModel.set(model.slug, []);
    });

    // 处理历史数据 - 只处理DeepSeek
    history.forEach((record: any) => {
      const timestamp = Math.floor(new Date(record.timestamp).getTime() / 1000);
      
      if (record.model === 'deepseek-chat-v3.1' && dataByModel.has('deepseek-chat-v3.1')) {
        dataByModel.get('deepseek-chat-v3.1')!.push({
          time: timestamp as any,
          value: parseFloat(record.account_value || record.balance || 100),
        });
      }
      // Qwen已禁用
    });

    // 如果没有历史数据，添加初始点
    models.forEach((model) => {
      const data = dataByModel.get(model.slug) || [];
      if (data.length === 0) {
        const now = Math.floor(Date.now() / 1000);
        data.push({
          time: now as any,
          value: 100, // 初始资金
        });
      }
      
      const series = seriesRefs.current.get(model.slug);
      if (series) {
        // 按时间排序
        data.sort((a, b) => a.time - b.time);
        series.setData(data);
      }
    });

    if (chartRef.current) {
      chartRef.current.timeScale().fitContent();
    }
  };

  return (
    <div className="relative w-full h-full bg-white">
      <div ref={chartContainerRef} className="w-full h-full" />
    </div>
  );
}

