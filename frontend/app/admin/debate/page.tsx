"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface DebateHistory {
  id: number;
  decision_id: string;
  symbol: string;
  debate_rounds: number;
  final_recommendation: string;
  confidence: number;
  consensus_level: number;
  debate_duration_seconds: number;
  created_at: string;
}

export default function DebateHistoryPage() {
  const [debates, setDebates] = useState<DebateHistory[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [limit] = useState(20);
  const [symbolFilter, setSymbolFilter] = useState("");
  const [recommendationFilter, setRecommendationFilter] = useState("");

  useEffect(() => {
    fetchDebates();
  }, [page, symbolFilter, recommendationFilter]);

  const fetchDebates = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        skip: (page * limit).toString(),
        limit: limit.toString(),
      });

      if (symbolFilter) params.append("symbol", symbolFilter);
      if (recommendationFilter) params.append("recommendation", recommendationFilter);

      const response = await fetch(`/api/v1/debate/history?${params}`);
      const data = await response.json();

      setDebates(data.items || []);
      setTotal(data.total || 0);
    } catch (error) {
      console.error("Failed to fetch debates:", error);
    } finally {
      setLoading(false);
    }
  };

  const getRecommendationBadge = (recommendation: string) => {
    const colors = {
      BUY: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
      SELL: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
      HOLD: "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200",
    };
    return colors[recommendation as keyof typeof colors] || colors.HOLD;
  };

  const getConsensusColor = (level: number) => {
    if (level >= 0.7) return "text-green-600 dark:text-green-400";
    if (level >= 0.4) return "text-yellow-600 dark:text-yellow-400";
    return "text-red-600 dark:text-red-400";
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          辩论历史
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          查看多空辩论的历史记录和分析结果
        </p>
      </div>

      {/* 筛选器 */}
      <div className="mb-6 flex gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            币种
          </label>
          <select
            value={symbolFilter}
            onChange={(e) => {
              setSymbolFilter(e.target.value);
              setPage(0);
            }}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value="">全部</option>
            <option value="BTC">BTC</option>
            <option value="ETH">ETH</option>
            <option value="SOL">SOL</option>
            <option value="XRP">XRP</option>
            <option value="DOGE">DOGE</option>
            <option value="BNB">BNB</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            推荐结果
          </label>
          <select
            value={recommendationFilter}
            onChange={(e) => {
              setRecommendationFilter(e.target.value);
              setPage(0);
            }}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value="">全部</option>
            <option value="BUY">BUY</option>
            <option value="SELL">SELL</option>
            <option value="HOLD">HOLD</option>
          </select>
        </div>
      </div>

      {/* 表格 */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-500 dark:text-gray-400">
            加载中...
          </div>
        ) : debates.length === 0 ? (
          <div className="p-8 text-center text-gray-500 dark:text-gray-400">
            暂无辩论记录
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-900">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    时间
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    币种
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    推荐
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    置信度
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    共识度
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    轮次
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    耗时
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {debates.map((debate) => (
                  <tr key={debate.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                      {new Date(debate.created_at).toLocaleString("zh-CN")}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">
                      {debate.symbol}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-1 text-xs font-semibold rounded-full ${getRecommendationBadge(
                          debate.final_recommendation
                        )}`}
                      >
                        {debate.final_recommendation}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                      {(debate.confidence * 100).toFixed(0)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={getConsensusColor(debate.consensus_level)}>
                        {(debate.consensus_level * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                      {debate.debate_rounds}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                      {debate.debate_duration_seconds}s
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <Link
                        href={`/admin/debate/${debate.id}`}
                        className="text-blue-600 dark:text-blue-400 hover:underline"
                      >
                        查看详情
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* 分页 */}
        {total > limit && (
          <div className="px-6 py-4 flex items-center justify-between border-t border-gray-200 dark:border-gray-700">
            <div className="text-sm text-gray-700 dark:text-gray-300">
              显示 {page * limit + 1} - {Math.min((page + 1) * limit, total)} / 共 {total} 条
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(Math.max(0, page - 1))}
                disabled={page === 0}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-white"
              >
                上一页
              </button>
              <button
                onClick={() => setPage(page + 1)}
                disabled={(page + 1) * limit >= total}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-white"
              >
                下一页
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

