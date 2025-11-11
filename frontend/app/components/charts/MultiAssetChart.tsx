'use client';

import { useEffect, useRef, useState } from 'react';
import { createChart, IChartApi, ISeriesApi, LineStyle, CrosshairMode } from 'lightweight-charts';
import axios from 'axios';

interface Asset {
  symbol: string;
  name: string;
  color: string;
  enabled: boolean;
}

interface MultiAssetChartProps {
  assets: Asset[];
}

interface PriceDataPoint {
  time: number;
  value: number;
}

const DEFAULT_ASSETS: Asset[] = [
  { symbol: 'BTCUSDT', name: 'BTC', color: '#f7931a', enabled: true },
  { symbol: 'ETHUSDT', name: 'ETH', color: '#627eea', enabled: true },
  { symbol: 'SOLUSDT', name: 'SOL', color: '#00d4aa', enabled: true },
  { symbol: 'XRPUSDT', name: 'XRP', color: '#23292f', enabled: false },
  { symbol: 'DOGEUSDT', name: 'DOGE', color: '#c2a633', enabled: false },
  { symbol: 'BNBUSDT', name: 'BNB', color: '#f3ba2f', enabled: false },
];

export default function MultiAssetChart({ assets = DEFAULT_ASSETS }: MultiAssetChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRefs = useRef<Map<string, ISeriesApi<'Line'>>>(new Map());
  
  const [loading, setLoading] = useState(true);
  const [assetStates, setAssetStates] = useState<Asset[]>(assets);
  const [selectedAsset, setSelectedAsset] = useState<string | null>(null);
  const [priceData, setPriceData] = useState<Map<string, PriceDataPoint[]>>(new Map());
  const [hoveredPrice, setHoveredPrice] = useState<Map<string, number>>(new Map());
  // 浮动价格标签
  const [tooltipData, setTooltipData] = useState<{ visible: boolean; x: number; y: number; price: string; color: string; assetName: string }>({
    visible: false,
    x: 0,
    y: 0,
    price: '',
    color: '#f7931a',
    assetName: ''
  });
  // 存储真实价格映射（时间戳 -> 真实价格）
  const priceMapRef = useRef<Map<string, Map<number, number>>>(new Map());
  // 存储最新的资产状态（用于事件监听器）
  const assetStatesRef = useRef<Asset[]>(assets);
  const selectedAssetRef = useRef<string | null>(null);

  // 同步assetStates和selectedAsset到ref
  useEffect(() => {
    assetStatesRef.current = assetStates;
  }, [assetStates]);

  useEffect(() => {
    selectedAssetRef.current = selectedAsset;
  }, [selectedAsset]);

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
          visible: false, // 隐藏横线
        },
      },
      rightPriceScale: {
        borderColor: 'rgba(197, 203, 206, 0.8)',
        scaleMargins: {
          top: 0.05,
          bottom: 0.05,
        },
        mode: 2, // 百分比模式，便于对比多个资产
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

    // 为每个资产创建价格线
    assetStates.forEach((asset) => {
      const series = chart.addLineSeries({
        color: asset.color,
        lineWidth: 2,
        crosshairMarkerVisible: true,
        crosshairMarkerRadius: 6,
        crosshairMarkerBorderColor: asset.color,
        crosshairMarkerBackgroundColor: '#ffffff',
        lastValueVisible: true,
        priceLineVisible: false,
        visible: asset.enabled,
      });
      seriesRefs.current.set(asset.symbol, series);
    });

    // 加载所有资产数据
    loadAllAssets();

    // 十字光标移动事件 - 显示浮动价格标签
    chart.subscribeCrosshairMove((param) => {
      if (!param.point || !param.time || !chartContainerRef.current) {
        setTooltipData({ visible: false, x: 0, y: 0, price: '', color: '#f7931a', assetName: '' });
        return;
      }

      const timestamp = typeof param.time === 'number' ? param.time : (param.time as any).timestamp;
      
      // 查找鼠标最接近的K线（根据Y坐标距离）
      let closestAsset: Asset | null = null;
      let closestPrice: number | null = null;
      let minDistance = Infinity;
      
      for (const asset of assetStatesRef.current) {
        if (!asset.enabled && !selectedAssetRef.current) continue;
        if (selectedAssetRef.current && asset.symbol !== selectedAssetRef.current) continue;
        
        const series = seriesRefs.current.get(asset.symbol);
        const seriesData = series ? param.seriesData.get(series) : null;
        
        if (seriesData) {
          const assetPriceMap = priceMapRef.current.get(asset.symbol);
          if (assetPriceMap) {
            const realPrice = assetPriceMap.get(timestamp);
            // 简化逻辑：如果该系列有数据，就显示该系列的价格
            // lightweight-charts的圆圈标记已经指示了鼠标最接近的线
            if (realPrice) {
              closestAsset = asset;
              closestPrice = realPrice;
              break; // 找到有数据的系列就显示
            }
          }
        }
      }
      
      if (closestAsset && closestPrice !== null) {
        setTooltipData({
          visible: true,
          x: param.point.x,
          y: param.point.y,
          price: `$${closestPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
          color: closestAsset.color,
          assetName: closestAsset.name
        });
      } else {
        setTooltipData({ visible: false, x: 0, y: 0, price: '', color: '#f7931a', assetName: '' });
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
  }, []);

  // 当资产状态改变时，更新系列可见性
  useEffect(() => {
    assetStates.forEach((asset) => {
      const series = seriesRefs.current.get(asset.symbol);
      if (series) {
        // 如果有选中的资产，只显示选中的
        if (selectedAsset) {
          series.applyOptions({
            visible: asset.symbol === selectedAsset,
            lineWidth: asset.symbol === selectedAsset ? 3 : 2,
          });
        } else {
          // 否则根据enabled状态显示
          series.applyOptions({
            visible: asset.enabled,
            lineWidth: 2,
          });
        }
      }
    });
  }, [assetStates, selectedAsset]);

  const loadAllAssets = async () => {
    try {
      setLoading(true);
      const newPriceData = new Map<string, PriceDataPoint[]>();

      // 并行加载所有资产数据
      await Promise.all(
        assetStates.map(async (asset) => {
          try {
            const response = await axios.get(
              `/api/v1/market/klines/multi/${asset.symbol}?intervals=1h`
            );

            if (response.data.success && response.data.data.klines['1h']) {
              const klines = response.data.data.klines['1h'];
              
              // 转换为价格线数据（标准化处理）
              const firstPrice = parseFloat(klines[0].close);
              const assetPriceMap = new Map<number, number>();
              const lineData = klines.map((k: any) => {
                const price = parseFloat(k.close);
                const timestamp = k.timestamp;
                assetPriceMap.set(timestamp, price); // 存储真实价格映射
                // 标准化：第一个价格点为基准100，其他按比例显示
                const normalizedValue = (price / firstPrice) * 100;
                return {
                  time: timestamp as any,
                  value: normalizedValue,
                };
              });

              // 保存价格映射
              priceMapRef.current.set(asset.symbol, assetPriceMap);

              const series = seriesRefs.current.get(asset.symbol);
              if (series) {
                series.setData(lineData);
              }

              // 保存原始价格数据
              const originalData = klines.map((k: any) => ({
                time: k.timestamp,
                value: parseFloat(k.close),
              }));
              newPriceData.set(asset.symbol, originalData);
            }
          } catch (error) {
            console.error(`Failed to load ${asset.symbol}:`, error);
          }
        })
      );

      setPriceData(newPriceData);
      
      // 自动调整视图
      if (chartRef.current) {
        chartRef.current.timeScale().fitContent();
      }

      setLoading(false);
    } catch (error) {
      console.error('Failed to load asset data:', error);
      setLoading(false);
    }
  };

  const toggleAsset = (symbol: string) => {
    if (selectedAsset === symbol) {
      // 如果点击的是已选中的资产，取消选中
      setSelectedAsset(null);
    } else {
      // 选中新资产
      setSelectedAsset(symbol);
    }
  };

  const enableAsset = (symbol: string) => {
    setAssetStates((prev) =>
      prev.map((asset) =>
        asset.symbol === symbol ? { ...asset, enabled: !asset.enabled } : asset
      )
    );
  };

  // 计算统计数据
  const getAssetStats = (symbol: string) => {
    const data = priceData.get(symbol);
    if (!data || data.length === 0) {
      return { current: 0, change: 0, changePercent: 0 };
    }

    const current = data[data.length - 1].value;
    const first = data[0].value;
    const change = current - first;
    const changePercent = (change / first) * 100;

    return { current, change, changePercent };
  };

  return (
    <div className="w-full h-full flex flex-col">
      {/* 资产选择器 */}
      <div className="mb-4 px-4 py-3 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-gray-700">资产对比</h3>
          {selectedAsset && (
            <button
              onClick={() => setSelectedAsset(null)}
              className="text-xs text-blue-600 hover:text-blue-800 font-medium"
            >
              ← 返回多资产视图
            </button>
          )}
        </div>
        
        <div className="flex flex-wrap gap-2">
          {assetStates.map((asset) => {
            const stats = getAssetStats(asset.symbol);
            const isSelected = selectedAsset === asset.symbol;
            const isActive = !selectedAsset && asset.enabled;
            
            return (
              <div
                key={asset.symbol}
                className={`flex items-center px-4 py-2 rounded-lg border-2 transition-all cursor-pointer ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50'
                    : isActive
                    ? 'border-gray-300 bg-white hover:border-gray-400'
                    : 'border-gray-200 bg-gray-100 opacity-60 hover:opacity-100'
                }`}
                onClick={() => toggleAsset(asset.symbol)}
              >
                {/* 颜色指示器 */}
                <div
                  className="w-3 h-3 rounded-full mr-2"
                  style={{ backgroundColor: asset.color }}
                ></div>
                
                {/* 资产信息 */}
                <div className="flex flex-col">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-gray-900">{asset.name}</span>
                    {stats.current > 0 && (
                      <span
                        className={`text-xs font-semibold ${
                          stats.changePercent >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}
                      >
                        {stats.changePercent >= 0 ? '+' : ''}
                        {stats.changePercent.toFixed(2)}%
                      </span>
                    )}
                  </div>
                  {stats.current > 0 && (
                    <span className="text-xs text-gray-600">
                      ${stats.current.toLocaleString('en-US', { 
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2 
                      })}
                    </span>
                  )}
                </div>

                {/* 启用/禁用按钮 */}
                {!selectedAsset && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      enableAsset(asset.symbol);
                    }}
                    className={`ml-3 w-5 h-5 rounded border-2 flex items-center justify-center ${
                      asset.enabled
                        ? 'border-blue-500 bg-blue-500'
                        : 'border-gray-300 bg-white'
                    }`}
                  >
                    {asset.enabled && (
                      <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                      </svg>
                    )}
                  </button>
                )}
              </div>
            );
          })}
        </div>

        <div className="mt-3 text-xs text-gray-500">
          {selectedAsset 
            ? '💡 点击资产卡片返回多资产对比视图'
            : '💡 点击资产名称查看单独详情，勾选框启用/禁用显示'
          }
        </div>
      </div>

      {/* 图表容器 */}
      <div className="flex-1 relative pb-12">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-90 z-10">
            <div className="text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-500 mx-auto"></div>
              <p className="mt-4 text-sm font-medium text-gray-700">加载图表数据...</p>
              <p className="mt-1 text-xs text-gray-500">正在获取{assetStates.length}个资产的历史价格</p>
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
              {tooltipData.assetName}: {tooltipData.price}
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

