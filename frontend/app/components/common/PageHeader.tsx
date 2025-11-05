/**
 * 统一的页面头部组件
 * 用于所有管理后台页面,确保风格一致
 */

import React from 'react';

interface PageHeaderProps {
  icon: string;           // emoji图标,如 "🤖"
  title: string;          // 页面标题
  description: string;    // 页面描述
  color?: 'blue' | 'orange' | 'pink' | 'purple' | 'green' | 'cyan';  // 主题颜色
  actions?: React.ReactNode;  // 右侧操作按钮
}

const colorMap = {
  blue: {
    title: 'text-blue-900',
    desc: 'text-blue-700',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
  },
  orange: {
    title: 'text-orange-900',
    desc: 'text-orange-700',
    bg: 'bg-orange-50',
    border: 'border-orange-200',
  },
  pink: {
    title: 'text-pink-900',
    desc: 'text-pink-700',
    bg: 'bg-pink-50',
    border: 'border-pink-200',
  },
  purple: {
    title: 'text-purple-900',
    desc: 'text-purple-700',
    bg: 'bg-purple-50',
    border: 'border-purple-200',
  },
  green: {
    title: 'text-green-900',
    desc: 'text-green-700',
    bg: 'bg-green-50',
    border: 'border-green-200',
  },
  cyan: {
    title: 'text-cyan-900',
    desc: 'text-cyan-700',
    bg: 'bg-cyan-50',
    border: 'border-cyan-200',
  },
};

export default function PageHeader({
  icon,
  title,
  description,
  color = 'blue',
  actions,
}: PageHeaderProps) {
  const colors = colorMap[color];

  return (
    <div className={`${colors.bg} ${colors.border} border rounded-xl p-6 mb-6`}>
      <div className="flex items-start justify-between">
        <div>
          <h1 className={`text-2xl font-bold ${colors.title} mb-2 flex items-center gap-2`}>
            <span className="text-3xl">{icon}</span>
            {title}
          </h1>
          <p className={`text-base ${colors.desc}`}>
            {description}
          </p>
        </div>
        {actions && (
          <div className="flex items-center gap-3">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}
