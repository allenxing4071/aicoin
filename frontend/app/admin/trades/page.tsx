"use client";

import { useEffect, useState } from "react";
import DataTable from "@/app/components/admin/DataTable";
import FilterBar from "@/app/components/admin/FilterBar";
import PageHeader from '../../components/common/PageHeader';

export default function TradesPage() {
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
        `http://localhost:8000/api/v1/admin/trades?${params}`
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
      console.error("Failed to fetch trades:", error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { key: "id", label: "ID" },
    { key: "symbol", label: "交易品种" },
    {
      key: "side",
      label: "方向",
      render: (value: string) => (
        <span
          className={`px-2 py-1 text-xs font-medium rounded ${
            value === "BUY"
              ? "bg-green-100 text-green-800"
              : "bg-red-100 text-red-800"
          }`}
        >
          {value === "BUY" ? "买入" : "卖出"}
        </span>
      ),
    },
    {
      key: "price",
      label: "价格",
      render: (value: string) => `$${parseFloat(value).toFixed(2)}`,
    },
    {
      key: "size",
      label: "数量",
      render: (value: string) => parseFloat(value).toFixed(4),
    },
    {
      key: "pnl",
      label: "盈亏",
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
    { key: "model", label: "AI模型" },
    {
      key: "confidence",
      label: "置信度",
      render: (value: string | null) =>
        value ? `${(parseFloat(value) * 100).toFixed(0)}%` : "-",
    },
    {
      key: "timestamp",
      label: "时间",
      render: (value: string) => new Date(value).toLocaleString("zh-CN"),
    },
  ];

  const filterFields = [
    { key: "symbol", label: "交易品种", type: "text" as const },
    {
      key: "side",
      label: "交易方向",
      type: "select" as const,
      options: [
        { value: "BUY", label: "买入" },
        { value: "SELL", label: "卖出" },
      ],
    },
    { key: "model", label: "AI模型", type: "text" as const },
    { key: "start_time", label: "开始时间", type: "date" as const },
    { key: "end_time", label: "结束时间", type: "date" as const },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        icon="💰"
        title="交易记录"
        description="查看所有交易的详细记录"
        color="pink"
      />

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

