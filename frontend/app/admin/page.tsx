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
}

export default function AdminPage() {
  const [tables, setTables] = useState<TableInfo[]>([]);
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // 获取表列表
      const tablesRes = await fetch("http://localhost:8000/api/v1/admin/tables");
      const tablesData = await tablesRes.json();
      if (tablesData.success) {
        setTables(tablesData.data);
      }

      // 获取统计信息
      const statsRes = await fetch("http://localhost:8000/api/v1/admin/stats");
      const statsData = await statsRes.json();
      if (statsData.success) {
        setStats(statsData.data);
      }
    } catch (error) {
      console.error("Failed to fetch admin data:", error);
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

        {stats?.latest_account_balance && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-500 mb-1">最新账户余额</div>
              <div className="text-2xl font-bold text-gray-900">
                ${parseFloat(stats.latest_account_balance).toFixed(2)}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-500 mb-1">最新账户净值</div>
              <div className="text-2xl font-bold text-gray-900">
                ${parseFloat(stats.latest_account_equity || "0").toFixed(2)}
              </div>
            </div>
          </div>
        )}
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

      {/* API文档链接 */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">
          API 文档
        </h3>
        <p className="text-blue-700 mb-4">
          查看完整的 API 接口文档和在线测试
        </p>
        <div className="flex space-x-4">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Swagger UI
          </a>
          <a
            href="http://localhost:8000/redoc"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            ReDoc
          </a>
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
    <div className="bg-white rounded-lg shadow p-6">
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
      className="block bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6"
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

