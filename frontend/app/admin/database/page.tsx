"use client";

import { useState, useEffect } from "react";
import axios from "axios";

interface TableInfo {
  table_name: string;
  table_comment: string | null;
  row_count: number;
  columns: ColumnInfo[];
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

// 表说明配置
const tableDescriptions: Record<string, { icon: string; description: string }> = {
  account_snapshots: { icon: "💼", description: "账户快照 - 定期记录账户余额、权益、盈亏、夏普比率等关键财务指标" },
  admin_users: { icon: "👤", description: "管理员用户 - 存储后台管理系统的用户账号、角色权限和登录信息" },
  ai_decisions: { icon: "🤖", description: "AI决策日志 - 记录AI每次决策的市场数据输入、决策输出、执行状态和拒绝原因" },
  ai_lessons: { icon: "📚", description: "AI经验教训 - 知识库(L3)，存储AI从历史交易中学习到的成功经验和失败教训" },
  ai_strategies: { icon: "📋", description: "AI策略评估 - 知识库(L3)，记录各交易策略的性能指标、适用条件和历史表现" },
  alembic_version: { icon: "🔧", description: "数据库版本 - Alembic迁移工具使用的版本控制表" },
  exchange_configs: { icon: "🏦", description: "交易所配置 - 存储币安等交易所的API密钥和连接配置" },
  intelligence_feedback: { icon: "💬", description: "情报反馈 - 记录用户对情报的反馈和使用效果，用于优化情报质量" },
  intelligence_platforms: { icon: "☁️", description: "情报平台配置 - 管理AI云平台（Qwen、腾讯混元、火山引擎等）的连接配置和性能指标" },
  intelligence_reports: { icon: "📊", description: "情报报告 - Qwen情报官收集的市场情报和分析报告，包含新闻、巨鲸活动、链上数据等" },
  intelligence_source_weights: { icon: "⚖️", description: "情报源权重 - 记录各情报源（RSS、API等）的权重和有效性评分，用于智能筛选" },
  market_data_kline: { icon: "📈", description: "K线数据 - 存储各币种的历史K线图数据（开高低收、成交量等）" },
  market_patterns: { icon: "📊", description: "市场模式 - AI识别的市场走势模式（趋势反转、突破、盘整等）及其历史表现" },
  model_performance_metrics: { icon: "📈", description: "模型性能指标 - 记录各AI模型的决策准确率、盈利率、响应时间等性能数据" },
  orders: { icon: "📝", description: "订单记录 - 记录所有交易订单的创建、执行、成交状态和交易所订单ID" },
  permission_level_configs: { icon: "🔐", description: "权限等级配置 - 定义L0-L5各等级的交易限制、升降级条件和风控参数" },
  risk_events: { icon: "⚠️", description: "风控事件 - 记录触发的风控警报、事件类型、严重程度和处理措施" },
  routing_decisions: { icon: "🔀", description: "路由决策日志 - 记录AI模型路由策略选择过程和多模型协作决策的详细信息" },
  trades: { icon: "💰", description: "成交记录 - 记录所有已成交的交易明细，包括价格、数量、盈亏、AI决策依据等完整信息" },
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
      setTables(tablesRes.data);
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
                tables.map((table) => {
                  // 优先使用数据库注释，回退到硬编码配置
                  const tableInfo = tableDescriptions[table.table_name];
                  const comment = table.table_comment || tableInfo?.description;
                  // 从注释中提取图标（如果有）
                  const iconMatch = table.table_comment?.match(/^([\u{1F300}-\u{1F9FF}])/u);
                  const icon = iconMatch ? iconMatch[1] : tableInfo?.icon;
                  
                  return (
                    <button
                      key={table.table_name}
                      onClick={() => loadTableData(table.table_name)}
                      className={`w-full text-left p-4 hover:bg-gray-50 transition-colors ${
                        selectedTable === table.table_name ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                      }`}
                    >
                      <div className="flex items-center gap-2 font-medium text-gray-900">
                        {icon && <span className="text-lg">{icon}</span>}
                        <span>{table.table_name}</span>
                      </div>
                      <div className="text-sm text-gray-600 mt-1">
                        {table.row_count} 行 · {table.columns.length} 列
                      </div>
                      {comment && (
                        <div className="text-xs text-gray-500 mt-2 whitespace-nowrap overflow-hidden text-ellipsis">
                          {comment}
                        </div>
                      )}
                    </button>
                  );
                })
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

