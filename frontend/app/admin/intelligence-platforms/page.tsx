"use client";

import { useState, useEffect } from "react";

interface CloudPlatform {
  id: number;
  name: string;
  provider: string;
  platform_type: string;
  enabled: boolean;
  base_url: string;
  performance: {
    total_calls: number;
    success_rate: number;
    avg_response_time: number;
    total_cost: number;
  };
  health: {
    status: string;
    last_check: string | null;
  };
}

export default function IntelligencePlatformsPage() {
  const [platforms, setPlatforms] = useState<CloudPlatform[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);

  useEffect(() => {
    fetchPlatforms();
  }, []);

  const fetchPlatforms = async () => {
    try {
      const response = await fetch("/api/v1/intelligence/platforms");
      const data = await response.json();
      setPlatforms(data.platforms || []);
    } catch (error) {
      console.error("获取平台列表失败:", error);
    } finally {
      setLoading(false);
    }
  };

  const togglePlatform = async (id: number, enabled: boolean) => {
    try {
      await fetch(`/api/v1/intelligence/platforms/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled })
      });
      fetchPlatforms();
    } catch (error) {
      console.error("切换平台状态失败:", error);
    }
  };

  const getProviderIcon = (provider: string) => {
    const icons: Record<string, string> = {
      baidu: "🟦",
      tencent: "🟩",
      volcano: "🟧",
      aws: "🟨"
    };
    return icons[provider] || "⚪";
  };

  if (loading) {
    return <div className="p-6">加载中...</div>;
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Qwen情报员 - 云平台管理</h1>
        <button
          onClick={() => setShowAddForm(true)}
          className="px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded hover:from-blue-600 hover:to-blue-700"
        >
          ➕ 添加平台
        </button>
      </div>

      {/* 平台列表 */}
      <div className="grid gap-4">
        {platforms.map((platform) => (
          <div key={platform.id} className="bg-white p-6 rounded-xl shadow border border-gray-200">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{getProviderIcon(platform.provider)}</span>
                  <h3 className="text-lg font-semibold">{platform.name}</h3>
                  <span className={`px-2 py-1 text-xs rounded ${
                    platform.enabled 
                      ? "bg-green-100 text-green-800" 
                      : "bg-gray-100 text-gray-800"
                  }`}>
                    {platform.enabled ? "✅ 启用" : "⏸️ 停用"}
                  </span>
                  {platform.health.status && (
                    <span className={`px-2 py-1 text-xs rounded ${
                      platform.health.status === "healthy"
                        ? "bg-green-100 text-green-800"
                        : "bg-red-100 text-red-800"
                    }`}>
                      {platform.health.status === "healthy" ? "🟢 健康" : "🔴 异常"}
                    </span>
                  )}
                </div>
                
                <div className="mt-2 text-sm text-gray-600">
                  <p>提供商: {platform.provider}</p>
                  <p>类型: {platform.platform_type}</p>
                  <p>API地址: {platform.base_url}</p>
                </div>

                <div className="mt-3 grid grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">调用次数</p>
                    <p className="font-semibold">{platform.performance.total_calls}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">成功率</p>
                    <p className="font-semibold">
                      {(platform.performance.success_rate * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500">平均响应时间</p>
                    <p className="font-semibold">
                      {platform.performance.avg_response_time?.toFixed(2) || "N/A"}s
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500">累计成本</p>
                    <p className="font-semibold">
                      ${platform.performance.total_cost.toFixed(4)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex gap-2 ml-4">
                <button
                  onClick={() => togglePlatform(platform.id, !platform.enabled)}
                  className={`px-3 py-1 rounded text-sm ${
                    platform.enabled
                      ? "bg-yellow-100 text-yellow-800 hover:bg-yellow-200"
                      : "bg-green-100 text-green-800 hover:bg-green-200"
                  }`}
                >
                  {platform.enabled ? "停用" : "启用"}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {platforms.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p>暂无平台配置</p>
          <p className="text-sm mt-2">点击"添加平台"按钮添加第一个云平台</p>
        </div>
      )}

      {/* 添加平台表单（简化版） */}
      {showAddForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-xl max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">添加新平台</h2>
            <p className="text-sm text-gray-600 mb-4">
              添加AWS或其他云平台需要配置API密钥和端点地址
            </p>
            <div className="flex gap-2">
              <button 
                onClick={() => setShowAddForm(false)}
                className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
              >
                取消
              </button>
              <button 
                className="px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded hover:from-blue-600 hover:to-blue-700"
              >
                添加
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

