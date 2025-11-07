"use client";

import { useState, useEffect } from "react";
import axios from "axios";

interface TableInfo {
  table_name: string;
  table_comment: string | null;
  row_count: number;
  columns: ColumnInfo[];
  icon?: string;  // 从注释中提取的 emoji
  description?: string;  // 从注释中提取的描述
}

interface ColumnInfo {
  column_name: string;
  data_type: string;
  is_nullable: string;
  column_default: string | null;
}

interface DatabaseStats {
  database_name: string;
  database_size: string;
  total_tables: number;
  connection_status: string;
}

/**
 * 从表注释中提取 emoji 和描述
 * 注释格式: "🔥 表名 - 描述信息"
 */
const parseTableComment = (comment: string | null): { icon: string; description: string } => {
  if (!comment) {
    return { icon: "📊", description: "暂无说明" };
  }
  
  // 提取 emoji（通常是第一个字符）
  // 使用更兼容的正则表达式，匹配常见的 emoji 范围
  const emojiRegex = /^[\u2600-\u27BF\uD83C-\uDBFF\uDC00-\uDFFF]+/;
  const emojiMatch = comment.match(emojiRegex);
  const icon = emojiMatch ? emojiMatch[0] : "📊";
  
  // 提取描述（去掉 emoji 后的内容）
  const description = comment.replace(emojiRegex, "").trim();
  
  return { icon, description };
};

// 字段说明配置（针对account_snapshots表）
const fieldDescriptions: Record<string, Record<string, string>> = {
  account_snapshots: {
    id: "主键ID，唯一标识每条快照记录",
    timestamp: "快照时间戳，记录数据采集时间",
    account_value: "账户总价值（USDC），包含所有资产的估值",
    total_margin_used: "已使用保证金，当前持仓占用的保证金金额",
    total_ntl_pos: "总名义持仓价值，所有持仓的名义价值总和",
    total_unrealized_pnl: "未实现盈亏，当前持仓的浮动盈亏",
    total_raw_usd: "可用余额（USDC），可用于开仓的余额",
    withdrawable: "可提现金额，扣除保证金后可提现的金额",
    cross_margin_summary: "全仓保证金汇总信息（JSON格式）",
    created_at: "记录创建时间，数据入库时间",
  },
};

