'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';

interface EquityData {
  time: string;
  value: number;
  pnl: number;
}

export default function EquityCurve() {
  const [data, setData] = useState<EquityData[]>([]);
  const [stats, setStats] = useState({
    currentValue: 11530.33,
    change: 48.34,
    maxDrawdown: -6.8,
    sharpeRatio: 2.1
  });

  useEffect(() => {
    generateMockData();
    const interval = setInterval(() => {
      updateData();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const generateMockData = () => {
    const now = Date.now();
    const data: EquityData[] = [];
    let value = 10000;

    for (let i = 100; i >= 0; i--) {
      const time = new Date(now - i * 3600000 * 4).toISOString();
      const change = (Math.random() - 0.45) * 200; // 略微向上偏移
      value += change;
      data.push({
        time,
        value: Math.max(9000, value),
        pnl: value - 10000
      });
    }

    setData(data);
    setStats({
      currentValue: data[data.length - 1].value,
      change: ((data[data.length - 1].value - 10000) / 10000) * 100,
      maxDrawdown: -6.8,
      sharpeRatio: 2.1
    });
  };

  const updateData = () => {
    setData(prev => {
      if (prev.length === 0) return prev;
      const lastValue = prev[prev.length - 1].value;
      const change = (Math.random() - 0.45) * 50;
      const newValue = Math.max(9000, lastValue + change);
      
      const newData = [
        ...prev.slice(1),
        {
          time: new Date().toISOString(),
          value: newValue,
          pnl: newValue - 10000
        }
      ];

      setStats({
        currentValue: newValue,
        change: ((newValue - 10000) / 10000) * 100,
        maxDrawdown: -6.8,
        sharpeRatio: 2.1
      });

      return newData;
    });
  };

  const formatTime = (time: string) => {
    const date = new Date(time);
    return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' });
  };

  const formatValue = (value: number) => {
    return `$${value.toFixed(0)}`;
  };

  return (
    <div className="bg-[#0a0b0d] rounded-lg border border-gray-800 p-4">
      <div className="mb-4">
        <div className="flex items-baseline justify-between mb-2">
          <h3 className="text-lg font-bold text-white">账户总值</h3>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-xs text-gray-400">夏普比率</div>
              <div className="text-sm font-semibold text-blue-400">{stats.sharpeRatio}</div>
            </div>
            <div className="text-right">
              <div className="text-xs text-gray-400">最大回撤</div>
              <div className="text-sm font-semibold text-red-400">{stats.maxDrawdown}%</div>
            </div>
          </div>
        </div>
        <div className="flex items-baseline space-x-3">
          <span className="text-3xl font-bold text-white">
            ${stats.currentValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </span>
          <span className={`text-lg font-semibold ${stats.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {stats.change >= 0 ? '+' : ''}{stats.change.toFixed(2)}%
          </span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
          <XAxis
            dataKey="time"
            tickFormatter={formatTime}
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <YAxis
            tickFormatter={formatValue}
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1f2937',
              border: '1px solid #374151',
              borderRadius: '8px',
              color: '#fff'
            }}
            formatter={(value: number) => [`$${value.toFixed(2)}`, '账户价值']}
            labelFormatter={formatTime}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke="#3b82f6"
            strokeWidth={2}
            fill="url(#colorValue)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

