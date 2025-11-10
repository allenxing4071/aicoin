'use client';

/**
 * 历史报告页面
 * 
 * 路径: /admin/intelligence/reports
 * 
 * 功能：
 * - 报告列表查询
 * - 报告详情查看
 * - 搜索和筛选
 * - 数据导出
 */

import React, { useState, useEffect } from 'react';
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

export default function IntelligenceReportsPage() {
  const [reports, setReports] = useState<IntelligenceReport[]>([]);
  const [filteredReports, setFilteredReports] = useState<IntelligenceReport[]>([]);
  const [selectedReport, setSelectedReport] = useState<IntelligenceReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [filterSentiment, setFilterSentiment] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  
  // 使用统一的橙色主题
  const theme = getThemeStyles('orange');

  useEffect(() => {
    fetchReports();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [reports, filterSentiment, searchQuery, dateRange]);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const res = await fetch('http://localhost:8000/api/v1/intelligence/reports?limit=100');
      const data = await res.json();
      
      if (data.success && data.data) {
        setReports(data.data);
      }
    } catch (error) {
      console.error('Failed to fetch reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...reports];

    // 情绪筛选
    if (filterSentiment !== 'all') {
      filtered = filtered.filter(r => r.market_sentiment === filterSentiment);
    }

    // 搜索筛选
    if (searchQuery) {
      filtered = filtered.filter(r =>
        r.qwen_analysis?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.risk_factors?.some(f => f.toLowerCase().includes(searchQuery.toLowerCase())) ||
        r.opportunities?.some(o => o.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    // 日期范围筛选
    if (dateRange.start) {
      filtered = filtered.filter(r => new Date(r.timestamp) >= new Date(dateRange.start));
    }
    if (dateRange.end) {
      filtered = filtered.filter(r => new Date(r.timestamp) <= new Date(dateRange.end));
    }

    setFilteredReports(filtered);
  };

  const getSentimentColor = (sentiment: string) => {
    if (sentiment === 'BULLISH') return 'bg-green-100 text-green-800';
    if (sentiment === 'BEARISH') return 'bg-red-100 text-red-800';
    return 'bg-gray-100 text-gray-600';
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

  const exportToJSON = () => {
    const dataStr = JSON.stringify(filteredReports, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `intelligence_reports_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        icon="📊"
        title="历史报告"
        description="查看和分析历史情报报告"
        color="blue"
      />

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 shadow-lg border-2 border-blue-300">
          <div className="text-sm text-gray-500 mb-1">总报告数</div>
          <div className="text-3xl font-bold text-blue-600">{reports.length}</div>
        </div>
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 shadow-lg border-2 border-green-300">
          <div className="text-sm text-gray-500 mb-1">看涨报告</div>
          <div className="text-3xl font-bold text-green-600">
            {reports.filter(r => r.market_sentiment === 'BULLISH').length}
          </div>
        </div>
        <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-xl p-6 shadow-lg border-2 border-red-300">
          <div className="text-sm text-gray-500 mb-1">看跌报告</div>
          <div className="text-3xl font-bold text-red-600">
            {reports.filter(r => r.market_sentiment === 'BEARISH').length}
          </div>
        </div>
        <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-6 shadow-lg border-2 border-gray-300">
          <div className="text-sm text-gray-500 mb-1">中性报告</div>
          <div className="text-3xl font-bold text-gray-600">
            {reports.filter(r => r.market_sentiment === 'NEUTRAL').length}
          </div>
        </div>
      </div>

      {/* 筛选和搜索 */}
      <div className="bg-white rounded-xl shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">市场情绪</label>
            <select
              value={filterSentiment}
              onChange={(e) => setFilterSentiment(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">全部</option>
              <option value="BULLISH">看涨</option>
              <option value="BEARISH">看跌</option>
              <option value="NEUTRAL">中性</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">开始日期</label>
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">结束日期</label>
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">搜索关键词</label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索报告内容..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
          <div className="text-sm text-gray-600">
            找到 <span className="font-semibold text-blue-600">{filteredReports.length}</span> 条报告
          </div>
          <button
            onClick={exportToJSON}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            📥 导出JSON
          </button>
        </div>
      </div>

      {/* 报告列表 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📋 报告列表</h3>
        
        <div className="space-y-3">
          {filteredReports.map((report) => (
            <div
              key={report.id}
              className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors"
              onClick={() => setSelectedReport(report)}
            >
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
                  <span className="text-sm text-gray-600">
                    情绪: <span className={`font-semibold ${getConfidenceColor(Math.abs(report.sentiment_score))}`}>
                      {report.sentiment_score.toFixed(2)}
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
                <span>⛓️ {report.on_chain_metrics ? '链上数据' : '无'}</span>
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

        {filteredReports.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <div className="text-4xl mb-2">📊</div>
            <p>未找到匹配的报告</p>
            <p className="text-sm mt-2">尝试调整筛选条件</p>
          </div>
        )}
      </div>

      {/* 报告详情模态框 */}
      {selectedReport && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 p-6">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">情报报告详情</h3>
                  <div className="flex items-center gap-3">
                    <span className={`px-3 py-1 text-sm rounded-full font-medium ${getSentimentColor(selectedReport.market_sentiment)}`}>
                      {getSentimentIcon(selectedReport.market_sentiment)} {selectedReport.market_sentiment}
                    </span>
                    <span className="text-sm text-gray-600">
                      {new Date(selectedReport.timestamp).toLocaleString('zh-CN')}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedReport(null)}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  ×
                </button>
              </div>
            </div>

            <div className="p-6 space-y-6">
              {/* 基本信息 */}
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-500 mb-1">情绪得分</div>
                  <div className={`text-2xl font-bold ${getConfidenceColor(Math.abs(selectedReport.sentiment_score))}`}>
                    {selectedReport.sentiment_score.toFixed(2)}
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-500 mb-1">置信度</div>
                  <div className={`text-2xl font-bold ${getConfidenceColor(selectedReport.confidence)}`}>
                    {(selectedReport.confidence * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-500 mb-1">报告ID</div>
                  <div className="text-2xl font-bold text-gray-900">#{selectedReport.id}</div>
                </div>
              </div>

              {/* AI分析 */}
              {selectedReport.qwen_analysis && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">🤖 AI综合分析</h4>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-700 whitespace-pre-wrap">{selectedReport.qwen_analysis}</p>
                  </div>
                </div>
              )}

              {/* 风险和机会 */}
              <div className="grid grid-cols-2 gap-4">
                {selectedReport.risk_factors && selectedReport.risk_factors.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-red-600 mb-2">⚠️ 风险因素</h4>
                    <ul className="space-y-2">
                      {selectedReport.risk_factors.map((risk, idx) => (
                        <li key={idx} className="text-sm text-gray-700 bg-red-50 rounded p-2">• {risk}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {selectedReport.opportunities && selectedReport.opportunities.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-green-600 mb-2">💡 机会点</h4>
                    <ul className="space-y-2">
                      {selectedReport.opportunities.map((opp, idx) => (
                        <li key={idx} className="text-sm text-gray-700 bg-green-50 rounded p-2">• {opp}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* 数据来源 */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">📊 数据来源</h4>
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-blue-50 rounded-lg p-4">
                    <div className="text-sm text-gray-600 mb-1">关键新闻</div>
                    <div className="text-2xl font-bold text-blue-600">
                      {selectedReport.key_news ? selectedReport.key_news.length : 0}
                    </div>
                  </div>
                  <div className="bg-purple-50 rounded-lg p-4">
                    <div className="text-sm text-gray-600 mb-1">巨鲸活动</div>
                    <div className="text-2xl font-bold text-purple-600">
                      {selectedReport.whale_signals ? selectedReport.whale_signals.length : 0}
                    </div>
                  </div>
                  <div className="bg-green-50 rounded-lg p-4">
                    <div className="text-sm text-gray-600 mb-1">链上指标</div>
                    <div className="text-2xl font-bold text-green-600">
                      {selectedReport.on_chain_metrics ? '✓' : '✗'}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
