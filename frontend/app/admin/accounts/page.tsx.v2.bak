"use client";

import { useEffect, useState } from "react";
import DataTable from "@/app/components/admin/DataTable";
import FilterBar from "@/app/components/admin/FilterBar";

export default function AccountsPage() {
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
  }, [pagination.page, pagination.pageSize, filters]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: String(pagination.page),
        page_size: String(pagination.pageSize),
        ...filters,
      });

      const response = await fetch(
        `http://localhost:8000/api/v1/admin/accounts?${params}`
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
      console.error("Failed to fetch accounts:", error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { key: "id", label: "ID" },
    {
      key: "balance",
      label: "余额",
      render: (value: string) => `$${parseFloat(value).toFixed(2)}`,
    },
    {
      key: "equity",
      label: "净值",
      render: (value: string) => `$${parseFloat(value).toFixed(2)}`,
    },
    {
      key: "unrealized_pnl",
      label: "未实现盈亏",
      render: (value: string | null) =>
        value ? (
          <span
            className={
              parseFloat(value) >= 0 ? "text-green-600" : "text-red-600"
            }
          >
            ${parseFloat(value).toFixed(2)}
          </span>
        ) : (
          "-"
        ),
    },
    {
      key: "realized_pnl",
      label: "已实现盈亏",
      render: (value: string | null) =>
        value ? (
          <span
            className={
              parseFloat(value) >= 0 ? "text-green-600" : "text-red-600"
            }
          >
            ${parseFloat(value).toFixed(2)}
          </span>
        ) : (
          "-"
        ),
    },
    {
      key: "sharpe_ratio",
      label: "夏普比率",
      render: (value: string | null) =>
        value ? parseFloat(value).toFixed(2) : "-",
    },
    {
      key: "max_drawdown",
      label: "最大回撤",
      render: (value: string | null) =>
        value ? `${(parseFloat(value) * 100).toFixed(2)}%` : "-",
    },
    { key: "total_trades", label: "总交易数" },
    {
      key: "win_rate",
      label: "胜率",
      render: (value: string | null) =>
        value ? `${(parseFloat(value) * 100).toFixed(2)}%` : "-",
    },
    {
      key: "timestamp",
      label: "时间",
      render: (value: string) => new Date(value).toLocaleString("zh-CN"),
    },
  ];

  const filterFields = [
    { key: "start_time", label: "开始时间", type: "date" as const },
    { key: "end_time", label: "结束时间", type: "date" as const },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">账户快照</h1>

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

