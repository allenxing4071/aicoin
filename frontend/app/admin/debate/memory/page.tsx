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
    <div className="space-y-6">
      {/* 标题区域 - 使用渐变背景 */}
      <div className="bg-gradient-to-r from-orange-50 to-amber-50 border border-orange-200 rounded-xl p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🧠 记忆管理
        </h1>
        <p className="text-gray-600">
          管理辩论系统的历史记忆和限流状态
        </p>
      </div>

      {/* 消息提示 */}
      {message && (
        <div
          className={`p-4 rounded-xl font-semibold shadow-lg ${
            message.includes("失败")
              ? "bg-gradient-to-r from-red-50 to-pink-50 border border-red-200 text-red-800"
              : "bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 text-green-800"
          }`}
        >
          {message}
        </div>
      )}

      {/* 记忆统计 - 使用彩色渐变卡片 */}
      <div className="bg-gradient-to-br from-purple-50 to-indigo-50 border border-purple-200 rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-bold mb-4" style={{ color: '#000000' }}>
          记忆统计
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-4xl mb-2">🐂</div>
            <div className="text-sm font-bold" style={{ color: '#000000' }}>
              多头记忆
            </div>
            <div className="text-2xl font-bold mt-2" style={{ color: '#000000' }}>
              {memoryStats.bull_memory_count}
            </div>
          </div>

          <div className="text-center">
            <div className="text-4xl mb-2">🐻</div>
            <div className="text-sm font-bold" style={{ color: '#000000' }}>
              空头记忆
            </div>
            <div className="text-2xl font-bold mt-2" style={{ color: '#000000' }}>
              {memoryStats.bear_memory_count}
            </div>
          </div>

          <div className="text-center">
            <div className="text-4xl mb-2">📊</div>
            <div className="text-sm font-bold" style={{ color: '#000000' }}>
              经理记忆
            </div>
            <div className="text-2xl font-bold mt-2" style={{ color: '#000000' }}>
              {memoryStats.manager_memory_count}
            </div>
          </div>

          <div className="text-center">
            <div className="text-4xl mb-2">💾</div>
            <div className="text-sm font-bold" style={{ color: '#000000' }}>
              总记忆数
            </div>
            <div className="text-2xl font-bold mt-2" style={{ color: '#000000' }}>
              {memoryStats.total_memory_count}
            </div>
          </div>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={handleClearMemory}
            className="px-8 py-3 bg-red-600 hover:bg-red-700 text-white rounded-xl font-bold shadow-lg transition-all transform hover:scale-105 active:scale-95"
          >
            清空所有记忆
          </button>
        </div>
      </div>

      {/* 限流状态 - 使用白色卡片 */}
      {rateLimitStatus && (
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            限流状态
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 每日限制 */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-bold dark:text-gray-300" style={{ color: '#111827' }}>
                  每日辩论次数
                </span>
                <span className="text-sm font-bold text-gray-900 dark:text-white">
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
              <div className="mt-1 text-xs font-bold dark:text-gray-400" style={{ color: '#374151' }}>
                剩余: {rateLimitStatus.daily_remaining} 次
              </div>
            </div>

            {/* 每小时限制 */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-bold dark:text-gray-300" style={{ color: '#111827' }}>
                  每小时辩论次数
                </span>
                <span className="text-sm font-bold text-gray-900 dark:text-white">
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
              <div className="mt-1 text-xs font-bold dark:text-gray-400" style={{ color: '#374151' }}>
                剩余: {rateLimitStatus.hourly_remaining} 次
              </div>
            </div>
          </div>

          <div className="mt-6 flex justify-end">
            <button
              onClick={handleResetRateLimit}
              className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold shadow-lg transition-all transform hover:scale-105 active:scale-95"
            >
              重置限流计数
            </button>
          </div>
        </div>
      )}

      {/* 说明 - 使用渐变背景 */}
      <div className="bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-200 rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-3">
          💡 关于记忆系统
        </h3>
        <ul className="text-sm font-bold space-y-2" style={{ color: '#1f2937' }}>
          <li>• 记忆系统使用 Qdrant 向量数据库存储历史辩论经验</li>
          <li>• Bull/Bear/Manager 分别拥有各自独立的记忆空间</li>
          <li>• 记忆会在辩论时自动采集和回忆，帮助提升决策质量</li>
          <li>• 清空记忆将删除所有历史经验，谨慎操作</li>
        </ul>
      </div>
    </div>
  );
}

