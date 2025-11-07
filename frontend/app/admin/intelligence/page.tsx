'use client';

/**
 * 情报系统配置和监控页面
 * 
 * 路径: /admin/intelligence
 * 
 * 功能：
 * - 数据源配置: Qwen情报官的配置和监控
 * - 云平台管理: AWS等云平台的配置和监控
 */

import React, { useState } from 'react';
import Link from 'next/link';
import IntelligenceConfigPanel from '@/app/components/intelligence/IntelligenceConfigPanel';
import IntelligencePlatformsPanel from '@/app/components/intelligence/IntelligencePlatformsPanel';
import PageHeader from '../../components/common/PageHeader';

type TabType = 'datasources' | 'platforms';

export default function IntelligenceAdminPage() {
  const [activeTab, setActiveTab] = useState<TabType>('platforms');

  return (
    <div className="space-y-6">
      {/* 页头 - 统一风格 */}
      <PageHeader
        icon="🕵️‍♀️"
        title="Qwen情报系统管理"
        description="配置和监控市场情报收集系统、云平台管理"
        color="orange"
      />

      {/* Tab切换 */}
      <div className="flex gap-2 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('datasources')}
          className={`px-4 py-3 font-medium text-sm transition-colors border-b-2 ${
            activeTab === 'datasources'
              ? 'text-blue-600 border-blue-600'
              : 'text-gray-600 border-transparent hover:text-blue-600'
          }`}
        >
          📊 数据源配置
        </button>
        <button
          onClick={() => setActiveTab('platforms')}
          className={`px-4 py-3 font-medium text-sm transition-colors border-b-2 ${
            activeTab === 'platforms'
              ? 'text-blue-600 border-blue-600'
              : 'text-gray-600 border-transparent hover:text-blue-600'
          }`}
        >
          ☁️ 云平台管理
        </button>
      </div>

      {/* Tab内容 */}
      <div>
        {activeTab === 'datasources' ? (
          <IntelligenceConfigPanel />
        ) : (
          <IntelligencePlatformsPanel />
        )}
      </div>
    </div>
  );
}

