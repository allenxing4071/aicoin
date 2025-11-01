'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import CoinIcon from '../common/CoinIcon';
import DeepSeekLogo from '../common/DeepSeekLogo';

interface Model {
  name: string;
  slug?: string;
  value: number;
  change: number;
  color: string;
  icon?: string;
}

interface Trade {
  id: number;
  model: string;
  modelIcon: string;
  type: 'long' | 'short';
  symbol: string;
  price: string;
  quantity: string;
  notional: string;
  holdingTime: string;
  pnl: number;
  timestamp: string;
}

interface TradeListCompleteProps {
  selectedModel: string;
  models: Model[];
}

const API_BASE = 'http://localhost:8000/api/v1';

export default function TradeListComplete({ selectedModel, models }: TradeListCompleteProps) {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRealTrades();
    // 每30秒更新一次
    const interval = setInterval(fetchRealTrades, 30000);
    return () => clearInterval(interval);
  }, [models]);

  const fetchRealTrades = async () => {
    try {
      const response = await axios.get(`${API_BASE}/trading/trades?limit=100`);
      
      if (response.data && response.data.trades) {
        const realTrades = response.data.trades.map((trade: any, index: number) => {
          // 找到对应的模型
          const modelData = models.find(m => m.slug === trade.model) || models[0];
          
          return {
            id: trade.id || index,
            model: modelData.name,
            modelIcon: modelData.icon || '🤖',
            type: trade.side.toLowerCase() === 'buy' ? 'long' as const : 'short' as const,
            symbol: trade.symbol,
            price: `$${parseFloat(trade.price).toFixed(4)}`,
            quantity: parseFloat(trade.size).toFixed(4),
            notional: `$${(parseFloat(trade.size) * parseFloat(trade.price) / 1000).toFixed(3)}k`,
            holdingTime: formatHoldingTime(trade.timestamp),
            pnl: parseFloat(trade.pnl || 0),
            timestamp: formatTimestamp(trade.timestamp)
          };
        });
        
        setTrades(realTrades);
        setLoading(false);
      } else {
        // 如果API返回空数据，使用演示数据
        generateMockTrades();
      }
    } catch (error) {
      console.error('Failed to fetch trades, using mock data:', error);
      generateMockTrades();
    }
  };

  const formatHoldingTime = (timestamp: string): string => {
    try {
      const tradeTime = new Date(timestamp);
      const now = new Date();
      const diffMs = now.getTime() - tradeTime.getTime();
      const hours = Math.floor(diffMs / (1000 * 60 * 60));
      const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
      return `${hours}H ${minutes}M`;
    } catch {
      return '0H 0M';
    }
  };

  const formatTimestamp = (timestamp: string): string => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString('en-US', { 
        month: '2-digit', 
        day: '2-digit', 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
      });
    } catch {
      return '';
    }
  };

  const generateMockTrades = () => {
    const symbols = ['DOGE!', 'ETH!', 'SOL!', 'XRP!', 'BTC!', 'BNB!'];
    const mockTrades: Trade[] = [];
    
    let id = 1;
    models.forEach((model) => {
      const tradeCount = 15 + Math.floor(Math.random() * 5);
      
      for (let i = 0; i < tradeCount; i++) {
        const symbol = symbols[Math.floor(Math.random() * symbols.length)];
        const type = Math.random() > 0.5 ? 'long' : 'short';
        const price1 = 50 + Math.random() * 100;
        const price2 = price1 * (0.95 + Math.random() * 0.1);
        const quantity = (Math.random() * 50) - 25;
        const notional = Math.random() * 20000;
        const pnl = (Math.random() - 0.3) * 1000;
        
        const hours = Math.floor(Math.random() * 72);
        const minutes = Math.floor(Math.random() * 60);
        
        mockTrades.push({
          id: id++,
          model: model.name,
          modelIcon: model.icon || '🤖',
          type,
          symbol,
          price: `$${price1.toFixed(4)} → $${price2.toFixed(4)}`,
          quantity: quantity.toFixed(2),
          notional: `$${(notional / 1000).toFixed(3)} → $${((notional + pnl) / 1000).toFixed(3)}`,
          holdingTime: `${hours}H ${minutes}M`,
          pnl,
          timestamp: `10/22, ${Math.floor(Math.random() * 12)}:${String(Math.floor(Math.random() * 60)).padStart(2, '0')} ${Math.random() > 0.5 ? 'AM' : 'PM'}`
        });
      }
    });

    mockTrades.sort(() => Math.random() - 0.5);
    setTrades(mockTrades.slice(0, 100));
  };

  const filteredTrades = selectedModel === 'all' 
    ? trades 
    : trades.filter(t => {
        const modelSlug = models.find(m => m.name === t.model)?.slug || '';
        return modelSlug === selectedModel || t.model.toLowerCase().includes(selectedModel);
      });

  return (
    <div className="h-full overflow-y-auto p-4 space-y-3 bg-white">
      {filteredTrades.map((trade) => (
        <div 
          key={trade.id} 
          className="bg-white border border-gray-200 rounded-lg p-4 hover:border-gray-300 hover:shadow-sm transition-all"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <DeepSeekLogo size={20} />
              <span className="text-sm font-bold text-gray-900">
                {trade.model.split(' ')[0]} {trade.model.includes('2.5') ? '2.5' : ''} {trade.model.includes('PRO') ? 'Pro' : trade.model.includes('MAX') ? 'Max' : ''}
              </span>
              <span className="text-xs text-gray-600">完成了一笔</span>
              <span className={`text-xs font-bold ${trade.type === 'long' ? 'text-green-600' : 'text-red-600'}`}>
                {trade.type === 'long' ? '做多' : '做空'}
              </span>
              <span className="text-xs text-gray-600">交易于</span>
            </div>
            <span className="text-xs text-gray-500 font-mono">{trade.timestamp}</span>
          </div>

          <div className="mb-3">
            <span className="text-lg font-bold text-gray-900 flex items-center gap-2">
              <CoinIcon symbol={trade.symbol} size={24} />
              {trade.symbol}
            </span>
          </div>

          <div className="space-y-1 text-xs font-mono">
            <div className="flex justify-between">
              <span className="text-gray-500">价格:</span>
              <span className="text-gray-900">{trade.price}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">数量:</span>
              <span className="text-gray-900">{trade.quantity}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">名义价值:</span>
              <span className="text-gray-900">{trade.notional}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">持仓时间:</span>
              <span className="text-gray-900">{trade.holdingTime}</span>
            </div>
          </div>

          <div className="mt-3 pt-3 border-t border-gray-200 flex justify-between items-center">
            <span className="text-xs text-gray-500 font-mono">净盈亏:</span>
            <span className={`text-lg font-bold ${trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {trade.pnl >= 0 ? '+' : ''}${Math.abs(trade.pnl).toFixed(2)}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
