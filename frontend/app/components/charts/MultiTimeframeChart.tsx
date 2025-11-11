'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import LightweightChart from './LightweightChart';

const API_BASE = '/api/v1';

interface MultiTimeframeChartProps {
  symbol: string;
  marketType?: string;
}

export default function MultiTimeframeChart({ symbol, marketType = 'spot' }: MultiTimeframeChartProps) {
  const [selectedInterval, setSelectedInterval] = useState('1h');
  const [multiKlines, setMultiKlines] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [summaries, setSummaries] = useState<any>({});

  const intervals = ['1m', '5m', '15m', '1h', '4h', '1d'];

  useEffect(() => {
    fetchMultiTimeframeData();
    const interval = setInterval(fetchMultiTimeframeData, 60000); // 每分钟刷新
    return () => clearInterval(interval);
  }, [symbol, marketType]);

  const fetchMultiTimeframeData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get(
        `${API_BASE}/market/klines/multi/${symbol}?market_type=${marketType}&intervals=${intervals.join(',')}`
      );
      
      if (response.data.success) {
        setMultiKlines(response.data.data.klines);
        setSummaries(response.data.data.summaries || {});
      }
    } catch (err: any) {
      console.error('获取多周期K线失败:', err);
      setError(err.response?.data?.detail || '获取数据失败');
    } finally {
      setLoading(false);
    }
  };

  if (loading && Object.keys(multiKlines).length === 0) {
    return (
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="h-96 bg-gray-700 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/20 backdrop-blur-sm rounded-lg p-6 border border-red-700">
        <div className="flex items-center gap-2 text-red-400">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{error}</span>
        </div>
      </div>
    );
  }

  const currentKlines = multiKlines[selectedInterval] || [];
  const currentSummary = summaries[selectedInterval] || {};

  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
      {/* 标题和周期选择器 */}
      <div className="flex flex-wrap items-center justify-between mb-4 gap-4">
        <div>
          <h3 className="text-lg font-bold text-white mb-1">
            多周期K线分析 - {symbol}
          </h3>
          <p className="text-sm text-gray-400">
            {marketType === 'spot' ? '现货' : marketType === 'futures' ? '合约' : '永续'}
          </p>
        </div>

        {/* 周期切换按钮 */}
        <div className="flex gap-2">
          {intervals.map((interval) => (
            <button
              key={interval}
              onClick={() => setSelectedInterval(interval)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                selectedInterval === interval
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {interval}
            </button>
          ))}
        </div>

        {/* 刷新按钮 */}
        <button
          onClick={fetchMultiTimeframeData}
          disabled={loading}
          className="p-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors disabled:opacity-50"
          title="刷新数据"
        >
          <svg className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>

      {/* K线摘要信息 */}
      {currentSummary.current_price && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4 text-sm">
          <div className="bg-gray-700/50 p-3 rounded-lg">
            <div className="text-gray-400 mb-1">当前价格</div>
            <div className="text-white font-mono font-bold">
              ${currentSummary.current_price.toFixed(2)}
            </div>
          </div>
          
          <div className="bg-gray-700/50 p-3 rounded-lg">
            <div className="text-gray-400 mb-1">涨跌幅</div>
            <div className={`font-mono font-bold ${
              currentSummary.price_change_pct >= 0 ? 'text-green-400' : 'text-red-400'
            }`}>
              {currentSummary.price_change_pct >= 0 ? '+' : ''}
              {currentSummary.price_change_pct?.toFixed(2)}%
            </div>
          </div>
          
          <div className="bg-gray-700/50 p-3 rounded-lg">
            <div className="text-gray-400 mb-1">最高</div>
            <div className="text-white font-mono">
              ${currentSummary.highest?.toFixed(2)}
            </div>
          </div>
          
          <div className="bg-gray-700/50 p-3 rounded-lg">
            <div className="text-gray-400 mb-1">最低</div>
            <div className="text-white font-mono">
              ${currentSummary.lowest?.toFixed(2)}
            </div>
          </div>
          
          <div className="bg-gray-700/50 p-3 rounded-lg">
            <div className="text-gray-400 mb-1">数据点</div>
            <div className="text-white font-mono">
              {currentSummary.count || 0}
            </div>
          </div>
        </div>
      )}

      {/* K线图表 */}
      <div className="bg-gray-900 rounded-lg p-4">
        {currentKlines.length > 0 ? (
          <LightweightChart 
            symbol={`${symbol}-${marketType.toUpperCase()}`} 
            data={currentKlines.map((k: any) => ({
              time: k.timestamp,
              open: k.open,
              high: k.high,
              low: k.low,
              close: k.close,
              volume: k.volume
            }))}
          />
        ) : (
          <div className="h-96 flex items-center justify-center text-gray-500">
            暂无{selectedInterval}周期数据
          </div>
        )}
      </div>

      {/* 所有周期的小缩略图 */}
      <div className="grid grid-cols-3 md:grid-cols-6 gap-2 mt-4">
        {intervals.map((interval) => {
          const summary = summaries[interval] || {};
          const hasData = multiKlines[interval]?.length > 0;
          
          return (
            <button
              key={interval}
              onClick={() => setSelectedInterval(interval)}
              className={`p-2 rounded-lg border transition-all ${
                selectedInterval === interval
                  ? 'border-blue-500 bg-blue-900/30'
                  : 'border-gray-700 bg-gray-800/30 hover:border-gray-600'
              }`}
            >
              <div className="text-xs text-gray-400 mb-1">{interval}</div>
              {hasData ? (
                <>
                  <div className="text-sm font-mono text-white">
                    ${summary.current_price?.toFixed(2) || '-'}
                  </div>
                  <div className={`text-xs font-mono ${
                    (summary.price_change_pct || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {(summary.price_change_pct || 0) >= 0 ? '+' : ''}
                    {summary.price_change_pct?.toFixed(2)}%
                  </div>
                </>
              ) : (
                <div className="text-xs text-gray-600">无数据</div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

