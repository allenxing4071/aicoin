"use client";

import { useEffect, useState } from "react";
import DataTable from "@/app/components/admin/DataTable";
import FilterBar from "@/app/components/admin/FilterBar";

export default function RiskEventsPage() {
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
        `http://localhost:8000/api/v1/admin/risk-events?${params}`
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
      console.error("Failed to fetch risk events:", error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { key: "id", label: "ID" },
    { key: "event_type", label: "事件类型" },
    {
      key: "severity",
      label: "严重程度",
      render: (value: string) => {
        const severityMap: Record<string, { label: string; color: string }> = {
          LOW: { label: "低", color: "bg-blue-100 text-blue-800" },
          MEDIUM: { label: "中", color: "bg-yellow-100 text-yellow-800" },
          HIGH: { label: "高", color: "bg-orange-100 text-orange-800" },
          CRITICAL: { label: "严重", color: "bg-red-100 text-red-800" },
        };
        const severity = severityMap[value] || {
          label: value,
          color: "bg-gray-100 text-gray-800",
        };
        return (
          <span
            className={`px-2 py-1 text-xs font-medium rounded ${severity.color}`}
          >
            {severity.label}
          </span>
        );
      },
    },
    {
      key: "description",
      label: "描述",
      render: (value: string) => (
        <div className="max-w-md truncate" title={value}>
          {value}
        </div>
      ),
    },
    {
      key: "action_taken",
      label: "处理措施",
      render: (value: string | null) =>
        value ? (
          <div className="max-w-xs truncate" title={value}>
            {value}
          </div>
        ) : (
          "-"
        ),
    },
    {
      key: "resolved",
      label: "已解决",
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
      key: "timestamp",
      label: "时间",
      render: (value: string) => new Date(value).toLocaleString("zh-CN"),
    },
  ];

  const filterFields = [
    { key: "event_type", label: "事件类型", type: "text" as const },
    {
      key: "severity",
      label: "严重程度",
      type: "select" as const,
      options: [
        { value: "LOW", label: "低" },
        { value: "MEDIUM", label: "中" },
        { value: "HIGH", label: "高" },
        { value: "CRITICAL", label: "严重" },
      ],
    },
    { key: "resolved", label: "是否已解决", type: "boolean" as const },
    { key: "start_time", label: "开始时间", type: "date" as const },
    { key: "end_time", label: "结束时间", type: "date" as const },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">风控事件</h1>

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

