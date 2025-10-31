'use client';

interface MetricCardProps {
  title: string;
  value: string;
  change?: number;
  trend?: 'up' | 'down' | 'neutral';
  subtitle?: string;
}

export default function MetricCard({ title, value, change, trend = 'neutral', subtitle }: MetricCardProps) {
  const getTrendColor = () => {
    if (trend === 'up') return 'text-green-600';
    if (trend === 'down') return 'text-red-600';
    return 'text-gray-600';
  };

  const getTrendIcon = () => {
    if (trend === 'up') return '↗';
    if (trend === 'down') return '↘';
    return '→';
  };

  return (
    <div className="bg-white border border-gray-200 p-3">
      <div className="text-xs text-gray-600 mb-1">{title}</div>
      <div className={`text-2xl font-bold ${getTrendColor()}`}>
        {value}
      </div>
      {change !== undefined && (
        <div className="flex items-center space-x-1 mt-1">
          <span className={`text-xs font-mono ${getTrendColor()}`}>
            {getTrendIcon()} {change >= 0 ? '+' : ''}{change.toFixed(2)}%
          </span>
          {subtitle && (
            <span className="text-xs text-gray-500">{subtitle}</span>
          )}
        </div>
      )}
    </div>
  );
}

