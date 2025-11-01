'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

interface PermissionStatus {
  current_level: string;
  display_name: string;
  config: {
    max_position_pct: number;
    max_leverage: number;
    confidence_threshold: number;
    max_daily_trades: number;
  };
  upgrade: {
    can_upgrade: boolean;
    target_level: string;
    progress_pct: number;
    message: string;
  };
}

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
      const res = await axios.get(`${API_BASE}/ai/permission`);
      setPermission(res.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch permission:', error);
      setLoading(false);
    }
  };

  if (loading || !permission) {
    return (
      <div className="bg-white border border-gray-200 p-4">
        <div className="text-sm text-gray-500">加载权限信息中...</div>
      </div>
    );
  }

  const levels = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5'];
  const currentIndex = levels.indexOf(permission.current_level);

  return (
    <div className="bg-white border border-gray-200">
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
        <h3 className="text-sm font-bold text-gray-900">🔑 权限等级</h3>
      </div>
      
      <div className="p-4 space-y-4">
        {/* 等级进度条 */}
        <div>
          <div className="flex justify-between items-center mb-2">
            {levels.map((level, index) => (
              <div key={level} className="flex flex-col items-center">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border-2 ${
                    index === currentIndex
                      ? 'bg-blue-500 text-white border-blue-500'
                      : index < currentIndex
                      ? 'bg-green-500 text-white border-green-500'
                      : 'bg-gray-200 text-gray-500 border-gray-300'
                  }`}
                >
                  {level}
                </div>
                {index < levels.length - 1 && (
                  <div
                    className={`h-0.5 w-12 mt-4 ${
                      index < currentIndex ? 'bg-green-500' : 'bg-gray-300'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
          
          <div className="text-center mt-3">
            <div className="text-sm font-semibold text-gray-900">
              当前: {permission.current_level} ({permission.display_name})
            </div>
            {permission.upgrade.target_level && (
              <div className="text-xs text-gray-500 mt-1">
                升级进度: {permission.upgrade.progress_pct.toFixed(1)}% → {permission.upgrade.target_level}
              </div>
            )}
          </div>
        </div>

        {/* 当前权限配置 */}
        <div className="border-t border-gray-200 pt-3">
          <div className="text-xs font-bold text-gray-700 mb-2">当前权限</div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <div className="text-gray-500">最大仓位:</div>
              <div className="font-mono font-semibold">
                {(permission.config.max_position_pct * 100).toFixed(0)}%
              </div>
            </div>
            <div>
              <div className="text-gray-500">最大杠杆:</div>
              <div className="font-mono font-semibold">{permission.config.max_leverage}x</div>
            </div>
            <div>
              <div className="text-gray-500">信心阈值:</div>
              <div className="font-mono font-semibold">
                {(permission.config.confidence_threshold * 100).toFixed(0)}%
              </div>
            </div>
            <div>
              <div className="text-gray-500">日交易次数:</div>
              <div className="font-mono font-semibold">
                {permission.config.max_daily_trades === 999 ? '∞' : permission.config.max_daily_trades}
              </div>
            </div>
          </div>
        </div>

        {/* 升级提示 */}
        {permission.upgrade.message && (
          <div className="border-t border-gray-200 pt-3">
            <div className="text-xs text-gray-600 bg-blue-50 border border-blue-200 rounded p-2">
              💡 {permission.upgrade.message}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

