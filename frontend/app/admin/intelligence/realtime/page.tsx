'use client';

/**
 * 实时情报页面
 * 
 * 路径: /admin/intelligence/realtime
 * 
 * 功能：
 * - 实时情报流
 * - AI分析结果
 * - 市场情绪
 * - 风险和机会
 */

import React, { useState, useEffect, useCallback } from 'react';
import PageHeader from '@/app/components/common/PageHeader';
import { unifiedDesignSystem, getThemeStyles } from '@/app/admin/unified-design-system';
import { StatCardGrid, StatCard } from '@/app/components/common/Cards';

interface IntelligenceReport {
  id: number;
  timestamp: string;
  market_sentiment: string;
  sentiment_score: number;
  confidence: number;
  key_news: any[];
  whale_signals: any[];
  on_chain_metrics: any;
  risk_factors: string[];
  opportunities: string[];
  qwen_analysis: string;
  created_at: string;
}

export default function RealtimeIntelligencePage() {
  const [reports, setReports] = useState<IntelligenceReport[]>([]);
  const [latestReport, setLatestReport] = useState<IntelligenceReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  
  // 使用统一的橙色主题
  const theme = getThemeStyles('orange');

  const fetchReports = useCallback(async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/v1/intelligence/reports?limit=20');
      const data = await res.json();
      
      if (data.success && data.data) {
        setReports(data.data);
        if (data.data.length > 0) {
          setLatestReport(data.data[0]);
        }
      }
    } catch (error) {
      console.error('Failed to fetch reports:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchReports();
    
    // 自动刷新
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(() => {
        fetchReports();
      }, 30000); // 每30秒刷新
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoRefresh]);

  const getSentimentColor = (sentiment: string) => {
    if (sentiment === 'BULLISH') return 'bg-green-100 text-green-800 border-green-500';
    if (sentiment === 'BEARISH') return 'bg-red-100 text-red-800 border-red-500';
    return 'bg-gray-100 text-gray-600 border-gray-500';
  };

  const getSentimentIcon = (sentiment: string) => {
    if (sentiment === 'BULLISH') return '🚀';
    if (sentiment === 'BEARISH') return '📉';
    return '➖';
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.7) return 'text-green-600';
    if (confidence >= 0.4) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading && reports.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        icon="⚡"
        title="实时情报"
        description="查看实时市场情报和AI分析结果"
        color="orange"
      />

      {/* 控制栏 */}
      <div className="bg-white rounded-xl shadow p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={fetchReports}
              disabled={loading}
              className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:bg-gray-400"
            >
              {loading ? '刷新中...' : '🔄 手动刷新'}
            </button>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="w-4 h-4"
              />
              <span className="text-sm text-gray-700">自动刷新 (30秒)</span>
            </label>
          </div>
          <div className="text-sm text-gray-500">
            最后更新: {latestReport ? new Date(latestReport.created_at).toLocaleString('zh-CN') : '未知'}
          </div>
        </div>
      </div>

      {/* 最新情报概览 */}
      {latestReport && (
        <div className={`bg-white rounded-xl shadow p-6 border-l-4 ${getSentimentColor(latestReport.market_sentiment).split(' ')[2]}`}>
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                {getSentimentIcon(latestReport.market_sentiment)} 最新市场情绪
              </h3>
              <div className="flex items-center gap-4">
                <span className={`px-4 py-2 rounded-lg font-semibold ${getSentimentColor(latestReport.market_sentiment)}`}>
                  {latestReport.market_sentiment}
                </span>
                <span className="text-sm text-gray-600">
                  情绪得分: <span className={`font-semibold ${getConfidenceColor(Math.abs(latestReport.sentiment_score))}`}>
                    {latestReport.sentiment_score.toFixed(2)}
                  </span>
                </span>
                <span className="text-sm text-gray-600">
                  置信度: <span className={`font-semibold ${getConfidenceColor(latestReport.confidence)}`}>
                    {(latestReport.confidence * 100).toFixed(0)}%
                  </span>
                </span>
              </div>
            </div>
            <span className="text-sm text-gray-500">
              {new Date(latestReport.timestamp).toLocaleString('zh-CN')}
            </span>
          </div>

          {/* AI分析 */}
          {latestReport.qwen_analysis && (
            <div className="bg-gray-50 rounded-lg p-4 mb-4">
              <h4 className="font-semibold text-gray-900 mb-2">🤖 AI分析</h4>
              <p className="text-sm text-gray-700 whitespace-pre-wrap">{latestReport.qwen_analysis}</p>
            </div>
          )}

          {/* 风险和机会 */}
          <div className="grid grid-cols-2 gap-4">
            {latestReport.risk_factors && latestReport.risk_factors.length > 0 && (
              <div>
                <h4 className="font-semibold text-red-600 mb-2">⚠️ 风险因素</h4>
                <ul className="space-y-1">
                  {latestReport.risk_factors.map((risk, idx) => (
                    <li key={idx} className="text-sm text-gray-700">• {risk}</li>
                  ))}
                </ul>
              </div>
            )}
            {latestReport.opportunities && latestReport.opportunities.length > 0 && (
              <div>
                <h4 className="font-semibold text-green-600 mb-2">💡 机会点</h4>
                <ul className="space-y-1">
                  {latestReport.opportunities.map((opp, idx) => (
                    <li key={idx} className="text-sm text-gray-700">• {opp}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* 数据来源统计 */}
          <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-gray-200">
            <div>
              <div className="text-xs text-gray-500">关键新闻</div>
              <div className="text-lg font-semibold text-blue-600">
                {latestReport.key_news ? latestReport.key_news.length : 0} 条
              </div>
            </div>
            <div>
              <div className="text-xs text-gray-500">巨鲸活动</div>
              <div className="text-lg font-semibold text-purple-600">
                {latestReport.whale_signals ? latestReport.whale_signals.length : 0} 次
              </div>
            </div>
            <div>
              <div className="text-xs text-gray-500">链上指标</div>
              <div className="text-lg font-semibold text-green-600">
                {latestReport.on_chain_metrics ? '✓ 已更新' : '✗ 未更新'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 历史情报流 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 情报时间线</h3>
        
        <div className="space-y-4">
          {reports.map((report) => (
            <div key={report.id} className="border-l-4 border-orange-500 pl-4 py-3 hover:bg-gray-50 transition-colors">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-3">
                  <span className={`px-3 py-1 text-xs rounded-full font-medium ${getSentimentColor(report.market_sentiment)}`}>
                    {getSentimentIcon(report.market_sentiment)} {report.market_sentiment}
                  </span>
                  <span className="text-sm text-gray-600">
                    置信度: <span className={`font-semibold ${getConfidenceColor(report.confidence)}`}>
                      {(report.confidence * 100).toFixed(0)}%
                    </span>
                  </span>
                </div>
                <span className="text-xs text-gray-500">
                  {new Date(report.timestamp).toLocaleString('zh-CN')}
                </span>
              </div>
              
              {report.qwen_analysis && (
                <p className="text-sm text-gray-700 line-clamp-2 mb-2">{report.qwen_analysis}</p>
              )}
              
              <div className="flex items-center gap-4 text-xs text-gray-500">
                <span>📰 {report.key_news ? report.key_news.length : 0} 新闻</span>
                <span>🐋 {report.whale_signals ? report.whale_signals.length : 0} 巨鲸</span>
                <span>⛓️ {report.on_chain_metrics ? '链上数据' : '无链上数据'}</span>
                {report.risk_factors && report.risk_factors.length > 0 && (
                  <span>⚠️ {report.risk_factors.length} 风险</span>
                )}
                {report.opportunities && report.opportunities.length > 0 && (
                  <span>💡 {report.opportunities.length} 机会</span>
                )}
              </div>
            </div>
          ))}
        </div>

        {reports.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <div className="text-4xl mb-2">⚡</div>
            <p>暂无情报数据</p>
            <p className="text-sm mt-2">情报系统将自动收集和分析市场数据</p>
          </div>
        )}
      </div>
    </div>
  );
}
