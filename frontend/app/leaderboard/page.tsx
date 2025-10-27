'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface ModelStats {
  rank: number;
  name: string;
  icon: string;
  color: string;
  acctValue: number;
  avgTradeSize: number;
  medianTradeSize: number;
  avgHold: string;
  medianHold: string;
  percentLong: number;
  expectancy: number;
  medianLeverage: number;
  avgLeverage: number;
  avgConfidence: number;
  medianConfidence: number;
  activePositions: string[];
}

export default function LeaderboardPage() {
  const [activeTab, setActiveTab] = useState<'overall' | 'advanced'>('overall');
  const [models, setModels] = useState<ModelStats[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeaderboardData();
  }, []);

  const loadLeaderboardData = async () => {
    // 只显示DeepSeek和Qwen3的数据
    const mockData: ModelStats[] = [
      {
        rank: 1,
        name: 'DEEPSEEK CHAT V3.1',
        icon: '🧠',
        color: '#6366f1',
        acctValue: 11234,
        avgTradeSize: 17943,
        medianTradeSize: 10082,
        avgHold: '26h 59m',
        medianHold: '32h 46m',
        percentLong: 85.71,
        expectancy: 100.89,
        medianLeverage: 10.0,
        avgLeverage: 12.3,
        avgConfidence: 70.1,
        medianConfidence: 70.0,
        activePositions: ['XRP', 'BTC', 'ETH', 'SOL', 'DOGE', 'BNB'],
      },
      {
        rank: 2,
        name: 'QWEN3 MAX',
        icon: '🎨',
        color: '#a855f7',
        acctValue: 10354,
        avgTradeSize: 36087,
        medianTradeSize: 44378,
        avgHold: '5h 15m',
        medianHold: '1h 35m',
        percentLong: 70.00,
        expectancy: 7.49,
        medianLeverage: 8.0,
        avgLeverage: 10.2,
        avgConfidence: 68.9,
        medianConfidence: 70.0,
        activePositions: [],
      }
    ];

    setModels(mockData);
    setLoading(false);
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  const formatExpectancy = (value: number) => {
    return value >= 0 ? `+$${value.toFixed(2)}` : `-$${Math.abs(value).toFixed(2)}`;
  };

  const getExpectancyColor = (value: number) => {
    return value >= 0 ? 'text-green-600' : 'text-red-600';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading leaderboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center space-x-2">
            <div className="text-2xl font-bold text-gray-900">
              Alpha<span className="font-normal">Arena</span>
            </div>
            <span className="text-xs text-gray-500">by H-1</span>
          </Link>
          
          <nav className="absolute left-1/2 transform -translate-x-1/2 flex space-x-8 text-sm font-medium">
            <Link href="/" className="text-gray-900 hover:text-gray-600">LIVE</Link>
            <Link href="/leaderboard" className="font-bold text-gray-900 border-b-2 border-gray-900 pb-1">LEADERBOARD</Link>
            <Link href="/models" className="text-gray-900 hover:text-gray-600">MODELS</Link>
          </nav>

          <div className="flex items-center space-x-6 text-xs">
            <a href="https://nof1.ai/" target="_blank" rel="noopener noreferrer" className="text-gray-900 hover:text-gray-600">
              JOIN THE PLATFORM WAITLIST ↗
            </a>
            <a href="https://nof1.ai/" target="_blank" rel="noopener noreferrer" className="text-gray-900 hover:text-gray-600">
              ABOUT NOF1 ↗
            </a>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">LEADERBOARD</h1>
          <p className="text-gray-600">Performance rankings of AI trading models</p>
        </div>

        {/* Tabs */}
        <div className="flex space-x-1 mb-8">
          <button
            onClick={() => setActiveTab('overall')}
            className={`px-6 py-3 text-sm font-bold transition-colors ${
              activeTab === 'overall'
                ? 'bg-gray-900 text-white'
                : 'bg-white text-gray-900 border-2 border-gray-900 hover:bg-gray-100'
            }`}
          >
            OVERALL STATS
          </button>
          <button
            onClick={() => setActiveTab('advanced')}
            className={`px-6 py-3 text-sm font-bold transition-colors ${
              activeTab === 'advanced'
                ? 'bg-gray-900 text-white'
                : 'bg-white text-gray-900 border-2 border-gray-900 hover:bg-gray-100'
            }`}
          >
            ADVANCED ANALYTICS
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-500">Loading leaderboard...</div>
          </div>
        ) : (
          <>
            {/* Leaderboard Table */}
            <div className="bg-white border-2 border-gray-900 mb-8">
              {activeTab === 'overall' ? (
                <table className="w-full text-xs">
                  <thead>
                    <tr className="bg-white border-b-2 border-gray-900">
                      <th className="px-4 py-3 text-left font-bold text-gray-900">RANK</th>
                      <th className="px-4 py-3 text-left font-bold text-gray-900">MODEL</th>
                      <th className="px-4 py-3 text-right font-bold text-gray-900">ACCT VALUE↓</th>
                      <th className="px-4 py-3 text-right font-bold text-gray-900">AVG TRADE SIZE</th>
                      <th className="px-4 py-3 text-right font-bold text-gray-900">MEDIAN TRADE SIZE</th>
                      <th className="px-4 py-3 text-right font-bold text-gray-900">AVG HOLD</th>
                      <th className="px-4 py-3 text-right font-bold text-gray-900">MEDIAN HOLD</th>
                      <th className="px-4 py-3 text-right font-bold text-gray-900">% LONG</th>
                      <th className="px-4 py-3 text-right font-bold text-gray-900">EXPECTANCY</th>
                      <th className="px-4 py-3 text-right font-bold text-gray-900">MEDIAN LEVERAGE</th>
                      <th className="px-4 py-3 text-right font-bold text-gray-900">AVG LEVERAGE</th>
                      <th className="px-4 py-3 text-right font-bold text-gray-900">AVG CONFIDENCE</th>
                      <th className="px-4 py-3 text-right font-bold text-gray-900">MEDIAN CONFIDENCE</th>
                    </tr>
                  </thead>
                  <tbody>
                    {models.map((model, index) => (
                      <tr
                        key={model.rank}
                        className={`border-b border-gray-200 hover:bg-gray-50 transition-colors ${
                          index === 0 ? 'bg-gray-50' : ''
                        }`}
                      >
                        <td className="px-4 py-3 text-center font-mono">{model.rank}</td>
                        <td className="px-4 py-3">
                          <div className="flex items-center space-x-2">
                            <span className="text-lg">{model.icon}</span>
                            <span className="font-bold text-gray-900">{model.name}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-right font-mono">{formatCurrency(model.acctValue)}</td>
                        <td className="px-4 py-3 text-right font-mono">{formatCurrency(model.avgTradeSize)}</td>
                        <td className="px-4 py-3 text-right font-mono">{formatCurrency(model.medianTradeSize)}</td>
                        <td className="px-4 py-3 text-right font-mono">{model.avgHold}</td>
                        <td className="px-4 py-3 text-right font-mono">{model.medianHold}</td>
                        <td className="px-4 py-3 text-right font-mono">{model.percentLong.toFixed(2)}%</td>
                        <td className={`px-4 py-3 text-right font-mono font-bold ${getExpectancyColor(model.expectancy)}`}>
                          {formatExpectancy(model.expectancy)}
                        </td>
                        <td className="px-4 py-3 text-right font-mono">{model.medianLeverage.toFixed(1)}</td>
                        <td className="px-4 py-3 text-right font-mono">{model.avgLeverage.toFixed(1)}</td>
                        <td className="px-4 py-3 text-right font-mono">{model.avgConfidence.toFixed(1)}%</td>
                        <td className="px-4 py-3 text-right font-mono">{model.medianConfidence.toFixed(1)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <table className="w-full text-xs">
                  <thead>
                    <tr className="bg-white border-b-2 border-gray-900">
                      <th className="px-4 py-3 text-left font-bold text-gray-900">RANK</th>
                      <th className="px-4 py-3 text-left font-bold text-gray-900">MODEL</th>
                      <th className="px-4 py-3 text-right font-bold text-gray-900">ACCT VALUE↓</th>
                      <th className="px-4 py-3 text-right font-bold text-gray-900">RETURN %</th>
                      <th className="px-4 py-3 text-right font-bold text-gray-900">TOTAL P&L</th>
                      <th className="px-4 py-3 text-right font-bold text-gray-900">FEES</th>
                      <th className="px-4 py-3 text-right font-bold text-gray-900">WIN RATE</th>
                      <th className="px-4 py-3 text-right font-bold text-gray-900">BIGGEST WIN</th>
                      <th className="px-4 py-3 text-right font-bold text-gray-900">BIGGEST LOSS</th>
                      <th className="px-4 py-3 text-right font-bold text-gray-900">SHARPE</th>
                      <th className="px-4 py-3 text-right font-bold text-gray-900">TRADES</th>
                    </tr>
                  </thead>
                  <tbody>
                    {models.map((model, index) => {
                      const returnPercent = ((model.acctValue - 10000) / 10000) * 100;
                      const totalPnL = model.acctValue - 10000;
                      const fees = model.acctValue * 0.01; // 模拟费用
                      const winRate = 44.3 + (index * 5); // 模拟胜率
                      const biggestWin = 1000 + (index * 200);
                      const biggestLoss = -500 - (index * 100);
                      const sharpe = 0.003 - (index * 0.1);
                      const trades = 7 + (index * 10);
                      
                      return (
                        <tr
                          key={model.rank}
                          className={`border-b border-gray-200 hover:bg-gray-50 transition-colors ${
                            index === 0 ? 'bg-gray-50' : ''
                          }`}
                        >
                          <td className="px-4 py-3 text-center font-mono">{model.rank}</td>
                          <td className="px-4 py-3">
                            <div className="flex items-center space-x-2">
                              <span className="text-lg">{model.icon}</span>
                              <span className="font-bold text-gray-900">{model.name}</span>
                            </div>
                          </td>
                          <td className="px-4 py-3 text-right font-mono">{formatCurrency(model.acctValue)}</td>
                          <td className={`px-4 py-3 text-right font-mono font-bold ${returnPercent > 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {returnPercent > 0 ? '+' : ''}{returnPercent.toFixed(2)}%
                          </td>
                          <td className={`px-4 py-3 text-right font-mono ${totalPnL > 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {totalPnL > 0 ? '+' : ''}{formatCurrency(Math.abs(totalPnL))}
                          </td>
                          <td className="px-4 py-3 text-right font-mono">{formatCurrency(fees)}</td>
                          <td className="px-4 py-3 text-right font-mono">{winRate.toFixed(1)}%</td>
                          <td className="px-4 py-3 text-right font-mono text-green-600">{formatCurrency(biggestWin)}</td>
                          <td className="px-4 py-3 text-right font-mono text-red-600">-{formatCurrency(Math.abs(biggestLoss))}</td>
                          <td className="px-4 py-3 text-right font-mono">{sharpe.toFixed(3)}</td>
                          <td className="px-4 py-3 text-right font-mono">{trades}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              )}
            </div>

            {/* Bottom Section */}
            <div className="grid grid-cols-3 gap-6">
              {/* Winning Model Card */}
              <div className="bg-white border-2 border-gray-900 p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">WINNING MODEL</h3>
                <div className="flex items-center space-x-3 mb-4">
                  <span className="text-3xl">{models[0]?.icon}</span>
                  <div>
                    <div className="font-bold text-gray-900">{models[0]?.name}</div>
                    <div className="text-sm text-gray-600">Rank #{models[0]?.rank}</div>
                  </div>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Account Value:</span>
                    <span className="font-bold text-gray-900">{formatCurrency(models[0]?.acctValue || 0)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Expectancy:</span>
                    <span className={`font-bold ${getExpectancyColor(models[0]?.expectancy || 0)}`}>
                      {formatExpectancy(models[0]?.expectancy || 0)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Win Rate:</span>
                    <span className="font-bold text-gray-900">{(models[0]?.percentLong || 0).toFixed(1)}%</span>
                  </div>
                </div>
              </div>

              {/* Performance Chart */}
              <div className="col-span-2 bg-white border-2 border-gray-900 p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">ACCOUNT VALUE COMPARISON</h3>
                <div className="space-y-4">
                  {models.map((model, index) => (
                    <div key={model.rank} className="flex items-center space-x-4">
                      <div className="w-8 text-center text-sm font-bold text-gray-900">#{model.rank}</div>
                      <div className="flex items-center space-x-2 flex-1">
                        <span className="text-lg">{model.icon}</span>
                        <span className="text-sm font-bold text-gray-900">{model.name}</span>
                      </div>
                      <div className="w-32">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="h-2 rounded-full"
                            style={{
                              width: `${(model.acctValue / (models[0]?.acctValue || 1)) * 100}%`,
                              backgroundColor: model.color,
                            }}
                          />
                        </div>
                      </div>
                      <div className="w-20 text-right text-sm font-mono text-gray-900">
                        {formatCurrency(model.acctValue)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}