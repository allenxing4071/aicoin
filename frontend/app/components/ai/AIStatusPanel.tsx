'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE = '/api/v1';

interface OrchestratorStatus {
  running: boolean;
  permission_level: string;
  permission_name?: string;
  permission_config?: {
    max_position_pct: number;
    max_leverage: number;
    confidence_threshold: number;
    max_daily_trades: number;
  };
  runtime_hours: number;
  total_decisions: number;
  approved: number;
  approval_rate: number;
  decision_interval: number;
}

interface ConstraintStatus {
  name: string;
  current: string;
  threshold: string;
  status: 'pass' | 'warning' | 'violated';
  description: string;
}

// 权限等级名称映射
const getPermissionName = (level?: string): string => {
  const nameMap: Record<string, string> = {
    'L0': '保护模式',
    'L1': '新手级',
    'L2': '成长级',
    'L3': '稳定级',
    'L4': '熟练级',
    'L5': '专家级'
  };
  return nameMap[level || 'L1'] || '未知';
};

export default function AIStatusPanel() {
  const [orchestratorStatus, setOrchestratorStatus] = useState<OrchestratorStatus | null>(null);
  const [constraints, setConstraints] = useState<Record<string, ConstraintStatus>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000); // 每10秒刷新
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      // 获取AI状态 - 使用/api/v1/ai/status端点（包含完整权限信息）
      const statusRes = await axios.get(`${API_BASE}/ai/status`);
      if (statusRes.data && statusRes.data.orchestrator) {
        const orch = statusRes.data.orchestrator;
        setOrchestratorStatus({
          running: orch.is_running || false,
          permission_level: orch.permission_level || 'L1',
          permission_name: orch.permission_name,
          permission_config: orch.permission_config,
          runtime_hours: orch.runtime_hours || 0,
          total_decisions: orch.total_decisions || 0,
          approved: orch.approved_decisions || 0,
          approval_rate: orch.approval_rate || 0,
          decision_interval: orch.decision_interval || 300
        });
      }

      // 获取约束状态
      const constraintsRes = await axios.get(`${API_BASE}/constraints/status`);
      if (constraintsRes.data.hard_constraints) {
        setConstraints(constraintsRes.data.hard_constraints);
      }

      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch AI status:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6 shadow-sm">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-3"></div>
          <div className="text-sm text-blue-600 font-medium">加载AI状态中...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* AI Orchestrator状态 */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300">
        <div className="px-5 py-4 border-b border-blue-200 bg-gradient-to-r from-blue-100/50 to-indigo-100/50 rounded-t-xl">
          <h3 className="text-base font-bold text-gray-900 flex items-center">
            <span className="text-2xl mr-2">🤖</span> 
            <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">AI编排器状态</span>
          </h3>
        </div>
        <div className="p-5 space-y-3">
          <div className="flex justify-between items-center py-2 px-3 bg-white/60 rounded-lg hover:bg-white/80 transition-colors">
            <span className="text-gray-700 font-medium">运行状态:</span>
            <span className="font-semibold">
              {orchestratorStatus?.running ? (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-green-100 text-green-700 border border-green-200">
                  ✅ 运行中
                </span>
              ) : (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-red-100 text-red-700 border border-red-200">
                  ❌ 已停止
                </span>
              )}
            </span>
          </div>
          <div className="flex justify-between items-center py-2 px-3 bg-white/60 rounded-lg hover:bg-white/80 transition-colors">
            <span className="text-gray-700 font-medium">权限等级:</span>
            <span className="font-mono font-bold text-lg bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              {orchestratorStatus?.permission_level || 'L1'} <span className="text-sm text-gray-600 font-normal">({getPermissionName(orchestratorStatus?.permission_level)})</span>
            </span>
          </div>
          <div className="flex justify-between items-center py-2 px-3 bg-white/60 rounded-lg hover:bg-white/80 transition-colors">
            <span className="text-gray-700 font-medium">运行时长:</span>
            <span className="font-mono text-gray-900 font-semibold">{orchestratorStatus?.runtime_hours?.toFixed(2) || '0.00'}小时</span>
          </div>
          <div className="flex justify-between items-center py-2 px-3 bg-white/60 rounded-lg hover:bg-white/80 transition-colors">
            <span className="text-gray-700 font-medium">决策次数:</span>
            <div className="flex items-center gap-2">
              <span className="font-mono font-bold text-gray-900">{orchestratorStatus?.total_decisions || 0}</span>
              <span className="text-xs text-gray-500">
                (<span className="text-green-600 font-semibold">✅ {orchestratorStatus?.approved || 0}</span>, 
                <span className="text-red-600 font-semibold ml-1">❌ {(orchestratorStatus?.total_decisions || 0) - (orchestratorStatus?.approved || 0)}</span>)
              </span>
            </div>
          </div>
          <div className="flex justify-between items-center py-2 px-3 bg-white/60 rounded-lg hover:bg-white/80 transition-colors">
            <span className="text-gray-700 font-medium">批准率:</span>
            <span className={`font-mono font-bold text-lg ${
              (orchestratorStatus?.approval_rate || 0) > 20 ? 'text-green-600' : 
              (orchestratorStatus?.approval_rate || 0) > 10 ? 'text-yellow-600' : 'text-red-600'
            }`}>
              {orchestratorStatus?.approval_rate?.toFixed(1) || '0.0'}%
            </span>
          </div>
          <div className="flex justify-between items-center py-2 px-3 bg-white/60 rounded-lg hover:bg-white/80 transition-colors">
            <span className="text-gray-700 font-medium">决策间隔:</span>
            <span className="font-mono font-semibold text-gray-900">{orchestratorStatus?.decision_interval || 300}秒</span>
          </div>
        </div>
      </div>

      {/* 约束状态 */}
      <div className="bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-200 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300">
        <div className="px-5 py-4 border-b border-amber-200 bg-gradient-to-r from-amber-100/50 to-orange-100/50 rounded-t-xl">
          <h3 className="text-base font-bold text-gray-900 flex items-center">
            <span className="text-2xl mr-2">🛡️</span> 
            <span className="bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">约束状态</span>
          </h3>
        </div>
        <div className="p-5 space-y-3">
          {orchestratorStatus?.permission_config && (
            <>
              <div className="flex justify-between items-center py-2 px-3 bg-white/60 rounded-lg hover:bg-white/80 transition-colors">
                <span className="text-gray-700 font-medium">最大仓位限制</span>
                <span className="font-mono font-bold text-amber-700">{(orchestratorStatus.permission_config.max_position_pct * 100).toFixed(0)}% <span className="text-gray-400">/</span></span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-white/60 rounded-lg hover:bg-white/80 transition-colors">
                <span className="text-gray-700 font-medium">最大杠杆限制</span>
                <span className="font-mono font-bold text-amber-700">{orchestratorStatus.permission_config.max_leverage}x <span className="text-gray-400">/</span></span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-white/60 rounded-lg hover:bg-white/80 transition-colors">
                <span className="text-gray-700 font-medium">最小置信度</span>
                <span className="font-mono font-bold text-amber-700">{(orchestratorStatus.permission_config.confidence_threshold * 100).toFixed(0)}% <span className="text-gray-400">/</span></span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-white/60 rounded-lg hover:bg-white/80 transition-colors">
                <span className="text-gray-700 font-medium">每日交易次数</span>
                <span className="font-mono font-bold text-amber-700">0/{orchestratorStatus.permission_config.max_daily_trades} <span className="text-gray-400">/</span></span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-white/60 rounded-lg hover:bg-white/80 transition-colors">
                <span className="text-gray-700 font-medium">最大回撤限制</span>
                <span className="font-mono font-bold text-amber-700">0% <span className="text-gray-400">/</span></span>
              </div>
            </>
          )}
          {Object.entries(constraints).length > 0 && (
            <div className="mt-4 pt-4 border-t border-amber-200 space-y-2">
              {Object.entries(constraints).map(([key, constraint]) => (
                <div key={key} className="flex items-center justify-between py-2 px-3 bg-white/60 rounded-lg hover:bg-white/80 transition-colors">
                  <div className="flex-1">
                    <div className="font-semibold text-gray-900 text-sm">{constraint.name}</div>
                    <div className="text-gray-600 font-mono mt-1 text-xs">
                      {constraint.current} / {constraint.threshold}
                    </div>
                  </div>
                  <div className="text-xl">
                    {constraint.status === 'pass' && <span className="text-green-600">✅</span>}
                    {constraint.status === 'warning' && <span className="text-yellow-600">⚠️</span>}
                    {constraint.status === 'violated' && <span className="text-red-600">❌</span>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* 记忆系统状态 */}
      <div className="bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300">
        <div className="px-5 py-4 border-b border-purple-200 bg-gradient-to-r from-purple-100/50 to-pink-100/50 rounded-t-xl">
          <h3 className="text-base font-bold text-gray-900 flex items-center">
            <span className="text-2xl mr-2">🧠</span> 
            <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">记忆系统状态</span>
          </h3>
        </div>
        <div className="p-5 space-y-3">
          <div className="flex justify-between items-center py-2 px-3 bg-white/60 rounded-lg hover:bg-white/80 transition-colors">
            <span className="text-gray-700 font-medium">短期记忆:</span>
            <span className="font-mono font-bold text-purple-700">{orchestratorStatus?.total_decisions || 0} <span className="text-gray-600 font-normal">条决策</span></span>
          </div>
          <div className="flex justify-between items-center py-2 px-3 bg-white/60 rounded-lg hover:bg-white/80 transition-colors">
            <span className="text-gray-700 font-medium">长期记忆:</span>
            <span className="font-mono text-gray-400">0 <span className="font-normal">个模式</span></span>
          </div>
          <div className="flex justify-between items-center py-2 px-3 bg-white/60 rounded-lg hover:bg-white/80 transition-colors">
            <span className="text-gray-700 font-medium">知识库:</span>
            <span className="font-mono text-gray-400">0 <span className="font-normal">条经验</span></span>
          </div>
        </div>
      </div>

      {/* Qwen情报官状态 */}
      <div className="bg-gradient-to-br from-indigo-50 to-cyan-50 border border-indigo-200 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300">
        <div className="px-5 py-4 border-b border-indigo-200 bg-gradient-to-r from-indigo-100/50 to-cyan-100/50 rounded-t-xl">
          <h3 className="text-base font-bold text-gray-900 flex items-center">
            <span className="text-2xl mr-2">🕵️‍♀️</span> 
            <span className="bg-gradient-to-r from-indigo-600 to-cyan-600 bg-clip-text text-transparent">Qwen情报官</span>
          </h3>
        </div>
        <div className="p-5 space-y-3">
          <div className="flex justify-between items-center py-2 px-3 bg-white/60 rounded-lg hover:bg-white/80 transition-colors">
            <span className="text-gray-700 font-medium">运行状态:</span>
            <span className={`font-bold ${orchestratorStatus?.running ? 'text-green-600' : 'text-red-600'}`}>
              {orchestratorStatus?.running ? '✓ 运行中' : '× 已停止'}
            </span>
          </div>
          <div className="flex justify-between items-center py-2 px-3 bg-white/60 rounded-lg hover:bg-white/80 transition-colors">
            <span className="text-gray-700 font-medium">更新间隔:</span>
            <span className="font-mono font-bold text-indigo-700">30 <span className="text-gray-600 font-normal">分钟</span></span>
          </div>
          <div className="flex justify-between items-center py-2 px-3 bg-white/60 rounded-lg hover:bg-white/80 transition-colors">
            <span className="text-gray-700 font-medium">协作模式:</span>
            <span className="text-cyan-600 font-semibold">Qwen → DeepSeek</span>
          </div>
          <div className="mt-4 pt-3 border-t border-indigo-100">
            <p className="text-xs text-gray-600 leading-relaxed">
              <span className="font-semibold">情报官:</span> Qwen收集市场情报、分析新闻和巨鲸活动<br/>
              <span className="font-semibold">交易官:</span> DeepSeek基于情报做出交易决策
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

