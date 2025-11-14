"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";

interface DebateDetail {
  id: number;
  decision_id: string;
  symbol: string;
  debate_rounds: number;
  bull_arguments: string;
  bear_arguments: string;
  debate_full_history: string;
  final_recommendation: string;
  confidence: number;
  consensus_level: number;
  debate_duration_seconds: number;
  created_at: string;
}

export default function DebateDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [debate, setDebate] = useState<DebateDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (params.id) {
      fetchDebateDetail(params.id as string);
    }
  }, [params.id]);

  const fetchDebateDetail = async (id: string) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/debate/history/${id}`);
      if (!response.ok) throw new Error("Failed to fetch debate detail");
      const data = await response.json();
      setDebate(data);
    } catch (error) {
      console.error("Failed to fetch debate detail:", error);
    } finally {
      setLoading(false);
    }
  };

  const getRecommendationColor = (recommendation: string) => {
    const colors = {
      BUY: "text-green-600 dark:text-green-400",
      SELL: "text-red-600 dark:text-red-400",
      HOLD: "text-gray-600 dark:text-gray-400",
    };
    return colors[recommendation as keyof typeof colors] || colors.HOLD;
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="text-center text-gray-500 dark:text-gray-400">
          加载中...
        </div>
      </div>
    );
  }

  if (!debate) {
    return (
      <div className="p-6">
        <div className="text-center text-gray-500 dark:text-gray-400">
          辩论记录不存在
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* 返回按钮 */}
      <button
        onClick={() => router.back()}
        className="mb-4 text-blue-600 dark:text-blue-400 hover:underline"
      >
        ← 返回列表
      </button>

      {/* 辩论概览 */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          辩论详情 - {debate.symbol}
        </h1>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="text-sm text-gray-500 dark:text-gray-400">决策ID</div>
            <div className="text-sm font-mono text-gray-900 dark:text-gray-100">
              {debate.decision_id}
            </div>
          </div>

          <div>
            <div className="text-sm text-gray-500 dark:text-gray-400">最终推荐</div>
            <div className={`text-lg font-bold ${getRecommendationColor(debate.final_recommendation)}`}>
              {debate.final_recommendation}
            </div>
          </div>

          <div>
            <div className="text-sm text-gray-500 dark:text-gray-400">置信度</div>
            <div className="text-lg font-bold text-gray-900 dark:text-gray-100">
              {(debate.confidence * 100).toFixed(0)}%
            </div>
          </div>

          <div>
            <div className="text-sm text-gray-500 dark:text-gray-400">共识度</div>
            <div className="text-lg font-bold text-gray-900 dark:text-gray-100">
              {(debate.consensus_level * 100).toFixed(0)}%
            </div>
          </div>

          <div>
            <div className="text-sm text-gray-500 dark:text-gray-400">辩论轮次</div>
            <div className="text-lg font-bold text-gray-900 dark:text-gray-100">
              {debate.debate_rounds}
            </div>
          </div>

          <div>
            <div className="text-sm text-gray-500 dark:text-gray-400">耗时</div>
            <div className="text-lg font-bold text-gray-900 dark:text-gray-100">
              {debate.debate_duration_seconds}秒
            </div>
          </div>

          <div className="col-span-2">
            <div className="text-sm text-gray-500 dark:text-gray-400">创建时间</div>
            <div className="text-sm text-gray-900 dark:text-gray-100">
              {new Date(debate.created_at).toLocaleString("zh-CN")}
            </div>
          </div>
        </div>
      </div>

      {/* 辩论过程 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* 多头论点 */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-green-600 dark:text-green-400 mb-4 flex items-center">
            <span className="text-2xl mr-2">🐂</span>
            多头分析师 (Bull Analyst)
          </h2>
          <div className="prose dark:prose-invert max-w-none">
            <pre className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-900 p-4 rounded">
              {debate.bull_arguments || "无"}
            </pre>
          </div>
        </div>

        {/* 空头论点 */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-red-600 dark:text-red-400 mb-4 flex items-center">
            <span className="text-2xl mr-2">🐻</span>
            空头分析师 (Bear Analyst)
          </h2>
          <div className="prose dark:prose-invert max-w-none">
            <pre className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-900 p-4 rounded">
              {debate.bear_arguments || "无"}
            </pre>
          </div>
        </div>
      </div>

      {/* 完整辩论历史 */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center">
          <span className="text-2xl mr-2">📊</span>
          完整辩论历史
        </h2>
        <div className="prose dark:prose-invert max-w-none">
          <pre className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-900 p-4 rounded max-h-96 overflow-y-auto">
            {debate.debate_full_history || "无"}
          </pre>
        </div>
      </div>
    </div>
  );
}

