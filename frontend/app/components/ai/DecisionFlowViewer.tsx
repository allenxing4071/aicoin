'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = '/api/v1';

interface DecisionStep {
  step: number;
  name: string;
  status: 'completed' | 'failed' | 'skipped';
  duration_ms: number;
  data?: any;
}

interface DecisionDetail {
  decision_id: string;
  timestamp: string;
  result: string;
  reason: string;
  steps: DecisionStep[];
  metadata: any;
  reasoning?: any;
}

export default function DecisionFlowViewer({ decisionId }: { decisionId: string }) {
  const [decision, setDecision] = useState<DecisionDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (decisionId) {
      fetchDecisionDetail();
    }
  }, [decisionId]);

  const fetchDecisionDetail = async () => {
    try {
      const res = await axios.get(`${API_BASE}/ai/decisions/${decisionId}`);
      setDecision(res.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch decision detail:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-4 text-sm text-gray-500">Loading decision flow...</div>;
  }

  if (!decision) {
    return <div className="p-4 text-sm text-red-600">Decision not found</div>;
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅';
      case 'failed': return '❌';
      case 'skipped': return '⏭️';
      default: return '⏸️';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600';
      case 'failed': return 'text-red-600';
      case 'skipped': return 'text-gray-400';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-4">
      {/* 决策头部信息 */}
      <div className="bg-gray-50 border border-gray-200 p-3">
        <div className="flex items-center justify-between mb-2">
          <div className="text-xs font-bold text-gray-900">{decision.decision_id}</div>
          <div className="text-xs text-gray-500">
            {new Date(decision.timestamp).toLocaleString()}
          </div>
        </div>
        <div className="flex items-center justify-between text-xs">
          <div>
            <span className="text-gray-600">Result: </span>
            <span className={`font-mono font-semibold ${
              decision.result.includes('approved') ? 'text-green-600' : 'text-red-600'
            }`}>
              {decision.result}
            </span>
          </div>
          <div>
            <span className="text-gray-600">Duration: </span>
            <span className="font-mono">{decision.metadata?.total_duration_ms}ms</span>
          </div>
        </div>
        {decision.reason && (
          <div className="mt-2 text-xs text-gray-700 bg-yellow-50 border border-yellow-200 rounded p-2">
            💡 {decision.reason}
          </div>
        )}
      </div>

      {/* 10步流程 */}
      <div className="bg-white border border-gray-200">
        <div className="px-3 py-2 border-b border-gray-200 bg-gray-50">
          <h4 className="text-xs font-bold text-gray-900">DECISION FLOW (10 STEPS)</h4>
        </div>
        <div className="p-3 space-y-2">
          {decision.steps.map((step) => (
            <div key={step.step} className="border-l-2 border-gray-300 pl-3">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2">
                  <span className={getStatusColor(step.status)}>
                    {getStatusIcon(step.status)}
                  </span>
                  <span className="font-semibold text-gray-900">
                    Step {step.step}: {step.name}
                  </span>
                </div>
                <div className="text-gray-500 font-mono">
                  {step.duration_ms}ms
                </div>
              </div>
              {step.data && Object.keys(step.data).length > 0 && (
                <div className="mt-1 ml-6 text-xs text-gray-600">
                  {Object.entries(step.data).slice(0, 3).map(([key, value]) => (
                    <div key={key} className="font-mono">
                      {key}: {typeof value === 'object' ? JSON.stringify(value).slice(0, 50) : String(value)}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* AI推理 */}
      {decision.reasoning && (
        <div className="bg-white border border-gray-200">
          <div className="px-3 py-2 border-b border-gray-200 bg-gray-50">
            <h4 className="text-xs font-bold text-gray-900">AI REASONING</h4>
          </div>
          <div className="p-3 space-y-2 text-xs text-gray-700">
            {decision.reasoning.market_analysis && (
              <div>
                <span className="font-semibold">Market: </span>
                {decision.reasoning.market_analysis}
              </div>
            )}
            {decision.reasoning.risk_assessment && (
              <div>
                <span className="font-semibold">Risk: </span>
                {decision.reasoning.risk_assessment}
              </div>
            )}
            {decision.reasoning.decision_rationale && (
              <div>
                <span className="font-semibold">Rationale: </span>
                {decision.reasoning.decision_rationale}
              </div>
            )}
            {decision.reasoning.confidence_explanation && (
              <div className="bg-blue-50 border border-blue-200 rounded p-2 mt-2">
                <span className="font-semibold">Confidence: </span>
                {decision.reasoning.confidence_explanation}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

