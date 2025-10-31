'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import DecisionFlowViewer from './DecisionFlowViewer';

const API_BASE = 'http://localhost:8000/api/v1';

interface Decision {
  decision_id: string;
  timestamp: string;
  type: string;
  symbol: string;
  result: string;
  reason: string;
  confidence: number;
  permission_level: string;
  duration_ms: number;
}

export default function DecisionTimeline() {
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [selectedDecisionId, setSelectedDecisionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'approved' | 'rejected'>('all');

  useEffect(() => {
    fetchDecisions();
    const interval = setInterval(fetchDecisions, 30000); // 每30秒刷新
    return () => clearInterval(interval);
  }, [filter]);

  const fetchDecisions = async () => {
    try {
      const status = filter === 'all' ? undefined : filter;
      const res = await axios.get(`${API_BASE}/ai/decisions`, {
        params: { limit: 25, status }
      });
      setDecisions(res.data.decisions || []);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch decisions:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white border border-gray-200 p-4">
        <div className="text-sm text-gray-500">Loading decisions...</div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* 决策详情查看器 */}
      {selectedDecisionId && (
        <div className="bg-white border-2 border-blue-500">
          <div className="px-3 py-2 bg-blue-50 border-b border-blue-500 flex items-center justify-between">
            <h3 className="text-xs font-bold text-gray-900">DECISION DETAIL</h3>
            <button
              onClick={() => setSelectedDecisionId(null)}
              className="text-xs font-bold text-blue-600 hover:text-blue-800"
            >
              ✕ CLOSE
            </button>
          </div>
          <div className="p-3 max-h-96 overflow-y-auto">
            <DecisionFlowViewer decisionId={selectedDecisionId} />
          </div>
        </div>
      )}

      {/* 决策时间轴 */}
      <div className="bg-white border border-gray-200">
        <div className="px-3 py-2 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
          <h3 className="text-xs font-bold text-gray-900">DECISION TIMELINE</h3>
          <div className="flex space-x-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-2 py-1 text-xs font-bold rounded ${
                filter === 'all' ? 'bg-gray-900 text-white' : 'bg-gray-200 text-gray-600'
              }`}
            >
              ALL
            </button>
            <button
              onClick={() => setFilter('approved')}
              className={`px-2 py-1 text-xs font-bold rounded ${
                filter === 'approved' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-600'
              }`}
            >
              APPROVED
            </button>
            <button
              onClick={() => setFilter('rejected')}
              className={`px-2 py-1 text-xs font-bold rounded ${
                filter === 'rejected' ? 'bg-red-600 text-white' : 'bg-gray-200 text-gray-600'
              }`}
            >
              REJECTED
            </button>
          </div>
        </div>

        <div className="divide-y divide-gray-200">
          {decisions.length === 0 ? (
            <div className="p-4 text-sm text-gray-500 text-center">
              No decisions found
            </div>
          ) : (
            decisions.map((decision) => (
              <div
                key={decision.decision_id}
                onClick={() => setSelectedDecisionId(decision.decision_id)}
                className="p-3 hover:bg-gray-50 cursor-pointer transition-colors"
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center space-x-2">
                    <span className={`text-xs font-bold ${
                      decision.result === 'approved' || decision.result === 'approved_hard'
                        ? 'text-green-600'
                        : 'text-red-600'
                    }`}>
                      {decision.result === 'approved' || decision.result === 'approved_hard' ? '✅' : '❌'}
                    </span>
                    <span className={`px-2 py-0.5 text-xs font-bold rounded ${
                      decision.type === 'LONG' ? 'bg-green-100 text-green-700' :
                      decision.type === 'SHORT' ? 'bg-red-100 text-red-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {decision.type}
                    </span>
                    <span className="text-xs font-mono text-gray-900">
                      {decision.symbol}
                    </span>
                  </div>
                  <div className="text-xs text-gray-500 font-mono">
                    {new Date(decision.timestamp).toLocaleTimeString()}
                  </div>
                </div>
                
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-3">
                    <div>
                      <span className="text-gray-600">Confidence: </span>
                      <span className={`font-mono font-semibold ${
                        decision.confidence >= 0.8 ? 'text-green-600' :
                        decision.confidence >= 0.6 ? 'text-yellow-600' :
                        'text-red-600'
                      }`}>
                        {(decision.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">Level: </span>
                      <span className="font-mono">{decision.permission_level}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Duration: </span>
                      <span className="font-mono">{decision.duration_ms}ms</span>
                    </div>
                  </div>
                </div>

                {decision.reason && (
                  <div className="mt-1 text-xs text-gray-600">
                    💡 {decision.reason}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

