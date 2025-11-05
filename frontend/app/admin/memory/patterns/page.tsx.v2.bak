"use client";

import { useEffect, useState } from "react";
import DataTable from "@/app/components/admin/DataTable";
import FilterBar from "@/app/components/admin/FilterBar";

export default function MarketPatternsPage() {
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
        `http://localhost:8000/api/v1/admin/memory/patterns?${params}`
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
      console.error("Failed to fetch market patterns:", error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { key: "id", label: "ID" },
    {
      key: "pattern_type",
      label: "模式类型",
      render: (value: string) => {
        const typeMap: Record<string, { label: string; color: string }> = {
          trend_reversal: { label: "趋势反转", color: "bg-purple-100 text-purple-800" },
          breakout: { label: "突破", color: "bg-blue-100 text-blue-800" },
          consolidation: { label: "盘整", color: "bg-yellow-100 text-yellow-800" },
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
    { key: "symbol", label: "交易品种" },
    {
      key: "features",
      label: "特征",
      render: (value: any) => (
        <div className="max-w-xs truncate text-sm" title={JSON.stringify(value)}>
          {Object.keys(value).length} 个特征
        </div>
      ),
    },
    { key: "occurrences", label: "出现次数" },
    {
      key: "success_rate",
      label: "成功率",
      render: (value: number | null) =>
        value !== null ? (
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
        ) : (
          "-"
        ),
    },
    {
      key: "avg_profit",
      label: "平均收益",
      render: (value: number | null) =>
        value !== null ? (
          <span className={value >= 0 ? "text-green-600" : "text-red-600"}>
            ${value.toFixed(2)}
          </span>
        ) : (
          "-"
        ),
    },
    {
      key: "detected_at",
      label: "首次检测",
      render: (value: string) => new Date(value).toLocaleString("zh-CN"),
    },
    {
      key: "last_seen_at",
      label: "最近出现",
      render: (value: string) => new Date(value).toLocaleString("zh-CN"),
    },
  ];

  const filterFields = [
    {
      key: "pattern_type",
      label: "模式类型",
      type: "select" as const,
      options: [
        { value: "trend_reversal", label: "趋势反转" },
        { value: "breakout", label: "突破" },
        { value: "consolidation", label: "盘整" },
      ],
    },
    { key: "symbol", label: "交易品种", type: "text" as const },
  ];

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          📈 市场模式
        </h1>
        <p className="text-gray-600">
          AI识别的市场模式及其历史表现统计
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

