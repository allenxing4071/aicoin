'use client';

import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import PriceTicker from './components/ticker/PriceTicker';
import MultiModelChart from './components/charts/MultiModelChart';
import ModelCard from './components/models/ModelCard';
import DeepSeekLogo from './components/common/DeepSeekLogo';
import PermissionIndicator from './components/ai/PermissionIndicator';

// ✨ 性能优化: 懒加载非关键组件,减少首屏加载时间
const TradeListComplete = dynamic(() => import('./components/trades/TradeListComplete'), {
  ssr: false,
  loading: () => <div className="flex items-center justify-center h-64"><div className="text-gray-400">加载交易列表...</div></div>
});

const AIDecisionChat = dynamic(() => import('./components/chat/AIDecisionChat'), {
  ssr: false,
  loading: () => <div className="flex items-center justify-center h-64"><div className="text-gray-400">加载AI聊天...</div></div>
});

const TradingChart = dynamic(() => import('./components/charts/TradingChart'), {
  ssr: false,
  loading: () => <div className="flex items-center justify-center h-64"><div className="text-gray-400">加载图表...</div></div>
});

const PositionsList = dynamic(() => import('./components/positions/PositionsList'), {
  ssr: false,
  loading: () => <div className="flex items-center justify-center h-64"><div className="text-gray-400">加载持仓...</div></div>
});

const AIStatusPanel = dynamic(() => import('./components/ai/AIStatusPanel'), {
  ssr: false,
  loading: () => <div className="flex items-center justify-center h-64"><div className="text-gray-400">加载AI状态...</div></div>
});

const DecisionTimeline = dynamic(() => import('./components/ai/DecisionTimeline'), {
  ssr: false,
  loading: () => <div className="flex items-center justify-center h-64"><div className="text-gray-400">加载决策时间线...</div></div>
});

const PerformanceDashboard = dynamic(() => import('./components/performance/PerformanceDashboard'), {
  ssr: false,
  loading: () => <div className="flex items-center justify-center h-64"><div className="text-gray-400">加载性能面板...</div></div>
});

const IntelligencePanel = dynamic(() => import('./components/intelligence/IntelligencePanel'), {
  ssr: false,
  loading: () => <div className="flex items-center justify-center h-64"><div className="text-gray-400">加载情报面板...</div></div>
});

