'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

interface PermissionLevel {
  level: string;
  name: string;
  upgrade_win_rate_7d?: number;
  upgrade_win_rate_30d?: number;
  upgrade_sharpe_ratio?: number;
  upgrade_min_trades?: number;
  upgrade_min_days?: number;
}

interface PermissionStatus {
  current_level: string;
  display_name: string;
  upgrade_conditions?: PermissionLevel;
}

// 权限等级名称映射
const getLevelName = (level: string): string => {
  const nameMap: Record<string, string> = {
    'L0': '保护模式',
    'L1': '新手级',
    'L2': '成长级',
    'L3': '稳定级',
    'L4': '熟练级',
    'L5': '专家级'
  };
  return nameMap[level] || '未知';
};

export default function PermissionIndicator() {
  const [permission, setPermission] = useState<PermissionStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPermission();
    const interval = setInterval(fetchPermission, 30000); // 每30秒刷新
    return () => clearInterval(interval);
  }, []);

  const fetchPermission = async () => {
    try {
      // 从AI状态获取当前权限等级
      const statusRes = await axios.get(`${API_BASE}/ai/status`);
      const currentLevel = statusRes.data?.orchestrator?.permission_level || 'L1';
      
      // 获取所有权限等级配置，找到下一级的升级条件
      const levelsRes = await axios.get(`${API_BASE}/admin/permissions/levels`);
      const levels = levelsRes.data || [];
      
      // 找到下一级
      const currentIndex = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5'].indexOf(currentLevel);
      const nextLevel = currentIndex < 5 ? ['L0', 'L1', 'L2', 'L3', 'L4', 'L5'][currentIndex + 1] : null;
      
      // 找到下一级的配置
      const nextLevelConfig = nextLevel ? levels.find((l: any) => l.level === nextLevel) : null;
      
      setPermission({
        current_level: currentLevel,
        display_name: getLevelName(currentLevel),
        upgrade_conditions: nextLevelConfig
      });
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch permission:', error);
      setLoading(false);
    }
  };

  if (loading || !permission) {
    return (
      <div className="bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200 rounded-xl p-6 shadow-sm">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-emerald-600 mr-3"></div>
          <div className="text-sm text-emerald-600 font-medium">加载权限信息中...</div>
        </div>
      </div>
    );
  }

  const levels = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5'];
  const currentIndex = levels.indexOf(permission.current_level);
  const nextLevel = permission.upgrade_conditions;
  const isMaxLevel = currentIndex === 5;

  return (
    <div className="bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300">
      <div className="px-5 py-4 border-b border-emerald-200 bg-gradient-to-r from-emerald-100/50 to-teal-100/50 rounded-t-xl">
        <h3 className="text-base font-bold text-gray-900 flex items-center">
          <span className="text-2xl mr-2">🔑</span> 
          <span className="bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">权限等级</span>
        </h3>
      </div>
      
      <div className="p-5 space-y-4">
        {/* 等级进度条 */}
        <div className="bg-white/60 rounded-xl p-4">
          <div className="flex justify-between items-center mb-4">
            {levels.map((level, index) => (
              <div key={level} className="flex flex-col items-center relative">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center text-xs font-bold border-2 shadow-md transition-all duration-300 ${
                    index === currentIndex
                      ? 'bg-gradient-to-br from-emerald-500 to-teal-500 text-white border-emerald-500 scale-110 shadow-lg'
                      : index < currentIndex
                      ? 'bg-gradient-to-br from-green-400 to-emerald-400 text-white border-green-400'
                      : 'bg-gray-100 text-gray-400 border-gray-300'
                  }`}
                >
                  {level}
                </div>
                {index < levels.length - 1 && (
                  <div className="absolute top-5 left-10 w-8 h-1 rounded-full"
                    style={{
                      background: index < currentIndex 
                        ? 'linear-gradient(to right, #10b981, #14b8a6)' 
                        : '#e5e7eb'
                    }}
                  />
                )}
              </div>
            ))}
          </div>
          
          <div className="text-center mt-4 p-3 bg-gradient-to-r from-emerald-100/50 to-teal-100/50 rounded-lg border border-emerald-200">
            <div className="text-base font-bold bg-gradient-to-r from-emerald-700 to-teal-700 bg-clip-text text-transparent">
              当前: {permission.current_level} ({permission.display_name})
            </div>
          </div>
        </div>

        {/* 升级条件 */}
        {!isMaxLevel && nextLevel ? (
          <div className="border-t border-emerald-200 pt-4">
            <div className="text-sm font-bold text-gray-800 mb-3 flex items-center">
              <span className="text-lg mr-2">🎯</span>
              升级到 {nextLevel.level} ({nextLevel.name}) 需要
            </div>
            <div className="space-y-2">
              {nextLevel.upgrade_win_rate_7d && (
                <div className="flex justify-between items-center py-2 px-3 bg-white/60 rounded-lg">
                  <span className="text-sm text-gray-700">7日胜率</span>
                  <span className="font-mono font-semibold text-emerald-700">
                    ≥ {(nextLevel.upgrade_win_rate_7d * 100).toFixed(0)}%
                  </span>
                </div>
              )}
              {nextLevel.upgrade_win_rate_30d && (
                <div className="flex justify-between items-center py-2 px-3 bg-white/60 rounded-lg">
                  <span className="text-sm text-gray-700">30日胜率</span>
                  <span className="font-mono font-semibold text-emerald-700">
                    ≥ {(nextLevel.upgrade_win_rate_30d * 100).toFixed(0)}%
                  </span>
                </div>
              )}
              {nextLevel.upgrade_sharpe_ratio && (
                <div className="flex justify-between items-center py-2 px-3 bg-white/60 rounded-lg">
                  <span className="text-sm text-gray-700">夏普比率</span>
                  <span className="font-mono font-semibold text-emerald-700">
                    ≥ {nextLevel.upgrade_sharpe_ratio.toFixed(1)}
                  </span>
                </div>
              )}
              {nextLevel.upgrade_min_trades && (
                <div className="flex justify-between items-center py-2 px-3 bg-white/60 rounded-lg">
                  <span className="text-sm text-gray-700">最少交易次数</span>
                  <span className="font-mono font-semibold text-emerald-700">
                    {nextLevel.upgrade_min_trades} 笔
                  </span>
                </div>
              )}
              {nextLevel.upgrade_min_days && (
                <div className="flex justify-between items-center py-2 px-3 bg-white/60 rounded-lg">
                  <span className="text-sm text-gray-700">运行天数</span>
                  <span className="font-mono font-semibold text-emerald-700">
                    ≥ {nextLevel.upgrade_min_days} 天
                  </span>
                </div>
              )}
            </div>
          </div>
        ) : isMaxLevel ? (
          <div className="border-t border-emerald-200 pt-4">
            <div className="text-sm text-center text-gray-700 bg-gradient-to-r from-yellow-50 to-amber-50 border border-yellow-200 rounded-lg p-4 shadow-sm">
              <span className="text-3xl mb-2 block">🏆</span>
              <span className="font-bold text-amber-700">恭喜！您已达到最高等级</span>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

