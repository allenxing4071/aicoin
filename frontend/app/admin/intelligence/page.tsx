'use client';

/**
 * 情报中枢导航页面
 * 
 * 路径: /admin/intelligence
 * 
 * 功能：
 * - 情报数据源导航
 * - 情报分析导航
 */

import React from 'react';
import Link from 'next/link';
import PageHeader from '../../components/common/PageHeader';

export default function IntelligenceHubPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        icon="🕵️"
        title="情报中枢"
        description="管理所有情报数据源和分析功能"
        color="orange"
      />

      {/* 数据源管理 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📡 数据源管理</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <Link
            href="/admin/intelligence/rss"
            className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="text-3xl mb-2">📰</div>
            <h4 className="font-semibold text-gray-900 mb-1">RSS新闻源</h4>
            <p className="text-sm text-gray-600">配置和监控新闻数据源</p>
            <div className="mt-2 text-xs text-gray-500">即将上线</div>
          </Link>

          <Link
            href="/admin/intelligence/whale"
            className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="text-3xl mb-2">🐋</div>
            <h4 className="font-semibold text-gray-900 mb-1">巨鲸监控</h4>
            <p className="text-sm text-gray-600">追踪大额交易和巨鲸动向</p>
            <div className="mt-2 text-xs text-gray-500">即将上线</div>
          </Link>

          <Link
            href="/admin/intelligence/onchain"
            className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="text-3xl mb-2">⛓️</div>
            <h4 className="font-semibold text-gray-900 mb-1">链上数据</h4>
            <p className="text-sm text-gray-600">分析链上交易和资金流向</p>
            <div className="mt-2 text-xs text-gray-500">即将上线</div>
          </Link>

          <Link
            href="/admin/intelligence/kol"
            className="p-4 border-2 border-purple-200 bg-purple-50 rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="text-3xl mb-2">👥</div>
            <h4 className="font-semibold text-purple-900 mb-1">KOL追踪</h4>
            <p className="text-sm text-purple-700">追踪KOL意见和市场情绪</p>
            <div className="mt-2 text-xs text-purple-600">✓ 已上线</div>
          </Link>

          <Link
            href="/admin/intelligence/smart-money"
            className="p-4 border-2 border-green-200 bg-green-50 rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="text-3xl mb-2">💰</div>
            <h4 className="font-semibold text-green-900 mb-1">聪明钱跟单</h4>
            <p className="text-sm text-green-700">学习聪明钱交易策略</p>
            <div className="mt-2 text-xs text-green-600">✓ 已上线</div>
          </Link>
        </div>
      </div>

      {/* 情报分析 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🔍 情报分析</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            href="/admin/intelligence/realtime"
            className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="text-3xl mb-2">⚡</div>
            <h4 className="font-semibold text-gray-900 mb-1">实时情报</h4>
            <p className="text-sm text-gray-600">查看实时市场情报和AI分析</p>
            <div className="mt-2 text-xs text-gray-500">即将上线</div>
          </Link>

          <Link
            href="/admin/intelligence/reports"
            className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="text-3xl mb-2">📊</div>
            <h4 className="font-semibold text-gray-900 mb-1">历史报告</h4>
            <p className="text-sm text-gray-600">查看历史情报分析报告</p>
            <div className="mt-2 text-xs text-gray-500">即将上线</div>
          </Link>
        </div>
      </div>
    </div>
  );
}

