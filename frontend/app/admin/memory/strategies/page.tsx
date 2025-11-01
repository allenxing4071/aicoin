"use client";

import { useEffect, useState } from "react";
import DataTable from "@/app/components/admin/DataTable";
import FilterBar from "@/app/components/admin/FilterBar";

export default function AIStrategiesPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 50,
    total: 0,
    totalPages: 0,
  });
  const [filters, setFilters] = useState<Record<string, any>>({});

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pagination.page, pagination.pageSize]);

  useEffect(() => {
    if (Object.keys(filters).length > 0) {
      fetchData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: String(pagination.page),
        page_size: String(pagination.pageSize),
        ...filters,
      });

      const response = await fetch(
        `http://localhost:8000/api/v1/admin/memory/strategies?${params}`
      );
      const result = await response.json();

      if (result.success) {
        setData(result.data);
        if (result.meta) {
          setPagination({
            page: result.meta.page,
            pageSize: result.meta.page_size,
            total: result.meta.total,
            totalPages: result.meta.total_pages,
          });
        }
      }
    } catch (error) {
      console.error("Failed to fetch AI strategies:", error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { key: "id", label: "ID" },
    {
      key: "strategy_name",
      label: "策略名称",
      render: (value: string) => (
        <div className="font-medium text-gray-900">{value}</div>
      ),
    },
    {
      key: "status",
      label: "状态",
      render: (value: string) => {
        const statusMap: Record<string, { label: string; color: string }> = {
          active: { label: "活跃", color: "bg-green-100 text-green-800" },
          deprecated: { label: "已弃用", color: "bg-gray-100 text-gray-800" },
          testing: { label: "测试中", color: "bg-yellow-100 text-yellow-800" },
        };
        const status = statusMap[value] || {
          label: value,
          color: "bg-gray-100 text-gray-800",
        };
        return (
          <span className={`px-2 py-1 text-xs font-medium rounded ${status.color}`}>
            {status.label}
          </span>
        );
      },
    },
    { key: "market_regime", label: "市场状态" },
    { key: "total_trades", label: "总交易数" },
    { key: "winning_trades", label: "盈利交易" },
    {
      key: "win_rate",
      label: "胜率",
      render: (value: number) => (
        <span
          className={
            value >= 0.6
              ? "text-green-600 font-medium"
              : value >= 0.4
              ? "text-yellow-600"
              : "text-red-600"
          }
        >
          {(value * 100).toFixed(1)}%
        </span>
      ),
    },
    {
      key: "avg_pnl",
      label: "平均盈亏",
      render: (value: number) => (
        <span className={value >= 0 ? "text-green-600" : "text-red-600"}>
          ${value.toFixed(2)}
        </span>
      ),
    },
    {
      key: "sharpe_ratio",
      label: "夏普比率",
      render: (value: number) => (
        <span
          className={
            value >= 1.5
              ? "text-green-600 font-medium"
              : value >= 1.0
              ? "text-blue-600"
              : "text-gray-600"
          }
        >
          {value.toFixed(2)}
        </span>
      ),
    },
    {
      key: "max_drawdown",
      label: "最大回撤",
      render: (value: number) => (
        <span className="text-red-600">{(value * 100).toFixed(2)}%</span>
      ),
    },
    {
      key: "last_used_at",
      label: "最后使用",
      render: (value: string | null) =>
        value ? new Date(value).toLocaleString("zh-CN") : "-",
    },
  ];

  const filterFields = [
    {
      key: "status",
      label: "策略状态",
      type: "select" as const,
      options: [
        { value: "active", label: "活跃" },
        { value: "deprecated", label: "已弃用" },
        { value: "testing", label: "测试中" },
      ],
    },
    { key: "market_regime", label: "市场状态", type: "text" as const },
  ];

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          📊 AI策略评估
        </h1>
        <p className="text-gray-600">
          各交易策略的性能评估,包含胜率、夏普比率等关键指标
        </p>
      </div>

      <FilterBar
        fields={filterFields}
        onFilter={(newFilters) => {
          setFilters(newFilters);
          setPagination((prev) => ({ ...prev, page: 1 }));
        }}
        onReset={() => {
          setFilters({});
          setPagination((prev) => ({ ...prev, page: 1 }));
        }}
      />

      <DataTable
        columns={columns}
        data={data}
        loading={loading}
        pagination={pagination}
        onPageChange={(page) =>
          setPagination((prev) => ({ ...prev, page }))
        }
        onPageSizeChange={(pageSize) =>
          setPagination((prev) => ({ ...prev, page: 1, pageSize }))
        }
      />
    </div>
  );
}

