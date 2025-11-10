/**
 * 统一卡片组件库
 * 
 * 提供可复用的卡片组件，所有页面直接使用这些组件
 * 避免重复代码，统一样式管理
 */

import React from 'react';

// ============================================
// 1. 统计卡片组件（方形卡片 - 图1样式）
// ============================================

interface StatCardProps {
  label: string;
  value: string | number;
  icon?: string;
  color?: 'purple' | 'blue' | 'green' | 'orange' | 'red' | 'pink' | 'yellow' | 'indigo' | 'gray';
  className?: string;
}

export function StatCard({ label, value, icon, color = 'blue', className = '' }: StatCardProps) {
  const colorClasses = {
    purple: 'bg-purple-50 border-purple-200 text-purple-900',
    blue: 'bg-blue-50 border-blue-200 text-blue-900',
    green: 'bg-green-50 border-green-200 text-green-900',
    orange: 'bg-orange-50 border-orange-200 text-orange-900',
    red: 'bg-red-50 border-red-200 text-red-900',
    pink: 'bg-pink-50 border-pink-200 text-pink-900',
    yellow: 'bg-yellow-50 border-yellow-200 text-yellow-900',
    indigo: 'bg-indigo-50 border-indigo-200 text-indigo-900',
    gray: 'bg-gray-50 border-gray-200 text-gray-900',
  };

  const valueColorClasses = {
    purple: 'text-purple-600',
    blue: 'text-blue-600',
    green: 'text-green-600',
    orange: 'text-orange-600',
    red: 'text-red-600',
    pink: 'text-pink-600',
    yellow: 'text-yellow-600',
    indigo: 'text-indigo-600',
    gray: 'text-gray-600',
  };

  return (
    <div className={`rounded-lg p-4 border ${colorClasses[color]} ${className}`}>
      {icon && (
        <div className="flex items-center gap-2 mb-2">
          <span className="text-2xl">{icon}</span>
          <div className="text-sm text-gray-600">{label}</div>
        </div>
      )}
      {!icon && (
        <div className="text-sm text-gray-600 mb-2">{label}</div>
      )}
      <div className={`text-2xl font-bold ${valueColorClasses[color]}`}>
        {value}
      </div>
    </div>
  );
}

// ============================================
// 2. 信息卡片组件（带图标的提示卡片）
// ============================================

interface InfoCardProps {
  icon: string;
  title: string;
  description: string;
  color?: 'purple' | 'blue' | 'green' | 'orange' | 'red' | 'pink' | 'yellow' | 'indigo';
  className?: string;
}

export function InfoCard({ icon, title, description, color = 'blue', className = '' }: InfoCardProps) {
  const colorClasses = {
    purple: 'bg-purple-50 border-purple-200',
    blue: 'bg-blue-50 border-blue-200',
    green: 'bg-green-50 border-green-200',
    orange: 'bg-orange-50 border-orange-200',
    red: 'bg-red-50 border-red-200',
    pink: 'bg-pink-50 border-pink-200',
    yellow: 'bg-yellow-50 border-yellow-200',
    indigo: 'bg-indigo-50 border-indigo-200',
  };

  const iconColorClasses = {
    purple: 'text-purple-600',
    blue: 'text-blue-600',
    green: 'text-green-600',
    orange: 'text-orange-600',
    red: 'text-red-600',
    pink: 'text-pink-600',
    yellow: 'text-yellow-600',
    indigo: 'text-indigo-600',
  };

  const titleColorClasses = {
    purple: 'text-purple-900',
    blue: 'text-blue-900',
    green: 'text-green-900',
    orange: 'text-orange-900',
    red: 'text-red-900',
    pink: 'text-pink-900',
    yellow: 'text-yellow-900',
    indigo: 'text-indigo-900',
  };

  return (
    <div className={`flex items-start gap-3 p-4 rounded-lg border ${colorClasses[color]} ${className}`}>
      <div className={`${iconColorClasses[color]} mt-1 text-xl`}>{icon}</div>
      <div>
        <div className={`font-semibold ${titleColorClasses[color]} mb-1`}>{title}</div>
        <div className="text-sm text-gray-600">{description}</div>
      </div>
    </div>
  );
}

