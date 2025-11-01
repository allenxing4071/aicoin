"use client";

import { useEffect, useState } from "react";
import DataTable from "@/app/components/admin/DataTable";
import FilterBar from "@/app/components/admin/FilterBar";

export default function AIDecisionsPage() {
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
        `http://localhost:8000/api/v1/admin/ai-decisions?${params}`
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
      console.error("Failed to fetch AI decisions:", error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { key: "id", label: "ID" },
    { key: "symbol", label: "交易品种" },
    { key: "model_name", label: "模型" },
    {
      key: "executed",
      label: "已执行",
      render: (value: boolean) => (
        <span
          className={`px-2 py-1 text-xs font-medium rounded ${
            value
              ? "bg-green-100 text-green-800"
              : "bg-gray-100 text-gray-800"
          }`}
        >
          {value ? "是" : "否"}
        </span>
      ),
    },
    {
      key: "decision",
      label: "决策内容",
      render: (value: any) => (
        <div className="max-w-xs truncate" title={JSON.stringify(value)}>
          {value?.action || "-"}
        </div>
      ),
    },
    {
      key: "reject_reason",
      label: "拒绝原因",
      render: (value: string | null) =>
        value ? (
          <div className="max-w-xs truncate text-red-600" title={value}>
            {value}
          </div>
        ) : (
          "-"
        ),
    },
    {
      key: "latency_ms",
      label: "延迟(ms)",
      render: (value: number | null) => (value ? value : "-"),
    },
    {
      key: "timestamp",
      label: "时间",
      render: (value: string) => new Date(value).toLocaleString("zh-CN"),
    },
  ];

  const filterFields = [
    { key: "symbol", label: "交易品种", type: "text" as const },
    { key: "model_name", label: "模型名称", type: "text" as const },
    { key: "executed", label: "是否已执行", type: "boolean" as const },
    { key: "start_time", label: "开始时间", type: "date" as const },
    { key: "end_time", label: "结束时间", type: "date" as const },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">AI决策日志</h1>

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

