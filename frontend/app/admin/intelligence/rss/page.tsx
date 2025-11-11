'use client';

/**
 * RSS新闻源管理页面
 * 
 * 路径: /admin/intelligence/rss
 * 
 * 功能：
 * - 数据源配置管理
 * - 新闻列表展示
 * - 连接测试
 * - 启用/禁用数据源
 */

import React, { useState, useEffect } from 'react';
import PageHeader from '@/app/components/common/PageHeader';
import { unifiedDesignSystem, getThemeStyles } from '@/app/admin/unified-design-system';

interface DataSource {
  type: string;
  name: string;
  url: string | null;
  api_key: string | null;
  enabled: boolean;
  update_interval: number;
  description: string;
}

interface NewsItem {
  title: string;
  source: string;
  url: string;
  published_at: string;
  content: string;
  impact: string;
  sentiment: string;
}

interface SourceStatus {
  name: string;
  type: string;
  status: string;
  last_update: string | null;
  last_error: string | null;
  total_calls: number;
  success_rate: number;
  data_source_url: string | null;
  description: string;
}

export default function RSSNewsPage() {
  const theme = getThemeStyles('blue');
  const [sources, setSources] = useState<DataSource[]>([]);
  const [newsItems, setNewsItems] = useState<NewsItem[]>([]);
  const [sourceStatuses, setSourceStatuses] = useState<SourceStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // 获取数据源配置
      const configRes = await fetch('/api/v1/admin/intelligence/config');
      const configData = await configRes.json();
      if (configData.success && configData.data.data_sources) {
        // 只显示RSS新闻源
        const rssSources = configData.data.data_sources.filter(
          (s: DataSource) => s.type === 'news'
        );
        setSources(rssSources);
      }

      // 获取数据源状态
      const statusRes = await fetch('/api/v1/admin/intelligence/data-sources/status');
      const statusData = await statusRes.json();
      if (Array.isArray(statusData)) {
        const rssStatuses = statusData.filter((s: SourceStatus) => s.type === 'news');
        setSourceStatuses(rssStatuses);
      }

      // 获取最新新闻（从情报报告中提取）
      const reportsRes = await fetch('/api/v1/intelligence/reports?limit=10');
      const reportsData = await reportsRes.json();
      if (reportsData.success && reportsData.data) {
        // 提取所有新闻
        const allNews: NewsItem[] = [];
        reportsData.data.forEach((report: any) => {
          if (report.key_news && Array.isArray(report.key_news)) {
            allNews.push(...report.key_news);
          }
        });
        setNewsItems(allNews.slice(0, 20)); // 只显示最新20条
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleSource = async (sourceName: string, currentEnabled: boolean) => {
    try {
      const res = await fetch(
        `/api/v1/admin/intelligence/data-sources/${encodeURIComponent(sourceName)}/toggle?enabled=${!currentEnabled}`,
        { method: 'POST' }
      );
      const data = await res.json();
      if (data.success) {
        alert(`✅ 数据源已${!currentEnabled ? '启用' : '禁用'}`);
        fetchData();
      } else {
        alert(`❌ 操作失败: ${data.message}`);
      }
    } catch (error) {
      alert(`❌ 操作失败: ${error}`);
    }
  };

  const handleTestConnection = async (sourceName: string) => {
    try {
      setTesting(sourceName);
      const res = await fetch(
        `/api/v1/admin/intelligence/data-sources/${encodeURIComponent(sourceName)}/test-connection`,
        { method: 'POST' }
      );
      const data = await res.json();
      
      if (data.success) {
        alert(`✅ 连接成功！\n响应时间: ${data.data.response_time_ms}ms\n内容长度: ${data.data.content_length || 'N/A'}`);
      } else {
        alert(`❌ 连接失败: ${data.message}`);
      }
    } catch (error) {
      alert(`❌ 测试失败: ${error}`);
    } finally {
      setTesting(null);
    }
  };

  const getSentimentColor = (sentiment: string) => {
    if (sentiment === 'positive') return 'bg-green-100 text-green-800';
    if (sentiment === 'negative') return 'bg-red-100 text-red-800';
    return 'bg-gray-100 text-gray-600';
  };

  const getSentimentIcon = (sentiment: string) => {
    if (sentiment === 'positive') return '📈';
    if (sentiment === 'negative') return '📉';
    return '📊';
  };

  const getImpactColor = (impact: string) => {
    if (impact === 'high') return 'bg-red-100 text-red-800';
    if (impact === 'medium') return 'bg-yellow-100 text-yellow-800';
    return 'bg-blue-100 text-blue-800';
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
        icon="📰"
        title="RSS新闻源管理"
        description="管理和监控RSS新闻源，获取实时市场资讯"
        color="blue"
      />

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 shadow-lg border-2 border-blue-300">
          <div className="text-sm text-gray-500 mb-1">配置源</div>
          <div className="text-3xl font-bold text-blue-600">{sources.length}</div>
          <div className="text-xs text-gray-500 mt-1">
            启用: {sources.filter(s => s.enabled).length}
          </div>
        </div>
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 shadow-lg border-2 border-green-300">
          <div className="text-sm text-gray-500 mb-1">总新闻数</div>
          <div className="text-3xl font-bold text-green-600">{newsItems.length}</div>
        </div>
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 shadow-lg border-2 border-purple-300">
          <div className="text-sm text-gray-500 mb-1">平均成功率</div>
          <div className="text-3xl font-bold text-purple-600">
            {sourceStatuses.length > 0
              ? (sourceStatuses.reduce((sum, s) => sum + s.success_rate, 0) / sourceStatuses.length).toFixed(1)
              : '0.0'}%
          </div>
        </div>
        <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-6 shadow-lg border-2 border-orange-300">
          <div className="text-sm text-gray-500 mb-1">总调用次数</div>
          <div className="text-3xl font-bold text-orange-600">
            {sourceStatuses.reduce((sum, s) => sum + s.total_calls, 0)}
          </div>
        </div>
      </div>

      {/* 数据源列表 */}
      <div className="bg-white rounded-xl shadow p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">📡 RSS数据源</h3>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all shadow-md hover:shadow-lg"
          >
            + 添加数据源
          </button>
        </div>

        <div className="space-y-4">
          {sources.map((source, idx) => {
            const status = sourceStatuses.find(s => s.name === source.name);
            return (
              <div key={idx} className={`${unifiedDesignSystem.listCard.container} ${theme.listCardBorder}`}>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-semibold text-gray-900">{source.name}</h4>
                      <span
                        className={`px-3 py-1 text-xs rounded-full font-medium ${
                          source.enabled
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-600'
                        }`}
                      >
                        {source.enabled ? '✓ 启用' : '✗ 禁用'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{source.description}</p>
                    <p className="text-xs text-gray-500 font-mono">{source.url}</p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleTestConnection(source.name)}
                      disabled={testing === source.name}
                      className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
                    >
                      {testing === source.name ? '测试中...' : '测试连接'}
                    </button>
                    <button
                      onClick={() => handleToggleSource(source.name, source.enabled)}
                      className={`px-3 py-1 text-sm rounded ${
                        source.enabled
                          ? 'bg-gray-600 text-white hover:bg-gray-700'
                          : 'bg-green-600 text-white hover:bg-green-700'
                      }`}
                    >
                      {source.enabled ? '禁用' : '启用'}
                    </button>
                  </div>
                </div>

                {/* 状态信息 */}
                {status && (
                  <div className="grid grid-cols-4 gap-4 pt-3 border-t border-gray-200">
                    <div>
                      <div className="text-xs text-gray-500">总调用</div>
                      <div className="text-sm font-semibold text-gray-900">{status.total_calls}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">成功率</div>
                      <div className="text-sm font-semibold text-green-600">{status.success_rate.toFixed(1)}%</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">更新间隔</div>
                      <div className="text-sm font-semibold text-gray-900">{source.update_interval / 60}分钟</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">最后更新</div>
                      <div className="text-sm font-semibold text-gray-900">
                        {status.last_update
                          ? new Date(status.last_update).toLocaleString('zh-CN', {
                              month: '2-digit',
                              day: '2-digit',
                              hour: '2-digit',
                              minute: '2-digit',
                            })
                          : '未更新'}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {sources.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <div className="text-4xl mb-2">📰</div>
            <p>暂无RSS数据源</p>
            <p className="text-sm mt-2">点击"添加数据源"开始配置</p>
          </div>
        )}
      </div>

      {/* 最新新闻列表 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📄 最新新闻</h3>
        
        <div className="space-y-4">
          {newsItems.map((news, idx) => (
            <div key={idx} className="border-l-4 border-blue-500 pl-4 py-2">
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-semibold text-gray-900 flex-1">{news.title}</h4>
                <div className="flex gap-2 ml-4">
                  {news.impact && (
                    <span className={`px-2 py-1 text-xs rounded-full font-medium ${getImpactColor(news.impact)}`}>
                      {news.impact === 'high' ? '高影响' : news.impact === 'medium' ? '中影响' : '低影响'}
                    </span>
                  )}
                  {news.sentiment && (
                    <span className={`px-2 py-1 text-xs rounded-full font-medium ${getSentimentColor(news.sentiment)}`}>
                      {getSentimentIcon(news.sentiment)} {news.sentiment}
                    </span>
                  )}
                </div>
              </div>
              <p className="text-sm text-gray-700 mb-2">{news.content}</p>
              <div className="flex items-center gap-4 text-xs text-gray-500">
                <span>来源: {news.source}</span>
                <span>发布: {new Date(news.published_at).toLocaleString('zh-CN')}</span>
                {news.url && (
                  <a
                    href={news.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    查看原文 →
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>

        {newsItems.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <div className="text-4xl mb-2">📄</div>
            <p>暂无新闻数据</p>
            <p className="text-sm mt-2">启用RSS数据源后将自动收集新闻</p>
          </div>
        )}
      </div>

      {/* 添加数据源模态框 */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">添加RSS数据源</h3>
            <p className="text-gray-600 mb-4">添加自定义RSS数据源功能开发中...</p>
            <p className="text-sm text-gray-500 mb-4">
              当前系统已预配置 CoinDesk 和 CoinTelegraph 两个主流新闻源。
            </p>
            <button
              onClick={() => setShowAddModal(false)}
              className="w-full px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              关闭
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