// ============================================
// 3. 列表卡片组件（带左边框的卡片）
// ============================================

interface ListCardProps {
  children: React.ReactNode;
  color?: 'purple' | 'blue' | 'green' | 'orange' | 'red' | 'pink' | 'yellow' | 'indigo';
  className?: string;
}

export function ListCard({ children, color = 'blue', className = '' }: ListCardProps) {
  const borderColorClasses = {
    purple: 'border-purple-500',
    blue: 'border-blue-500',
    green: 'border-green-500',
    orange: 'border-orange-500',
    red: 'border-red-500',
    pink: 'border-pink-500',
    yellow: 'border-yellow-500',
    indigo: 'border-indigo-500',
  };

  return (
    <div className={`bg-white rounded-xl shadow-sm p-6 border-l-4 ${borderColorClasses[color]} ${className}`}>
      {children}
    </div>
  );
}

// ============================================
// 4. 页面头部组件（带渐变背景）
// ============================================

interface PageHeaderCardProps {
  icon: string;
  title: string;
  description: string;
  color?: 'purple' | 'blue' | 'green' | 'orange' | 'red' | 'pink' | 'yellow' | 'indigo';
  action?: React.ReactNode;
  className?: string;
}

export function PageHeaderCard({ 
  icon, 
  title, 
  description, 
  color = 'blue', 
  action,
  className = '' 
}: PageHeaderCardProps) {
  const colorClasses = {
    purple: 'bg-gradient-to-r from-purple-50 to-purple-100 border-purple-200',
    blue: 'bg-gradient-to-r from-blue-50 to-blue-100 border-blue-200',
    green: 'bg-gradient-to-r from-green-50 to-green-100 border-green-200',
    orange: 'bg-gradient-to-r from-orange-50 to-orange-100 border-orange-200',
    red: 'bg-gradient-to-r from-red-50 to-red-100 border-red-200',
    pink: 'bg-gradient-to-r from-pink-50 to-pink-100 border-pink-200',
    yellow: 'bg-gradient-to-r from-yellow-50 to-yellow-100 border-yellow-200',
    indigo: 'bg-gradient-to-r from-indigo-50 to-indigo-100 border-indigo-200',
  };

  return (
    <div className={`rounded-xl p-6 border shadow-sm ${colorClasses[color]} ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="text-4xl">{icon}</div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
            <p className="text-sm text-gray-600 mt-1">{description}</p>
          </div>
        </div>
        {action && <div>{action}</div>}
      </div>
    </div>
  );
}

// ============================================
// 5. 统计卡片网格容器
// ============================================

interface StatCardGridProps {
  children: React.ReactNode;
  columns?: 2 | 3 | 4 | 5 | 6;
  className?: string;
}

export function StatCardGrid({ children, columns = 4, className = '' }: StatCardGridProps) {
  const gridClasses = {
    2: 'grid grid-cols-1 md:grid-cols-2 gap-4',
    3: 'grid grid-cols-1 md:grid-cols-3 gap-4',
    4: 'grid grid-cols-1 md:grid-cols-4 gap-4',
    5: 'grid grid-cols-1 md:grid-cols-5 gap-4',
    6: 'grid grid-cols-1 md:grid-cols-6 gap-4',
  };

  return (
    <div className={`${gridClasses[columns]} ${className}`}>
      {children}
    </div>
  );
}

// ============================================
// 6. 内容卡片组件（白色背景，带阴影）
// ============================================

interface ContentCardProps {
  children: React.ReactNode;
  title?: string;
  className?: string;
}

export function ContentCard({ children, title, className = '' }: ContentCardProps) {
  return (
    <div className={`bg-white rounded-xl border border-gray-200 shadow-sm ${className}`}>
      {title && (
        <div className="border-b border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        </div>
      )}
      <div className="p-6">
        {children}
      </div>
    </div>
  );
}

// ============================================
// 7. 导出所有组件
// ============================================

export default {
  StatCard,
  InfoCard,
  ListCard,
  PageHeaderCard,
  StatCardGrid,
  ContentCard,
};

