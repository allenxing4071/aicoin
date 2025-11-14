"use client";

import { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface DebateStatistics {
  id: number;
  date: string;
  total_debates: number;
  bull_wins: number;
  bear_wins: number;
  holds: number;
  avg_consensus: number;
  avg_confidence: number;
  avg_duration: number;
  created_at: string;
}

export default function DebateStatisticsPage() {
  const [stats, setStats] = useState<DebateStatistics[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(7);

  useEffect(() => {
    fetchStatistics();
  }, [days]);

  const fetchStatistics = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/debate/statistics?days=${days}`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error("Failed to fetch statistics:", error);
    } finally {
      setLoading(false);
    }
  };

  // 计算汇总数据
  const totalDebates = stats.reduce((sum, s) => sum + s.total_debates, 0);
  const totalBullWins = stats.reduce((sum, s) => sum + s.bull_wins, 0);
  const totalBearWins = stats.reduce((sum, s) => sum + s.bear_wins, 0);
  const totalHolds = stats.reduce((sum, s) => sum + s.holds, 0);

  // 饼图数据
  const pieData = [
    { name: "多头胜利", value: totalBullWins, color: "#10b981" },
    { name: "空头胜利", value: totalBearWins, color: "#ef4444" },
    { name: "持有", value: totalHolds, color: "#6b7280" },
  ];

  // 趋势图数据
  const trendData = stats.map((s) => ({
    date: new Date(s.date).toLocaleDateString("zh-CN", {
      month: "short",
      day: "numeric",
    }),
    共识度: (s.avg_consensus * 100).toFixed(1),
    置信度: (s.avg_confidence * 100).toFixed(1),
  }));

  // 时长分布数据
  const durationData = stats.map((s) => ({
    date: new Date(s.date).toLocaleDateString("zh-CN", {
      month: "short",
      day: "numeric",
    }),
    平均时长: s.avg_duration,
  }));

  if (loading) {
    return (
      <div className="p-6">
        <div className="text-center text-gray-500 dark:text-gray-400">
          加载中...
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            辩论统计
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            查看多空辩论的统计数据和趋势分析
          </p>
        </div>

        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        >
          <option value={7}>最近 7 天</option>
          <option value={14}>最近 14 天</option>
          <option value={30}>最近 30 天</option>
          <option value={90}>最近 90 天</option>
        </select>
      </div>

      {/* 汇总卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            总辩论次数
          </div>
          <div className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
            {totalDebates}
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            多头胜率
          </div>
          <div className="text-3xl font-bold text-green-600 dark:text-green-400 mt-2">
            {totalDebates > 0
              ? ((totalBullWins / totalDebates) * 100).toFixed(1)
              : 0}
            %
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            空头胜率
          </div>
          <div className="text-3xl font-bold text-red-600 dark:text-red-400 mt-2">
            {totalDebates > 0
              ? ((totalBearWins / totalDebates) * 100).toFixed(1)
              : 0}
            %
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            持有比例
          </div>
          <div className="text-3xl font-bold text-gray-600 dark:text-gray-400 mt-2">
            {totalDebates > 0
              ? ((totalHolds / totalDebates) * 100).toFixed(1)
              : 0}
            %
          </div>
        </div>
      </div>

      {/* 图表 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 推荐结果分布（饼图） */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            推荐结果分布
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) =>
                  `${name} ${(percent * 100).toFixed(0)}%`
                }
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* 共识度和置信度趋势（折线图） */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            共识度与置信度趋势
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="共识度"
                stroke="#3b82f6"
                strokeWidth={2}
              />
              <Line
                type="monotone"
                dataKey="置信度"
                stroke="#10b981"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* 辩论时长分布（柱状图） */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 lg:col-span-2">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            平均辩论时长（秒）
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={durationData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="平均时长" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