export default function DatabaseManagementPage() {
  const [tables, setTables] = useState<TableInfo[]>([]);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [tableData, setTableData] = useState<any[]>([]);
  const [dbStats, setDbStats] = useState<DatabaseStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [dataLoading, setDataLoading] = useState(false);

  useEffect(() => {
    loadDatabaseInfo();
  }, []);

  const loadDatabaseInfo = async () => {
    setLoading(true);
    try {
      // 获取数据库统计信息 - 使用完整URL强制刷新
      const statsRes = await axios.get("http://localhost:8000/api/v1/admin/database/stats");
      setDbStats(statsRes.data);

      // 获取所有表信息
      const tablesRes = await axios.get("http://localhost:8000/api/v1/admin/database/tables");
      
      // 解析每个表的注释，提取 emoji 和描述
      const tablesWithParsedComments = tablesRes.data.map((table: TableInfo) => {
        const { icon, description } = parseTableComment(table.table_comment);
        return {
          ...table,
          icon,
          description
        };
      });
      
      setTables(tablesWithParsedComments);
    } catch (error) {
      console.error("加载数据库信息失败:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadTableData = async (tableName: string) => {
    setSelectedTable(tableName);
    setDataLoading(true);
    try {
      const res = await axios.get(`http://localhost:8000/api/v1/admin/database/tables/${tableName}/data?limit=50`);
      setTableData(res.data);
    } catch (error) {
      console.error("加载表数据失败:", error);
      setTableData([]);
    } finally {
      setDataLoading(false);
    }
  };

  const selectedTableInfo = tables.find(t => t.table_name === selectedTable);

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">数据库管理器</h1>
        <p className="text-gray-600 mt-2">查看数据库连接、表结构和数据内容</p>
      </div>

      {/* 数据库连接信息 */}
      {dbStats && (
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">📊 数据库连接信息</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 rounded-xl p-4">
              <div className="text-sm text-gray-600 mb-1">数据库名称</div>
              <div className="text-lg font-semibold text-gray-900">{dbStats.database_name}</div>
            </div>
            <div className="bg-gray-50 rounded-xl p-4">
              <div className="text-sm text-gray-600 mb-1">数据库大小</div>
              <div className="text-lg font-semibold text-gray-900">{dbStats.database_size}</div>
            </div>
            <div className="bg-gray-50 rounded-xl p-4">
              <div className="text-sm text-gray-600 mb-1">数据表数量</div>
              <div className="text-lg font-semibold text-gray-900">{dbStats.total_tables} 张</div>
            </div>
            <div className="bg-gray-50 rounded-xl p-4">
              <div className="text-sm text-gray-600 mb-1">连接状态</div>
              <div className="text-lg font-semibold text-green-600">● {dbStats.connection_status}</div>
            </div>
          </div>
        </div>
      )}

      {/* 主要内容区域 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左侧：表列表 */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">数据表列表</h3>
              <p className="text-sm text-gray-600 mt-1">点击表名查看详情</p>
            </div>
            <div className="divide-y divide-gray-200 max-h-[600px] overflow-y-auto">
              {loading ? (
                <div className="p-4 text-center text-gray-500">加载中...</div>
              ) : (
                tables.map((table) => (
                  <button
                    key={table.table_name}
                    onClick={() => loadTableData(table.table_name)}
                    className={`w-full text-left p-4 hover:bg-gray-50 transition-colors ${
                      selectedTable === table.table_name ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                    }`}
                  >
                    <div className="flex items-center gap-2 font-medium text-gray-900">
                      {table.icon && <span className="text-lg">{table.icon}</span>}
                      <span>{table.table_name}</span>
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      {table.row_count} 行 · {table.columns.length} 列
                    </div>
                    {table.description && (
                      <div className="text-xs text-gray-500 mt-2 whitespace-nowrap overflow-hidden text-ellipsis">
                        {table.description}
                      </div>
                    )}
                  </button>
                ))
              )}
            </div>
          </div>
        </div>

        {/* 右侧：表详情 */}
        <div className="lg:col-span-2">
          {!selectedTable ? (
            <div className="bg-white rounded-xl shadow p-12 text-center">
              <div className="text-gray-400 text-6xl mb-4">📋</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">选择一个表</h3>
              <p className="text-gray-600">从左侧列表中选择一个表来查看其结构和数据</p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* 表结构 */}
              {selectedTableInfo && (
                <div className="bg-white rounded-xl shadow">
                  <div className="p-4 border-b border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900">表结构：{selectedTable}</h3>
                    <p className="text-sm text-gray-600 mt-1">{selectedTableInfo.columns.length} 个字段</p>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            字段名
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            数据类型
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            允许空值
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            默认值
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            说明
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {selectedTableInfo.columns.map((col) => {
                          const tableFields = fieldDescriptions[selectedTable];
                          const fieldDesc = tableFields ? tableFields[col.column_name] : null;
                          return (
                            <tr key={col.column_name} className="hover:bg-gray-50">
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                {col.column_name}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-mono">
                                  {col.data_type}
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                {col.is_nullable === 'YES' ? (
                                  <span className="text-green-600">✓ 是</span>
                                ) : (
                                  <span className="text-red-600">✗ 否</span>
                                )}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 font-mono">
                                {col.column_default || '-'}
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-500">
                                {fieldDesc ? (
                                  <span className="whitespace-normal">{fieldDesc}</span>
                                ) : (
                                  <span className="text-gray-400">-</span>
                                )}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* 表数据 */}
              <div className="bg-white rounded-xl shadow">
                <div className="p-4 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900">表数据（最近50条）</h3>
                  <p className="text-sm text-gray-600 mt-1">只读模式，仅供查看</p>
                </div>
                <div className="overflow-x-auto">
                  {dataLoading ? (
                    <div className="p-8 text-center text-gray-500">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                      加载数据中...
                    </div>
                  ) : tableData.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                      该表暂无数据
                    </div>
                  ) : (
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          {Object.keys(tableData[0] || {}).map((key) => (
                            <th
                              key={key}
                              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap"
                            >
                              {key}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {tableData.map((row, idx) => (
                          <tr key={idx} className="hover:bg-gray-50">
                            {Object.entries(row).map(([key, value]) => (
                              <td
                                key={key}
                                className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate"
                                title={String(value)}
                              >
                                {value === null ? (
                                  <span className="text-gray-400 italic">NULL</span>
                                ) : typeof value === 'object' ? (
                                  <span className="text-blue-600 font-mono text-xs">
                                    {JSON.stringify(value)}
                                  </span>
                                ) : (
                                  String(value)
                                )}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

