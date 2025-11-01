"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface MemoryOverview {
  short_term_memory: {
    recent_decisions_count: number;
    today_trade_count: number;
    performance_7d: any;
    performance_30d: any;
  };
  long_term_memory: {
    total_vectors: number;
    collection_status: string;
    index_size_mb: number;
  };
  knowledge_base_lessons: number;
  knowledge_base_strategies: number;
  knowledge_base_patterns: number;
}

export default function MemorySystemPage() {
  const [overview, setOverview] = useState<MemoryOverview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOverview();
  }, []);

  const fetchOverview = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        "http://localhost:8000/api/v1/admin/memory/overview"
      );
      const result = await response.json();
      if (result.success) {
        setOverview(result.data);
      }
    } catch (error) {
      console.error("Failed to fetch memory overview:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          三层记忆系统
        </h1>
        <p className="text-gray-600">
          查看AI的短期记忆(Redis)、长期记忆(Qdrant)和知识库(PostgreSQL)
        </p>
      </div>

      {/* 系统架构图 */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border border-blue-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          📐 三层记忆架构
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4 shadow">
            <div className="text-sm font-medium text-blue-600 mb-2">
              L1: 短期记忆 (Redis)
            </div>
            <div className="text-xs text-gray-600 mb-3">
              最近100个决策、当日统计、实时性能
            </div>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-500">最近决策:</span>
                <span className="font-medium">
                  {overview?.short_term_memory.recent_decisions_count || 0} 条
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">今日交易:</span>
                <span className="font-medium">
                  {overview?.short_term_memory.today_trade_count || 0} 次
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">查询速度:</span>
                <span className="text-green-600 font-medium">&lt;10ms</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 shadow">
            <div className="text-sm font-medium text-purple-600 mb-2">
              L2: 长期记忆 (Qdrant)
            </div>
            <div className="text-xs text-gray-600 mb-3">
              向量化历史决策、相似情况检索
            </div>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-500">向量数量:</span>
                <span className="font-medium">
                  {overview?.long_term_memory.total_vectors || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">状态:</span>
                <span
                  className={`font-medium ${
                    overview?.long_term_memory.collection_status === "ready"
                      ? "text-green-600"
                      : "text-yellow-600"
                  }`}
                >
                  {overview?.long_term_memory.collection_status || "未初始化"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">查询速度:</span>
                <span className="text-green-600 font-medium">&lt;100ms</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 shadow">
            <div className="text-sm font-medium text-green-600 mb-2">
              L3: 知识库 (PostgreSQL)
            </div>
            <div className="text-xs text-gray-600 mb-3">
              经验教训、策略评估、市场模式
            </div>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-500">经验教训:</span>
                <span className="font-medium">
                  {overview?.knowledge_base_lessons || 0} 条
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">策略评估:</span>
                <span className="font-medium">
                  {overview?.knowledge_base_strategies || 0} 个
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">市场模式:</span>
                <span className="font-medium">
                  {overview?.knowledge_base_patterns || 0} 个
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 知识库数据表 */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          📚 知识库 (L3) - 可查看数据
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            href="/admin/memory/lessons"
            className="block bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6"
          >
            <div className="flex items-start justify-between mb-2">
              <h3 className="text-lg font-semibold text-gray-900">
                📗 AI经验教训
              </h3>
              <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
                {overview?.knowledge_base_lessons || 0} 条
              </span>
            </div>
            <p className="text-sm text-gray-600 mb-3">
              从历史交易中提取的成功经验和失败教训
            </p>
            <div className="text-xs text-gray-500">
              包含: 成功案例、失败教训、市场洞察
            </div>
          </Link>

          <Link
            href="/admin/memory/strategies"
            className="block bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6"
          >
            <div className="flex items-start justify-between mb-2">
              <h3 className="text-lg font-semibold text-gray-900">
                📊 AI策略评估
              </h3>
              <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                {overview?.knowledge_base_strategies || 0} 个
              </span>
            </div>
            <p className="text-sm text-gray-600 mb-3">
              各交易策略的性能评估和统计数据
            </p>
            <div className="text-xs text-gray-500">
              指标: 胜率、夏普比率、最大回撤等
            </div>
          </Link>

          <Link
            href="/admin/memory/patterns"
            className="block bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6"
          >
            <div className="flex items-start justify-between mb-2">
              <h3 className="text-lg font-semibold text-gray-900">
                📈 市场模式
              </h3>
              <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded">
                {overview?.knowledge_base_patterns || 0} 个
              </span>
            </div>
            <p className="text-sm text-gray-600 mb-3">
              识别的市场模式和历史表现统计
            </p>
            <div className="text-xs text-gray-500">
              类型: 趋势反转、突破、盘整等
            </div>
          </Link>
        </div>
      </div>

      {/* 说明文档 */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-yellow-900 mb-3">
          💡 关于三层记忆系统
        </h3>
        <div className="space-y-2 text-sm text-yellow-800">
          <p>
            <strong>L1 短期记忆 (Redis)</strong>: 存储最近的决策和实时性能指标,提供毫秒级查询速度。
          </p>
          <p>
            <strong>L2 长期记忆 (Qdrant)</strong>: 将所有历史决策向量化存储,支持语义搜索相似市场情况。
          </p>
          <p>
            <strong>L3 知识库 (PostgreSQL)</strong>: 存储结构化的经验教训、策略评估和市场模式,支持复杂查询和统计分析。
          </p>
          <p className="mt-3 pt-3 border-t border-yellow-300">
            <strong>核心价值</strong>: AI可以从历史中学习,避免重复错误,参考成功经验做出更明智的决策。
          </p>
        </div>
      </div>
    </div>
  );
}

