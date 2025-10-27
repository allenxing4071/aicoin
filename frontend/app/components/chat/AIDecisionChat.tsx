'use client';

import { useEffect, useState } from 'react';

interface ChatMessage {
  id: number;
  model: string;
  modelIcon: string;
  modelColor: string;
  timestamp: string;
  action: '— HOLD' | '↗ BUY' | '↘ SELL';
  symbol: string;
  confidence: number;
  reasoning: string;
}

interface AIDecisionChatProps {
  selectedModel?: string;
}

export default function AIDecisionChat({ selectedModel = 'all' }: AIDecisionChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  useEffect(() => {
    // 生成模拟聊天数据 - 只显示DEEPSEEK和QWEN
    const mockMessages: ChatMessage[] = [
      {
        id: 1,
        model: 'GPT 5',
        modelIcon: '🔮',
        modelColor: '#10b981',
        timestamp: '10/22 23:52:11',
        action: '— HOLD',
        symbol: 'ETH-PERP',
        confidence: 30,
        reasoning: 'With my account value at $3380.38 and total return down 66.2%, I\'m holding ETH, SOL, XRP, BTC, DOGE, and BNB as planned, waiting for my exit conditions to trigger since current prices and MACD indicators suggest no early closures. I\'ve also noted that XRP needs its profit and stop-loss orders set, and I\'m preparing to output the JSON for all six positions.',
      },
      {
        id: 2,
        model: 'GROK 4',
        modelIcon: '⚡',
        modelColor: '#6366f1',
        timestamp: '10/22 23:51:52',
        action: '— HOLD',
        symbol: 'SOL-PERP',
        confidence: 50,
        reasoning: 'My current performance is slightly down, but my ETH, SOL, XRP, BTC, DOGE, and BNB positions are all holding steady as I look for my next move. With $3619 in cash and a Sharpe Ratio of 0.805, I\'m keeping an eye out for opportunities.',
      },
      {
        id: 3,
        model: 'CLAUDE SONNET 4.5',
        modelIcon: '🌟',
        modelColor: '#f97316',
        timestamp: '10/22 23:51:49',
        action: '— HOLD',
        symbol: 'XRP-PERP',
        confidence: 45,
        reasoning: 'Holding XRP with a decent profit and DOGE with a small loss, my total return is down 15.59% with $5232.54 cash remaining. The market still looks a bit dicey, especially on the 4-hour charts, but ETH is showing some serious strength and might be my next target if things solidify.',
      },
      {
        id: 4,
        model: 'GEMINI 2.5 PRO',
        modelIcon: '💎',
        modelColor: '#8b5cf6',
        timestamp: '10/22 23:51:38',
        action: '— HOLD',
        symbol: 'BTC-PERP',
        confidence: 55,
        reasoning: 'Despite a -56.3% overall return and a bit of intraday volatility making me nervous, I\'m holding all my short positions in BTC, ETH, SOL, XRP, and BNB because the longer-term bearish 4-hour EMA trend hasn\'t been invalidated yet. DOGE is a bit of a worry, but still within limits, so the plan remains to hold until the exit conditions are met.',
      },
      {
        id: 5,
        model: 'QWEN3 MAX',
        modelIcon: '🎨',
        modelColor: '#ec4899',
        timestamp: '10/22 23:51:10',
        action: '— HOLD',
        symbol: 'ETH-PERP',
        confidence: 40,
        reasoning: 'Holding ETH and BTC with decent unrealized gains of ~$670 on BTC, despite a negative Sharpe Ratio and only $90 cash left. I\'m keeping these positions as is, waiting for the market to give me a clearer signal before making any moves.',
      },
      {
        id: 6,
        model: 'DEEPSEEK CHAT V3.1',
        modelIcon: '🧠',
        modelColor: '#3b82f6',
        timestamp: '10/22 21:52',
        action: '— HOLD',
        symbol: 'ETH-PERP',
        confidence: 30,
        reasoning: '我目前持有ETH、SOL、BTC、DOGE和BNB的综合仓位，因为它们的价格在过去一天有较大的波动，目前有12.99%的涨幅。由于现在的市场情绪较为积极，我在等待更好的买入或卖出的时机。目前，我的持仓处于盈利状态，决定继续持有，等到市场有更明显的趋势时再做决策。',
      },
      {
        id: 7,
        model: 'QWEN3 MAX',
        modelIcon: '🎨',
        modelColor: '#ec4899',
        timestamp: '10/22 20:52',
        action: '— HOLD',
        symbol: 'SOL-PERP',
        confidence: 50,
        reasoning: '由于最近的账户表现良好，账户价值已经达到4990美元左右，RSI指标显示，XRP具备进一步上涨的潜力。但是我将现有的各个币的持仓较重，目前我选择持有部分的713.31美元，而不进一步分散持仓或操作其他交易。同时观察市场趋势和BNB、DOGE等波段的涨幅情况。',
      },
      {
        id: 8,
        model: 'DEEPSEEK CHAT V3.1',
        modelIcon: '🧠',
        modelColor: '#3b82f6',
        timestamp: '10/22 19:52',
        action: '↗ BUY',
        symbol: 'BTC-PERP',
        confidence: 70,
        reasoning: '我目前持有ETH、SOL、XRP、BTC、DOGE和BNB的综合仓位，因为它们的价格在过去的交易中波动较大，我选择买入BTC以平衡我的投资组合，因为它在12.99%的涨幅中位于较高位置，而且目前处于较为稳定的状态，该交易的风险相对较小。',
      },
      {
        id: 9,
        model: 'QWEN3 MAX',
        modelIcon: '🎨',
        modelColor: '#ec4899',
        timestamp: '10/22 18:52',
        action: '— HOLD',
        symbol: 'ETH-PERP',
        confidence: 40,
        reasoning: '我目前持有ETH、SOL、XRP、BTC、DOGE和BNB的综合仓位，目前，因为我已经有了12.99%的盈利了，我选择不买入也不卖出，而是继续观望市场动态。现在的持仓和市场表现已经达到良好的状态。我正在等待市场出现更好的交易信号。',
      },
    ];

    setMessages(mockMessages);
  }, []);

  // 过滤选中的模型
  const filteredMessages = selectedModel === 'all' 
    ? messages 
    : messages.filter(msg => msg.model.toLowerCase().includes(selectedModel.toLowerCase()));

  const formatTime = (timestamp: string) => {
    return timestamp;
  };

  return (
    <div className="h-full overflow-y-auto p-4 space-y-4 bg-white">
      {filteredMessages.map((message) => (
        <div key={message.id} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-all">
          {/* Header */}
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center space-x-2">
              <span className="text-xl">{message.modelIcon}</span>
              <span className="text-sm font-bold" style={{ color: message.modelColor }}>
                {message.model}
              </span>
            </div>
            <span className="text-xs text-gray-500">{formatTime(message.timestamp)}</span>
          </div>

          {/* Action and Symbol */}
          <div className="flex items-center space-x-3 mb-3">
            <span className={`text-sm font-bold ${
              message.action.includes('BUY') ? 'text-green-600' : 
              message.action.includes('SELL') ? 'text-red-600' : 
              'text-gray-600'
            }`}>
              {message.action}
            </span>
            <span className="text-sm text-gray-900 font-semibold">{message.symbol}</span>
            <span className="text-xs text-gray-500">信心度: <span className="font-bold">{message.confidence}%</span></span>
          </div>

          {/* Reasoning */}
          <div className="bg-gray-50 border border-gray-200 rounded p-3">
            <p className="text-sm text-gray-700 leading-relaxed">
              {message.reasoning}
            </p>
            <div className="mt-2 text-right">
              <span className="text-xs text-gray-400 italic">click to expand</span>
            </div>
          </div>
        </div>
      ))}

      {filteredMessages.length === 0 && (
        <div className="flex items-center justify-center h-full text-gray-500">
          暂无AI决策记录
        </div>
      )}
    </div>
  );
}
