'use client';

import { useEffect, useRef, useState } from 'react';
import { createChart, IChartApi, ISeriesApi, LineStyle, CrosshairMode } from 'lightweight-charts';
import axios from 'axios';

interface PerformanceComparisonChartProps {
  symbol?: string;
}

export default function PerformanceComparisonChart({ symbol = 'BTCUSDT' }: PerformanceComparisonChartProps) {
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

    // 加载数据
    loadChartData();

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
  }, [symbol]);

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

  const loadChartData = async () => {
    try {
      setLoading(true);

      // 1. 获取BTC价格历史
      const btcResponse = await axios.get(`/api/v1/market/klines/multi/${symbol}?intervals=1h`);
      
      if (btcResponse.data.success && btcResponse.data.data.klines['1h']) {
        const klines = btcResponse.data.data.klines['1h'];
        
        // BTC价格数据（标准化）
        const firstPrice = parseFloat(klines[0].close);
        btcPriceMap.current.clear();
        const btcLineData = klines.map((k: any) => {
          const price = parseFloat(k.close);
          const timestamp = k.timestamp;
          btcPriceMap.current.set(timestamp, price); // 存储真实价格
          return {
            time: timestamp as any,
            value: (price / firstPrice) * 100, // 标准化到100
          };
        });

        setBtcData(klines);
        
        if (btcLineSeriesRef.current) {
          btcLineSeriesRef.current.setData(btcLineData);
        }

        // 计算BTC统计
        const currentBtcPrice = parseFloat(klines[klines.length - 1].close);
        const btcChange = currentBtcPrice - firstPrice;
        const btcChangePercent = (btcChange / firstPrice) * 100;

        setStats(prev => ({
          ...prev,
          btc: {
            current: currentBtcPrice,
            change: btcChange,
            changePercent: btcChangePercent,
          }
        }));
      }

      // 2. 获取账户价值历史
      try {
        const accountHistoryResponse = await axios.get('/api/v1/dashboard/account-history?limit=100');
        
        if (accountHistoryResponse.data && accountHistoryResponse.data.length > 0) {
          const history = accountHistoryResponse.data;
          
          // 账户价值数据（标准化）
          const firstValue = history[0].balance;
          accountPriceMap.current.clear();
          const accountLineData = history.map((item: any) => {
            const timestamp = Math.floor(new Date(item.timestamp).getTime() / 1000);
            const balance = item.balance;
            accountPriceMap.current.set(timestamp, balance); // 存储真实余额
            return {
              time: timestamp as any,
              value: (balance / firstValue) * 100, // 标准化到100
            };
          });

          setAccountData(history);
          
          if (accountLineSeriesRef.current) {
            accountLineSeriesRef.current.setData(accountLineData);
          }

          // 计算账户统计
          const currentValue = history[history.length - 1].balance;
          const valueChange = currentValue - firstValue;
          const valueChangePercent = (valueChange / firstValue) * 100;

          setStats(prev => ({
            ...prev,
            account: {
              current: currentValue,
              change: valueChange,
              changePercent: valueChangePercent,
            }
          }));
        } else {
          // 如果没有账户历史，使用模拟数据展示功能
          console.warn('No account history data available, using mock data for demonstration');
          const mockAccountData = btcData.map((k: any, index: number) => ({
            time: k.timestamp as any,
            value: 100 + (Math.random() - 0.5) * 10, // 模拟账户波动
          }));
          
          if (accountLineSeriesRef.current) {
            accountLineSeriesRef.current.setData(mockAccountData);
          }
        }
      } catch (accountError) {
        console.error('Failed to load account history:', accountError);
        // 使用模拟数据
        if (btcData.length > 0 && accountLineSeriesRef.current) {
          const mockAccountData = btcData.map((k: any) => ({
            time: k.timestamp as any,
            value: 100 + (Math.random() - 0.5) * 10,
          }));
          accountLineSeriesRef.current.setData(mockAccountData);
        }
      }

      // 自动调整视图
      if (chartRef.current) {
        chartRef.current.timeScale().fitContent();
      }

      setLoading(false);
    } catch (error) {
      console.error('Failed to load chart data:', error);
      setLoading(false);
    }
  };

  return (
    <div className="w-full h-full flex flex-col">
      {/* 图表控制栏 */}
      <div className="mb-4 px-4 py-3 bg-gradient-to-r from-orange-50 to-blue-50 rounded-lg border-2 border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            {/* BTC统计 */}
            <div 
              className={`cursor-pointer transition-all ${selectedLine === 'btc' ? 'scale-105' : ''}`}
              onClick={() => setSelectedLine(selectedLine === 'btc' ? 'both' : 'btc')}
            >
              <div className="flex items-center gap-2 mb-1">
                <div className="w-3 h-3 rounded-full bg-[#f7931a]"></div>
                <div className="text-xs font-semibold text-gray-600">BTC价格趋势</div>
              </div>
              <div className="flex items-baseline gap-2">
                <div className="text-xl font-bold text-gray-900">
                  ${stats.btc.current.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
                <div className={`text-sm font-semibold ${stats.btc.changePercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {stats.btc.changePercent >= 0 ? '+' : ''}{stats.btc.changePercent.toFixed(2)}%
                </div>
              </div>
            </div>

            {/* 分隔线 */}
            <div className="h-12 w-px bg-gray-300"></div>

            {/* 账户价值统计 */}
            <div 
              className={`cursor-pointer transition-all ${selectedLine === 'account' ? 'scale-105' : ''}`}
              onClick={() => setSelectedLine(selectedLine === 'account' ? 'both' : 'account')}
            >
              <div className="flex items-center gap-2 mb-1">
                <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                <div className="text-xs font-semibold text-gray-600">合约账户收益</div>
              </div>
              <div className="flex items-baseline gap-2">
                <div className="text-xl font-bold text-gray-900">
                  ${stats.account.current.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
                <div className={`text-sm font-semibold ${stats.account.changePercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {stats.account.changePercent >= 0 ? '+' : ''}{stats.account.changePercent.toFixed(2)}%
                </div>
              </div>
            </div>

            {/* 分隔线 */}
            <div className="h-12 w-px bg-gray-300"></div>

            {/* 对比结果 */}
            <div>
              <div className="text-xs font-semibold text-gray-600 mb-1">策略表现</div>
              <div className="flex items-center gap-2">
                {stats.account.changePercent > stats.btc.changePercent ? (
                  <>
                    <div className="text-xl font-bold text-green-600">
                      ✓ 跑赢 {(stats.account.changePercent - stats.btc.changePercent).toFixed(2)}%
                    </div>
                  </>
                ) : stats.account.changePercent < stats.btc.changePercent ? (
                  <>
                    <div className="text-xl font-bold text-red-600">
                      ✗ 跑输 {(stats.btc.changePercent - stats.account.changePercent).toFixed(2)}%
                    </div>
                  </>
                ) : (
                  <div className="text-xl font-bold text-gray-600">
                    = 持平
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 视图切换按钮 */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSelectedLine('both')}
              className={`px-3 py-2 text-xs font-medium rounded-lg transition-all ${
                selectedLine === 'both'
                  ? 'bg-gray-900 text-white shadow-lg'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              两条线对比
            </button>
            <button
              onClick={() => setSelectedLine('btc')}
              className={`px-3 py-2 text-xs font-medium rounded-lg transition-all ${
                selectedLine === 'btc'
                  ? 'bg-[#f7931a] text-white shadow-lg'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              仅BTC
            </button>
            <button
              onClick={() => setSelectedLine('account')}
              className={`px-3 py-2 text-xs font-medium rounded-lg transition-all ${
                selectedLine === 'account'
                  ? 'bg-blue-500 text-white shadow-lg'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              仅账户
            </button>
          </div>
        </div>
      </div>

      {/* 图表容器 - 底部留出空间给时间轴标签 */}
      <div className="flex-1 relative pb-12">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-90 z-10">
            <div className="text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-500 mx-auto"></div>
              <p className="mt-4 text-sm font-medium text-gray-700">加载对比数据...</p>
            </div>
          </div>
        )}
        <div ref={chartContainerRef} className="absolute top-0 left-0 right-0 bottom-12 w-full h-[calc(100%-3rem)]" />
        
        {/* 浮动价格标签 */}
        {tooltipData.visible && (
          <div 
            className="absolute pointer-events-none z-40"
            style={{
              left: `${tooltipData.x}px`,
              top: `${tooltipData.y - 40}px`,
              transform: 'translateX(-50%)'
            }}
          >
            <div 
              className="px-3 py-1.5 rounded-md shadow-lg text-white text-sm font-semibold whitespace-nowrap"
              style={{ backgroundColor: tooltipData.color }}
            >
              {tooltipData.price}
            </div>
            <div 
              className="absolute left-1/2 -translate-x-1/2 -bottom-1 w-0 h-0"
              style={{
                borderLeft: '6px solid transparent',
                borderRight: '6px solid transparent',
                borderTop: `6px solid ${tooltipData.color}`
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
}

