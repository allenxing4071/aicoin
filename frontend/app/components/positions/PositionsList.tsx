'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import CoinIcon from '../common/CoinIcon';

interface Position {
  id: string;
  model: string;
  modelIcon: string;
  modelColor: string;
  side: 'LONG' | 'SHORT';
  coin: string;
  coinIcon: string;
  leverage: string;
  notional: number;
  unrealizedPnL: number;
  totalUnrealizedPnL: number;
  availableCash: number;
}

interface PositionsListProps {
  selectedModel?: string;
}

const API_BASE = 'http://localhost:8000/api/v1';

const COIN_ICONS: Record<string, string> = {
  'BTC': '₿',
  'ETH': 'Ξ',
  'SOL': '☀️',
  'BNB': '🔶',
  'DOGE': '🐕',
  'XRP': '🪝'
};

export default function PositionsList({ selectedModel = 'all' }: PositionsListProps) {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRealPositions();
    // 每10秒更新一次
    const interval = setInterval(fetchRealPositions, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchRealPositions = async () => {
    try {
      const response = await axios.get(`${API_BASE}/trading/positions`);
      
      if (response.data && response.data.success && response.data.positions) {
        const realPositions = response.data.positions.map((pos: any, index: number) => {
          const symbol = (pos.coin || pos.symbol || '').replace('-PERP', '');
          return {
            id: `pos_${index}`,
            model: 'SHARED WALLET',  // 所有AI共享同一个钱包
            modelIcon: '🤖',
            modelColor: '#6b7280',
            side: (pos.side === 'long' || (pos.size && pos.size > 0)) ? 'LONG' as const : 'SHORT' as const,
            coin: symbol,
            coinIcon: COIN_ICONS[symbol] || '💰',
            leverage: pos.leverage ? `${pos.leverage}X` : '1X',
            notional: Math.abs((pos.size || 0) * (pos.entry_price || 0)),
            unrealizedPnL: pos.unrealized_pnl || 0,
            totalUnrealizedPnL: pos.unrealized_pnl || 0,
            availableCash: 0  // 从account API获取
          };
        });
        
        setPositions(realPositions);
        setLoading(false);
      } else {
        // 没有持仓时显示空列表
        setPositions([]);
        setLoading(false);
      }
    } catch (error) {
      console.error('Failed to fetch positions:', error);
      // API失败时显示空列表
      setPositions([]);
      setLoading(false);
    }
  };


  // 按模型分组持仓
  const groupedPositions = positions.reduce((acc, position) => {
    if (!acc[position.model]) {
      acc[position.model] = {
        model: position.model,
        modelIcon: position.modelIcon,
        modelColor: position.modelColor,
        totalUnrealizedPnL: position.totalUnrealizedPnL,
        availableCash: position.availableCash,
        positions: [],
      };
    }
    acc[position.model].positions.push(position);
    return acc;
  }, {} as Record<string, any>);

  // 过滤选中的模型
  const filteredGroups = Object.values(groupedPositions).filter((group: any) => {
    if (selectedModel === 'all') return true;
    return group.model.toLowerCase().includes(selectedModel.toLowerCase());
  });

  return (
    <div className="h-full overflow-y-auto p-4 space-y-4 bg-gradient-to-br from-green-50 to-teal-50">
      {filteredGroups.map((group: any) => (
        <div key={group.model} className="bg-gradient-to-br from-white to-green-50/30 border border-green-200 rounded-xl p-4 shadow-lg hover:shadow-xl transition-all duration-300">
          {/* 模型头部 */}
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-green-200">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">{group.modelIcon}</span>
              <span className="text-sm font-bold bg-gradient-to-r from-green-600 to-teal-600 bg-clip-text text-transparent">
                {group.model}
              </span>
            </div>
            <div className="flex items-center space-x-6">
              <div className="text-right">
                <div className="text-xs text-gray-500 font-semibold">总未实现盈亏:</div>
                <div className={`text-base font-bold font-mono ${group.totalUnrealizedPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {group.totalUnrealizedPnL >= 0 ? '+' : ''}${Math.abs(group.totalUnrealizedPnL).toFixed(2)}
                </div>
              </div>
            </div>
          </div>

          {/* 表头 */}
          <div className="grid grid-cols-6 gap-4 mb-2 text-xs font-bold text-gray-500 uppercase px-2">
            <div>SIDE</div>
            <div>COIN</div>
            <div className="text-right">LEVERAGE</div>
            <div className="text-right">NOTIONAL</div>
            <div className="text-center">EXIT PLAN</div>
            <div className="text-right">UNREAL P&L</div>
          </div>

          {/* 持仓列表 */}
          <div className="space-y-2">
            {group.positions.map((position: Position) => (
              <div key={position.id} className="grid grid-cols-6 gap-4 items-center py-2 px-2 hover:bg-green-50/50 rounded-lg transition-colors">
                <div className={`text-sm font-bold ${position.side === 'LONG' ? 'text-green-600' : 'text-red-600'}`}>
                  {position.side}
                </div>
                <div className="flex items-center space-x-2">
                  <CoinIcon symbol={position.coin} size={20} />
                  <span className="text-sm font-semibold text-gray-900">{position.coin}</span>
                </div>
                <div className="text-sm text-gray-900 text-right">{position.leverage}</div>
                <div className="text-sm text-green-600 font-semibold text-right">
                  ${position.notional.toLocaleString()}
                </div>
                <div className="text-center">
                  <button className="px-3 py-1 text-xs border border-gray-300 rounded hover:bg-gray-50">
                    VIEW
                  </button>
                </div>
                <div className={`text-sm font-bold text-right ${position.unrealizedPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {position.unrealizedPnL >= 0 ? '+' : ''}${Math.abs(position.unrealizedPnL).toFixed(2)}
                </div>
              </div>
            ))}
          </div>

          {/* 可用现金 */}
          <div className="mt-4 pt-3 border-t border-green-200">
            <div className="text-xs text-gray-600 font-semibold">
              可用现金: <span className="font-bold text-green-700 font-mono">${group.availableCash.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
            </div>
          </div>
        </div>
      ))}

      {filteredGroups.length === 0 && (
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="text-4xl mb-3">📊</div>
            <div className="text-sm text-gray-500">暂无持仓记录</div>
          </div>
        </div>
      )}
    </div>
  );
}

