'use client';

import { useEffect, useRef, useState } from 'react';
import { createChart, IChartApi, ISeriesApi, LineStyle, CrosshairMode } from 'lightweight-charts';
import axios from 'axios';

interface HybridChartProps {
  symbol: string;
  showKlines?: boolean; // 是否显示K线
  showPriceLine?: boolean; // 是否显示价格线
}

interface PriceData {
  timestamp: number;
  price: number;
}

export default function HybridChart({ 
  symbol, 
  showKlines = true, 
  showPriceLine = true 
}: HybridChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const priceLineSeriesRef = useRef<ISeriesApi<'Line'> | null>(null);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'both' | 'kline' | 'price'>('both');
  const [priceData, setPriceData] = useState<PriceData[]>([]);
  const [currentPrice, setCurrentPrice] = useState<number>(0);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // 创建图表
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: '#ffffff' },
        textColor: '#6b7280',
      },
      grid: {
        vertLines: { 
          color: '#e5e7eb',
          style: LineStyle.Solid 
        },
        horzLines: { 
          color: '#e5e7eb',
          style: LineStyle.Solid 
        },
      },
      width: chartContainerRef.current.clientWidth,
      height: 500,
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: {
          color: '#9ca3af',
          width: 1,
          style: LineStyle.Dashed,
          labelBackgroundColor: '#1f2937',
        },
        horzLine: {
          color: '#9ca3af',
          width: 1,
          style: LineStyle.Dashed,
          labelBackgroundColor: '#1f2937',
        },
      },
      rightPriceScale: {
        borderColor: '#d1d5db',
        scaleMargins: {
          top: 0.1,
          bottom: 0.1,
        },
      },
      timeScale: {
        borderColor: '#d1d5db',
        timeVisible: true,
        secondsVisible: false,
        fixLeftEdge: true,
        fixRightEdge: true,
      },
    });

    chartRef.current = chart;

    // 创建K线系列
    if (showKlines) {
      const candlestickSeries = chart.addCandlestickSeries({
        upColor: '#10b981',
        downColor: '#ef4444',
        borderUpColor: '#10b981',
        borderDownColor: '#ef4444',
        wickUpColor: '#10b981',
        wickDownColor: '#ef4444',
      });
      candlestickSeriesRef.current = candlestickSeries;
    }

    // 创建价格线系列
    if (showPriceLine) {
      const priceLineSeries = chart.addLineSeries({
        color: '#3b82f6',
        lineWidth: 2,
        crosshairMarkerVisible: true,
        crosshairMarkerRadius: 4,
        crosshairMarkerBorderColor: '#3b82f6',
        crosshairMarkerBackgroundColor: '#ffffff',
        lastValueVisible: true,
        priceLineVisible: true,
      });
      priceLineSeriesRef.current = priceLineSeries;
    }

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
  }, [symbol, showKlines, showPriceLine]);

  // 当视图模式改变时，更新系列可见性
  useEffect(() => {
    if (!chartRef.current) return;

    if (candlestickSeriesRef.current) {
      candlestickSeriesRef.current.applyOptions({
        visible: viewMode === 'both' || viewMode === 'kline',
      });
    }

    if (priceLineSeriesRef.current) {
      priceLineSeriesRef.current.applyOptions({
        visible: viewMode === 'both' || viewMode === 'price',
      });
    }
  }, [viewMode]);

  const loadChartData = async () => {
    try {
      setLoading(true);
      
      // 获取K线数据
      const klineResponse = await axios.get(`/api/v1/market/klines/multi/${symbol}?intervals=1h`);
      
      if (klineResponse.data.success && klineResponse.data.data.klines['1h']) {
        const klines = klineResponse.data.data.klines['1h'];
        
        // K线数据
        const candleData = klines.map((k: any) => ({
          time: k.timestamp as any,
          open: parseFloat(k.open),
          high: parseFloat(k.high),
          low: parseFloat(k.low),
          close: parseFloat(k.close),
        }));

        // 价格线数据（使用收盘价）
        const lineData = klines.map((k: any) => ({
          time: k.timestamp as any,
          value: parseFloat(k.close),
        }));

        if (candlestickSeriesRef.current && showKlines) {
          candlestickSeriesRef.current.setData(candleData);
        }

        if (priceLineSeriesRef.current && showPriceLine) {
          priceLineSeriesRef.current.setData(lineData);
        }

        // 保存价格数据用于统计
        const prices = klines.map((k: any) => ({
          timestamp: k.timestamp,
          price: parseFloat(k.close),
        }));
        setPriceData(prices);
        setCurrentPrice(prices[prices.length - 1]?.price || 0);

        // 自动调整视图
        if (chartRef.current) {
          chartRef.current.timeScale().fitContent();
        }
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Failed to load chart data:', error);
      setLoading(false);
    }
  };

  // 计算统计数据
  const stats = {
    current: currentPrice,
    high: Math.max(...priceData.map(d => d.price)),
    low: Math.min(...priceData.map(d => d.price)),
    change: priceData.length > 1 
      ? ((currentPrice - priceData[0].price) / priceData[0].price * 100)
      : 0,
  };

  return (
    <div className="w-full h-full flex flex-col">
      {/* 图表控制栏 */}
      <div className="flex items-center justify-between mb-4 px-4 py-2 bg-gray-50 rounded-lg">
        {/* 价格统计 */}
        <div className="flex items-center gap-6">
          <div>
            <div className="text-xs text-gray-500">当前价格</div>
            <div className={`text-lg font-bold ${stats.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              ${stats.current.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500">24h涨跌</div>
            <div className={`text-sm font-semibold ${stats.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {stats.change >= 0 ? '+' : ''}{stats.change.toFixed(2)}%
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500">24h最高</div>
            <div className="text-sm font-medium text-gray-900">
              ${stats.high.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500">24h最低</div>
            <div className="text-sm font-medium text-gray-900">
              ${stats.low.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </div>
          </div>
        </div>

        {/* 视图切换按钮 */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-600">视图模式:</span>
          <div className="flex bg-white border border-gray-300 rounded-md overflow-hidden">
            <button
              onClick={() => setViewMode('both')}
              className={`px-3 py-1 text-xs font-medium transition-colors ${
                viewMode === 'both'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              K线+价格线
            </button>
            <button
              onClick={() => setViewMode('kline')}
              className={`px-3 py-1 text-xs font-medium transition-colors border-l ${
                viewMode === 'kline'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              仅K线
            </button>
            <button
              onClick={() => setViewMode('price')}
              className={`px-3 py-1 text-xs font-medium transition-colors border-l ${
                viewMode === 'price'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              仅价格线
            </button>
          </div>
        </div>
      </div>

      {/* 图表容器 */}
      <div className="flex-1 relative">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 z-10">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
              <p className="mt-4 text-sm text-gray-600">加载图表数据...</p>
            </div>
          </div>
        )}
        <div ref={chartContainerRef} className="w-full h-full" />
      </div>

      {/* 图例说明 */}
      <div className="mt-4 flex items-center gap-4 px-4 py-2 bg-gray-50 rounded-lg">
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${viewMode === 'both' || viewMode === 'kline' ? 'bg-green-500' : 'bg-gray-300'}`}></div>
          <span className="text-xs text-gray-600">K线蜡烛图</span>
        </div>
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${viewMode === 'both' || viewMode === 'price' ? 'bg-blue-500' : 'bg-gray-300'}`}></div>
          <span className="text-xs text-gray-600">价格趋势线</span>
        </div>
        <div className="text-xs text-gray-500 ml-auto">
          提示: 点击视图模式按钮可切换不同的图表显示方式
        </div>
      </div>
    </div>
  );
}

