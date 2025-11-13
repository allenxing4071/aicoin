"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface TableInfo {
  name: string;
  display_name: string;
  description: string;
  record_count: number;
  endpoint: string;
}

interface SystemStats {
  total_trades: number;
  total_orders: number;
  total_ai_decisions: number;
  total_risk_events: number;
  latest_account_balance: string | null;
  latest_account_equity: string | null;
  database_size_mb: number | null;
  total_tables?: number;
}

interface PermissionLevel {
  level: string;
  name: string;
  max_position_pct: number;
  max_leverage: number;
  confidence_threshold: number;
  max_daily_trades: number;
}

export default function AdminPage() {
  const [tables, setTables] = useState<TableInfo[]>([]);
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [tradingEnabled, setTradingEnabled] = useState<boolean | null>(null);
  const [controlLoading, setControlLoading] = useState(false);
  const [permissionLevels, setPermissionLevels] = useState<PermissionLevel[]>([]);
  const [selectedLevel, setSelectedLevel] = useState<string>('L1');
  const [currentLevel, setCurrentLevel] = useState<string>('L1');
  const [totalTableCount, setTotalTableCount] = useState<number>(0);
  const [apiVersion, setApiVersion] = useState<string>('loading...');

  useEffect(() => {
    fetchData();
    fetchTradingStatus();
    fetchPermissionLevels();
    fetchCurrentLevel();
    fetchApiVersion();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // 获取表列表
      const tablesRes = await fetch("/api/v1/admin/tables");
      const tablesData = await tablesRes.json();
      if (tablesData.success) {
        setTables(tablesData.data);
      }

      // 获取统计信息
      const statsRes = await fetch("/api/v1/admin/stats");
      const statsData = await statsRes.json();
      if (statsData.success) {
        setStats(statsData.data);
        // 从统计信息中获取总表数
        if (statsData.data.total_tables) {
          setTotalTableCount(statsData.data.total_tables);
        }
      }
    } catch (error) {
      console.error("Failed to fetch admin data:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTradingStatus = async () => {
    try {
      const res = await fetch("/api/v1/constraints/trading-control");
      const data = await res.json();
      if (data.success) {
        setTradingEnabled(data.trading_enabled);
      }
    } catch (error) {
      console.error("Failed to fetch trading status:", error);
    }
  };

  const fetchPermissionLevels = async () => {
    try {
      const res = await fetch("/api/v1/admin/permissions/levels");
      const data = await res.json();
      if (data && Array.isArray(data)) {
        const levels = data.map((item: any) => ({
          level: item.level,
          name: item.name,
          max_position_pct: item.trading_params?.max_position_pct || 0,
          max_leverage: item.trading_params?.max_leverage || 1,
          confidence_threshold: item.trading_params?.confidence_threshold || 1,
          max_daily_trades: item.trading_params?.max_daily_trades || 0
        }));
        setPermissionLevels(levels);
      } else {
        // 使用默认权限等级
        setPermissionLevels(getDefaultPermissionLevels());
      }
    } catch (error) {
      console.error("Failed to fetch permission levels:", error);
      // 使用默认权限等级
      setPermissionLevels(getDefaultPermissionLevels());
    }
  };

  const getDefaultPermissionLevels = (): PermissionLevel[] => {
    return [
      { level: 'L0', name: '保护模式', max_position_pct: 0.0, max_leverage: 1, confidence_threshold: 1.0, max_daily_trades: 0 },
      { level: 'L1', name: '新手级', max_position_pct: 0.10, max_leverage: 2, confidence_threshold: 0.50, max_daily_trades: 10 },
      { level: 'L2', name: '成长级', max_position_pct: 0.12, max_leverage: 2, confidence_threshold: 0.75, max_daily_trades: 2 },
      { level: 'L3', name: '稳定级', max_position_pct: 0.15, max_leverage: 3, confidence_threshold: 0.70, max_daily_trades: 4 },
      { level: 'L4', name: '熟练级', max_position_pct: 0.20, max_leverage: 4, confidence_threshold: 0.65, max_daily_trades: 6 },
      { level: 'L5', name: '专家级', max_position_pct: 0.25, max_leverage: 5, confidence_threshold: 0.60, max_daily_trades: 999 },
    ];
  };

  const fetchCurrentLevel = async () => {
    try {
      const res = await fetch("/api/v1/ai/status");
      const data = await res.json();
      if (data.success && data.orchestrator?.permission_level) {
        setCurrentLevel(data.orchestrator.permission_level);
        setSelectedLevel(data.orchestrator.permission_level);
      }
    } catch (error) {
      console.error("Failed to fetch current level:", error);
    }
  };

  const fetchApiVersion = async () => {
    try {
      const res = await fetch("/openapi.json");
      const data = await res.json();
      if (data.info?.version) {
        setApiVersion(data.info.version);
      }
    } catch (error) {
      console.error("Failed to fetch API version:", error);
      setApiVersion('3.2.0'); // 默认值
    }
  };

  const handleToggleTrading = async (enable: boolean) => {
    setControlLoading(true);
    try {
      // 如果是启动交易，先设置权限等级
      if (enable && selectedLevel !== currentLevel) {
        await handleSetPermissionLevel(selectedLevel);
      }

      const res = await fetch("/api/v1/constraints/trading-control", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ trading_enabled: enable }),
      });
      
      const data = await res.json();
      
      if (data.success) {
        setTradingEnabled(enable);
        const levelInfo = permissionLevels.find(l => l.level === selectedLevel);
        alert(`✅ 交易功能已${enable ? '启动' : '停止'}！\n${enable ? `AI现在以 ${selectedLevel}（${levelInfo?.name}）权限等级运行\n• 最大仓位：${(levelInfo?.max_position_pct || 0) * 100}%\n• 最大杠杆：${levelInfo?.max_leverage}x\n• 置信度阈值：${(levelInfo?.confidence_threshold || 0) * 100}%\n• 每日最大交易：${levelInfo?.max_daily_trades}` : 'AI停止建仓，但可以平仓已有持仓。'}`);
      } else {
        alert(`❌ 操作失败：${data.message || '未知错误'}`);
      }
    } catch (error) {
      console.error("Failed to toggle trading:", error);
      alert(`❌ 操作失败：${error}`);
    } finally {
      setControlLoading(false);
    }
  };

  const handleSetPermissionLevel = async (level: string) => {
    try {
      // 设置为默认等级
      const res = await fetch(`/api/v1/admin/permissions/levels/${level}/set-default`, {
        method: "POST"
      });
      if (res.ok) {
        setCurrentLevel(level);
      }
    } catch (error) {
      console.error("Failed to set permission level:", error);
      throw error;
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
      {/* 交易控制区域 */}
      <div className="bg-gradient-to-r from-purple-50 to-indigo-50 border-2 border-purple-200 rounded-xl p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">🎮 交易控制中心</h2>
        <p className="text-gray-600 mb-4">控制AI是否可以建仓和平仓</p>
        
        {/* 当前状态 */}
        {tradingEnabled !== null && (
          <div className="flex items-center gap-2 mb-6">
            <div className={`w-3 h-3 rounded-full ${tradingEnabled ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></div>
            <span className={`font-semibold ${tradingEnabled ? 'text-green-700' : 'text-red-700'}`}>
              {tradingEnabled ? '✅ 交易已启用（可建仓/平仓）' : '⛔ 交易已停用（仅可平仓）'}
            </span>
          </div>
        )}

        {/* 控制按钮 */}
        <div className="flex items-center justify-between">
          {/* 权限等级选择 */}
          <div className="flex items-center gap-3">
            <label className="text-sm font-semibold text-gray-900">
              🔑 权限等级:
            </label>
            <select
              value={selectedLevel}
              onChange={(e) => setSelectedLevel(e.target.value)}
              className="px-4 py-2 border-2 border-purple-300 rounded-xl font-medium text-gray-900 focus:outline-none focus:border-purple-500"
              disabled={controlLoading}
            >
              {permissionLevels.length > 0 ? permissionLevels.map((level) => (
                <option key={level.level} value={level.level}>
                  {level.level} - {level.name}
                </option>
              )) : (
                <option value="L1">L1 - 新手级</option>
              )}
            </select>
            {currentLevel && (
              <span className="text-sm text-blue-700 font-semibold">
                (当前: {currentLevel})
              </span>
            )}
          </div>
          
          <div className="flex gap-4">
            <button
              onClick={() => handleToggleTrading(true)}
              disabled={controlLoading || tradingEnabled === true}
              className={`px-8 py-4 rounded-xl font-bold text-white shadow-lg transition-all transform hover:scale-105 ${
                tradingEnabled === true
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-green-600 hover:bg-green-700 active:scale-95'
              }`}
            >
              {controlLoading && tradingEnabled !== true ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  启动中...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  启动交易
                </span>
              )}
            </button>
            
            <button
              onClick={() => handleToggleTrading(false)}
              disabled={controlLoading || tradingEnabled === false}
              className={`px-8 py-4 rounded-xl font-bold text-white shadow-lg transition-all transform hover:scale-105 ${
                tradingEnabled === false
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-red-600 hover:bg-red-700 active:scale-95'
              }`}
            >
              {controlLoading && tradingEnabled !== false ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  停止中...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  停止交易
                </span>
              )}
            </button>
          </div>
        </div>
        
        <div className="mt-4 bg-white rounded-xl p-4 border border-purple-200">
          <h3 className="font-semibold text-gray-900 mb-2">💡 说明</h3>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• <strong>选择权限等级</strong>：先选择AI运行的权限等级（L0-L5），不同等级有不同的策略参数（仓位、杠杆、置信度、交易频率等）</li>
            <li>• <strong>启动交易</strong>：点击后AI将以选定等级的参数开始建仓和平仓</li>
            <li>• <strong>停止交易</strong>：AI停止建新仓，但可以平仓已有持仓（风控保护）</li>
            <li>• 提示：可以在<a href="/admin/permissions" className="text-blue-600 hover:underline">权限管理页面</a>查看和调整各等级的详细参数</li>
          </ul>
        </div>
      </div>

      {/* 系统统计 */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">系统统计</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="总交易数"
            value={stats?.total_trades || 0}
            color="blue"
          />
          <StatCard
            title="总订单数"
            value={stats?.total_orders || 0}
            color="green"
          />
          <StatCard
            title="AI决策数"
            value={stats?.total_ai_decisions || 0}
            color="purple"
          />
          <StatCard
            title="风控事件"
            value={stats?.total_risk_events || 0}
            color="red"
          />
        </div>

        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white rounded-xl shadow p-6">
            <div className="text-sm text-gray-500 mb-1">最新账户余额</div>
            <div className="text-2xl font-bold text-gray-900">
              {stats?.latest_account_balance !== null && stats?.latest_account_balance !== undefined 
                ? `$${parseFloat(String(stats.latest_account_balance)).toFixed(2)}`
                : <span className="text-gray-400 text-lg">获取中...</span>}
            </div>
          </div>
          <div className="bg-white rounded-xl shadow p-6">
            <div className="text-sm text-gray-500 mb-1">最新账户净值</div>
            <div className="text-2xl font-bold text-gray-900">
              {stats?.latest_account_equity !== null && stats?.latest_account_equity !== undefined 
                ? `$${parseFloat(String(stats.latest_account_equity)).toFixed(2)}`
                : <span className="text-gray-400 text-lg">获取中...</span>}
            </div>
          </div>
        </div>
      </div>

      {/* 数据表列表 */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">数据表</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {tables.map((table) => (
            <TableCard key={table.name} table={table} />
          ))}
        </div>
      </div>

      {/* 快速链接区域 */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">快速链接</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* 权限管理 */}
          <Link
            href="/admin/permissions"
            className="bg-gradient-to-br from-purple-50 to-indigo-50 border border-purple-200 rounded-xl p-6 hover:shadow-lg transition-shadow"
          >
            <div className="text-3xl mb-2">🔐</div>
            <h3 className="text-lg font-semibold text-purple-900 mb-2">权限管理</h3>
            <p className="text-sm text-purple-700">
              查看和管理AI权限等级（L0-L5）、升级条件和降级规则
            </p>
          </Link>

          {/* 三层记忆系统 */}
          <Link
            href="/admin/memory"
            className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-xl p-6 hover:shadow-lg transition-shadow"
          >
            <div className="text-3xl mb-2">🧠</div>
            <h3 className="text-lg font-semibold text-green-900 mb-2">三层记忆系统</h3>
            <p className="text-sm text-green-700">
              查看AI的短期记忆、长期记忆和知识库状态
            </p>
          </Link>

          {/* AI平台管理 */}
          <Link
            href="/admin/ai-platforms/intelligence"
            className="bg-gradient-to-br from-blue-50 to-cyan-50 border border-blue-200 rounded-xl p-6 hover:shadow-lg transition-shadow"
          >
            <div className="text-3xl mb-2">☁️</div>
            <h3 className="text-lg font-semibold text-blue-900 mb-2">AI平台管理</h3>
            <p className="text-sm text-blue-700">
              管理所有AI模型配置、成本监控和性能分析
            </p>
          </Link>

          {/* 情报中枢 */}
          <Link
            href="/admin/intelligence"
            className="bg-gradient-to-br from-orange-50 to-amber-50 border border-orange-200 rounded-xl p-6 hover:shadow-lg transition-shadow"
          >
            <div className="text-3xl mb-2">🕵️</div>
            <h3 className="text-lg font-semibold text-orange-900 mb-2">情报中枢</h3>
            <p className="text-sm text-orange-700">
              管理所有情报数据源（新闻、巨鲸、链上、KOL、聪明钱）
            </p>
          </Link>

          {/* 成本监控 */}
          <Link
            href="/admin/ai-cost"
            className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-xl p-6 hover:shadow-lg transition-shadow"
          >
            <div className="text-3xl mb-2">💰</div>
            <h3 className="text-lg font-semibold text-green-900 mb-2">成本监控</h3>
            <p className="text-sm text-green-700">
              实时监控AI平台调用成本和预算管理
            </p>
          </Link>
        </div>
      </div>

      {/* 底部区域：API文档 + 数据库管理 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 左侧：API文档 */}
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">
            📚 API 文档
          </h3>
          <p className="text-blue-700 mb-4">
            查看完整的 API 接口文档和在线测试
          </p>
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <a
                href="/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="block px-4 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl hover:from-blue-600 hover:to-blue-700 transition-colors text-center font-medium"
              >
                Swagger UI
              </a>
              <a
                href="/redoc"
                target="_blank"
                rel="noopener noreferrer"
                className="block px-4 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl hover:from-blue-600 hover:to-blue-700 transition-colors text-center font-medium"
              >
                ReDoc
              </a>
            </div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="bg-white rounded p-3 border border-blue-200">
                <div className="text-gray-600 text-xs">API版本</div>
                <div className="font-semibold text-blue-800">v{apiVersion}</div>
              </div>
              <div className="bg-white rounded p-3 border border-blue-200">
                <div className="text-gray-600 text-xs">文档状态</div>
                <div className="font-semibold text-blue-600">● 在线</div>
              </div>
              <div className="bg-white rounded p-3 border border-blue-200">
                <div className="text-gray-600 text-xs">接口协议</div>
                <div className="font-semibold text-blue-800">REST API</div>
              </div>
              <div className="bg-white rounded p-3 border border-blue-200">
                <div className="text-gray-600 text-xs">认证方式</div>
                <div className="font-semibold text-blue-800">Token</div>
              </div>
            </div>
          </div>
        </div>

        {/* 右侧：数据库管理 */}
        <div className="bg-green-50 border border-green-200 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-green-900 mb-2">
            📊 数据库管理
          </h3>
          <p className="text-green-700 mb-4">
            查看数据库连接、表结构和数据内容
          </p>
          <div className="space-y-3">
            <Link
              href="/admin/database"
              className="block w-full px-4 py-3 bg-green-600 text-white rounded-xl hover:bg-green-700 transition-colors text-center font-medium"
            >
              🔍 打开数据库管理器
            </Link>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="bg-white rounded p-3 border border-green-200">
                <div className="text-gray-600 text-xs">数据库类型</div>
                <div className="font-semibold text-green-800">PostgreSQL</div>
              </div>
              <div className="bg-white rounded p-3 border border-green-200">
                <div className="text-gray-600 text-xs">连接状态</div>
                <div className="font-semibold text-green-600">● 已连接</div>
              </div>
              <div className="bg-white rounded p-3 border border-green-200">
                <div className="text-gray-600 text-xs">数据表数量</div>
                <div className="font-semibold text-green-800">{totalTableCount || tables.length} 张</div>
              </div>
              <div className="bg-white rounded p-3 border border-green-200">
                <div className="text-gray-600 text-xs">总记录数</div>
                <div className="font-semibold text-green-800">
                  {tables.reduce((sum, t) => sum + t.record_count, 0)} 条
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  color,
}: {
  title: string;
  value: number;
  color: string;
}) {
  const colorClasses = {
    blue: "bg-blue-50 text-blue-700",
    green: "bg-green-50 text-green-700",
    purple: "bg-purple-50 text-purple-700",
    red: "bg-red-50 text-red-700",
  };

  return (
    <div className="bg-white rounded-xl shadow p-6">
      <div className="text-sm text-gray-500 mb-1">{title}</div>
      <div className={`text-3xl font-bold ${colorClasses[color as keyof typeof colorClasses]}`}>
        {value.toLocaleString()}
      </div>
    </div>
  );
}

function TableCard({ table }: { table: TableInfo }) {
  const getTablePath = (name: string) => {
    const pathMap: { [key: string]: string } = {
      trades: "/admin/trades",
      orders: "/admin/orders",
      account_snapshots: "/admin/accounts",
      ai_decisions: "/admin/ai-decisions",
      market_data_kline: "/admin/market-data",
      risk_events: "/admin/risk-events",
    };
    return pathMap[name] || "/admin";
  };

  return (
    <Link
      href={getTablePath(table.name)}
      className="block bg-white rounded-xl shadow hover:shadow-lg transition-shadow p-6"
    >
      <div className="flex items-start justify-between mb-2">
        <h3 className="text-lg font-semibold text-gray-900">
          {table.display_name}
        </h3>
        <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded">
          {table.record_count?.toLocaleString() || 0} 条
        </span>
      </div>
      <p className="text-sm text-gray-600">{table.description}</p>
    </Link>
  );
}

