'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import PageHeader from '../../components/common/PageHeader';
import { usePermissions } from '../PermissionsProvider';

const API_BASE = '/api/v1/admin';

interface Backup {
  filename: string;
  size: string;
  created_at: string;
  path: string;
}

interface DataStats {
  [key: string]: {
    total: number;
    oldest: string | null;
    newest: string | null;
    days_span: number;
  };
}

export default function BackupPage() {
  const router = useRouter();
  const { hasPermission, loading: permLoading } = usePermissions();
  
  const [backups, setBackups] = useState<Backup[]>([]);
  const [stats, setStats] = useState<DataStats>({});
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [cleaning, setCleaning] = useState(false);

  // 备份配置
  const [compress, setCompress] = useState(true);

  // 清理配置
  const [daysToKeep, setDaysToKeep] = useState(30);
  const [confirmCleanup, setConfirmCleanup] = useState(false);

  // 自动备份配置
  const [maxBackups, setMaxBackups] = useState(7);

  // 加载数据
  useEffect(() => {
    loadData();
  }, []); // 组件挂载时加载一次

  const getAuthHeaders = () => {
    const token = localStorage.getItem('admin_token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  };

  const loadData = async () => {
    try {
      setLoading(true);
      const [backupsRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/backup/backups`, { headers: getAuthHeaders() }),
        fetch(`${API_BASE}/backup/stats`, { headers: getAuthHeaders() })
      ]);

      if (backupsRes.ok) {
        const data = await backupsRes.json();
        if (data.success) {
          setBackups(data.data);
        }
      }

      if (statsRes.ok) {
        const data = await statsRes.json();
        if (data.success) {
          setStats(data.data);
        }
      }
    } catch (error) {
      console.error('加载数据失败:', error);
      alert('加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  const createBackup = async () => {
    if (!confirm('确定要创建完整数据库备份吗？\n\n将备份所有表的数据。')) return;

    try {
      setCreating(true);
      const response = await fetch(`${API_BASE}/backup/backup`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          include_tables: ['all'],  // 始终备份所有表
          compress: compress
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          alert(`✅ 备份创建成功！\n文件: ${data.data.filename}\n大小: ${data.data.size}`);
          loadData();
        }
      } else {
        const errorData = await response.json();
        alert(`❌ 创建备份失败: ${errorData.detail || '未知错误'}`);
      }
    } catch (error: any) {
      console.error('创建备份失败:', error);
      alert(`❌ 创建备份失败: ${error.message}`);
    } finally {
      setCreating(false);
    }
  };

  const deleteBackup = async (filename: string) => {
    if (!confirm(`确定要删除备份文件 ${filename} 吗？\n\n此操作不可撤销！`)) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/backup/delete/${filename}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          alert('✅ 备份删除成功！');
          loadData();
        }
      } else {
        const errorData = await response.json();
        alert(`❌ 删除失败: ${errorData.detail || '未知错误'}`);
      }
    } catch (error: any) {
      console.error('删除备份失败:', error);
      alert(`❌ 删除失败: ${error.message}`);
    }
  };

  const cleanupOldBackups = async (maxBackups: number) => {
    try {
      const response = await fetch(`${API_BASE}/backup/auto-cleanup`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ max_backups: maxBackups })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          return data.data;
        }
      }
    } catch (error: any) {
      console.error('清理旧备份失败:', error);
    }
    return null;
  };

  const cleanupWithBackup = async () => {
    if (!confirmCleanup) {
      alert('⚠️ 请先勾选确认框');
      return;
    }

    if (!confirm(`⚠️ 危险操作！\n\n将执行以下操作：\n1. 自动创建【完整数据库备份】（所有表）\n2. 删除所有表中 ${daysToKeep} 天前的数据\n\n✅ 备份包含所有表，确保数据安全！\n\n确定继续吗？`)) {
      return;
    }

    try {
      setCleaning(true);
      
      // 步骤1：先创建完整数据库备份（所有表）
      alert('📦 正在创建完整数据库备份...');
      const backupRes = await fetch(`${API_BASE}/backup/backup`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          include_tables: ['all'],  // 备份所有表，确保数据安全
          compress: compress
        })
      });

      if (!backupRes.ok) {
        throw new Error('备份失败，取消清理操作');
      }

      const backupData = await backupRes.json();
      
      // 步骤2：执行清理（清理所有表）
      const cleanupRes = await fetch(`${API_BASE}/backup/cleanup`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          table: 'all',  // 清理所有表
          days_to_keep: daysToKeep,
          confirm: true
        })
      });

      if (cleanupRes.ok) {
        const result = await cleanupRes.json();
        if (result.success) {
          const data = result.data;
          alert(`✅ 清理完成！\n\n备份: ${backupData.data.filename}\n删除: ${data.deleted_count} 条\n保留: ${data.kept_count} 条`);
          setConfirmCleanup(false);
          loadData();
        }
      } else {
        const errorData = await cleanupRes.json();
        alert(`❌ 清理失败: ${errorData.detail || '未知错误'}\n\n但备份已创建: ${backupData.data.filename}`);
        loadData();
      }
    } catch (error: any) {
      console.error('操作失败:', error);
      alert(`❌ 操作失败: ${error.message}`);
    } finally {
      setCleaning(false);
    }
  };

  const cleanupTableOptions = [
    { value: 'trades', label: '交易记录' },
    { value: 'orders', label: '订单记录' },
    { value: 'accounts', label: '账户快照' },
    { value: 'ai_decisions', label: 'AI决策' },
    { value: 'market_data', label: '市场数据' },
    { value: 'risk_events', label: '风控事件' }
  ];

  // 移除页面级权限检查，由菜单控制访问

  return (
    <div className="space-y-6">
      <PageHeader
        icon="💾"
        title="数据备份与清理"
        description="管理数据库备份和清理旧数据"
        color="purple"
      />

      {/* 数据统计 */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4">📊 数据统计</h2>
        {loading ? (
          <div className="text-center py-8 text-gray-500">加载中...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(stats).map(([table, data]) => (
              <div key={table} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-gray-900">
                    {cleanupTableOptions.find(t => t.value === table)?.label || table}
                  </h3>
                  <span className="text-2xl font-bold text-blue-600">{data.total}</span>
                </div>
                <div className="text-xs text-gray-600 space-y-1">
                  <div>最早: {data.oldest ? new Date(data.oldest).toLocaleDateString() : '-'}</div>
                  <div>最新: {data.newest ? new Date(data.newest).toLocaleDateString() : '-'}</div>
                  <div>时间跨度: {data.days_span} 天</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 创建备份 */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border-2 border-blue-200 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4">📦 创建完整数据库备份</h2>
        
        <div className="bg-blue-100 border border-blue-300 rounded-lg p-4 mb-4">
          <p className="text-sm text-blue-800 font-medium mb-2">
            ✅ 将备份整个数据库的所有表和数据
          </p>
          <p className="text-xs text-blue-700">
            💡 包含：交易记录、订单记录、账户快照、AI决策、市场数据、风控事件等所有数据
          </p>
        </div>

        <div className="space-y-4">
          <div>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={compress}
                onChange={(e) => setCompress(e.target.checked)}
                className="w-4 h-4"
              />
              <span className="text-sm font-medium text-gray-700">压缩备份文件 (推荐，可节省90%存储空间)</span>
            </label>
          </div>

          <button
            onClick={createBackup}
            disabled={creating}
            className="w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white rounded-xl transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed font-medium text-lg"
          >
            {creating ? '⏳ 创建中...' : '🚀 立即创建完整备份'}
          </button>
        </div>
      </div>

      {/* 备份列表 */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-900">📂 备份列表 ({backups.length})</h2>
          {backups.length > maxBackups && (
            <button
              onClick={async () => {
                if (confirm(`确定要清理旧备份吗？\n\n将删除超过 ${maxBackups} 个的旧备份文件`)) {
                  const result = await cleanupOldBackups(maxBackups);
                  if (result) {
                    alert(`✅ 清理完成！\n\n删除: ${result.deleted_count} 个\n保留: ${result.kept_count} 个`);
                    loadData();
                  }
                }
              }}
              className="px-3 py-1.5 bg-orange-100 hover:bg-orange-200 text-orange-700 rounded-lg text-sm font-medium transition-colors"
            >
              🗑️ 清理旧备份 (保留{maxBackups}个)
            </button>
          )}
        </div>
        {backups.length === 0 ? (
          <div className="text-center py-8 text-gray-500">暂无备份</div>
        ) : (
          <div className="space-y-2">
            {backups.map((backup, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors">
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{backup.filename}</div>
                  <div className="text-sm text-gray-600">
                    {new Date(backup.created_at).toLocaleString('zh-CN')} · {backup.size}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(backup.path);
                      alert('路径已复制到剪贴板');
                    }}
                    className="px-3 py-1.5 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-lg text-sm font-medium transition-colors"
                  >
                    📋 复制路径
                  </button>
                  <button
                    onClick={() => deleteBackup(backup.filename)}
                    className="px-3 py-1.5 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg text-sm font-medium transition-colors"
                  >
                    🗑️ 删除
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 自动备份配置 */}
      <div className="bg-gradient-to-r from-green-50 to-teal-50 rounded-xl border-2 border-green-200 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4">⚙️ 自动备份配置</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              保留备份数量
            </label>
            <input
              type="number"
              value={maxBackups}
              onChange={(e) => setMaxBackups(parseInt(e.target.value))}
              min="1"
              max="30"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <p className="text-xs text-gray-600 mt-1">
              💡 当备份数量超过 {maxBackups} 个时，可以手动清理旧备份
            </p>
          </div>

          <div className="bg-green-100 border border-green-300 rounded-lg p-4">
            <p className="text-sm text-green-800">
              <strong>提示：</strong> 每次创建备份时，系统会保留所有备份文件。当备份数量超过设定值时，可以在备份列表中手动清理旧备份。
            </p>
          </div>
        </div>
      </div>

      {/* 清理旧数据 */}
      <div className="bg-gradient-to-r from-red-50 to-orange-50 rounded-xl border-2 border-red-200 p-6">
        <h2 className="text-lg font-bold text-red-900 mb-4">🔄 清理旧数据（自动备份）</h2>
        <div className="bg-blue-100 border border-blue-300 rounded-lg p-4 mb-4">
          <p className="text-sm text-blue-800 font-medium mb-2">
            ✅ 清理前会自动创建<strong>完整数据库备份</strong>（包含所有表）
          </p>
          <p className="text-xs text-blue-700">
            💡 将清理所有表中的旧数据，并自动备份整个数据库，确保数据绝对安全！
          </p>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              保留最近多少天的数据
            </label>
            <input
              type="number"
              value={daysToKeep}
              onChange={(e) => setDaysToKeep(parseInt(e.target.value))}
              min="1"
              max="365"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
            />
            <p className="text-xs text-gray-600 mt-1">
              将删除 {daysToKeep} 天前的所有数据
            </p>
          </div>

          <div>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={confirmCleanup}
                onChange={(e) => setConfirmCleanup(e.target.checked)}
                className="w-4 h-4"
              />
              <span className="text-sm font-medium text-red-700">
                我已了解风险，确认要清理数据
              </span>
            </label>
          </div>

          <button
            onClick={cleanupWithBackup}
            disabled={cleaning || !confirmCleanup}
            className="w-full px-6 py-3 bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600 text-white rounded-xl transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {cleaning ? '处理中...' : '🔄 备份并清理数据'}
          </button>
        </div>
      </div>
    </div>
  );
}

