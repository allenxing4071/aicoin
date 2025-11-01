"use client";

import { useState } from "react";

interface FilterField {
  key: string;
  label: string;
  type: "text" | "select" | "date" | "boolean";
  options?: { value: string; label: string }[];
}

interface FilterBarProps {
  fields: FilterField[];
  onFilter: (filters: Record<string, any>) => void;
  onReset: () => void;
}

export default function FilterBar({
  fields,
  onFilter,
  onReset,
}: FilterBarProps) {
  const [filters, setFilters] = useState<Record<string, any>>({});
  const [expanded, setExpanded] = useState(true);

  const handleChange = (key: string, value: any) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // 过滤掉空值
    const cleanFilters = Object.entries(filters).reduce(
      (acc, [key, value]) => {
        if (value !== "" && value !== null && value !== undefined) {
          acc[key] = value;
        }
        return acc;
      },
      {} as Record<string, any>
    );
    onFilter(cleanFilters);
  };

  const handleReset = () => {
    setFilters({});
    onReset();
  };

  return (
    <div className="bg-white rounded-lg shadow p-4 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900">筛选条件</h3>
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-sm text-blue-600 hover:text-blue-700"
        >
          {expanded ? "收起" : "展开"}
        </button>
      </div>

      {expanded && (
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
            {fields.map((field) => (
              <div key={field.key}>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {field.label}
                </label>
                {field.type === "text" && (
                  <input
                    type="text"
                    value={filters[field.key] || ""}
                    onChange={(e) => handleChange(field.key, e.target.value)}
                    className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder={`输入${field.label}`}
                  />
                )}
                {field.type === "select" && (
                  <select
                    value={filters[field.key] || ""}
                    onChange={(e) => handleChange(field.key, e.target.value)}
                    className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">全部</option>
                    {field.options?.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                )}
                {field.type === "date" && (
                  <input
                    type="datetime-local"
                    value={filters[field.key] || ""}
                    onChange={(e) => handleChange(field.key, e.target.value)}
                    className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                )}
                {field.type === "boolean" && (
                  <select
                    value={filters[field.key] || ""}
                    onChange={(e) => {
                      const value = e.target.value;
                      handleChange(
                        field.key,
                        value === "" ? null : value === "true"
                      );
                    }}
                    className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">全部</option>
                    <option value="true">是</option>
                    <option value="false">否</option>
                  </select>
                )}
              </div>
            ))}
          </div>

          <div className="flex space-x-3">
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-sm"
            >
              应用筛选
            </button>
            <button
              type="button"
              onClick={handleReset}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors text-sm"
            >
              重置
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

