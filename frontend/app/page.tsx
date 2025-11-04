'use client';

import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import Link from 'next/link';
import PriceTicker from './components/ticker/PriceTicker';
import MultiModelChart from './components/charts/MultiModelChart';
import TradeListComplete from './components/trades/TradeListComplete';
import AIDecisionChat from './components/chat/AIDecisionChat';
import ModelCard from './components/models/ModelCard';
import TradingChart from './components/charts/TradingChart';
import PositionsList from './components/positions/PositionsList';
import AIStatusPanel from './components/ai/AIStatusPanel';
import PermissionIndicator from './components/ai/PermissionIndicator';
import DecisionTimeline from './components/ai/DecisionTimeline';
import PerformanceDashboard from './components/performance/PerformanceDashboard';
import DeepSeekLogo from './components/common/DeepSeekLogo';
import IntelligencePanel from './components/intelligence/IntelligencePanel';

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

  // 使用useMemo稳定models引用，避免React重新渲染错误
  const modelsWithData = useMemo(() => modelsData, [JSON.stringify(modelsData)]);

  // 使用真实的单一账户余额
  const totalValue = modelsWithData.length > 0 ? modelsWithData[0].value : 0;
  const currentModel = modelsWithData.length > 0 ? modelsWithData[0] : null;

  useEffect(() => {
    checkApiStatus();
    fetchAccountData();
    fetchModelsData();
    fetchAiHealth();
    const interval = setInterval(() => {
      checkApiStatus();
      fetchAccountData();
      fetchModelsData();
      fetchAiHealth();
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  const checkApiStatus = async () => {
    try {
      const response = await axios.get('http://localhost:8000/health');
      setApiStatus(response.data);
    } catch (error) {
      setApiStatus({ status: 'unavailable', version: 'N/A' });
    }
  };

  const fetchAccountData = async () => {
    try {
      const response = await axios.get(`${API_BASE}/account/info`);
      setAccountData(response.data);
    } catch (error) {
      console.log('Using mock data for account info');
    }
  };

  const fetchAiHealth = async () => {
    try {
      // 获取系统状态（包含orchestrator信息）
      const response = await axios.get(`${API_BASE}/status`);
      if (response.data) {
        // 解析orchestrator状态
        const orchestratorData = response.data.orchestrator || {};
        setAiHealth({
          success: true,
          orchestrator_running: orchestratorData.is_running || false,
          stats: {
            total_trades: orchestratorData.total_decisions || 0,
            successful_trades: orchestratorData.approved_decisions || 0,
          },
          permission_level: orchestratorData.permission_level || 'L0',
          ...response.data
        });
      }
    } catch (error) {
      console.log('Failed to fetch AI health:', error);
      // Fallback to default values
      setAiHealth({
        success: false,
        orchestrator_running: false,
        stats: { total_trades: 0, successful_trades: 0 },
        permission_level: 'L0'
      });
    }
  };

  const fetchModelsData = async () => {
    try {
      // 从Hyperliquid获取真实账户余额
      const accountResponse = await axios.get(`${API_BASE}/account/info`);
      const realBalance = parseFloat(accountResponse.data.equity || accountResponse.data.balance || 0);
      
      // 计算收益率（暂时使用简单的计算方式）
      // TODO: 从数据库获取历史初始值来计算真实收益率
      const deepseekChange = 0; // 暂时设为0，等待实现历史记录API
      
      setModelsData([
        { 
          name: 'DEEPSEEK CHAT V3.1', 
          slug: 'deepseek-chat-v3.1', 
          value: realBalance,  // 使用Hyperliquid真实余额
          change: deepseekChange, 
          color: '#3b82f6', 
          icon: 'deepseek' // 使用DeepSeek logo
        },
      ]);
      setLoadingModels(false);
    } catch (error) {
      console.log('Failed to fetch models data:', error);
      // API失败时，保持加载状态
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
        <div className="w-[500px] bg-white flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <button 
                  onClick={() => setActiveTab('trades')}
                  className={`px-3 py-2 text-xs font-bold rounded transition-colors ${
                    activeTab === 'trades' ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:text-gray-900'
                  }`}
                >
                  已完成交易
                </button>
                <button 
                  onClick={() => setActiveTab('chat')}
                  className={`px-3 py-2 text-xs font-bold rounded transition-colors ${
                    activeTab === 'chat' ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:text-gray-900'
                  }`}
                >
                  模型对话
                </button>
                <button 
                  onClick={() => setActiveTab('positions')}
                  className={`px-3 py-2 text-xs font-bold rounded transition-colors ${
                    activeTab === 'positions' ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:text-gray-900'
                  }`}
                >
                  持仓
                </button>
                <button 
                  onClick={() => setActiveTab('readme')}
                  className={`px-3 py-2 text-xs font-bold rounded transition-colors ${
                    activeTab === 'readme' ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:text-gray-900'
                  }`}
                >
                  关于项目
                </button>
                <button 
                  onClick={() => setActiveTab('ai')}
                  className={`px-3 py-2 text-xs font-bold rounded transition-colors ${
                    activeTab === 'ai' ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:text-gray-900'
                  }`}
                >
                  AI状态
                </button>
                <button 
                  onClick={() => setActiveTab('decisions')}
                  className={`px-3 py-2 text-xs font-bold rounded transition-colors ${
                    activeTab === 'decisions' ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:text-gray-900'
                  }`}
                >
                  决策历史
                </button>
                <button 
                  onClick={() => setActiveTab('performance')}
                  className={`px-3 py-2 text-xs font-bold rounded transition-colors ${
                    activeTab === 'performance' ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:text-gray-900'
                  }`}
                >
                  性能仪表盘
                </button>
                <button 
                  onClick={() => setActiveTab('intelligence')}
                  className={`px-3 py-2 text-xs font-bold rounded transition-colors ${
                    activeTab === 'intelligence' ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:text-gray-900'
                  }`}
                >
                  🕵️‍♀️ 情报中心
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
            {activeTab === 'trades' && (
              <TradeListComplete selectedModel={selectedModel} models={modelsWithData} />
            )}
            {activeTab === 'chat' && (
              <AIDecisionChat selectedModel={selectedModel} />
            )}
            {activeTab === 'positions' && (
              <PositionsList selectedModel={selectedModel} />
            )}
            {activeTab === 'ai' && (
              <div className="h-full overflow-y-auto p-4 space-y-4">
                <AIStatusPanel />
                <PermissionIndicator />
              </div>
            )}
            {activeTab === 'decisions' && (
              <div className="h-full overflow-y-auto p-4">
                <DecisionTimeline />
              </div>
            )}
            {activeTab === 'performance' && (
              <div className="h-full overflow-y-auto p-4">
                <PerformanceDashboard />
              </div>
            )}

            {activeTab === 'intelligence' && (
              <div className="h-full overflow-y-auto p-4">
                <IntelligencePanel />
              </div>
            )}
            {activeTab === 'readme' && (
              <div className="h-full overflow-y-auto p-6 bg-gradient-to-br from-slate-50 to-gray-100">
                <div className="max-w-4xl mx-auto space-y-6">
                  <div className="bg-gradient-to-br from-white to-slate-50 border border-slate-200 rounded-xl p-6 shadow-lg">
                    <h2 className="text-2xl font-bold mb-4 bg-gradient-to-r from-slate-700 to-gray-900 bg-clip-text text-transparent">
                      ━━━ AI GHOST: AI交易系统 ━━━
                    </h2>
                    <p className="text-gray-700 font-mono text-sm leading-relaxed">
                      实时测试AI在真实市场中的投资能力和决策水平。
                    </p>
                  </div>

                  <div className="bg-gradient-to-br from-white to-blue-50 border border-blue-200 rounded-xl p-6 shadow-lg">
                    <h3 className="font-bold text-lg bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-3 flex items-center">
                      <span className="text-2xl mr-2">🎯</span>
                      系统概述
                    </h3>
                    <p className="text-gray-700 font-mono text-sm leading-relaxed">
                      DeepSeek AI 使用 <span className="font-bold text-green-600">$300</span> 真实资金在 Hyperliquid 主网进行交易。
                      目标：通过完全自主的交易决策最大化风险调整后收益。
                    </p>
                  </div>

                  <div className="bg-gradient-to-br from-white to-purple-50 border border-purple-200 rounded-xl p-6 shadow-lg">
                    <h3 className="font-bold text-lg bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-3 flex items-center">
                      <span className="text-2xl mr-2">🤖</span>
                      AI模型
                    </h3>
                    <div className="space-y-2 text-gray-700 font-mono text-sm">
                      <div className="flex items-center space-x-2 bg-white/60 p-3 rounded-lg">
                        <DeepSeekLogo size={20} />
                        <span className="font-semibold">DeepSeek Chat V3.1</span>
                        <span className="text-gray-500">- 高级推理模型</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-white to-green-50 border border-green-200 rounded-xl p-6 shadow-lg">
                    <h3 className="font-bold text-lg bg-gradient-to-r from-green-600 to-teal-600 bg-clip-text text-transparent mb-3 flex items-center">
                      <span className="text-2xl mr-2">📋</span>
                      系统配置
                    </h3>
                    <div className="space-y-2 text-gray-700 font-mono text-sm bg-white/60 p-4 rounded-lg">
                      <div>├─ <span className="font-semibold">初始资金:</span> $300 (共享钱包)</div>
                      <div>├─ <span className="font-semibold">市场:</span> 加密货币永续合约 (BTC, ETH, SOL, BNB, DOGE, XRP)</div>
                      <div>├─ <span className="font-semibold">平台:</span> Hyperliquid 主网</div>
                      <div>├─ <span className="font-semibold">交易模式:</span> 100% 自主 - AI决定一切</div>
                      <div>├─ <span className="font-semibold">风险控制:</span> 最小限制 - AI自我管理风险</div>
                      <div>├─ <span className="font-semibold">透明度:</span> 所有交易在Hyperliquid上可见</div>
                      <div>├─ <span className="font-semibold">决策间隔:</span> 每个AI模型30秒</div>
                      <div>└─ <span className="font-semibold">架构:</span> 受nof1.ai启发</div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-white to-amber-50 border border-amber-200 rounded-xl p-6 shadow-lg">
                    <h3 className="font-bold text-lg bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent mb-3 flex items-center">
                      <span className="text-2xl mr-2">⚙️</span>
                      技术细节
                    </h3>
                    <div className="space-y-2 text-gray-700 font-mono text-sm bg-white/60 p-4 rounded-lg">
                      <div><span className="font-semibold text-amber-700">前端:</span> Next.js 14 + TypeScript + TailwindCSS</div>
                      <div><span className="font-semibold text-amber-700">后端:</span> FastAPI + Python</div>
                      <div><span className="font-semibold text-amber-700">数据库:</span> PostgreSQL + Redis</div>
                      <div><span className="font-semibold text-amber-700">图表引擎:</span> TradingView Lightweight Charts</div>
                      <div><span className="font-semibold">实时通信:</span> WebSocket连接</div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-white to-red-50 border border-red-200 rounded-xl p-6 shadow-lg">
                    <h3 className="font-bold text-lg bg-gradient-to-r from-red-600 to-orange-600 bg-clip-text text-transparent mb-3 flex items-center">
                      <span className="text-2xl mr-2">⚠️</span>
                      自主AI交易
                    </h3>
                    <div className="space-y-2 text-gray-700 font-mono text-sm bg-white/60 p-4 rounded-lg">
                      <div>• <span className="font-semibold text-red-700">仓位规模:</span> AI决定 (最多至余额)</div>
                      <div>• <span className="font-semibold text-red-700">杠杆:</span> AI决定 (Hyperliquid默认)</div>
                      <div>• <span className="font-semibold text-red-700">进出场:</span> AI独立决定时机</div>
                      <div>• <span className="font-semibold text-red-700">风险管理:</span> AI自我管理投资组合风险</div>
                      <div>• <span className="font-semibold text-red-700">止损/止盈:</span> AI决定目标</div>
                      <div>• <span className="font-semibold text-red-700">交易频率:</span> 无限制 (AI优化)</div>
                      <div>• <span className="font-semibold text-red-700">理念:</span> 完全自主 - 最小人工干预</div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-white to-cyan-50 border border-cyan-200 rounded-xl p-6 shadow-lg">
                    <h3 className="font-bold text-lg bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent mb-3 flex items-center">
                      <span className="text-2xl mr-2">📊</span>
                      性能指标
                    </h3>
                    <div className="grid grid-cols-2 gap-2 text-gray-700 font-mono text-sm bg-white/60 p-4 rounded-lg">
                      <div>• 总收益率 (%)</div>
                      <div>• 总盈亏 ($)</div>
                      <div>• 胜率 (%)</div>
                      <div>• 夏普比率</div>
                      <div>• 最大回撤</div>
                      <div>• 平均交易规模</div>
                      <div>• 平均持仓时间</div>
                      <div>• 期望收益</div>
                      <div>• 利润因子</div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-white to-indigo-50 border border-indigo-200 rounded-xl p-6 shadow-lg">
                    <h3 className="font-bold text-lg bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-3 flex items-center">
                      <span className="text-2xl mr-2">🔗</span>
                      参考链接
                    </h3>
                    <div className="space-y-2 text-gray-700 font-mono text-sm bg-white/60 p-4 rounded-lg">
                      <div>• 灵感来源: <a href="https://nof1.ai" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-800 hover:underline font-semibold">nof1.ai</a></div>
                      <div>• Hyperliquid: <a href="https://hyperliquid.xyz" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-800 hover:underline font-semibold">hyperliquid.xyz</a></div>
                      <div>• DeepSeek: <a href="https://platform.deepseek.com" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-800 hover:underline font-semibold">platform.deepseek.com</a></div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-yellow-50 to-orange-50 border border-yellow-300 rounded-xl p-6 shadow-lg">
                    <p className="text-gray-700 text-sm font-mono leading-relaxed">
                      <span className="text-2xl mr-2">⚠️</span>
                      <span className="font-bold text-orange-700">免责声明：</span>
                      这是一个实验性的AI交易系统。所有交易涉及真实资金和真实风险。
                      过往表现不能保证未来结果。风险自负。
                    </p>
                  </div>

                  <div className="bg-gradient-to-br from-slate-100 to-gray-200 border border-slate-300 rounded-xl p-6 shadow-lg text-center">
                    <div className="text-gray-600 text-xs font-mono space-y-2">
                      <div className="text-slate-400">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</div>
                      <div className="font-semibold text-sm">© 2025 AIcoin Trading System | Version 1.0.0</div>
                      <div className="text-slate-400">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
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
