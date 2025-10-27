'use client';

import { useState, useEffect } from 'react';

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

export default function PositionsList({ selectedModel = 'all' }: PositionsListProps) {
  const [positions, setPositions] = useState<Position[]>([]);

  useEffect(() => {
    // 生成模拟持仓数据 - 只显示DEEPSEEK和QWEN
    const mockPositions: Position[] = [
      {
        id: '3',
        model: 'DEEPSEEK CHAT V3.1',
        modelIcon: '🧠',
        modelColor: '#3b82f6',
        side: 'LONG',
        coin: 'XRP',
        coinIcon: '🪝',
        leverage: '10X',
        notional: 8458,
        unrealizedPnL: -277.44,
        totalUnrealizedPnL: 261.01,
        availableCash: 4805.22,
      },
      {
        id: '4',
        model: 'DEEPSEEK CHAT V3.1',
        modelIcon: '🧠',
        modelColor: '#3b82f6',
        side: 'LONG',
        coin: 'DOGE',
        coinIcon: '🐕',
        leverage: '10X',
        notional: 5312,
        unrealizedPnL: 169.68,
        totalUnrealizedPnL: 261.01,
        availableCash: 4805.22,
      },
      {
        id: '5',
        model: 'DEEPSEEK CHAT V3.1',
        modelIcon: '🧠',
        modelColor: '#3b82f6',
        side: 'LONG',
        coin: 'BTC',
        coinIcon: '₿',
        leverage: '10X',
        notional: 12968,
        unrealizedPnL: 87.30,
        totalUnrealizedPnL: 261.01,
        availableCash: 4805.22,
      },
      {
        id: '6',
        model: 'DEEPSEEK CHAT V3.1',
        modelIcon: '🧠',
        modelColor: '#3b82f6',
        side: 'LONG',
        coin: 'ETH',
        coinIcon: 'Ξ',
        leverage: '10X',
        notional: 11870,
        unrealizedPnL: 67.64,
        totalUnrealizedPnL: 261.01,
        availableCash: 4805.22,
      },
      {
        id: '7',
        model: 'DEEPSEEK CHAT V3.1',
        modelIcon: '🧠',
        modelColor: '#3b82f6',
        side: 'LONG',
        coin: 'SOL',
        coinIcon: '☀️',
        leverage: '15X',
        notional: 14981,
        unrealizedPnL: 26.59,
        totalUnrealizedPnL: 261.01,
        availableCash: 4805.22,
      },
      {
        id: '8',
        model: 'DEEPSEEK CHAT V3.1',
        modelIcon: '🧠',
        modelColor: '#3b82f6',
        side: 'LONG',
        coin: 'BNB',
        coinIcon: '🔶',
        leverage: '10X',
        notional: 8846,
        unrealizedPnL: 187.23,
        totalUnrealizedPnL: 261.01,
        availableCash: 4805.22,
      },
      {
        id: '19',
        model: 'QWEN3 MAX',
        modelIcon: '🎨',
        modelColor: '#ec4899',
        side: 'SHORT',
        coin: 'XRP',
        coinIcon: '🪝',
        leverage: '20X',
        notional: 3592,
        unrealizedPnL: 16.32,
        totalUnrealizedPnL: -188.34,
        availableCash: 1819.47,
      },
      {
        id: '20',
        model: 'QWEN3 MAX',
        modelIcon: '🎨',
        modelColor: '#ec4899',
        side: 'LONG',
        coin: 'DOGE',
        coinIcon: '🐕',
        leverage: '10X',
        notional: 1508,
        unrealizedPnL: 15.45,
        totalUnrealizedPnL: -188.34,
        availableCash: 1819.47,
      },
      {
        id: '21',
        model: 'QWEN3 MAX',
        modelIcon: '🎨',
        modelColor: '#ec4899',
        side: 'SHORT',
        coin: 'BTC',
        coinIcon: '₿',
        leverage: '15X',
        notional: 3242,
        unrealizedPnL: -3.01,
        totalUnrealizedPnL: -188.34,
        availableCash: 1819.47,
      },
      {
        id: '22',
        model: 'QWEN3 MAX',
        modelIcon: '🎨',
        modelColor: '#ec4899',
        side: 'LONG',
        coin: 'ETH',
        coinIcon: 'Ξ',
        leverage: '12X',
        notional: 6526,
        unrealizedPnL: -83.70,
        totalUnrealizedPnL: -188.34,
        availableCash: 1819.47,
      },
      {
        id: '23',
        model: 'QWEN3 MAX',
        modelIcon: '🎨',
        modelColor: '#ec4899',
        side: 'LONG',
        coin: 'SOL',
        coinIcon: '☀️',
        leverage: '15X',
        notional: 3814,
        unrealizedPnL: -98.84,
        totalUnrealizedPnL: -188.34,
        availableCash: 1819.47,
      },
      {
        id: '24',
        model: 'QWEN3 MAX',
        modelIcon: '🎨',
        modelColor: '#ec4899',
        side: 'SHORT',
        coin: 'BNB',
        coinIcon: '🔶',
        leverage: '10X',
        notional: 3848,
        unrealizedPnL: -34.55,
        totalUnrealizedPnL: -188.34,
        availableCash: 1819.47,
      },
    ];

    setPositions(mockPositions);
  }, []);

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
    <div className="h-full overflow-y-auto p-4 space-y-4 bg-white">
      {filteredGroups.map((group: any) => (
        <div key={group.model} className="bg-white border border-gray-200 rounded-lg p-4">
          {/* 模型头部 */}
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">{group.modelIcon}</span>
              <span className="text-sm font-bold" style={{ color: group.modelColor }}>
                {group.model}
              </span>
            </div>
            <div className="flex items-center space-x-6">
              <div className="text-right">
                <div className="text-xs text-gray-500">TOTAL UNREALIZED P&L:</div>
                <div className={`text-sm font-bold ${group.totalUnrealizedPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
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
              <div key={position.id} className="grid grid-cols-6 gap-4 items-center py-2 px-2 hover:bg-gray-50 rounded">
                <div className={`text-sm font-bold ${position.side === 'LONG' ? 'text-green-600' : 'text-red-600'}`}>
                  {position.side}
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{position.coinIcon}</span>
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
          <div className="mt-4 pt-3 border-t border-gray-200">
            <div className="text-xs text-gray-500">
              AVAILABLE CASH: <span className="font-bold text-gray-900">${group.availableCash.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
            </div>
          </div>
        </div>
      ))}

      {filteredGroups.length === 0 && (
        <div className="flex items-center justify-center h-full text-gray-500">
          暂无持仓记录
        </div>
      )}
    </div>
  );
}

