"use client";

import { useState, useEffect } from "react";

interface MemoryStats {
  bull_memory_count: number;
  bear_memory_count: number;
  manager_memory_count: number;
  total_memory_count: number;
}

interface RateLimitStatus {
  daily_count: number;
  daily_limit: number;
  daily_remaining: number;
  hourly_count: number;
  hourly_limit: number;
  hourly_remaining: number;
}

export default function DebateMemoryPage() {
  const [memoryStats, setMemoryStats] = useState<MemoryStats>({
    bull_memory_count: 0,
    bear_memory_count: 0,
    manager_memory_count: 0,
    total_memory_count: 0,
  });
  const [rateLimitStatus, setRateLimitStatus] = useState<RateLimitStatus | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchMemoryStats();
    fetchRateLimitStatus();
  }, []);

  const fetchMemoryStats = async () => {
    try {
      const response = await fetch("/api/v1/debate/memory/stats");
      const data = await response.json();
      setMemoryStats(data);
    } catch (error) {
      console.error("Failed to fetch memory stats:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRateLimitStatus = async () => {
    try {
      const response = await fetch("/api/v1/debate/rate-limit");
      const data = await response.json();
      if (data.success) {
        setRateLimitStatus(data.data);
      }
    } catch (error) {
      console.error("Failed to fetch rate limit status:", error);
    }
  };

  const handleClearMemory = async () => {
    if (
      !confirm(
        "⚠️  警告：这将删除所有辩论记忆，无法恢复！\n\n确定要继续吗？"
      )
    ) {
      return;
    }

    try {
      const response = await fetch("/api/v1/debate/memory", {
        method: "DELETE",
      });
      const data = await response.json();

      if (data.success) {
        setMessage("记忆已清空");
        await fetchMemoryStats();
      } else {
        setMessage(data.message || "清空失败");
      }
    } catch (error) {
      console.error("Failed to clear memory:", error);
      setMessage("清空失败");
    } finally {
      setTimeout(() => setMessage(""), 3000);
    }
  };

  const handleResetRateLimit = async () => {
    if (!confirm("确定要重置限流计数吗？")) {
      return;
    }

    try {
      const response = await fetch("/api/v1/debate/rate-limit/reset", {
        method: "POST",
      });
      const data = await response.json();

      if (data.success) {
        setMessage("限流计数已重置");
        await fetchRateLimitStatus();
      } else {
        setMessage("重置失败");
      }
    } catch (error) {
      console.error("Failed to reset rate limit:", error);
      setMessage("重置失败");
    } finally {
      setTimeout(() => setMessage(""), 3000);
    }
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

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          记忆管理
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          管理辩论系统的历史记忆和限流状态
        </p>
      </div>

      {message && (
        <div
          className={`mb-4 p-4 rounded-lg ${
            message.includes("失败")
              ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
              : "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
          }`}
        >
          {message}
        </div>
      )}

      {/* 记忆统计 */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          记忆统计
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-4xl mb-2">🐂</div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              多头记忆
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mt-2">
              {memoryStats.bull_memory_count}
            </div>
          </div>

          <div className="text-center">
            <div className="text-4xl mb-2">🐻</div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              空头记忆
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mt-2">
              {memoryStats.bear_memory_count}
            </div>
          </div>

          <div className="text-center">
            <div className="text-4xl mb-2">📊</div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              经理记忆
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mt-2">
              {memoryStats.manager_memory_count}
            </div>
          </div>

          <div className="text-center">
            <div className="text-4xl mb-2">💾</div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              总记忆数
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mt-2">
              {memoryStats.total_memory_count}
            </div>
          </div>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={handleClearMemory}
            className="px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium"
          >
            清空所有记忆
          </button>
        </div>
      </div>

      {/* 限流状态 */}
      {rateLimitStatus && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            限流状态
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 每日限制 */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  每日辩论次数
                </span>
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {rateLimitStatus.daily_count} / {rateLimitStatus.daily_limit}
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{
                    width: `${
                      (rateLimitStatus.daily_count /
                        rateLimitStatus.daily_limit) *
                      100
                    }%`,
                  }}
                ></div>
              </div>
              <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                剩余: {rateLimitStatus.daily_remaining} 次
              </div>
            </div>

            {/* 每小时限制 */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  每小时辩论次数
                </span>
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {rateLimitStatus.hourly_count} /{" "}
                  {rateLimitStatus.hourly_limit}
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-green-600 h-2 rounded-full"
                  style={{
                    width: `${
                      (rateLimitStatus.hourly_count /
                        rateLimitStatus.hourly_limit) *
                      100
                    }%`,
                  }}
                ></div>
              </div>
              <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                剩余: {rateLimitStatus.hourly_remaining} 次
              </div>
            </div>
          </div>

          <div className="mt-6 flex justify-end">
            <button
              onClick={handleResetRateLimit}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
            >
              重置限流计数
            </button>
          </div>
        </div>
      )}

      {/* 说明 */}
      <div className="mt-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-900 dark:text-blue-200 mb-2">
          💡 关于记忆系统
        </h3>
        <ul className="text-sm text-blue-800 dark:text-blue-300 space-y-1">
          <li>• 记忆系统使用 Qdrant 向量数据库存储历史辩论经验</li>
          <li>• Bull/Bear/Manager 分析师各有独立的记忆空间</li>
          <li>• 记忆会在辩论时自动检索相似情况，帮助改进决策</li>
          <li>• 清空记忆将删除所有历史经验，谨慎操作</li>
        </ul>
      </div>
    </div>
  );
}

