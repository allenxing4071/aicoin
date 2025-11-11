'use client';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE } from '../../../lib/api';

interface NewsItem {
  title: string;
  source: string;
  url: string;
  sentiment: string;
  published_at: string;
  impact: string;
}

interface WhaleActivity {
  symbol: string;
  action: string;
  amount_usd: number;
  timestamp: string;
  exchange: string | null;
}

interface OnChainMetrics {
  exchange_net_flow?: number;
  active_addresses?: number;
  gas_price?: number;
  transaction_volume?: number;
  timestamp?: string;
}

interface IntelligenceReport {
  timestamp: string;
  market_sentiment: string;
  sentiment_score: number;
  key_news: NewsItem[];
  whale_signals: WhaleActivity[];
  on_chain_metrics?: OnChainMetrics;
  risk_factors: string[];
  opportunities: string[];
  qwen_analysis: string;
  confidence: number;
}

export default function IntelligencePanel() {
  const [report, setReport] = useState<IntelligenceReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchLatestIntelligence();
    // Auto-refresh every 30 minutes
    const interval = setInterval(fetchLatestIntelligence, 30 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchLatestIntelligence = async () => {
    try {
      const response = await axios.get(`${API_BASE}/intelligence/latest`);
      if (response.data.success && response.data.data) {
        setReport(response.data.data);
      }
    } catch (error) {
      console.error('Failed to fetch intelligence:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const response = await axios.post(`${API_BASE}/intelligence/refresh`);
      if (response.data.success) {
        setReport(response.data.data);
      }
    } catch (error) {
      console.error('Failed to refresh intelligence:', error);
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="bg-gradient-to-br from-gray-50 to-gray-100 border border-gray-200 rounded-xl p-6 text-center">
        <p className="text-gray-600">暂无情报数据</p>
        <button
          onClick={handleRefresh}
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          立即收集情报
        </button>
      </div>
    );
  }

  const sentimentEmoji = {
    BULLISH: '🟢',
    BEARISH: '🔴',
    NEUTRAL: '🟡'
  }[report.market_sentiment] || '⚪';

  const sentimentColor = {
    BULLISH: 'text-green-600',
    BEARISH: 'text-red-600',
    NEUTRAL: 'text-yellow-600'
  }[report.market_sentiment] || 'text-gray-600';

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-gradient-to-br from-indigo-50 to-purple-50 border border-indigo-200 rounded-xl shadow-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent flex items-center">
            🕵️‍♀️ Qwen情报中心
          </h2>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="px-4 py-2 bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-lg hover:from-indigo-600 hover:to-purple-600 transition-all disabled:opacity-50"
          >
            {refreshing ? '刷新中...' : '🔄 刷新情报'}
          </button>
        </div>

        {/* Market Sentiment */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-xl p-4 shadow">
            <div className="text-sm text-gray-600 mb-1">市场情绪</div>
            <div className={`text-2xl font-bold ${sentimentColor} flex items-center`}>
              {sentimentEmoji} {report.market_sentiment}
            </div>
            <div className="text-sm text-gray-500 mt-1">
              分数: {report.sentiment_score > 0 ? '+' : ''}{report.sentiment_score.toFixed(2)}
            </div>
          </div>

          <div className="bg-white rounded-xl p-4 shadow">
            <div className="text-sm text-gray-600 mb-1">置信度</div>
            <div className="text-2xl font-bold text-blue-600">
              {(report.confidence * 100).toFixed(0)}%
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all"
                style={{ width: `${report.confidence * 100}%` }}
              ></div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-4 shadow">
            <div className="text-sm text-gray-600 mb-1">更新时间</div>
            <div className="text-lg font-semibold text-gray-800">
              {new Date(report.timestamp).toLocaleTimeString('zh-CN', {
                hour: '2-digit',
                minute: '2-digit'
              })}
            </div>
            <div className="text-sm text-gray-500 mt-1">
              {new Date(report.timestamp).toLocaleDateString('zh-CN')}
            </div>
          </div>
        </div>
      </div>

      {/* Key News */}
      <div className="bg-gradient-to-br from-blue-50 to-cyan-50 border border-blue-200 rounded-xl shadow-lg p-6">
        <h3 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent mb-4 flex items-center">
          📰 关键新闻
        </h3>
        <div className="space-y-3">
          {report.key_news.length > 0 ? (
            report.key_news.map((news, index) => {
              const sentimentIcon = {
                bullish: '📈',
                bearish: '📉',
                neutral: '➡️'
              }[news.sentiment] || '➡️';

              return (
                <div key={index} className="bg-white rounded-xl p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start">
                    <span className="text-2xl mr-3">{sentimentIcon}</span>
                    <div className="flex-1">
                      <a
                        href={news.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-semibold text-gray-800 hover:text-blue-600 transition-colors"
                      >
                        {news.title}
                      </a>
                      <div className="flex items-center gap-3 mt-2 text-sm text-gray-600">
                        <span className="font-medium">{news.source}</span>
                        <span className="px-2 py-1 bg-gray-50 rounded">{news.impact}</span>
                        <span>{new Date(news.published_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}</span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          ) : (
            <p className="text-gray-500 text-center py-4">暂无新闻数据</p>
          )}
        </div>
      </div>

      {/* Whale Activity */}
      <div className="bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 rounded-xl shadow-lg p-6">
        <h3 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-4 flex items-center">
          🐋 巨鲸活动
        </h3>
        <div className="space-y-3">
          {report.whale_signals.length > 0 ? (
            report.whale_signals.map((whale, index) => {
              const actionEmoji = {
                buy: '🟢',
                sell: '🔴',
                transfer: '🔄'
              }[whale.action] || '⚪';

              return (
                <div key={index} className="bg-white rounded-xl p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{actionEmoji}</span>
                      <div>
                        <div className="font-semibold text-gray-800">
                          {whale.symbol}: {whale.action.toUpperCase()}
                        </div>
                        <div className="text-sm text-gray-600">
                          ${whale.amount_usd.toLocaleString()}
                          {whale.exchange && ` • ${whale.exchange}`}
                        </div>
                      </div>
                    </div>
                    <div className="text-sm text-gray-500">
                      {new Date(whale.timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                </div>
              );
            })
          ) : (
            <p className="text-gray-500 text-center py-4">暂无巨鲸活动</p>
          )}
        </div>
      </div>

      {/* On-Chain Metrics */}
      {report.on_chain_metrics && Object.keys(report.on_chain_metrics).length > 0 && (
        <div className="bg-gradient-to-br from-cyan-50 to-teal-50 border border-cyan-200 rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold bg-gradient-to-r from-cyan-600 to-teal-600 bg-clip-text text-transparent mb-4 flex items-center">
            ⛓️ 链上指标
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {report.on_chain_metrics.exchange_net_flow !== undefined && (
              <div className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
                <div className="text-sm text-gray-600 mb-1">交易所净流入</div>
                <div className={`text-2xl font-bold ${report.on_chain_metrics.exchange_net_flow >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {report.on_chain_metrics.exchange_net_flow >= 0 ? '+' : ''}{(report.on_chain_metrics.exchange_net_flow / 1000000).toFixed(2)}M
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {report.on_chain_metrics.exchange_net_flow >= 0 ? '资金流入' : '资金流出'}
                </div>
              </div>
            )}
            
            {report.on_chain_metrics.active_addresses !== undefined && (
              <div className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
                <div className="text-sm text-gray-600 mb-1">活跃地址数</div>
                <div className="text-2xl font-bold text-blue-600">
                  {(report.on_chain_metrics.active_addresses / 1000).toFixed(1)}K
                </div>
                <div className="text-xs text-gray-500 mt-1">24小时</div>
              </div>
            )}
            
            {report.on_chain_metrics.gas_price !== undefined && (
              <div className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
                <div className="text-sm text-gray-600 mb-1">Gas价格</div>
                <div className="text-2xl font-bold text-purple-600">
                  {report.on_chain_metrics.gas_price.toFixed(0)}
                </div>
                <div className="text-xs text-gray-500 mt-1">Gwei</div>
              </div>
            )}
            
            {report.on_chain_metrics.transaction_volume !== undefined && (
              <div className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
                <div className="text-sm text-gray-600 mb-1">交易量</div>
                <div className="text-2xl font-bold text-orange-600">
                  ${(report.on_chain_metrics.transaction_volume / 1000000000).toFixed(2)}B
                </div>
                <div className="text-xs text-gray-500 mt-1">24小时</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Risk & Opportunities */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Risks */}
        <div className="bg-gradient-to-br from-red-50 to-orange-50 border border-red-200 rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold bg-gradient-to-r from-red-600 to-orange-600 bg-clip-text text-transparent mb-4 flex items-center">
            ⚠️ 风险因素
          </h3>
          <ul className="space-y-2">
            {report.risk_factors.length > 0 ? (
              report.risk_factors.map((risk, index) => (
                <li key={index} className="bg-white rounded-xl p-3 flex items-start">
                  <span className="text-red-500 mr-2">•</span>
                  <span className="text-gray-700">{risk}</span>
                </li>
              ))
            ) : (
              <p className="text-gray-500 text-center py-4">暂无风险提示</p>
            )}
          </ul>
        </div>

        {/* Opportunities */}
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent mb-4 flex items-center">
            ✨ 机会点
          </h3>
          <ul className="space-y-2">
            {report.opportunities.length > 0 ? (
              report.opportunities.map((opp, index) => (
                <li key={index} className="bg-white rounded-xl p-3 flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  <span className="text-gray-700">{opp}</span>
                </li>
              ))
            ) : (
              <p className="text-gray-500 text-center py-4">暂无机会提示</p>
            )}
          </ul>
        </div>
      </div>

      {/* Qwen Analysis */}
      {report.qwen_analysis && (
        <div className="bg-gradient-to-br from-gray-50 to-slate-50 border border-gray-200 rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold bg-gradient-to-r from-gray-700 to-slate-700 bg-clip-text text-transparent mb-4 flex items-center">
            📝 Qwen综合分析
          </h3>
          <div className="bg-white rounded-xl p-4 text-gray-700 leading-relaxed">
            {report.qwen_analysis}
          </div>
        </div>
      )}
    </div>
  );
}

