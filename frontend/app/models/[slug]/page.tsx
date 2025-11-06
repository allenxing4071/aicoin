'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import axios from 'axios';
import Link from 'next/link';
import TradeListComplete from '@/app/components/trades/TradeListComplete';
import DecisionTimeline from '@/app/components/ai/DecisionTimeline';

const API_BASE = 'http://localhost:8000/api/v1';

interface ModelStats {
  name: string;
  slug: string;
  status: 'active' | 'paused' | 'stopped';
  balance: number;
  totalReturn: number;
  totalTrades: number;
  winRate: number;
  sharpeRatio: number;
  maxDrawdown: number;
}

export default function ModelDetailPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params.slug as string;
  
  const [modelStats, setModelStats] = useState<ModelStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'trades' | 'decisions'>('overview');

  useEffect(() => {
    fetchModelData();
  }, [slug]);

  const fetchModelData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 获取账户信息
      const accountResponse = await axios.get(`${API_BASE}/account/info`);
      const balance = parseFloat(accountResponse.data.equity || accountResponse.data.balance || 0);

      // 获取性能指标
      const performanceResponse = await axios.get(`${API_BASE}/performance/metrics`);
      const metrics = performanceResponse.data;

      // 获取AI状态 - 使用正确的endpoint
      const statusResponse = await axios.get(`${API_BASE}/ai/status`);
      const orchestratorData = statusResponse.data.orchestrator || {};

      // 构建模型数据
      const modelData: ModelStats = {
        name: slug === 'deepseek-chat-v3.1' ? 'DEEPSEEK CHAT V3.1' : slug.toUpperCase(),
        slug: slug,
        status: orchestratorData.is_running ? 'active' : 'paused',
        balance: balance,
        totalReturn: Number(metrics.total_return) || 0,
        totalTrades: Number(metrics.total_trades) || 0,
        winRate: Number(metrics.win_rate) || 0,
        sharpeRatio: Number(metrics.sharpe_ratio) || 0,
        maxDrawdown: Number(metrics.max_drawdown) || 0,
      };

      setModelStats(modelData);
    } catch (err: any) {
      console.error('Error fetching model data:', err);
      setError('Failed to load model data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">加载模型数据中...</p>
        </div>
      </div>
    );
  }

  if (error || !modelStats) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">[ERROR]</h1>
          <h2 className="text-xl font-semibold text-gray-700 mb-4">MODEL NOT FOUND</h2>
          <p className="text-gray-600 mb-6">The specified AI model does not exist in the system.</p>
          <div className="flex gap-4 justify-center">
            <Link 
              href="/"
              className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              [BACK TO LIVE]
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-50';
      case 'paused': return 'text-yellow-600 bg-yellow-50';
      case 'stopped': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return '运行中';
      case 'paused': return '已暂停';
      case 'stopped': return '已停止';
      default: return '未知';
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <Link href="/" className="text-blue-600 hover:text-blue-700 flex items-center gap-2">
              <span>←</span>
              <span>返回主页</span>
            </Link>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{modelStats.name}</h1>
              <div className="flex items-center gap-4 text-sm">
                <span className={`px-3 py-1 rounded-full font-semibold ${getStatusColor(modelStats.status)}`}>
                  {getStatusText(modelStats.status)}
                </span>
                <span className="text-gray-600">Slug: {modelStats.slug}</span>
              </div>
            </div>
            
            <div className="text-right">
              <div className="text-sm text-gray-600 mb-1">账户余额</div>
              <div className="text-3xl font-bold text-gray-900">
                ${modelStats.balance.toFixed(2)}
              </div>
              <div className={`text-sm font-semibold ${modelStats.totalReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {modelStats.totalReturn >= 0 ? '+' : ''}{modelStats.totalReturn.toFixed(2)}%
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="border-b border-gray-200 bg-white sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-8">
            <button
              onClick={() => setActiveTab('overview')}
              className={`py-4 px-2 font-semibold border-b-2 transition-colors ${
                activeTab === 'overview'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              概览
            </button>
            <button
              onClick={() => setActiveTab('trades')}
              className={`py-4 px-2 font-semibold border-b-2 transition-colors ${
                activeTab === 'trades'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              交易历史
            </button>
            <button
              onClick={() => setActiveTab('decisions')}
              className={`py-4 px-2 font-semibold border-b-2 transition-colors ${
                activeTab === 'decisions'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              决策记录
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* 性能指标卡片 */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="text-sm text-gray-600 mb-2">总交易数</div>
              <div className="text-3xl font-bold text-gray-900">{modelStats.totalTrades}</div>
            </div>
            
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="text-sm text-gray-600 mb-2">胜率</div>
              <div className="text-3xl font-bold text-gray-900">{modelStats.winRate.toFixed(1)}%</div>
            </div>
            
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="text-sm text-gray-600 mb-2">夏普比率</div>
              <div className="text-3xl font-bold text-gray-900">{modelStats.sharpeRatio.toFixed(2)}</div>
            </div>
            
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="text-sm text-gray-600 mb-2">最大回撤</div>
              <div className="text-3xl font-bold text-red-600">{modelStats.maxDrawdown.toFixed(2)}%</div>
            </div>

            {/* 详细信息 */}
            <div className="col-span-full bg-gray-50 border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">模型信息</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">模型类型:</span>
                  <span className="ml-2 font-semibold text-gray-900">DeepSeek Chat V3.1</span>
                </div>
                <div>
                  <span className="text-gray-600">状态:</span>
                  <span className="ml-2 font-semibold text-gray-900">{getStatusText(modelStats.status)}</span>
                </div>
                <div>
                  <span className="text-gray-600">总收益:</span>
                  <span className={`ml-2 font-semibold ${modelStats.totalReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {modelStats.totalReturn >= 0 ? '+' : ''}{modelStats.totalReturn.toFixed(2)}%
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">账户余额:</span>
                  <span className="ml-2 font-semibold text-gray-900">${modelStats.balance.toFixed(2)}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'trades' && (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">交易历史</h3>
            <div className="h-[600px] overflow-y-auto">
              <TradeListComplete 
                selectedModel={modelStats.slug} 
                models={[{ name: modelStats.name, slug: modelStats.slug, value: modelStats.balance, change: modelStats.totalReturn, color: '#3b82f6', icon: 'deepseek' }]} 
              />
            </div>
          </div>
        )}

        {activeTab === 'decisions' && (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">决策记录</h3>
            <div className="h-[600px]">
              <DecisionTimeline filter={modelStats.slug} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

