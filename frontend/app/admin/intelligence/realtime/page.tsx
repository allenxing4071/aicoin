'use client';

/**
 * 实时情报页面 - 增强版（包含辩论系统）
 * 
 * 路径: /admin/intelligence/realtime
 * 
 * 功能：
 * - 实时情报流
 * - AI分析结果
 * - 市场情绪
 * - 多空辩论验证
 * - 风险和机会
 */

import React, { useState, useEffect, useCallback } from 'react';
import PageHeader from '@/app/components/common/PageHeader';
import { getThemeStyles } from '@/app/admin/unified-design-system';

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
  platform_contributions?: any;
  platform_consensus?: number;
  verification_metadata?: any;
  summary?: string;
}

interface DebatedReport {
  original_intelligence: any;
  debate_result: {
    recommendation: string;
    confidence: number;
    reasoning: string;
    bull_argument: string[];
    bear_argument: string[];
    consensus_level: number;
    total_rounds: number;
    duration_seconds: number;
  };
  enhanced_sentiment: string;
  enhanced_confidence: number;
  is_debated: boolean;
}

export default function RealtimeIntelligencePage() {
  const [reports, setReports] = useState<IntelligenceReport[]>([]);
  const [latestReport, setLatestReport] = useState<IntelligenceReport | null>(null);
  const [debatedReport, setDebatedReport] = useState<DebatedReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [debating, setDebating] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [showDebateDetails, setShowDebateDetails] = useState(false);
  
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

  const fetchDebatedReport = useCallback(async () => {
    try {
      setDebating(true);
      const res = await fetch('/api/v1/intelligence/debated-report');
      const data = await res.json();
      
      if (data.success && data.data) {
        setDebatedReport(data.data);
        setShowDebateDetails(true);
      }
    } catch (error) {
      console.error('Failed to fetch debated report:', error);
      alert('获取辩论报告失败，请查看控制台日志');
    } finally {
      setDebating(false);
    }
  }, []);

  const triggerDebate = useCallback(async () => {
    if (!confirm('启动多空辩论将消耗 API 额度，是否继续？')) {
      return;
    }
    
    try {
      setDebating(true);
      const res = await fetch('/api/v1/intelligence/trigger-debate', {
        method: 'POST'
      });
      const data = await res.json();
      
      if (data.success && data.data) {
        setDebatedReport(data.data);
        setShowDebateDetails(true);
        alert('✅ 辩论完成！');
      }
    } catch (error) {
      console.error('Failed to trigger debate:', error);
      alert('启动辩论失败，请查看控制台日志');
    } finally {
      setDebating(false);
    }
  }, []);

  useEffect(() => {
    fetchReports();
    fetchDebatedReport(); // 自动加载辩论后的报告
    
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(() => {
        fetchReports();
      }, 30000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, fetchReports, fetchDebatedReport]);

  const getSentimentColor = (sentiment: string) => {
    if (sentiment === 'BULLISH' || sentiment === 'BUY') return 'bg-green-100 text-green-800 border-green-500';
    if (sentiment === 'BEARISH' || sentiment === 'SELL') return 'bg-red-100 text-red-800 border-red-500';
    return 'bg-gray-100 text-gray-600 border-gray-500';
  };

  const getSentimentIcon = (sentiment: string) => {
    if (sentiment === 'BULLISH' || sentiment === 'BUY') return '🚀';
    if (sentiment === 'BEARISH' || sentiment === 'SELL') return '📉';
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
        title="Qwen情报中心（辩论增强版）"
        description="经过多空辩论验证的高质量情报"
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
              {loading ? '刷新中...' : '🔄 刷新情报'}
            </button>
            <button
              onClick={triggerDebate}
              disabled={debating}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 font-semibold"
            >
              {debating ? '辩论中...' : '⚔️ 启动辩论'}
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

      {/* 辩论后的综合分析 */}
      {debatedReport && (
        <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl shadow-lg p-6 border-2 border-purple-300">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-2xl font-bold text-purple-900 flex items-center gap-2">
              ⚔️ 多空辩论综合判断
              <span className="text-sm bg-purple-200 text-purple-800 px-3 py-1 rounded-full">
                已验证
              </span>
            </h3>
            <button
              onClick={() => setShowDebateDetails(!showDebateDetails)}
              className="text-sm text-purple-600 hover:text-purple-800 font-medium"
            >
              {showDebateDetails ? '收起详情 ▲' : '展开详情 ▼'}
            </button>
          </div>

          {/* 综合判断 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-white rounded-lg p-4 shadow">
              <div className="text-sm text-gray-600 mb-1">研究经理推荐</div>
              <div className={`text-2xl font-bold ${getSentimentColor(debatedReport.debate_result.recommendation).split(' ')[1]}`}>
                {getSentimentIcon(debatedReport.debate_result.recommendation)} {debatedReport.debate_result.recommendation}
              </div>
            </div>
            <div className="bg-white rounded-lg p-4 shadow">
              <div className="text-sm text-gray-600 mb-1">辩论后置信度</div>
              <div className={`text-2xl font-bold ${getConfidenceColor(debatedReport.debate_result.confidence)}`}>
                {(debatedReport.debate_result.confidence * 100).toFixed(0)}%
              </div>
              <div className="text-xs text-gray-500 mt-1">
                原始: {(debatedReport.original_intelligence.confidence * 100).toFixed(0)}% 
                → 提升 {((debatedReport.debate_result.confidence - debatedReport.original_intelligence.confidence) * 100).toFixed(0)}%
              </div>
            </div>
            <div className="bg-white rounded-lg p-4 shadow">
              <div className="text-sm text-gray-600 mb-1">多空共识度</div>
              <div className={`text-2xl font-bold ${getConfidenceColor(debatedReport.debate_result.consensus_level)}`}>
                {(debatedReport.debate_result.consensus_level * 100).toFixed(0)}%
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {debatedReport.debate_result.total_rounds} 轮辩论 · {debatedReport.debate_result.duration_seconds}秒
              </div>
            </div>
          </div>

          {/* 研究经理分析 */}
          <div className="bg-white rounded-lg p-4 shadow mb-4">
            <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
              <span className="text-xl">👔</span> 研究经理综合分析
            </h4>
            <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
              {debatedReport.debate_result.reasoning}
            </p>
          </div>

          {/* 辩论详情（可折叠） */}
          {showDebateDetails && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* 多头观点 */}
              <div className="bg-green-50 rounded-lg p-4 border-2 border-green-200">
                <h4 className="font-semibold text-green-900 mb-3 flex items-center gap-2">
                  <span className="text-xl">🐂</span> 多头分析师观点
                </h4>
                <div className="space-y-2">
                  {debatedReport.debate_result.bull_argument.map((arg, idx) => (
                    <div key={idx} className="bg-white rounded p-3 text-sm text-gray-700">
                      {arg}
                    </div>
                  ))}
                </div>
              </div>

              {/* 空头观点 */}
              <div className="bg-red-50 rounded-lg p-4 border-2 border-red-200">
                <h4 className="font-semibold text-red-900 mb-3 flex items-center gap-2">
                  <span className="text-xl">🐻</span> 空头分析师观点
                </h4>
                <div className="space-y-2">
                  {debatedReport.debate_result.bear_argument.map((arg, idx) => (
                    <div key={idx} className="bg-white rounded p-3 text-sm text-gray-700">
                      {arg}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 原始 Qwen 情报 */}
      {latestReport && (
        <div className={`bg-white rounded-xl shadow p-6 border-l-4 ${getSentimentColor(latestReport.market_sentiment).split(' ')[2]}`}>
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-2 flex items-center gap-2">
                {getSentimentIcon(latestReport.market_sentiment)} Qwen 原始情报
                <span className="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded">
                  未经辩论
                </span>
              </h3>
              <div className="flex items-center gap-4 flex-wrap">
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
