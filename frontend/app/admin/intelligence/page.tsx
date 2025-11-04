'use client';

/**
 * 情报系统配置和监控页面
 * 
 * 路径: /admin/intelligence
 * 
 * 功能：
 * - 显示Qwen情报官的配置
 * - 监控数据源状态
 * - 查看情报收集统计
 * - 管理数据源（启用/禁用）
 */

import React from 'react';
import Link from 'next/link';
import IntelligenceConfigPanel from '@/app/components/intelligence/IntelligenceConfigPanel';

export default function IntelligenceAdminPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* 页头 */}
        <div className="mb-6">
          <Link 
            href="/admin"
            className="text-blue-600 hover:text-blue-800 font-medium mb-2 inline-block"
          >
            ← 返回管理后台
          </Link>
          
          <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
            🕵️‍♀️ Qwen情报系统管理
          </h1>
          <p className="text-gray-600 mt-2">
            配置和监控市场情报收集系统
          </p>
        </div>

        {/* 情报配置面板 */}
        <IntelligenceConfigPanel />
      </div>
    </div>
  );
}

