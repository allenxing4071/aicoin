'use client';

interface RiskGaugeProps {
  title: string;
  value: number;
  max: number;
  unit: string;
  thresholds?: {
    warning: number;
    danger: number;
  };
  inverted?: boolean; // true for Sharpe where higher is better
}

export default function RiskGauge({ 
  title, 
  value, 
  max, 
  unit, 
  thresholds = { warning: max * 0.5, danger: max * 0.8 },
  inverted = false
}: RiskGaugeProps) {
  const percentage = Math.min(Math.abs(value) / max * 100, 100);
  
  const getColor = () => {
    if (inverted) {
      // For Sharpe ratio: higher is better
      if (value >= thresholds.warning) return 'bg-green-500';
      if (value >= thresholds.danger) return 'bg-yellow-500';
      return 'bg-red-500';
    } else {
      // For drawdown/volatility: lower is better
      if (Math.abs(value) <= thresholds.warning) return 'bg-green-500';
      if (Math.abs(value) <= thresholds.danger) return 'bg-yellow-500';
      return 'bg-red-500';
    }
  };

  const getTextColor = () => {
    if (inverted) {
      if (value >= thresholds.warning) return 'text-green-600';
      if (value >= thresholds.danger) return 'text-yellow-600';
      return 'text-red-600';
    } else {
      if (Math.abs(value) <= thresholds.warning) return 'text-green-600';
      if (Math.abs(value) <= thresholds.danger) return 'text-yellow-600';
      return 'text-red-600';
    }
  };

  return (
    <div className="bg-white border border-gray-200 p-3">
      <div className="text-xs text-gray-600 mb-2">{title}</div>
      
      {/* 仪表盘可视化 */}
      <div className="relative h-16 mb-2">
        <div className="absolute inset-0 flex items-end">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${getColor()}`}
              style={{ width: `${percentage}%` }}
            />
          </div>
        </div>
        <div className={`text-3xl font-bold ${getTextColor()}`}>
          {value.toFixed(2)}{unit}
        </div>
      </div>

      {/* 阈值指示 */}
      <div className="flex justify-between text-xs text-gray-500">
        <span>0{unit}</span>
        <span className="text-gray-400">
          {inverted ? 'Higher is better' : 'Lower is better'}
        </span>
        <span>{max}{unit}</span>
      </div>
    </div>
  );
}

