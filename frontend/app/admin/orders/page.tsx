"use client";

import { useEffect, useState } from "react";
import DataTable from "@/app/components/admin/DataTable";
import FilterBar from "@/app/components/admin/FilterBar";
import PageHeader from '../../components/common/PageHeader';

export default function OrdersPage() {
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
        `http://localhost:8000/api/v1/admin/orders?${params}`
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
      console.error("Failed to fetch orders:", error);
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
    { key: "type", label: "类型" },
    {
      key: "price",
      label: "价格",
      render: (value: string | null) =>
        value ? `$${parseFloat(value).toFixed(2)}` : "市价",
    },
    {
      key: "size",
      label: "数量",
      render: (value: string) => parseFloat(value).toFixed(4),
    },
    {
      key: "filled_size",
      label: "已成交",
      render: (value: string) => parseFloat(value).toFixed(4),
    },
    {
      key: "status",
      label: "状态",
      render: (value: string) => {
        const statusMap: Record<string, { label: string; color: string }> = {
          PENDING: { label: "待处理", color: "bg-yellow-100 text-yellow-800" },
          FILLED: { label: "已成交", color: "bg-green-100 text-green-800" },
          CANCELLED: { label: "已取消", color: "bg-gray-100 text-gray-800" },
          FAILED: { label: "失败", color: "bg-red-100 text-red-800" },
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
    {
      key: "created_at",
      label: "创建时间",
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
    {
      key: "status",
      label: "订单状态",
      type: "select" as const,
      options: [
        { value: "PENDING", label: "待处理" },
        { value: "FILLED", label: "已成交" },
        { value: "CANCELLED", label: "已取消" },
        { value: "FAILED", label: "失败" },
      ],
    },
    { key: "start_time", label: "开始时间", type: "date" as const },
    { key: "end_time", label: "结束时间", type: "date" as const },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        icon="📋"
        title="订单记录"
        description="查看所有订单的详细信息"
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

