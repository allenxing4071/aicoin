'use client';

/**
 * KOL意见追踪页面
 * 
 * 路径: /admin/intelligence/kol
 * 
 * 功能：
 * - KOL列表管理
 * - 意见时间线
 * - 统计数据
 */

import React, { useState, useEffect } from 'react';
import PageHeader from '@/app/components/common/PageHeader';
import { unifiedDesignSystem, getThemeStyles } from '@/app/admin/unified-design-system';

interface KOLSource {
  id: number;
  name: string;
  platform: string;
  channel_id: string;
  influence_score: number;
  accuracy_rate: number;
  enabled: boolean;
  total_posts: number;
  successful_predictions: number;
}

interface KOLOpinion {
  id: number;
  kol_name: string;
  platform: string;
  content: string;
  sentiment: string | null;
  mentioned_coins: string[] | null;
  created_at: string;
}

export default function KOLTrackingPage() {
  const theme = getThemeStyles('blue');
  const [kols, setKols] = useState<KOLSource[]>([]);
  const [opinions, setOpinions] = useState<KOLOpinion[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // 获取KOL列表
      const kolsRes = await fetch('/api/v1/kol/sources');
      const kolsData = await kolsRes.json();
      if (Array.isArray(kolsData)) {
        setKols(kolsData);
      }

      // 获取意见列表
      const opinionsRes = await fetch('/api/v1/kol/opinions?limit=20');
      const opinionsData = await opinionsRes.json();
      if (opinionsData.success) {
        setOpinions(opinionsData.data);
      }

      // 获取统计数据
      const statsRes = await fetch('/api/v1/kol/statistics');
      const statsData = await statsRes.json();
      if (statsData.success) {
        setStats(statsData.data);
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (sentiment: string | null) => {
    if (!sentiment) return 'bg-gray-100 text-gray-600';
    if (sentiment === 'bullish') return 'bg-green-100 text-green-800';
    if (sentiment === 'bearish') return 'bg-red-100 text-red-800';
    return 'bg-gray-100 text-gray-600';
  };

  const getSentimentIcon = (sentiment: string | null) => {
    if (!sentiment) return '⚪';
    if (sentiment === 'bullish') return '🟢';
    if (sentiment === 'bearish') return '🔴';
    return '⚪';
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
        icon="👥"
        title="KOL意见追踪"
        description="追踪和分析KOL（意见领袖）的市场观点和预测"
        color="purple"
      />

      {/* 统计卡片 */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 shadow-lg border-2 border-purple-300">
            <div className="text-sm text-gray-500 mb-1">跟踪KOL</div>
            <div className="text-3xl font-bold text-purple-600">{stats.enabled_kols}</div>
            <div className="text-xs text-gray-500 mt-1">总计: {stats.total_kols}</div>
          </div>
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 shadow-lg border-2 border-blue-300">
            <div className="text-sm text-gray-500 mb-1">总意见数</div>
            <div className="text-3xl font-bold text-blue-600">{stats.total_opinions}</div>
          </div>
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 shadow-lg border-2 border-green-300">
            <div className="text-sm text-gray-500 mb-1">平均准确率</div>
            <div className="text-3xl font-bold text-green-600">{stats.avg_accuracy.toFixed(1)}%</div>
          </div>
          <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-6 shadow-lg border-2 border-orange-300">
            <div className="text-sm text-gray-500 mb-1">今日新增</div>
            <div className="text-3xl font-bold text-orange-600">0</div>
          </div>
        </div>
      )}

      {/* KOL列表 */}
      <div className="bg-white rounded-xl shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">📋 KOL列表</h3>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            添加KOL
          </button>
        </div>

        <div className="space-y-3">
          {kols.map((kol) => (
            <div key={kol.id} className={`${unifiedDesignSystem.listCard.container} ${theme.listCardBorder}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="text-2xl">
                    {kol.platform === 'twitter' ? '🐦' : '✈️'}
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">{kol.name}</h4>
                    <p className="text-sm text-gray-500">
                      {kol.platform} • @{kol.channel_id}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="text-xs text-gray-500">影响力</div>
                    <div className="text-sm font-semibold text-purple-600">
                      {kol.influence_score.toFixed(0)}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-gray-500">准确率</div>
                    <div className="text-sm font-semibold text-green-600">
                      {kol.accuracy_rate.toFixed(1)}%
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-gray-500">发帖数</div>
                    <div className="text-sm font-semibold text-gray-900">
                      {kol.total_posts}
                    </div>
                  </div>
                  <span
                    className={`px-3 py-1 text-xs rounded-full font-medium ${
                      kol.enabled
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {kol.enabled ? '✓ 启用' : '✗ 禁用'}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {kols.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <div className="text-4xl mb-2">👥</div>
            <p>暂无KOL数据</p>
            <p className="text-sm mt-2">点击"添加KOL"开始追踪</p>
          </div>
        )}
      </div>

      {/* 最新意见时间线 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">💬 最新意见</h3>
        
        <div className="space-y-4">
          {opinions.map((opinion) => (
            <div key={opinion.id} className="border-l-4 border-purple-500 pl-4 py-2">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-gray-900">{opinion.kol_name}</span>
                  <span className="text-xs text-gray-500">
                    {new Date(opinion.created_at).toLocaleString('zh-CN')}
                  </span>
                </div>
                {opinion.sentiment && (
                  <span className={`px-2 py-1 text-xs rounded-full font-medium ${getSentimentColor(opinion.sentiment)}`}>
                    {getSentimentIcon(opinion.sentiment)} {opinion.sentiment}
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-700 mb-2">{opinion.content}</p>
              {opinion.mentioned_coins && opinion.mentioned_coins.length > 0 && (
                <div className="flex gap-2">
                  {opinion.mentioned_coins.map((coin, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded"
                    >
                      {coin}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {opinions.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <div className="text-4xl mb-2">💬</div>
            <p>暂无意见数据</p>
          </div>
        )}
      </div>

      {/* 添加KOL模态框（占位） */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">添加KOL</h3>
            <p className="text-gray-600 mb-4">添加KOL功能开发中...</p>
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

