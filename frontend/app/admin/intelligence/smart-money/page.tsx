'use client';

/**
 * 聪明钱跟单页面
 * 
 * 路径: /admin/intelligence/smart-money
 * 
 * 功能：
 * - 钱包列表管理
 * - 实时交易流
 * - 跟单设置
 */

import React, { useState, useEffect } from 'react';
import PageHeader from '@/app/components/common/PageHeader';
import { unifiedDesignSystem, getThemeStyles } from '@/app/admin/unified-design-system';

interface SmartMoneyWallet {
  id: number;
  wallet_address: string;
  nickname: string | null;
  chain: string;
  total_profit: number;
  win_rate: number;
  enabled: boolean;
  tags: string[] | null;
}

interface SmartMoneyTransaction {
  id: number;
  wallet_address: string;
  tx_hash: string;
  action: string;
  token_in: string | null;
  token_out: string | null;
  amount_out: number | null;
  price_usd: number | null;
  dex: string | null;
  timestamp: string;
}

export default function SmartMoneyPage() {
  const theme = getThemeStyles('blue');
  const [wallets, setWallets] = useState<SmartMoneyWallet[]>([]);
  const [transactions, setTransactions] = useState<SmartMoneyTransaction[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // 获取钱包列表
      const walletsRes = await fetch('/api/v1/smart-money/wallets');
      const walletsData = await walletsRes.json();
      if (Array.isArray(walletsData)) {
        setWallets(walletsData);
      }

      // 获取交易记录
      const txRes = await fetch('/api/v1/smart-money/transactions?limit=20');
      const txData = await txRes.json();
      if (txData.success) {
        setTransactions(txData.data);
      }

      // 获取统计数据
      const statsRes = await fetch('/api/v1/smart-money/statistics');
      const statsData = await statsRes.json();
      if (statsData.success) {
        setStats(statsData.data);
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getActionColor = (action: string) => {
    if (action === 'buy') return 'bg-green-100 text-green-800';
    if (action === 'sell') return 'bg-red-100 text-red-800';
    return 'bg-blue-100 text-blue-800';
  };

  const getActionIcon = (action: string) => {
    if (action === 'buy') return '🟢';
    if (action === 'sell') return '🔴';
    return '🔄';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        icon="💰"
        title="聪明钱跟单"
        description="追踪聪明钱钱包交易，学习高手操作策略"
        color="green"
      />

      {/* 统计卡片 */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 shadow-lg border-2 border-green-300">
            <div className="text-sm text-gray-500 mb-1">跟踪钱包</div>
            <div className="text-3xl font-bold text-green-600">{stats.enabled_wallets}</div>
            <div className="text-xs text-gray-500 mt-1">总计: {stats.total_wallets}</div>
          </div>
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 shadow-lg border-2 border-blue-300">
            <div className="text-sm text-gray-500 mb-1">总交易数</div>
            <div className="text-3xl font-bold text-blue-600">{stats.total_transactions}</div>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 shadow-lg border-2 border-purple-300">
            <div className="text-sm text-gray-500 mb-1">平均胜率</div>
            <div className="text-3xl font-bold text-purple-600">{stats.avg_win_rate.toFixed(1)}%</div>
          </div>
          <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-6 shadow-lg border-2 border-orange-300">
            <div className="text-sm text-gray-500 mb-1">总收益</div>
            <div className="text-3xl font-bold text-orange-600">${stats.total_profit.toFixed(2)}</div>
          </div>
        </div>
      )}

      {/* 钱包列表 */}
      <div className="bg-white rounded-xl shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">👛 聪明钱钱包</h3>
          <button
            onClick={() => alert('添加钱包功能开发中')}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            添加钱包
          </button>
        </div>

        <div className="space-y-3">
          {wallets.map((wallet) => (
            <div key={wallet.id} className={`${unifiedDesignSystem.listCard.container} ${theme.listCardBorder}`}>
              <div className="flex items-center justify-between mb-2">
                <div>
                  <h4 className="font-semibold text-gray-900">
                    {wallet.nickname || '未命名钱包'}
                  </h4>
                  <p className="text-xs text-gray-500 font-mono">
                    {wallet.wallet_address.slice(0, 6)}...{wallet.wallet_address.slice(-4)}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                    {wallet.chain}
                  </span>
                  <span
                    className={`px-3 py-1 text-xs rounded-full font-medium ${
                      wallet.enabled
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {wallet.enabled ? '✓ 启用' : '✗ 禁用'}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <div className="text-xs text-gray-500">总收益</div>
                  <div className="text-lg font-semibold text-green-600">
                    ${wallet.total_profit.toFixed(2)}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">胜率</div>
                  <div className="text-lg font-semibold text-purple-600">
                    {wallet.win_rate.toFixed(1)}%
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">标签</div>
                  <div className="text-sm text-gray-700">
                    {wallet.tags && wallet.tags.length > 0 ? wallet.tags.join(', ') : '无'}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {wallets.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <div className="text-4xl mb-2">👛</div>
            <p>暂无钱包数据</p>
            <p className="text-sm mt-2">点击"添加钱包"开始追踪</p>
          </div>
        )}
      </div>

      {/* 实时交易流 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 实时交易流</h3>
        
        <div className="space-y-3">
          {transactions.map((tx) => (
            <div key={tx.id} className="border-l-4 border-green-500 pl-4 py-2">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-sm text-gray-600">
                    {tx.wallet_address.slice(0, 6)}...{tx.wallet_address.slice(-4)}
                  </span>
                  <span className={`px-2 py-1 text-xs rounded-full font-medium ${getActionColor(tx.action)}`}>
                    {getActionIcon(tx.action)} {tx.action}
                  </span>
                </div>
                <span className="text-xs text-gray-500">
                  {new Date(tx.timestamp).toLocaleString('zh-CN')}
                </span>
              </div>
              <div className="text-sm text-gray-700">
                {tx.token_in && tx.token_out && (
                  <span>{tx.token_in} → {tx.token_out}</span>
                )}
                {tx.amount_out && (
                  <span className="ml-2">数量: {tx.amount_out.toFixed(4)}</span>
                )}
                {tx.price_usd && (
                  <span className="ml-2 text-green-600">${tx.price_usd.toFixed(2)}</span>
                )}
              </div>
              {tx.dex && (
                <div className="text-xs text-gray-500 mt-1">
                  DEX: {tx.dex}
                </div>
              )}
            </div>
          ))}
        </div>

        {transactions.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <div className="text-4xl mb-2">📊</div>
            <p>暂无交易数据</p>
          </div>
        )}
      </div>
    </div>
  );
}

