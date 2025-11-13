'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { createChart, IChartApi, ISeriesApi, LineStyle, CrosshairMode } from 'lightweight-charts';
import axios from 'axios';

interface PerformanceComparisonChartProps {
  symbol?: string;
  timeRange?: 'all' | '72h';
}

export default function PerformanceComparisonChart({ symbol = 'BTCUSDT', timeRange = 'all' }: PerformanceComparisonChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const btcLineSeriesRef = useRef<ISeriesApi<'Line'> | null>(null);
  const accountLineSeriesRef = useRef<ISeriesApi<'Line'> | null>(null);
  const tooltipRef = useRef<HTMLDivElement | null>(null);
  
  const [loading, setLoading] = useState(true);
  const [selectedLine, setSelectedLine] = useState<'both' | 'btc' | 'account'>('both');
  const [tooltipData, setTooltipData] = useState<{ visible: boolean; x: number; y: number; price: string; color: string }>({
    visible: false,
    x: 0,
    y: 0,
    price: '',
    color: '#f7931a'
  });
  const [btcData, setBtcData] = useState<any[]>([]);
  const [accountData, setAccountData] = useState<any[]>([]);
  const [stats, setStats] = useState({
    btc: { current: 0, change: 0, changePercent: 0 },
    account: { current: 0, change: 0, changePercent: 0 },
  });
  // 存储真实价格映射（时间戳 -> 真实价格）
  const btcPriceMap = useRef<Map<number, number>>(new Map());
  const accountPriceMap = useRef<Map<number, number>>(new Map());

  // 加载图表数据的函数（必须在使用它的useEffect之前定义）
  const loadChartData = useCallback(async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('admin_token');
      
      // 获取BTC价格数据
      const btcResponse = await axios.get(`/api/v1/market/klines?symbol=${symbol}&interval=1h&limit=500`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // 获取账户快照数据
      const accountResponse = await axios.get('/api/v1/accounts/snapshots', {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (btcResponse.data && Array.isArray(btcResponse.data)) {
        // 处理BTC数据
        const btcKlines = btcResponse.data;
        
        // 根据timeRange过滤数据
        let filteredBtcKlines = btcKlines;
        if (timeRange === '72h') {
          const now = Date.now();
          const hours72 = 72 * 60 * 60 * 1000;
          filteredBtcKlines = btcKlines.filter((k: any) => {
            const timestamp = new Date(k.timestamp).getTime();
            return (now - timestamp) <= hours72;
          });
        }

        if (filteredBtcKlines.length === 0) {
          console.warn('No BTC data available');
          return;
        }

        // 获取起始价格作为基准
        const basePrice = parseFloat(filteredBtcKlines[0].close);
        
        // 清空并重建价格映射
        btcPriceMap.current.clear();
        
        const btcChartData = filteredBtcKlines.map((kline: any) => {
          const price = parseFloat(kline.close);
          const timestamp = Math.floor(new Date(kline.timestamp).getTime() / 1000);
          const normalizedValue = ((price - basePrice) / basePrice) * 100;
          
          // 存储真实价格
          btcPriceMap.current.set(timestamp, price);
          
          return {
            time: timestamp,
            value: normalizedValue
          };
        });

        setBtcData(btcChartData);
        
        // 更新BTC统计数据
        const latestPrice = parseFloat(filteredBtcKlines[filteredBtcKlines.length - 1].close);
        const priceChange = latestPrice - basePrice;
        const priceChangePercent = (priceChange / basePrice) * 100;
        
        setStats(prev => ({
          ...prev,
          btc: {
            current: latestPrice,
            change: priceChange,
            changePercent: priceChangePercent
          }
        }));

        // 更新图表数据
        if (btcLineSeriesRef.current) {
          btcLineSeriesRef.current.setData(btcChartData);
        }
      }

      if (accountResponse.data && Array.isArray(accountResponse.data)) {
        // 处理账户数据
        const snapshots = accountResponse.data;
        
        // 根据timeRange过滤数据
        let filteredSnapshots = snapshots;
        if (timeRange === '72h') {
          const now = Date.now();
          const hours72 = 72 * 60 * 60 * 1000;
          filteredSnapshots = snapshots.filter((s: any) => {
            const timestamp = new Date(s.timestamp).getTime();
            return (now - timestamp) <= hours72;
          });
        }

        if (filteredSnapshots.length === 0) {
          console.warn('No account data available');
          return;
        }

        // 获取起始余额作为基准
        const baseBalance = parseFloat(filteredSnapshots[0].balance || '10000');
        
        // 清空并重建余额映射
        accountPriceMap.current.clear();
        
        const accountChartData = filteredSnapshots.map((snapshot: any) => {
          const balance = parseFloat(snapshot.balance || '10000');
          const timestamp = Math.floor(new Date(snapshot.timestamp).getTime() / 1000);
          const normalizedValue = ((balance - baseBalance) / baseBalance) * 100;
          
          // 存储真实余额
          accountPriceMap.current.set(timestamp, balance);
          
          return {
            time: timestamp,
            value: normalizedValue
          };
        });

        setAccountData(accountChartData);
        
        // 更新账户统计数据
        const latestBalance = parseFloat(filteredSnapshots[filteredSnapshots.length - 1].balance || '10000');
        const balanceChange = latestBalance - baseBalance;
        const balanceChangePercent = (balanceChange / baseBalance) * 100;
        
        setStats(prev => ({
          ...prev,
          account: {
            current: latestBalance,
            change: balanceChange,
            changePercent: balanceChangePercent
          }
        }));

        // 更新图表数据
        if (accountLineSeriesRef.current) {
          accountLineSeriesRef.current.setData(accountChartData);
        }
      }

      setLoading(false);
    } catch (error) {
      console.error('加载图表数据失败:', error);
      setLoading(false);
    }
  }, [symbol, timeRange]);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // 创建图表
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: '#ffffff' },
        textColor: '#333333',
      },
      grid: {
        vertLines: { 
          color: 'rgba(197, 203, 206, 0.3)',
          style: LineStyle.Solid 
        },
        horzLines: { 
          color: 'rgba(197, 203, 206, 0.3)',
          style: LineStyle.Solid 
        },
      },
      width: chartContainerRef.current.clientWidth,
      height: chartContainerRef.current.clientHeight,
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: {
          color: 'rgba(0, 0, 0, 0.5)',
          width: 1,
          style: LineStyle.Dashed,
          labelVisible: true,
          labelBackgroundColor: '#131722',
        },
        horzLine: {
          color: 'rgba(0, 0, 0, 0.5)',
          width: 1,
          style: LineStyle.Dashed,
          labelVisible: true,
          labelBackgroundColor: '#131722',
        },
      },
      rightPriceScale: {
        borderColor: 'rgba(197, 203, 206, 0.8)',
        scaleMargins: {
          top: 0.05,
          bottom: 0.05,
        },
        mode: 2, // 百分比模式
      },
      timeScale: {
        borderColor: 'rgba(197, 203, 206, 0.8)',
        timeVisible: true,
        secondsVisible: false,
        fixLeftEdge: true,
        fixRightEdge: true,
      },
    });

    chartRef.current = chart;

    // BTC价格线（橙色 - BTC品牌色）
    const btcSeries = chart.addLineSeries({
      color: '#f7931a',
      lineWidth: 3,
      crosshairMarkerVisible: true,
      crosshairMarkerRadius: 6,
      crosshairMarkerBorderColor: '#f7931a',
      crosshairMarkerBackgroundColor: '#ffffff',
      lastValueVisible: true,
      priceLineVisible: true,
      title: 'BTC价格',
    });
    btcLineSeriesRef.current = btcSeries;

    // 账户价值线（蓝色）
    const accountSeries = chart.addLineSeries({
      color: '#3b82f6',
      lineWidth: 3,
      crosshairMarkerVisible: true,
      crosshairMarkerRadius: 6,
      crosshairMarkerBorderColor: '#3b82f6',
      crosshairMarkerBackgroundColor: '#ffffff',
      lastValueVisible: true,
      priceLineVisible: true,
      title: '账户价值',
    });
    accountLineSeriesRef.current = accountSeries;

    // ❌ 移除这里的 loadChartData() 调用
    // 数据加载由第二个 useEffect 统一管理（监听 timeRange 变化）

    // 十字光标移动事件 - 显示浮动价格标签
    chart.subscribeCrosshairMove((param) => {
      if (!param.point || !param.time || !chartContainerRef.current) {
        setTooltipData({ visible: false, x: 0, y: 0, price: '', color: '#f7931a' });
        return;
      }

      const timestamp = typeof param.time === 'number' ? param.time : (param.time as any).timestamp;
      const btcSeriesData = param.seriesData.get(btcSeries);
      const accountSeriesData = param.seriesData.get(accountSeries);
      
      // 优先显示橙色BTC线的价格（使用真实价格）
      if (btcSeriesData && selectedLine !== 'account') {
        const realPrice = btcPriceMap.current.get(timestamp);
        if (realPrice) {
          setTooltipData({
            visible: true,
            x: param.point.x,
            y: param.point.y,
            price: `$${realPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
            color: '#f7931a'
          });
        }
      } else if (accountSeriesData && selectedLine !== 'btc') {
        const realBalance = accountPriceMap.current.get(timestamp);
        if (realBalance) {
          setTooltipData({
            visible: true,
            x: param.point.x,
            y: param.point.y,
            price: `$${realBalance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 6 })}`,
            color: '#3b82f6'
          });
        }
      }
    });

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
  }, [symbol]); // 只在 symbol 变化时重新创建图表
  
  // ✅ 单独的 useEffect 监听 timeRange 变化，重新加载数据
  useEffect(() => {
    if (chartRef.current && btcLineSeriesRef.current && accountLineSeriesRef.current) {
      loadChartData();
    }
  }, [timeRange, loadChartData]); // ✅ 添加 loadChartData 依赖

  // 当选择的线改变时，更新可见性
  useEffect(() => {
    if (btcLineSeriesRef.current) {
      btcLineSeriesRef.current.applyOptions({
        visible: selectedLine === 'both' || selectedLine === 'btc',
      });
    }

    if (accountLineSeriesRef.current) {
      accountLineSeriesRef.current.applyOptions({
        visible: selectedLine === 'both' || selectedLine === 'account',
      });
    }
  }, [selectedLine]);

  // loadChartData 已在文件顶部定义，这里不需要重复定义

  // 以下是原有的其他功能代码
  const handleLineToggle = (line: 'both' | 'btc' | 'account') => {
    setSelectedLine(line);
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      {/* 图表容器 */}
      <div ref={chartContainerRef} style={{ width: '100%', height: '100%' }} />
      
      {/* 加载状态 */}
      {loading && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          background: 'rgba(255, 255, 255, 0.9)',
          padding: '20px',
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          加载中...
        </div>
      )}
      
      {/* 浮动价格标签 */}
      {tooltipData.visible && (
        <div
          style={{
            position: 'absolute',
            left: `${tooltipData.x}px`,
            top: `${tooltipData.y - 40}px`,
            background: tooltipData.color,
            color: '#ffffff',
            padding: '6px 12px',
            borderRadius: '6px',
            fontSize: '14px',
            fontWeight: 'bold',
            pointerEvents: 'none',
            zIndex: 1000,
            boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
            whiteSpace: 'nowrap'
          }}
        >
          {tooltipData.price}
        </div>
      )}
      
      {/* 统计信息面板 */}
      <div style={{
        position: 'absolute',
        top: '10px',
        left: '10px',
        background: 'rgba(255, 255, 255, 0.95)',
        padding: '12px',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        zIndex: 100,
        minWidth: '200px'
      }}>
        <div style={{ marginBottom: '8px' }}>
          <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>BTC价格</div>
          <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#f7931a' }}>
            ${stats.btc.current.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: '12px', color: stats.btc.changePercent >= 0 ? '#10b981' : '#ef4444' }}>
            {stats.btc.changePercent >= 0 ? '+' : ''}{stats.btc.changePercent.toFixed(2)}%
          </div>
        </div>
        
        <div>
          <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>账户价值</div>
          <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#3b82f6' }}>
            ${stats.account.current.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 6 })}
          </div>
          <div style={{ fontSize: '12px', color: stats.account.changePercent >= 0 ? '#10b981' : '#ef4444' }}>
            {stats.account.changePercent >= 0 ? '+' : ''}{stats.account.changePercent.toFixed(2)}%
          </div>
        </div>
      </div>
      
      {/* 线条切换按钮 */}
      <div style={{
        position: 'absolute',
        top: '10px',
        right: '10px',
        background: 'rgba(255, 255, 255, 0.95)',
        padding: '8px',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        zIndex: 100,
        display: 'flex',
        gap: '4px'
      }}>
        <button
          onClick={() => handleLineToggle('both')}
          style={{
            padding: '4px 8px',
            fontSize: '12px',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            background: selectedLine === 'both' ? '#3b82f6' : '#e5e7eb',
            color: selectedLine === 'both' ? '#ffffff' : '#374151'
          }}
        >
          全部
        </button>
        <button
          onClick={() => handleLineToggle('btc')}
          style={{
            padding: '4px 8px',
            fontSize: '12px',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            background: selectedLine === 'btc' ? '#f7931a' : '#e5e7eb',
            color: selectedLine === 'btc' ? '#ffffff' : '#374151'
          }}
        >
          BTC
        </button>
        <button
          onClick={() => handleLineToggle('account')}
          style={{
            padding: '4px 8px',
            fontSize: '12px',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            background: selectedLine === 'account' ? '#3b82f6' : '#e5e7eb',
            color: selectedLine === 'account' ? '#ffffff' : '#374151'
          }}
        >
          账户
        </button>
      </div>
    </div>
  );
}

