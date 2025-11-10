'use client';

/**
 * 分析模型配置页面（预留）
 * 
 * 路径: /admin/ai-platforms/analysis
 * 
 * 功能：
 * - 预留Claude、GPT-4等模型配置
 * - 暂时显示"即将上线"
 */

import React from 'react';
import PageHeader from '@/app/components/common/PageHeader';
import { unifiedDesignSystem, getThemeStyles } from '@/app/admin/unified-design-system';

export default function AnalysisModelsPage() {
  // 使用统一的绿色主题
  const theme = getThemeStyles('green');
  
  return (
    <div className={unifiedDesignSystem.page.container}>
      {/* 页头 */}
      <div className={theme.pageHeader}>
        <div className={unifiedDesignSystem.pageHeader.content}>
          <div className={unifiedDesignSystem.pageHeader.titleSection}>
            <div className={unifiedDesignSystem.pageHeader.icon}>📊</div>
            <div className={unifiedDesignSystem.pageHeader.titleWrapper}>
              <h1 className={unifiedDesignSystem.pageHeader.title}>分析模型配置</h1>
              <p className={unifiedDesignSystem.pageHeader.description}>
                预留Claude、GPT-4等高级分析模型配置
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 即将上线提示 */}
      <div className={`${unifiedDesignSystem.contentCard.indigo} text-center`}>
        <div className="text-6xl mb-4">🚀</div>
        <h3 className={`text-2xl font-bold ${unifiedDesignSystem.contentCard.titleColors.indigo} mb-3`}>即将上线</h3>
        <p className="text-lg text-indigo-700 mb-6">
          我们正在集成更多强大的AI分析模型
        </p>
        
        <div className={unifiedDesignSystem.grid.cols3}>
          {/* Claude */}
          <div className={`${unifiedDesignSystem.statCard.container} ${unifiedDesignSystem.statCard.backgrounds.indigo}`}>
            <div className="text-3xl mb-2">🤖</div>
            <h4 className="font-semibold text-gray-900 mb-2">Claude</h4>
            <p className="text-sm text-gray-600">
              Anthropic的高级语言模型，擅长复杂分析和推理
            </p>
            <div className={`mt-3 ${unifiedDesignSystem.badge.info} inline-block`}>
              开发中
            </div>
          </div>

          {/* GPT-4 */}
          <div className={`${unifiedDesignSystem.statCard.container} ${unifiedDesignSystem.statCard.backgrounds.blue}`}>
            <div className="text-3xl mb-2">🧠</div>
            <h4 className="font-semibold text-gray-900 mb-2">GPT-4</h4>
            <p className="text-sm text-gray-600">
              OpenAI的旗舰模型，强大的理解和生成能力
            </p>
            <div className={`mt-3 ${unifiedDesignSystem.badge.info} inline-block`}>
              规划中
            </div>
          </div>

          {/* Gemini */}
          <div className={`${unifiedDesignSystem.statCard.container} ${unifiedDesignSystem.statCard.backgrounds.purple}`}>
            <div className="text-3xl mb-2">✨</div>
            <h4 className="font-semibold text-gray-900 mb-2">Gemini</h4>
            <p className="text-sm text-gray-600">
              Google的多模态AI模型，支持文本、图像等
            </p>
            <div className={`mt-3 ${unifiedDesignSystem.badge.info} inline-block`}>
              规划中
            </div>
          </div>
        </div>

        <div className="mt-8 text-sm text-indigo-600">
          💡 提示：如需使用这些模型，请联系管理员或查看开发路线图
        </div>
      </div>

      {/* 功能预览 */}
      <div className={`${unifiedDesignSystem.listCard.container} ${theme.listCardBorder}`}>
        <h3 className={`${unifiedDesignSystem.listCard.title} mb-4`}>🎯 计划功能</h3>
        <div className="space-y-3">
          <div className="flex items-start gap-3">
            <div className="text-green-500 mt-1">✓</div>
            <div>
              <div className="font-medium text-gray-900">多模型支持</div>
              <div className="text-sm text-gray-600">同时配置和管理多个AI分析模型</div>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="text-green-500 mt-1">✓</div>
            <div>
              <div className="font-medium text-gray-900">智能路由</div>
              <div className="text-sm text-gray-600">根据任务类型自动选择最合适的模型</div>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="text-green-500 mt-1">✓</div>
            <div>
              <div className="font-medium text-gray-900">成本优化</div>
              <div className="text-sm text-gray-600">平衡模型性能和调用成本</div>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="text-green-500 mt-1">✓</div>
            <div>
              <div className="font-medium text-gray-900">A/B测试</div>
              <div className="text-sm text-gray-600">对比不同模型的分析效果</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

