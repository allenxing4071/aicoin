'use client';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE } from '../../../lib/api';
import { formatBeijingTimeShort, formatBeijingDate } from '../../../lib/datetime';

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

interface DebatedReport {
  original_intelligence: IntelligenceReport;
  debate_result: {
    recommendation: string;
    confidence: number;
    rationale: string;
    bull_viewpoint?: string;
    bear_viewpoint?: string;
  };
  enhanced_sentiment: string;
  enhanced_confidence: number;
  is_debated: boolean;
}

export default function IntelligencePanel() {
  const [report, setReport] = useState<IntelligenceReport | null>(null);
  const [debatedReport, setDebatedReport] = useState<DebatedReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchDebatedIntelligence();
    // Auto-refresh every 30 minutes
    const interval = setInterval(fetchDebatedIntelligence, 30 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchDebatedIntelligence = async () => {
    try {
      // 优先获取辩论后的情报
      const response = await axios.get(`${API_BASE}/intelligence/debated-report`);
      if (response.data.success && response.data.data) {
        setDebatedReport(response.data.data);
        setReport(response.data.data.original_intelligence);
      } else {
        // 如果辩论报告不可用，降级到普通情报
        const fallbackResponse = await axios.get(`${API_BASE}/intelligence/latest`);
        if (fallbackResponse.data.success && fallbackResponse.data.data) {
          setReport(fallbackResponse.data.data);
        }
      }
    } catch (error) {
      console.error('Failed to fetch debated intelligence:', error);
      // 降级到普通情报
      try {
        const fallbackResponse = await axios.get(`${API_BASE}/intelligence/latest`);
        if (fallbackResponse.data.success && fallbackResponse.data.data) {
          setReport(fallbackResponse.data.data);
        }
      } catch (fallbackError) {
        console.error('Failed to fetch fallback intelligence:', fallbackError);
      }
    } finally {
      setLoading(false);
    }
  };

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
    NEUTRAL: '🟡',
    bullish: '🟢',  // 向后兼容小写
    bearish: '🔴',
    neutral: '🟡',
    '看涨': '🟢',
    '看跌': '🔴',
    '中性': '🟡'
  }[report.market_sentiment] || '⚪';

  const sentimentColor = {
    BULLISH: 'text-green-600',
    BEARISH: 'text-red-600',
    NEUTRAL: 'text-yellow-600',
    bullish: 'text-green-600',  // 向后兼容小写
    bearish: 'text-red-600',
    neutral: 'text-yellow-600',
    '看涨': 'text-green-600',
    '看跌': 'text-red-600',
    '中性': 'text-yellow-600'
  }[report.market_sentiment] || 'text-gray-600';

  const sentimentText = {
    BULLISH: '看涨',
    BEARISH: '看跌',
    NEUTRAL: '中性',
    bullish: '看涨',  // 向后兼容小写
    bearish: '看跌',
    neutral: '中性',
    '看涨': '看涨',
    '看跌': '看跌',
    '中性': '中性'
  }[report.market_sentiment] || report.market_sentiment;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-gradient-to-br from-indigo-50 to-purple-50 border border-indigo-200 rounded-xl shadow-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent flex items-center">
            🕵️‍♀️ Qwen情报中心
              {debatedReport?.is_debated && (
                <span className="ml-3 px-3 py-1 text-sm bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full">
                  ⚔️ 辩论增强版
                </span>
              )}
          </h2>
            {debatedReport?.is_debated && (
              <p className="text-sm text-gray-600 mt-1">经过多空辩论验证的高质量情报</p>
            )}
          </div>
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
              {sentimentEmoji} {sentimentText}
            </div>
            <div className="text-sm text-gray-500 mt-1">
              分数: {report.sentiment_score !== undefined ? (report.sentiment_score > 0 ? '+' : '') + report.sentiment_score.toFixed(2) : 'N/A'}
            </div>
          </div>

          <div className="bg-white rounded-xl p-4 shadow">
            <div className="text-sm text-gray-600 mb-1">置信度</div>
            <div className="text-2xl font-bold text-blue-600">
              {report.confidence !== undefined ? (report.confidence * 100).toFixed(0) : '0'}%
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
              {formatBeijingTimeShort(report.timestamp)}
            </div>
            <div className="text-sm text-gray-500 mt-1">
              {formatBeijingDate(report.timestamp)}
            </div>
          </div>
        </div>
      </div>

      {/* Debate Result - 紧跟头部信息，始终显示 */}
      <div className="bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-300 rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-4 flex items-center">
            ⚔️ 多空辩论后的综合判断
          </h3>
          
          {debatedReport?.is_debated && debatedReport.debate_result ? (
            <>
              {/* 研究经理推荐 */}
              <div className="bg-white rounded-xl p-6 mb-4 border-2 border-purple-200">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-lg font-bold text-gray-900">研究经理推荐</h4>
                  <span className={`px-4 py-2 rounded-full font-bold text-lg ${
                    debatedReport.debate_result.recommendation === 'BUY' ? 'bg-green-100 text-green-700' :
                    debatedReport.debate_result.recommendation === 'SELL' ? 'bg-red-100 text-red-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {debatedReport.debate_result.recommendation === 'BUY' ? '🟢 做多' :
                     debatedReport.debate_result.recommendation === 'SELL' ? '🔴 做空' :
                     '⚪ 观望'}
                  </span>
                </div>
                <div className="mb-3">
                  <div className="text-sm text-gray-600 mb-1">辩论后置信度</div>
                  <div className="flex items-center gap-3">
                    <div className="flex-1 bg-gray-200 rounded-full h-3">
                      <div
                        className={`h-3 rounded-full transition-all ${
                          debatedReport.debate_result.confidence >= 0.7 ? 'bg-green-500' :
                          debatedReport.debate_result.confidence >= 0.5 ? 'bg-yellow-500' :
                          'bg-red-500'
                        }`}
                        style={{ width: `${debatedReport.debate_result.confidence * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-lg font-bold text-gray-900">
                      {debatedReport.debate_result.confidence !== undefined ? (debatedReport.debate_result.confidence * 100).toFixed(0) : '0'}%
                    </span>
                  </div>
                </div>
                <div className="bg-purple-50 rounded-xl p-4 text-gray-700 leading-relaxed">
                  {debatedReport.debate_result.rationale}
                </div>
              </div>

              {/* 多头观点 */}
              {debatedReport.debate_result.bull_viewpoint && (
                <details className="bg-green-50 rounded-xl p-4 mb-3 border border-green-200">
                  <summary className="font-bold text-green-800 cursor-pointer hover:text-green-600">
                    🐂 多头分析师观点
                  </summary>
                  <div className="mt-3 text-gray-700 leading-relaxed">
                    {debatedReport.debate_result.bull_viewpoint}
                  </div>
                </details>
              )}

              {/* 空头观点 */}
              {debatedReport.debate_result.bear_viewpoint && (
                <details className="bg-red-50 rounded-xl p-4 border border-red-200">
                  <summary className="font-bold text-red-800 cursor-pointer hover:text-red-600">
                    🐻 空头分析师观点
                  </summary>
                  <div className="mt-3 text-gray-700 leading-relaxed">
                    {debatedReport.debate_result.bear_viewpoint}
                  </div>
                </details>
              )}
            </>
          ) : (
            /* 暂无辩论结果 */
            <div className="bg-white rounded-xl p-8 text-center border-2 border-purple-200">
              <div className="text-6xl mb-4">💭</div>
              <h4 className="text-xl font-bold text-gray-700 mb-2">暂未进行多空辩论</h4>
              <p className="text-gray-500 mb-4">
                多空辩论需要手动触发，将由AI分析师进行深度辩论分析
              </p>
              <a
                href="/admin/intelligence/realtime"
                className="inline-block px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all"
              >
                前往后台触发辩论 →
              </a>
            </div>
          )}
        </div>

      {/* Risk & Opportunities - 放在辩论结果后面 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Risks */}
        <div className="bg-gradient-to-br from-red-50 to-orange-50 border border-red-200 rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold bg-gradient-to-r from-red-600 to-orange-600 bg-clip-text text-transparent mb-4 flex items-center">
            ⚠️ 风险因素
          </h3>
          <ul className="space-y-2">
            {report.risk_factors && report.risk_factors.length > 0 ? (
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
            {report.opportunities && report.opportunities.length > 0 ? (
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

      {/* Key News */}
      <div className="bg-gradient-to-br from-blue-50 to-cyan-50 border border-blue-200 rounded-xl shadow-lg p-6">
        <h3 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent mb-4 flex items-center">
          📰 关键新闻
        </h3>
        <div className="space-y-3">
          {report.key_news && report.key_news.length > 0 ? (
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
                        <span>{formatBeijingTimeShort(news.published_at)}</span>
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
          {report.whale_signals && report.whale_signals.length > 0 ? (
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
                      {formatBeijingTimeShort(whale.timestamp)}
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
                <div className={`text-2xl font-bold ${(report.on_chain_metrics.exchange_net_flow ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {report.on_chain_metrics.exchange_net_flow !== undefined ? (
                    <>
                      {report.on_chain_metrics.exchange_net_flow >= 0 ? '+' : ''}{(report.on_chain_metrics.exchange_net_flow / 1000000).toFixed(2)}M
                    </>
                  ) : 'N/A'}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {(report.on_chain_metrics.exchange_net_flow ?? 0) >= 0 ? '资金流入' : '资金流出'}
                </div>
              </div>
            )}
            
            {report.on_chain_metrics.active_addresses !== undefined && (
              <div className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
                <div className="text-sm text-gray-600 mb-1">活跃地址数</div>
                <div className="text-2xl font-bold text-blue-600">
                  {report.on_chain_metrics.active_addresses !== undefined ? (report.on_chain_metrics.active_addresses / 1000).toFixed(1) : '0'}K
                </div>
                <div className="text-xs text-gray-500 mt-1">24小时</div>
              </div>
            )}
            
            {report.on_chain_metrics.gas_price !== undefined && (
              <div className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
                <div className="text-sm text-gray-600 mb-1">Gas价格</div>
                <div className="text-2xl font-bold text-purple-600">
                  {report.on_chain_metrics.gas_price !== undefined ? report.on_chain_metrics.gas_price.toFixed(0) : '0'}
                </div>
                <div className="text-xs text-gray-500 mt-1">Gwei</div>
              </div>
            )}
            
            {report.on_chain_metrics.transaction_volume !== undefined && (
              <div className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
                <div className="text-sm text-gray-600 mb-1">交易量</div>
                <div className="text-2xl font-bold text-orange-600">
                  ${report.on_chain_metrics.transaction_volume !== undefined ? (report.on_chain_metrics.transaction_volume / 1000000000).toFixed(2) : '0'}B
                </div>
                <div className="text-xs text-gray-500 mt-1">24小时</div>
              </div>
            )}
          </div>
        </div>
      )}

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

