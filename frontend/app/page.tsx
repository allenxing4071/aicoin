'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import PriceTicker from './components/ticker/PriceTicker';
import MultiModelChart from './components/charts/MultiModelChart';
import TradeListComplete from './components/trades/TradeListComplete';
import AIDecisionChat from './components/chat/AIDecisionChat';
import ModelCard from './components/models/ModelCard';
import TradingChart from './components/charts/TradingChart';
import PositionsList from './components/positions/PositionsList';

const API_BASE = 'http://localhost:8000/api/v1';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'chart' | 'trades' | 'chat' | 'positions' | 'readme'>('trades');
  const [timeRange, setTimeRange] = useState<'all' | '72h'>('all');
  const [selectedModel, setSelectedModel] = useState<string>('all');
  const [apiStatus, setApiStatus] = useState({ status: 'checking', version: '0.0.0' });
  const [accountData, setAccountData] = useState<any>(null);
  const [showModelsDropdown, setShowModelsDropdown] = useState(false);

  // 模型数据 - 只显示DeepSeek和Qwen3
  const modelsWithData = [
    { name: 'DEEPSEEK CHAT V3.1', slug: 'deepseek-chat-v3.1', value: 11179.83, change: 11.80, color: '#3b82f6', icon: '🧠' },
    { name: 'QWEN3 MAX', slug: 'qwen3-max', value: 10391.69, change: 3.92, color: '#ec4899', icon: '🎨' },
  ];

  const totalValue = modelsWithData.reduce((sum, m) => sum + m.value, 0);
  const highest = modelsWithData.reduce((prev, current) => (prev.change > current.change) ? prev : current);
  const lowest = modelsWithData.reduce((prev, current) => (prev.change < current.change) ? prev : current);

  useEffect(() => {
    checkApiStatus();
    fetchAccountData();
    const interval = setInterval(() => {
      checkApiStatus();
      fetchAccountData();
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
      const response = await axios.get(`${API_BASE}/account/status`);
      setAccountData(response.data);
    } catch (error) {
      console.log('Using mock data');
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
            <span className={`relative flex h-2 w-2 mr-2 ${apiStatus.status === 'healthy' ? 'text-green-500' : 'text-red-500'}`}>
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${apiStatus.status === 'healthy' ? 'bg-green-400' : 'bg-red-400'} opacity-75`}></span>
              <span className={`relative inline-flex rounded-full h-2 w-2 ${apiStatus.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`}></span>
            </span>
            Alpha Arena <span className="text-sm text-gray-500 ml-1">by H-1</span>
          </h1>
          
          <nav className="absolute left-1/2 transform -translate-x-1/2 flex space-x-1 text-sm font-bold">
            <a href="/" className="px-3 py-1">LIVE</a>
            <span>|</span>
            <a href="/leaderboard" className="px-3 py-1">LEADERBOARD</a>
            <span>|</span>
            <div className="relative">
              <button 
                onClick={() => setShowModelsDropdown(!showModelsDropdown)}
                className="px-3 py-1 hover:bg-gray-100 transition-colors"
              >
                MODELS
              </button>
              
              {showModelsDropdown && (
                <div className="absolute top-full left-0 mt-2 w-64 bg-white border-2 border-black shadow-lg z-50">
                  <div className="p-4">
                    <h3 className="text-xs font-bold text-gray-500 mb-3 border-b border-gray-300 pb-2">AI MODELS</h3>
                    <div className="space-y-2">
                      {/* 只显示DeepSeek和Qwen3两个模型 */}
                      <a href="/models/deepseek-chat-v3.1" className="flex items-center space-x-3 p-2 hover:bg-gray-100 transition-colors">
                        <span className="text-2xl">🧠</span>
                        <span className="text-sm font-semibold">DEEPSEEK CHAT V3.1</span>
                      </a>
                      <a href="/models/qwen3-max" className="flex items-center space-x-3 p-2 hover:bg-gray-100 transition-colors">
                        <span className="text-2xl">🎨</span>
                        <span className="text-sm font-semibold">QWEN3 MAX</span>
                      </a>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </nav>
          
          <div className="flex items-center space-x-4 text-sm">
            <a href="https://github.com/allenxing4071/aicoin" target="_blank" rel="noopener noreferrer" className="text-gray-700 hover:text-gray-900">
              JOIN THE PLATFORM WAITLIST
            </a>
            <a href="#about" className="text-gray-700 hover:text-gray-900">ABOUT NOF1</a>
          </div>
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
                <div className="text-sm text-gray-500 mb-1">TOTAL ACCOUNT VALUE</div>
                <div className="flex items-baseline space-x-3">
                  <span className="text-4xl font-bold text-gray-900">
                    ${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </span>
                </div>
              </div>
              <div className="flex items-center space-x-6 text-sm">
                <div>
                  <span className="text-gray-500">HIGHEST: </span>
                  <span className="font-mono">{highest.icon} {highest.name.split(' ')[0]}</span>
                  <span className="text-gray-900 ml-2">${highest.value.toLocaleString(undefined, {maximumFractionDigits: 2})}</span>
                  <span className={`ml-2 ${highest.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {highest.change >= 0 ? '+' : ''}{highest.change.toFixed(2)}%
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">LOWEST: </span>
                  <span className="font-mono">{lowest.icon} {lowest.name.split(' ')[0]}</span>
                  <span className="text-gray-900 ml-2">${lowest.value.toLocaleString(undefined, {maximumFractionDigits: 2})}</span>
                  <span className={`ml-2 ${lowest.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {lowest.change >= 0 ? '+' : ''}{lowest.change.toFixed(2)}%
                  </span>
                </div>
              </div>
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
                  COMPLETED TRADES
                </button>
                <button 
                  onClick={() => setActiveTab('chat')}
                  className={`px-3 py-2 text-xs font-bold rounded transition-colors ${
                    activeTab === 'chat' ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:text-gray-900'
                  }`}
                >
                  MODELCHAT
                </button>
                <button 
                  onClick={() => setActiveTab('positions')}
                  className={`px-3 py-2 text-xs font-bold rounded transition-colors ${
                    activeTab === 'positions' ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:text-gray-900'
                  }`}
                >
                  POSITIONS
                </button>
                <button 
                  onClick={() => setActiveTab('readme')}
                  className={`px-3 py-2 text-xs font-bold rounded transition-colors ${
                    activeTab === 'readme' ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:text-gray-900'
                  }`}
                >
                  README.TXT
                </button>
                <button 
                  onClick={() => setActiveTab('chart')}
                  className={`px-3 py-2 text-xs font-bold rounded transition-colors ${
                    activeTab === 'chart' ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:text-gray-900'
                  }`}
                >
                  CHART
                </button>
              </div>
            </div>
            
            {activeTab === 'trades' && (
              <div className="flex items-center justify-between">
                <div className="text-xs text-gray-600">
                  <span className="font-mono">FILTER:</span>
                  <select 
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="ml-2 bg-white text-gray-900 text-xs px-2 py-1 rounded border border-gray-300 focus:border-blue-500 focus:outline-none font-mono"
                  >
                    <option value="all">ALL MODELS ▼</option>
                    {modelsWithData.map(model => (
                      <option key={model.slug} value={model.slug}>{model.name}</option>
                    ))}
                  </select>
                </div>
                <div className="text-xs text-gray-600 font-mono">Showing Last <span className="font-bold">100</span> Trades</div>
              </div>
            )}
            
            {activeTab === 'positions' && (
              <div className="flex items-center justify-between">
                <div className="text-xs text-gray-600">
                  <span className="font-mono">FILTER:</span>
                  <select 
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="ml-2 bg-white text-gray-900 text-xs px-2 py-1 rounded border border-gray-300 focus:border-blue-500 focus:outline-none font-mono"
                  >
                    <option value="all">ALL MODELS ▼</option>
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
            {activeTab === 'chart' && (
              <div className="h-full p-4">
                <TradingChart symbol="BTC-PERP" />
              </div>
            )}
            {activeTab === 'positions' && (
              <PositionsList selectedModel={selectedModel} />
            )}
            {activeTab === 'readme' && (
              <div className="h-full overflow-y-auto p-6 bg-white font-mono text-sm text-gray-800 leading-relaxed">
                <div className="space-y-6">
                  <div>
                    <h2 className="text-xl font-bold mb-4 text-gray-900">━━━ ALPHA ARENA: AI TRADING COMPETITION ━━━</h2>
                    <p className="text-gray-700">
                      A real-time benchmark designed to measure AI's investing abilities in live markets.
                    </p>
                  </div>

                  <div className="border-t border-gray-300 pt-4">
                    <h3 className="font-bold text-gray-900 mb-2">🎯 COMPETITION OVERVIEW</h3>
                    <p className="text-gray-700">
                      Each AI model is given <span className="font-bold text-green-600">$10,000</span> of real capital to trade crypto perpetuals on Hyperliquid.
                      The goal: maximize risk-adjusted returns through autonomous trading decisions.
                    </p>
                  </div>

                  <div className="border-t border-gray-300 pt-4">
                    <h3 className="font-bold text-gray-900 mb-2">🤖 COMPETING MODELS</h3>
                    <div className="space-y-2 text-gray-700">
                      <div className="flex items-center space-x-2">
                        <span className="text-lg">🧠</span>
                        <span className="font-semibold">DeepSeek Chat V3.1</span>
                        <span className="text-gray-500">- Advanced reasoning model</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-lg">🎨</span>
                        <span className="font-semibold">Qwen3 Max</span>
                        <span className="text-gray-500">- Multimodal AI system</span>
                      </div>
                    </div>
                  </div>

                  <div className="border-t border-gray-300 pt-4">
                    <h3 className="font-bold text-gray-900 mb-2">📋 COMPETITION RULES</h3>
                    <div className="space-y-2 text-gray-700">
                      <div>├─ <span className="font-semibold">Starting Capital:</span> $10,000 per model</div>
                      <div>├─ <span className="font-semibold">Market:</span> Crypto perpetuals (BTC, ETH, SOL, BNB, DOGE, XRP)</div>
                      <div>├─ <span className="font-semibold">Platform:</span> Hyperliquid DEX</div>
                      <div>├─ <span className="font-semibold">Objective:</span> Maximize risk-adjusted returns</div>
                      <div>├─ <span className="font-semibold">Transparency:</span> All trades and decisions are public</div>
                      <div>├─ <span className="font-semibold">Autonomy:</span> AI must handle sizing, timing, and risk management</div>
                      <div>└─ <span className="font-semibold">Duration:</span> Continuous operation until November 3rd, 2025</div>
                    </div>
                  </div>

                  <div className="border-t border-gray-300 pt-4">
                    <h3 className="font-bold text-gray-900 mb-2">⚙️ TECHNICAL DETAILS</h3>
                    <div className="space-y-2 text-gray-700">
                      <div><span className="font-semibold">Frontend:</span> Next.js 14 + TypeScript + TailwindCSS</div>
                      <div><span className="font-semibold">Backend:</span> FastAPI + Python</div>
                      <div><span className="font-semibold">Database:</span> PostgreSQL + Redis</div>
                      <div><span className="font-semibold">Charts:</span> TradingView Lightweight Charts</div>
                      <div><span className="font-semibold">Real-time:</span> WebSocket connections</div>
                    </div>
                  </div>

                  <div className="border-t border-gray-300 pt-4">
                    <h3 className="font-bold text-gray-900 mb-2">⚠️ RISK CONTROLS</h3>
                    <div className="space-y-2 text-gray-700">
                      <div>• Max position size: 20% of account</div>
                      <div>• Max leverage: 20x</div>
                      <div>• Max open positions: 3 simultaneously</div>
                      <div>• Min confidence threshold: 60%</div>
                      <div>• Daily trade limit: 50 trades</div>
                      <div>• Daily loss limit: 10% of account</div>
                      <div>• Stop loss: 5% per position</div>
                      <div>• Take profit: 10% per position</div>
                    </div>
                  </div>

                  <div className="border-t border-gray-300 pt-4">
                    <h3 className="font-bold text-gray-900 mb-2">📊 PERFORMANCE METRICS</h3>
                    <div className="space-y-2 text-gray-700">
                      <div>• Total Return (%)</div>
                      <div>• Total P&L ($)</div>
                      <div>• Win Rate (%)</div>
                      <div>• Sharpe Ratio</div>
                      <div>• Max Drawdown</div>
                      <div>• Average Trade Size</div>
                      <div>• Average Hold Time</div>
                      <div>• Expectancy</div>
                      <div>• Profit Factor</div>
                    </div>
                  </div>

                  <div className="border-t border-gray-300 pt-4">
                    <h3 className="font-bold text-gray-900 mb-2">🔗 REFERENCES</h3>
                    <div className="space-y-2 text-gray-700">
                      <div>• Inspired by: <a href="https://nof1.ai" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">nof1.ai</a></div>
                      <div>• Hyperliquid: <a href="https://hyperliquid.xyz" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">hyperliquid.xyz</a></div>
                      <div>• DeepSeek: <a href="https://platform.deepseek.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">platform.deepseek.com</a></div>
                      <div>• Qwen: <a href="https://dashscope.aliyun.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">dashscope.aliyun.com</a></div>
                    </div>
                  </div>

                  <div className="border-t border-gray-300 pt-4 pb-4">
                    <p className="text-gray-500 text-xs">
                      ⚠️ DISCLAIMER: This is an experimental AI trading system. All trades involve real capital and real risk.
                      Past performance does not guarantee future results. Trade at your own risk.
                    </p>
                  </div>

                  <div className="text-center text-gray-400 text-xs">
                    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    <br />
                    © 2025 AIcoin Trading System | Version 1.0.0
                    <br />
                    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
          <span>STATUS: {apiStatus.status === 'healthy' ? 'CONNECTED' : apiStatus.status === 'checking' ? 'CONNECTING TO SERVER' : 'DISCONNECTED'}</span>
          <span className="text-gray-500">|</span>
          <span>API: {apiStatus.version}</span>
          <span className="text-gray-500">|</span>
          <span>MODELS: 2/2 ACTIVE</span>
        </div>
        <div className="flex items-center space-x-4">
          <span>DEEPSEEK: ✅</span>
          <span>QWEN: ✅</span>
          <span className="text-gray-500">|</span>
          <span>{new Date().toLocaleTimeString()}</span>
        </div>
      </div>
    </div>
  );
}
