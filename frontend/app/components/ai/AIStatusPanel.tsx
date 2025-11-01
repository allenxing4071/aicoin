'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

interface OrchestratorStatus {
  running: boolean;
  permission_level: string;
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
      // 获取AI状态
      const healthRes = await axios.get('http://localhost:8000/health');
      if (healthRes.data.orchestrator_status) {
        setOrchestratorStatus({
          running: healthRes.data.orchestrator_status.is_running,
          permission_level: healthRes.data.orchestrator_status.permission_level,
          runtime_hours: healthRes.data.orchestrator_status.runtime_hours,
          total_decisions: healthRes.data.orchestrator_status.total_decisions,
          approved: healthRes.data.orchestrator_status.approved_decisions,
          approval_rate: healthRes.data.orchestrator_status.approval_rate,
          decision_interval: healthRes.data.orchestrator_status.decision_interval
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
      <div className="bg-white border border-gray-200 p-4">
        <div className="text-sm text-gray-500">加载AI状态中...</div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* AI Orchestrator状态 */}
      <div className="bg-white border border-gray-200">
        <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
          <h3 className="text-sm font-bold text-gray-900">🤖 AI编排器状态</h3>
        </div>
        <div className="p-4 space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">运行状态:</span>
            <span className="font-mono">
              {orchestratorStatus?.running ? (
                <span className="text-green-600">✅ 运行中</span>
              ) : (
                <span className="text-red-600">❌ 已停止</span>
              )}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">权限等级:</span>
            <span className="font-mono font-semibold">
              {orchestratorStatus?.permission_level || 'L1'} (新手级)
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">运行时长:</span>
            <span className="font-mono">{orchestratorStatus?.runtime_hours?.toFixed(2) || '0.00'}小时</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">决策次数:</span>
            <span className="font-mono">
              {orchestratorStatus?.total_decisions || 0} 
              <span className="text-gray-400 ml-1">
                (✅ {orchestratorStatus?.approved || 0}, ❌ {(orchestratorStatus?.total_decisions || 0) - (orchestratorStatus?.approved || 0)})
              </span>
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">批准率:</span>
            <span className={`font-mono font-semibold ${
              (orchestratorStatus?.approval_rate || 0) > 20 ? 'text-green-600' : 
              (orchestratorStatus?.approval_rate || 0) > 10 ? 'text-yellow-600' : 'text-red-600'
            }`}>
              {orchestratorStatus?.approval_rate?.toFixed(1) || '0.0'}%
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">决策间隔:</span>
            <span className="font-mono">{orchestratorStatus?.decision_interval || 300}秒</span>
          </div>
        </div>
      </div>

      {/* 约束状态 */}
      <div className="bg-white border border-gray-200">
        <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
          <h3 className="text-sm font-bold text-gray-900">🛡️ 约束状态</h3>
        </div>
        <div className="p-4 space-y-2 text-xs">
          {Object.entries(constraints).map(([key, constraint]) => (
            <div key={key} className="flex items-center justify-between py-1">
              <div className="flex-1">
                <div className="font-semibold text-gray-900">{constraint.name}</div>
                <div className="text-gray-500 font-mono mt-0.5">
                  {constraint.current} / {constraint.threshold}
                </div>
              </div>
              <div>
                {constraint.status === 'pass' && <span className="text-green-600">✅</span>}
                {constraint.status === 'warning' && <span className="text-yellow-600">⚠️</span>}
                {constraint.status === 'violated' && <span className="text-red-600">❌</span>}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 记忆系统状态 */}
      <div className="bg-white border border-gray-200">
        <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
          <h3 className="text-sm font-bold text-gray-900">🧠 记忆系统状态</h3>
        </div>
        <div className="p-4 space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">短期记忆:</span>
            <span className="font-mono">{orchestratorStatus?.total_decisions || 0} 条决策</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">长期记忆:</span>
            <span className="font-mono text-gray-400">0 个模式</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">知识库:</span>
            <span className="font-mono text-gray-400">0 条经验</span>
          </div>
        </div>
      </div>
    </div>
  );
}