const API_BASE = 'http://localhost:8000/api/v1';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'chart' | 'trades' | 'chat' | 'positions' | 'readme' | 'ai' | 'decisions' | 'performance' | 'intelligence'>('trades');
  const [timeRange, setTimeRange] = useState<'all' | '72h'>('all');
  const [selectedModel, setSelectedModel] = useState<string>('all');
  const [apiStatus, setApiStatus] = useState({ status: 'checking', version: '0.0.0' });
  const [accountData, setAccountData] = useState<any>(null);
  const [showModelsDropdown, setShowModelsDropdown] = useState(false);
  const [aiHealth, setAiHealth] = useState<any>(null);
  const [modelsData, setModelsData] = useState<any[]>([
    { name: 'DEEPSEEK CHAT V3.1', slug: 'deepseek-chat-v3.1', value: 0, change: 0, color: '#3b82f6', icon: 'deepseek' },
    // Qwen已禁用 - 只使用DeepSeek单一AI模型
    // { name: 'QWEN3 MAX', slug: 'qwen3-max', value: 0, change: 0, color: '#ec4899', icon: '🎨' },
  ]);
  const [loadingModels, setLoadingModels] = useState(true);
  
  // ✨ 性能优化: 记录已访问过的标签页,避免重复加载
  const [loadedTabs, setLoadedTabs] = useState<Set<string>>(new Set(['trades']));

  // 使用useMemo稳定models引用，避免React重新渲染错误
  const modelsWithData = useMemo(() => modelsData, [JSON.stringify(modelsData)]);

  // 使用真实的单一账户余额
  const totalValue = modelsWithData.length > 0 ? modelsWithData[0].value : 0;
  const currentModel = modelsWithData.length > 0 ? modelsWithData[0] : null;

  // ✨ 性能优化: 使用统一的仪表板API
  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(() => {
      fetchDashboardData();
    }, 30000); // 优化: 30秒刷新一次 (原10秒)
    return () => clearInterval(interval);
  }, []);

  // ✨ 新方法: 一次性获取所有仪表板数据 (优化: 4个请求 → 1个请求)
  const fetchDashboardData = async () => {
    try {
      const response = await axios.get(`${API_BASE}/dashboard/summary`, {
        timeout: 15000 // 15秒超时 (交易服务初始化可能需要时间)
      });
      
      if (response.data.success) {
        const { api_status, account, models, ai_health } = response.data.data;
        
        // 设置API状态
        setApiStatus(api_status || { status: 'unavailable', version: 'N/A' });
        
        // 设置账户数据
        setAccountData(account || null);
        
        // 设置模型数据
        if (models && models.length > 0) {
          setModelsData(models);
          setLoadingModels(false);
        } else {
          setLoadingModels(true);
        }
        
        // 设置AI健康状态
        if (ai_health) {
          const orchestratorData = ai_health.orchestrator || {};
        setAiHealth({
          success: true,
          orchestrator_running: orchestratorData.is_running || false,
          stats: {
            total_trades: orchestratorData.total_decisions || 0,
            successful_trades: orchestratorData.approved_decisions || 0,
          },
          permission_level: orchestratorData.permission_level || 'L0',
            orchestrator: orchestratorData
        });
        }
        
      }
    } catch (error: any) {
      console.error('❌ Failed to fetch dashboard data:', error);
      
      // 降级处理: 使用默认值
      setApiStatus({ status: 'unavailable', version: 'N/A' });
      setAiHealth({
        success: false,
        orchestrator_running: false,
        stats: { total_trades: 0, successful_trades: 0 },
        permission_level: 'L0'
      });
      setLoadingModels(true);
    }
  };

  const handleModelClick = (slug: string) => {
    setSelectedModel(selectedModel === slug ? 'all' : slug);
  };

  return (
    <div className="min-h-screen bg-white text-gray-900">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-3 shadow-sm">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-900 flex items-center">
            {/* Ghost Icon */}
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="mr-2">
              <path d="M12 2C8.5 2 6 4.5 6 8V16C6 16.5 6.2 17 6.5 17.3L8 19L9.5 17.3C9.8 17 10.2 17 10.5 17.3L12 19L13.5 17.3C13.8 17 14.2 17 14.5 17.3L16 19L17.5 17.3C17.8 17 18 16.5 18 16V8C18 4.5 15.5 2 12 2Z" fill="#6B7280" stroke="#374151" strokeWidth="1"/>
              <circle cx="9.5" cy="9" r="1.5" fill="#374151"/>
              <circle cx="14.5" cy="9" r="1.5" fill="#374151"/>
              <path d="M9 12C9 12 10 13 12 13C14 13 15 12 15 12" stroke="#374151" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            <span className={`relative flex h-2 w-2 mr-2 ${apiStatus.status === 'healthy' ? 'text-green-500' : 'text-red-500'}`}>
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${apiStatus.status === 'healthy' ? 'bg-green-400' : 'bg-red-400'} opacity-75`}></span>
              <span className={`relative inline-flex rounded-full h-2 w-2 ${apiStatus.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`}></span>
            </span>
            AI Ghost <span className="text-sm text-gray-500 ml-1">by allen</span>
          </h1>
          
          <nav className="absolute left-1/2 transform -translate-x-1/2 flex space-x-1 text-sm font-bold">
            <a href="/" className="px-3 py-1">实时交易</a>
            <span>|</span>
            <div className="relative">
              <button 
                onClick={() => setShowModelsDropdown(!showModelsDropdown)}
                className="px-3 py-1 hover:bg-gray-100 transition-colors"
              >
                模型
              </button>
              
              {showModelsDropdown && (
                <div className="absolute top-full left-0 mt-2 w-64 bg-white border-2 border-black shadow-lg z-50">
                  <div className="p-4">
                    <h3 className="text-xs font-bold text-gray-500 mb-3 border-b border-gray-300 pb-2">AI MODELS</h3>
                    <div className="space-y-2">
                      {/* 只显示DeepSeek模型 */}
                      <Link 
                        href="/models/deepseek-chat-v3.1" 
                        className="flex items-center space-x-3 p-2 hover:bg-gray-100 transition-colors cursor-pointer"
                        onClick={() => setShowModelsDropdown(false)}
                      >
                        <DeepSeekLogo size={32} />
                        <div>
                          <div className="text-sm font-semibold text-gray-900">DEEPSEEK CHAT V3.1</div>
                          <div className="text-xs text-gray-600">查看模型详情 →</div>
                        </div>
                      </Link>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </nav>
          
          {/* 已移除: JOIN THE PLATFORM WAITLIST / ABOUT NOF1 链接 */}
        </div>
      </header>

      <PriceTicker />

      {/* Main Content */}
      <div className="flex h-[calc(100vh-140px)]">
        {/* Left - Chart Area */}
        <div className="flex-1 flex flex-col overflow-hidden border-r border-gray-200 bg-white">
          {/* Top Stats */}
          <div className="bg-white px-6 py-4 border-b border-gray-200">
            <div className="flex items-end justify-between">
              <div>
                <div className="text-sm text-gray-500 mb-1">账户总价值</div>
                <div className="flex items-baseline space-x-3">
                  {loadingModels ? (
                    <span className="text-2xl text-gray-400 animate-pulse">加载中...</span>
                  ) : (
                    <span className="text-4xl font-bold text-gray-900">
                      ${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 6 })}
                    </span>
                  )}
                </div>
              </div>
              {/* AI模型标签已删除 */}
            </div>
          </div>

          {/* Tabs */}
          <div className="bg-white border-b border-gray-200 px-6">
            <div className="flex space-x-6">
              <button 
                onClick={() => setTimeRange('all')}
                className={`px-4 py-3 text-sm font-bold border-b-2 transition-colors ${
                  timeRange === 'all' ? 'border-gray-900 text-gray-900' : 'border-transparent text-gray-500 hover:text-gray-900'
                }`}
              >
                ALL
              </button>
              <button 
                onClick={() => setTimeRange('72h')}
                className={`px-4 py-3 text-sm font-bold border-b-2 transition-colors ${
                  timeRange === '72h' ? 'border-gray-900 text-gray-900' : 'border-transparent text-gray-500 hover:text-gray-900'
                }`}
              >
                72H
              </button>
            </div>
          </div>

          {/* Chart */}
          <div className="flex-1 bg-white p-6">
            <MultiModelChart models={modelsWithData} timeRange={timeRange} />
          </div>

          {/* Model Cards */}
          <div className="bg-gray-50 border-t border-gray-200 p-4">
            <div className="flex flex-col gap-2">
              {modelsWithData.map((model, index) => (
                <div 
                  key={index}
                  onClick={() => handleModelClick(model.slug)}
                  className={selectedModel === model.slug ? 'ring-2 ring-blue-500 rounded-lg' : ''}
                >
                  <ModelCard model={model} />
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right - Content Area */}
        <div className="w-[600px] bg-white flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <div className="mb-3">
              <div className="flex flex-wrap gap-2">
                <button 
                  onClick={() => { setActiveTab('trades'); setLoadedTabs(prev => new Set(prev).add('trades')); }}
                  className={`px-3 py-2 text-xs font-bold rounded transition-colors whitespace-nowrap flex items-center gap-1 ${
                    activeTab === 'trades' ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <span>✅</span>
                  <span>已完成交易</span>
                </button>
                <button 
                  onClick={() => { setActiveTab('chat'); setLoadedTabs(prev => new Set(prev).add('chat')); }}
                  className={`px-3 py-2 text-xs font-bold rounded transition-colors whitespace-nowrap flex items-center gap-1 ${
                    activeTab === 'chat' ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <span>💬</span>
                  <span>挂单对话</span>
                </button>
                <button 
                  onClick={() => { setActiveTab('positions'); setLoadedTabs(prev => new Set(prev).add('positions')); }}
                  className={`px-3 py-2 text-xs font-bold rounded transition-colors whitespace-nowrap flex items-center gap-1 ${
                    activeTab === 'positions' ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <span>📊</span>
                  <span>持仓</span>
                </button>
                <button 
                  onClick={() => { setActiveTab('ai'); setLoadedTabs(prev => new Set(prev).add('ai')); }}
                  className={`px-3 py-2 text-xs font-bold rounded transition-colors whitespace-nowrap flex items-center gap-1 ${
                    activeTab === 'ai' ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <span>🤖</span>
                  <span>AI状态</span>
                </button>
                <button 
                  onClick={() => { setActiveTab('decisions'); setLoadedTabs(prev => new Set(prev).add('decisions')); }}
                  className={`px-3 py-2 text-xs font-bold rounded transition-colors whitespace-nowrap flex items-center gap-1 ${
                    activeTab === 'decisions' ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <span>📋</span>
                  <span>决策历史</span>
                </button>
                <button 
                  onClick={() => { setActiveTab('performance'); setLoadedTabs(prev => new Set(prev).add('performance')); }}
                  className={`px-3 py-2 text-xs font-bold rounded transition-colors whitespace-nowrap flex items-center gap-1 ${
                    activeTab === 'performance' ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <span>📈</span>
                  <span>性能仪表盘</span>
                </button>
                <button 
                  onClick={() => { setActiveTab('intelligence'); setLoadedTabs(prev => new Set(prev).add('intelligence')); }}
                  className={`px-3 py-2 text-xs font-bold rounded transition-colors whitespace-nowrap flex items-center gap-1 ${
                    activeTab === 'intelligence' ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <span>🕵️‍♀️</span>
                  <span>情报中心</span>
                </button>
              </div>
            </div>
            
            {activeTab === 'trades' && (
              <div className="flex items-center justify-between">
                <div className="text-xs text-gray-600">
                  <span className="font-mono">筛选:</span>
                  <select 
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="ml-2 bg-white text-gray-900 text-xs px-2 py-1 rounded border border-gray-300 focus:border-blue-500 focus:outline-none font-mono"
                  >
                    <option value="all">所有模型 ▼</option>
                    {modelsWithData.map(model => (
                      <option key={model.slug} value={model.slug}>{model.name}</option>
                    ))}
                  </select>
                </div>
                <div className="text-xs text-gray-600 font-mono">显示最近 <span className="font-bold">100</span> 笔交易</div>
              </div>
            )}
            
            {activeTab === 'positions' && (
              <div className="flex items-center justify-between">
                <div className="text-xs text-gray-600">
                  <span className="font-mono">筛选:</span>
                  <select 
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="ml-2 bg-white text-gray-900 text-xs px-2 py-1 rounded border border-gray-300 focus:border-blue-500 focus:outline-none font-mono"
                  >
                    <option value="all">所有模型 ▼</option>
                    {modelsWithData.map(model => (
                      <option key={model.slug} value={model.slug}>{model.name}</option>
                    ))}
                  </select>
                </div>
              </div>
            )}
          </div>

          <div className="flex-1 overflow-hidden">
            {/* ✨ 性能优化: 使用display控制显示,保持已加载组件在DOM中 */}
            <div style={{ display: activeTab === 'trades' ? 'block' : 'none', height: '100%' }}>
              {loadedTabs.has('trades') && <TradeListComplete selectedModel={selectedModel} models={modelsWithData} />}
            </div>
            <div style={{ display: activeTab === 'chat' ? 'block' : 'none', height: '100%' }}>
              {loadedTabs.has('chat') && <AIDecisionChat selectedModel={selectedModel} />}
            </div>
            <div style={{ display: activeTab === 'positions' ? 'block' : 'none', height: '100%' }}>
              {loadedTabs.has('positions') && <PositionsList selectedModel={selectedModel} />}
            </div>
            <div style={{ display: activeTab === 'ai' ? 'block' : 'none', height: '100%' }}>
              {loadedTabs.has('ai') && (
                <div className="h-full overflow-y-auto p-4 space-y-4">
                  <AIStatusPanel />
                  <PermissionIndicator />
                </div>
              )}
            </div>
            <div style={{ display: activeTab === 'decisions' ? 'block' : 'none', height: '100%' }}>
              {loadedTabs.has('decisions') && (
                <div className="h-full overflow-y-auto p-4">
                  <DecisionTimeline />
                </div>
              )}
            </div>
            <div style={{ display: activeTab === 'performance' ? 'block' : 'none', height: '100%' }}>
              {loadedTabs.has('performance') && (
                <div className="h-full overflow-y-auto p-4">
                  <PerformanceDashboard />
                </div>
              )}
            </div>
            <div style={{ display: activeTab === 'intelligence' ? 'block' : 'none', height: '100%' }}>
              {loadedTabs.has('intelligence') && (
                <div className="h-full overflow-y-auto p-4">
                  <IntelligencePanel />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Terminal Status Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-black text-green-400 font-mono text-xs py-2 px-4 flex items-center justify-between z-50">
        <div className="flex items-center space-x-4">
          <span>[████████████]</span>
          <span>状态: {apiStatus.status === 'healthy' ? '已连接' : apiStatus.status === 'checking' ? '连接中' : '未连接'}</span>
          <span className="text-gray-500">|</span>
          <span>API: {apiStatus.version}</span>
          <span className="text-gray-500">|</span>
          <span>编排器: {aiHealth?.orchestrator_running ? '运行中' : '已停止'}</span>
        </div>
        <div className="flex items-center space-x-4">
          <span>DEEPSEEK: {aiHealth?.models?.['deepseek-chat-v3.1']?.status === 'running' ? '✅' : '⏸️'}</span>
          <span className="text-gray-500">|</span>
          <span>交易数: {aiHealth?.stats?.total_trades || 0}</span>
          <span className="text-gray-500">|</span>
          <span suppressHydrationWarning>{new Date().toLocaleTimeString('zh-CN', { hour12: false })}</span>
        </div>
      </div>
    </div>
  );
}
