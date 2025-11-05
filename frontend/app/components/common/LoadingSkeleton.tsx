/**
 * Loading Skeleton 组件
 * 用于优化页面加载体验
 */

interface LoadingSkeletonProps {
  type?: 'dashboard' | 'table' | 'chart' | 'card';
  rows?: number;
}

export default function LoadingSkeleton({ type = 'dashboard', rows = 3 }: LoadingSkeletonProps) {
  if (type === 'dashboard') {
    return (
      <div className="animate-pulse space-y-4">
        {/* Header Section */}
        <div className="h-32 bg-gray-200 rounded-lg" />
        
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="h-24 bg-gray-200 rounded-lg" />
          <div className="h-24 bg-gray-200 rounded-lg" />
          <div className="h-24 bg-gray-200 rounded-lg" />
        </div>
        
        {/* Chart Area */}
        <div className="h-64 bg-gray-200 rounded-lg" />
        
        {/* Table Area */}
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-gray-200 rounded" />
          ))}
        </div>
      </div>
    );
  }

  if (type === 'table') {
    return (
      <div className="animate-pulse space-y-2">
        {/* Table Header */}
        <div className="h-12 bg-gray-200 rounded" />
        
        {/* Table Rows */}
        {[...Array(rows)].map((_, i) => (
          <div key={i} className="h-16 bg-gray-100 rounded" />
        ))}
      </div>
    );
  }

  if (type === 'chart') {
    return (
      <div className="animate-pulse">
        <div className="h-64 bg-gray-200 rounded-lg flex items-end justify-around p-4">
          {[...Array(12)].map((_, i) => (
            <div 
              key={i} 
              className="bg-gray-300 rounded-t"
              style={{ 
                width: '6%', 
                height: `${Math.random() * 80 + 20}%` 
              }}
            />
          ))}
        </div>
      </div>
    );
  }

  if (type === 'card') {
    return (
      <div className="animate-pulse">
        <div className="bg-gray-200 rounded-lg p-6 space-y-4">
          <div className="h-6 bg-gray-300 rounded w-3/4" />
          <div className="h-4 bg-gray-300 rounded w-1/2" />
          <div className="h-20 bg-gray-300 rounded" />
        </div>
      </div>
    );
  }

  return null;
}

/**
 * 仪表板专用加载组件
 */
export function DashboardSkeleton() {
  return (
    <div className="min-h-screen bg-white p-6">
      <div className="animate-pulse space-y-6">
        {/* Top Bar */}
        <div className="flex justify-between items-center">
          <div className="h-10 bg-gray-200 rounded w-48" />
          <div className="h-10 bg-gray-200 rounded w-32" />
        </div>

        {/* Balance Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="col-span-1 md:col-span-2">
            <div className="h-40 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 space-y-3">
              <div className="h-6 bg-blue-200 rounded w-32" />
              <div className="h-12 bg-blue-200 rounded w-48" />
              <div className="h-4 bg-blue-200 rounded w-24" />
          </div>
          </div>
          <div className="h-40 bg-gray-200 rounded-xl" />
          <div className="h-40 bg-gray-200 rounded-xl" />
        </div>

        {/* Tabs */}
        <div className="flex space-x-2">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-10 bg-gray-200 rounded w-24" />
          ))}
        </div>

        {/* Content Area */}
        <div className="h-96 bg-gray-100 rounded-xl" />
      </div>
    </div>
  );
}

/**
 * 紧凑型加载指示器
 */
export function InlineLoader({ text = '加载中...' }: { text?: string }) {
  return (
    <div className="flex items-center justify-center py-8">
      <div className="flex items-center space-x-3">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
        <span className="text-gray-500 text-sm">{text}</span>
      </div>
    </div>
  );
}

/**
 * 全屏加载指示器
 */
export function FullPageLoader() {
  return (
    <div className="fixed inset-0 bg-white bg-opacity-90 flex items-center justify-center z-50">
      <div className="text-center space-y-4">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-500 mx-auto"></div>
        <p className="text-gray-600 text-lg">正在加载数据...</p>
        <p className="text-gray-400 text-sm">请稍候</p>
      </div>
    </div>
  );
}

/**
 * 性能面板专用加载组件
 */
export function PerformanceSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white border border-gray-200 rounded-lg p-4 space-y-2">
            <div className="h-4 bg-gray-200 rounded w-24" />
            <div className="h-8 bg-gray-200 rounded w-32" />
            </div>
          ))}
        </div>
      
      {/* Chart Area */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="h-6 bg-gray-200 rounded w-48 mb-4" />
        <div className="h-64 bg-gray-100 rounded" />
      </div>
    </div>
  );
}

/**
 * 决策时间线专用加载组件
 */
export function DecisionSkeleton() {
  return (
    <div className="animate-pulse space-y-3">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <div className="w-10 h-10 bg-gray-200 rounded-full" />
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-200 rounded w-48" />
              <div className="h-3 bg-gray-100 rounded w-full" />
              <div className="h-3 bg-gray-100 rounded w-3/4" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
