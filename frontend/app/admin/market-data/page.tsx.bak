"use client";

import { useEffect, useState } from "react";
import DataTable from "@/app/components/admin/DataTable";
import FilterBar from "@/app/components/admin/FilterBar";

export default function MarketDataPage() {
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
        `http://localhost:8000/api/v1/admin/market-data?${params}`
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
      console.error("Failed to fetch market data:", error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { key: "id", label: "ID" },
    { key: "symbol", label: "交易品种" },
    { key: "interval", label: "周期" },
    {
      key: "open",
      label: "开盘价",
      render: (value: string) => `$${parseFloat(value).toFixed(2)}`,
    },
    {
      key: "high",
      label: "最高价",
      render: (value: string) => `$${parseFloat(value).toFixed(2)}`,
    },
    {
      key: "low",
      label: "最低价",
      render: (value: string) => `$${parseFloat(value).toFixed(2)}`,
    },
    {
      key: "close",
      label: "收盘价",
      render: (value: string) => `$${parseFloat(value).toFixed(2)}`,
    },
    {
      key: "volume",
      label: "成交量",
      render: (value: string) => parseFloat(value).toFixed(2),
    },
    {
      key: "open_time",
      label: "开盘时间",
      render: (value: string) => new Date(value).toLocaleString("zh-CN"),
    },
  ];

  const filterFields = [
    { key: "symbol", label: "交易品种", type: "text" as const },
    {
      key: "interval",
      label: "K线周期",
      type: "select" as const,
      options: [
        { value: "1m", label: "1分钟" },
        { value: "5m", label: "5分钟" },
        { value: "15m", label: "15分钟" },
        { value: "1h", label: "1小时" },
        { value: "4h", label: "4小时" },
        { value: "1d", label: "1天" },
      ],
    },
    { key: "start_time", label: "开始时间", type: "date" as const },
    { key: "end_time", label: "结束时间", type: "date" as const },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">K线数据</h1>

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

