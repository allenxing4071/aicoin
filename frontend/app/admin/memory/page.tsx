"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import PageHeader from "../../components/common/PageHeader";

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

interface QwenStorageStats {
  l1_redis: {
    total_reports: number;
    cache_hit_rate: number;
    today_reports: number;
    avg_query_time_ms: number;
  };
  l2_analyzer: {
    sources_tracked: number;
    avg_weight: number;
    behavior_records: number;
    last_optimization: string | null;
  };
  l3_postgres: {
    total_reports: number;
    oldest_report: string;
    storage_size_mb: number;
  };
  l4_qdrant: {
    vectorized_count: number;
    collection_size: number;
    last_vectorization: string;
  };
}

interface LatestIntelligenceReport {
  timestamp: string;
  market_sentiment: string;
  sentiment_score: number;
  confidence: number;
  platform_contributions?: {
    [platform: string]: {
      confidence: number;
      sentiment: string;
    };
  };
  platform_consensus?: number;
  verification_metadata?: {
    platforms_used: number;
    cross_validation: boolean;
    consensus_threshold: number;
  };
  summary?: string;
}

type ViewMode = "deepseek" | "qwen";

export default function MemorySystemPage() {
  const [viewMode, setViewMode] = useState<ViewMode>("deepseek");
  const [overview, setOverview] = useState<MemoryOverview | null>(null);
  const [qwenStats, setQwenStats] = useState<QwenStorageStats | null>(null);
  const [latestReport, setLatestReport] = useState<LatestIntelligenceReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (viewMode === "deepseek") {
      fetchOverview();
    } else {
      fetchQwenStats();
      fetchLatestReport();
    }
  }, [viewMode]);

  const fetchOverview = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        "/api/v1/admin/memory/overview"
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

  const fetchQwenStats = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        "/api/v1/intelligence/storage/stats"
      );
      const result = await response.json();
      if (result.success) {
        setQwenStats(result.data);
      }
    } catch (error) {
      console.error("Failed to fetch Qwen storage stats:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchLatestReport = async () => {
    try {
      const response = await fetch(
        "/api/v1/intelligence/storage/reports/latest"
      );
      const result = await response.json();
      if (result.success && result.data) {
        setLatestReport(result.data);
      }
    } catch (error) {
      console.error("Failed to fetch latest intelligence report:", error);
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
    <div className="space-y-6">
      {/* 页头 - 统一风格 */}
      <PageHeader
        icon="🤖"
        title="AI记忆系统"
        description="查看DeepSeek交易员和Qwen情报员的多层存储状态"
        color="purple"
      />

      {/* 标签页切换 */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8" aria-label="Tabs">
          <button
            onClick={() => setViewMode("deepseek")}
            className={`${
              viewMode === "deepseek"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            🤖 DeepSeek交易员记忆 (3层)
          </button>
          <button
            onClick={() => setViewMode("qwen")}
            className={`${
              viewMode === "qwen"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            🕵️ Qwen情报员存储 (4层)
          </button>
        </nav>
      </div>

      {/* DeepSeek交易员视图 */}
      {viewMode === "deepseek" && (
        <>
          {/* 系统架构图 */}
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-200">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              📐 DeepSeek三层记忆架构
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-xl p-4 shadow">
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

          <div className="bg-white rounded-xl p-4 shadow">
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

          <div className="bg-white rounded-xl p-4 shadow">
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
            className="block bg-white rounded-xl shadow hover:shadow-lg transition-shadow p-6"
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
            className="block bg-white rounded-xl shadow hover:shadow-lg transition-shadow p-6"
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
            className="block bg-white rounded-xl shadow hover:shadow-lg transition-shadow p-6"
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
          <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-yellow-900 mb-3">
              💡 关于DeepSeek三层记忆系统
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
        </>
      )}

      {/* Qwen情报员视图 */}
      {viewMode === "qwen" && (
        <>
          {/* 系统架构图 */}
          <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-200">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              📐 Qwen四层智能存储架构
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* L1: Redis短期缓存 */}
              <div className="bg-white rounded-xl p-4 shadow">
                <div className="text-sm font-medium text-pink-600 mb-2">
                  L1: 短期缓存 (Redis)
                </div>
                <div className="text-xs text-gray-600 mb-3">
                  原始情报数据、快速访问
                </div>
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-500">最近情报:</span>
                    <span className="font-medium">
                      {qwenStats?.l1_redis.total_reports || 0} 条
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">缓存命中率:</span>
                    <span className="font-medium text-green-600">
                      {((qwenStats?.l1_redis.cache_hit_rate || 0) * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">今日新增:</span>
                    <span className="font-medium">
                      {qwenStats?.l1_redis.today_reports || 0} 条
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">查询速度:</span>
                    <span className="text-green-600 font-medium">
                      &lt;{qwenStats?.l1_redis.avg_query_time_ms || 10}ms
                    </span>
                  </div>
                </div>
              </div>

              {/* L2: 中期分析 */}
              <div className="bg-white rounded-xl p-4 shadow">
                <div className="text-sm font-medium text-blue-600 mb-2">
                  L2: 中期分析层
                </div>
                <div className="text-xs text-gray-600 mb-3">
                  行为分析、权重计算
                </div>
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-500">信息源:</span>
                    <span className="font-medium">
                      {qwenStats?.l2_analyzer.sources_tracked || 0} 个
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">平均权重:</span>
                    <span className="font-medium">
                      {qwenStats?.l2_analyzer.avg_weight.toFixed(2) || "0.00"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">行为记录:</span>
                    <span className="font-medium">
                      {qwenStats?.l2_analyzer.behavior_records || 0} 条
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">最后优化:</span>
                    <span className="text-green-600 font-medium text-[10px]">
                      {qwenStats?.l2_analyzer.last_optimization
                        ? new Date(qwenStats.l2_analyzer.last_optimization).toLocaleString("zh-CN", {
                            month: "numeric",
                            day: "numeric",
                            hour: "2-digit",
                            minute: "2-digit",
                          })
                        : "未知"}
                    </span>
                  </div>
                </div>
              </div>

              {/* L3: PostgreSQL长期存储 */}
              <div className="bg-white rounded-xl p-4 shadow">
                <div className="text-sm font-medium text-green-600 mb-2">
                  L3: 长期存储 (PG)
                </div>
                <div className="text-xs text-gray-600 mb-3">
                  历史情报报告、结构化查询
                </div>
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-500">历史报告:</span>
                    <span className="font-medium">
                      {qwenStats?.l3_postgres.total_reports || 0} 条
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">最早记录:</span>
                    <span className="font-medium text-[10px]">
                      {qwenStats?.l3_postgres.oldest_report
                        ? new Date(qwenStats.l3_postgres.oldest_report).toLocaleDateString("zh-CN")
                        : "无"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">存储大小:</span>
                    <span className="font-medium">
                      {qwenStats?.l3_postgres.storage_size_mb.toFixed(1) || "0.0"} MB
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">保留策略:</span>
                    <span className="text-blue-600 font-medium">永久</span>
                  </div>
                </div>
              </div>

              {/* L4: Qdrant向量知识库 */}
              <div className="bg-white rounded-xl p-4 shadow">
                <div className="text-sm font-medium text-purple-600 mb-2">
                  L4: 向量知识库
                </div>
                <div className="text-xs text-gray-600 mb-3">
                  语义搜索、模式识别
                </div>
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-500">向量化数量:</span>
                    <span className="font-medium">
                      {qwenStats?.l4_qdrant.vectorized_count || 0} 条
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">向量维度:</span>
                    <span className="font-medium">
                      {qwenStats?.l4_qdrant.collection_size || 1536}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">最后向量化:</span>
                    <span className="font-medium text-[10px]">
                      {qwenStats?.l4_qdrant.last_vectorization
                        ? new Date(qwenStats.l4_qdrant.last_vectorization).toLocaleString("zh-CN", {
                            month: "numeric",
                            day: "numeric",
                            hour: "2-digit",
                            minute: "2-digit",
                          })
                        : "未知"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">功能:</span>
                    <span className="text-purple-600 font-medium">相似检索</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 多平台验证信息 */}
          {latestReport?.platform_contributions && (
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">
                  🔄 多平台验证信息
                </h2>
                {latestReport.platform_consensus !== undefined && (
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-600">平台共识度:</span>
                    <span className={`text-2xl font-bold ${
                      latestReport.platform_consensus >= 0.8 ? 'text-green-600' :
                      latestReport.platform_consensus >= 0.6 ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {(latestReport.platform_consensus * 100).toFixed(1)}%
                    </span>
                  </div>
                )}
              </div>

              {/* 共识度进度条 */}
              {latestReport.platform_consensus !== undefined && (
                <div className="mb-4">
                  <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className={`h-full transition-all ${
                        latestReport.platform_consensus >= 0.8 ? 'bg-green-500' :
                        latestReport.platform_consensus >= 0.6 ? 'bg-yellow-500' :
                        'bg-red-500'
                      }`}
                      style={{ width: `${latestReport.platform_consensus * 100}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-600 mt-1">
                    {latestReport.platform_consensus >= 0.8 ? '✓ 高度共识 - 多平台分析结果高度一致' :
                     latestReport.platform_consensus >= 0.6 ? '⚠ 中度共识 - 多平台分析存在一定差异' :
                     '⚠ 低度共识 - 多平台分析结果分歧较大'}
                  </p>
                </div>
              )}

              {/* 平台贡献详情 */}
              <div className="bg-white rounded-lg p-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">平台贡献详情</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {Object.entries(latestReport.platform_contributions).map(([platform, data]) => (
                    <div key={platform} className="border rounded-lg p-3 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-gray-900 capitalize">{platform}</span>
                        <span className={`text-xs px-2 py-1 rounded ${
                          data.sentiment === 'BULLISH' ? 'bg-green-100 text-green-800' :
                          data.sentiment === 'BEARISH' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {data.sentiment}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-500">置信度:</span>
                        <div className="flex-1">
                          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-blue-500"
                              style={{ width: `${data.confidence * 100}%` }}
                            />
                          </div>
                        </div>
                        <span className="text-xs font-medium text-blue-600">
                          {(data.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 验证元数据 */}
              {latestReport.verification_metadata && (
                <div className="mt-3 flex items-center gap-4 text-xs text-gray-600">
                  <span>✓ 使用 {latestReport.verification_metadata.platforms_used} 个平台</span>
                  {latestReport.verification_metadata.cross_validation && (
                    <span>✓ 交叉验证已启用</span>
                  )}
                  <span>✓ 共识阈值: {(latestReport.verification_metadata.consensus_threshold * 100).toFixed(0)}%</span>
                </div>
              )}
            </div>
          )}

          {/* 说明文档 */}
          <div className="bg-purple-50 border border-purple-200 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-purple-900 mb-3">
              💡 关于Qwen四层智能存储系统
            </h3>
            <div className="space-y-2 text-sm text-purple-800">
              <p>
                <strong>L1 短期缓存 (Redis)</strong>: 存储原始情报数据和最近的情报报告，提供毫秒级快速访问，24小时TTL。
              </p>
              <p>
                <strong>L2 中期分析层</strong>: 分析用户行为，为信息源打分加权，计算有效性评分，支持智能学习。
              </p>
              <p>
                <strong>L3 长期存储 (PostgreSQL)</strong>: 永久存储历史情报报告，支持结构化查询、时间范围筛选和统计分析。
              </p>
              <p>
                <strong>L4 向量知识库 (Qdrant)</strong>: 将情报内容向量化，支持语义相似度检索和市场模式识别。
              </p>
              <p className="mt-3 pt-3 border-t border-purple-300">
                <strong>核心价值</strong>: 通过智能分层存储和持续学习，优化信息源优先级，减少无效检索，提高情报质量。
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

