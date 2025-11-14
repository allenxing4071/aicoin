"use client";

import { useState, useEffect } from "react";

interface DebateConfig {
  id: number;
  config_key: string;
  config_value: string;
  description: string;
  updated_at: string;
}

export default function DebateConfigPage() {
  const [configs, setConfigs] = useState<DebateConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchConfigs();
  }, []);

  const fetchConfigs = async () => {
    setLoading(true);
    try {
      const response = await fetch("/api/v1/debate/config");
      const data = await response.json();
      setConfigs(data);
    } catch (error) {
      console.error("Failed to fetch configs:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async (configKey: string, newValue: string) => {
    setSaving(true);
    setMessage("");

    try {
      const response = await fetch(`/api/v1/debate/config/${configKey}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ config_value: newValue }),
      });

      if (!response.ok) throw new Error("Failed to update config");

      setMessage("配置已更新");
      await fetchConfigs();
    } catch (error) {
      console.error("Failed to update config:", error);
      setMessage("更新失败");
    } finally {
      setSaving(false);
      setTimeout(() => setMessage(""), 3000);
    }
  };

  const getConfigByKey = (key: string) => {
    return configs.find((c) => c.config_key === key);
  };

  const updateConfigValue = (key: string, value: string) => {
    setConfigs(
      configs.map((c) =>
        c.config_key === key ? { ...c, config_value: value } : c
      )
    );
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

  const debateEnabled = getConfigByKey("debate_enabled");
  const maxRounds = getConfigByKey("max_debate_rounds");
  const minPositionSize = getConfigByKey("min_position_size");
  const minPermissionLevel = getConfigByKey("min_permission_level");
  const timeoutSeconds = getConfigByKey("debate_timeout_seconds");
  const useMemory = getConfigByKey("use_memory");
  const dailyLimit = getConfigByKey("daily_limit");
  const hourlyLimit = getConfigByKey("hourly_limit");

  return (
    <div className="space-y-6">
      {/* 标题区域 - 使用渐变背景 */}
      <div className="bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-200 rounded-xl p-6">
        <h1 className="text-3xl font-bold mb-2" style={{ color: '#000000' }}>
          ⚙️ 辩论配置
        </h1>
        <p style={{ color: '#000000' }}>
          管理多空辩论系统的配置参数
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

      <div className="space-y-6">
        {/* 基础配置 */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4" style={{ color: '#000000' }}>
            基础配置
          </h2>

          <div className="space-y-4">
            {/* 启用辩论 */}
            {debateEnabled && (
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    启用辩论机制
                  </label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {debateEnabled.description}
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={debateEnabled.config_value === "true"}
                    onChange={(e) => {
                      const newValue = e.target.checked ? "true" : "false";
                      updateConfigValue("debate_enabled", newValue);
                      handleUpdate("debate_enabled", newValue);
                    }}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                </label>
              </div>
            )}

            {/* 最大辩论轮次 */}
            {maxRounds && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  最大辩论轮次
                </label>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                  {maxRounds.description}
                </p>
                <input
                  type="number"
                  min="1"
                  max="3"
                  value={maxRounds.config_value}
                  onChange={(e) =>
                    updateConfigValue("max_debate_rounds", e.target.value)
                  }
                  onBlur={(e) =>
                    handleUpdate("max_debate_rounds", e.target.value)
                  }
                  className="px-4 py-2 border-2 border-blue-200 rounded-xl bg-white text-gray-900 font-medium focus:outline-none focus:border-blue-500 transition-colors w-32"
                />
              </div>
            )}

            {/* 超时时间 */}
            {timeoutSeconds && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  超时时间（秒）
                </label>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                  {timeoutSeconds.description}
                </p>
                <input
                  type="number"
                  min="30"
                  max="300"
                  value={timeoutSeconds.config_value}
                  onChange={(e) =>
                    updateConfigValue("debate_timeout_seconds", e.target.value)
                  }
                  onBlur={(e) =>
                    handleUpdate("debate_timeout_seconds", e.target.value)
                  }
                  className="px-4 py-2 border-2 border-blue-200 rounded-xl bg-white text-gray-900 font-medium focus:outline-none focus:border-blue-500 transition-colors w-32"
                />
              </div>
            )}

            {/* 使用记忆 */}
            {useMemory && (
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    使用历史记忆
                  </label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {useMemory.description}
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={useMemory.config_value === "true"}
                    onChange={(e) => {
                      const newValue = e.target.checked ? "true" : "false";
                      updateConfigValue("use_memory", newValue);
                      handleUpdate("use_memory", newValue);
                    }}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                </label>
              </div>
            )}
          </div>
        </div>

        {/* 触发条件 */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4" style={{ color: '#000000' }}>
            触发条件
          </h2>

          <div className="space-y-4">
            {/* 最小仓位 */}
            {minPositionSize && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  最小仓位金额（USD）
                </label>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                  {minPositionSize.description}
                </p>
                <input
                  type="number"
                  min="0"
                  step="100"
                  value={minPositionSize.config_value}
                  onChange={(e) =>
                    updateConfigValue("min_position_size", e.target.value)
                  }
                  onBlur={(e) =>
                    handleUpdate("min_position_size", e.target.value)
                  }
                  className="px-4 py-2 border-2 border-blue-200 rounded-xl bg-white text-gray-900 font-medium focus:outline-none focus:border-blue-500 transition-colors w-48"
                />
              </div>
            )}

            {/* 最低权限等级 */}
            {minPermissionLevel && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  最低权限等级
                </label>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                  {minPermissionLevel.description}
                </p>
                <select
                  value={minPermissionLevel.config_value}
                  onChange={(e) => {
                    updateConfigValue("min_permission_level", e.target.value);
                    handleUpdate("min_permission_level", e.target.value);
                  }}
                  className="px-4 py-2 border-2 border-blue-200 rounded-xl bg-white text-gray-900 font-medium focus:outline-none focus:border-blue-500 transition-colors w-32"
                >
                  <option value="L0">L0</option>
                  <option value="L1">L1</option>
                  <option value="L2">L2</option>
                  <option value="L3">L3</option>
                  <option value="L4">L4</option>
                  <option value="L5">L5</option>
                </select>
              </div>
            )}
          </div>
        </div>

        {/* 限流配置 */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4" style={{ color: '#000000' }}>
            限流配置
          </h2>

          <div className="space-y-4">
            {/* 每日限制 */}
            {dailyLimit && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  每日最大辩论次数
                </label>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                  {dailyLimit.description}
                </p>
                <input
                  type="number"
                  min="1"
                  max="1000"
                  value={dailyLimit.config_value}
                  onChange={(e) =>
                    updateConfigValue("daily_limit", e.target.value)
                  }
                  onBlur={(e) => handleUpdate("daily_limit", e.target.value)}
                  className="px-4 py-2 border-2 border-blue-200 rounded-xl bg-white text-gray-900 font-medium focus:outline-none focus:border-blue-500 transition-colors w-32"
                />
              </div>
            )}

            {/* 每小时限制 */}
            {hourlyLimit && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  每小时最大辩论次数
                </label>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                  {hourlyLimit.description}
                </p>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={hourlyLimit.config_value}
                  onChange={(e) =>
                    updateConfigValue("hourly_limit", e.target.value)
                  }
                  onBlur={(e) => handleUpdate("hourly_limit", e.target.value)}
                  className="px-4 py-2 border-2 border-blue-200 rounded-xl bg-white text-gray-900 font-medium focus:outline-none focus:border-blue-500 transition-colors w-32"
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

