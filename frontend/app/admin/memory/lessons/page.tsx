"use client";

import { useEffect, useState } from "react";
import DataTable from "@/app/components/admin/DataTable";
import FilterBar from "@/app/components/admin/FilterBar";

export default function AILessonsPage() {
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
        `/api/v1/admin/memory/lessons?${params}`
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
      console.error("Failed to fetch AI lessons:", error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { key: "id", label: "ID" },
    {
      key: "lesson_type",
      label: "类型",
      render: (value: string) => {
        const typeMap: Record<string, { label: string; color: string }> = {
          success: { label: "成功经验", color: "bg-green-100 text-green-800" },
          failure: { label: "失败教训", color: "bg-red-100 text-red-800" },
          insight: { label: "市场洞察", color: "bg-blue-100 text-blue-800" },
        };
        const type = typeMap[value] || {
          label: value,
          color: "bg-gray-100 text-gray-800",
        };
        return (
          <span className={`px-2 py-1 text-xs font-medium rounded ${type.color}`}>
            {type.label}
          </span>
        );
      },
    },
    {
      key: "title",
      label: "标题",
      render: (value: string) => (
        <div className="max-w-md font-medium" title={value}>
          {value}
        </div>
      ),
    },
    {
      key: "description",
      label: "描述",
      render: (value: string) => (
        <div className="max-w-lg truncate text-sm text-gray-600" title={value}>
          {value}
        </div>
      ),
    },
    { key: "market_regime", label: "市场状态" },
    { key: "symbol", label: "品种" },
    {
      key: "confidence_score",
      label: "置信度",
      render: (value: number) => (
        <div className="flex items-center space-x-2">
          <div className="w-16 bg-gray-200 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full"
              style={{ width: `${value * 100}%` }}
            ></div>
          </div>
          <span className="text-sm">{(value * 100).toFixed(0)}%</span>
        </div>
      ),
    },
    { key: "sample_count", label: "样本数" },
    {
      key: "validated",
      label: "已验证",
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
      key: "created_at",
      label: "创建时间",
      render: (value: string) => new Date(value).toLocaleString("zh-CN"),
    },
  ];

  const filterFields = [
    {
      key: "lesson_type",
      label: "教训类型",
      type: "select" as const,
      options: [
        { value: "success", label: "成功经验" },
        { value: "failure", label: "失败教训" },
        { value: "insight", label: "市场洞察" },
      ],
    },
    { key: "market_regime", label: "市场状态", type: "text" as const },
    { key: "validated", label: "是否已验证", type: "boolean" as const },
  ];

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          📗 AI经验教训
        </h1>
        <p className="text-gray-600">
          从历史交易中提取的经验教训,帮助AI避免重复错误
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

