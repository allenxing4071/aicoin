'use client';

/**
 * Loading骨架屏组件
 * 提升加载体验
 */
export function DecisionSkeleton() {
  return (
    <div className="animate-pulse space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="bg-white border border-gray-200 p-3">
          <div className="flex items-center justify-between mb-2">
            <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            <div className="h-4 bg-gray-200 rounded w-16"></div>
          </div>
          <div className="space-y-2">
            <div className="h-3 bg-gray-200 rounded w-3/4"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      ))}
    </div>
  );
}

export function PerformanceSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="bg-white border border-gray-200 p-4">
        <div className="grid grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="space-y-2">
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              <div className="h-6 bg-gray-200 rounded w-3/4"></div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="h-96 bg-gray-200 rounded"></div>
    </div>
  );
}

