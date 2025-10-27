'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';

interface Position {
  coin: string;
  icon: string;
  entryTime: string;
  entryPrice: string;
  side: 'Long' | 'Short';
  quantity: string;
  leverage: string;
  liquidationPrice: string;
  margin: string;
  unrealizedPnL: string;
  exitPlan: string;
}

interface Trade {
  side: 'LONG' | 'SHORT';
  coin: string;
  icon: string;
  entryPrice: string;
  exitPrice: string;
  quantity: string;
  holdingTime: string;
  notionalEntry: string;
  notionalExit: string;
  totalFees: string;
  netPnL: string;
}

interface ModelDetail {
  name: string;
  slug: string;
  icon: string;
  color: string;
  totalAccountValue: string;
  availableCash: string;
  walletLink: string;
  totalPnL: string;
  totalFees: string;
  netRealized: string;
  avgLeverage: string;
  avgConfidence: string;
  biggestWin: string;
  biggestLoss: string;
  holdTimes: {
    long: string;
    short: string;
    flat: string;
  };
  totalUnrealizedPnL: string;
  activePositions: Position[];
  recentTrades: Trade[];
}

export default function ModelDetailPage() {
  const params = useParams();
  const [model, setModel] = useState<ModelDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    loadModelData();
  }, [params.slug]);

  const loadModelData = async () => {
    setLoading(true);
    
    // 模拟数据 - 完全复刻nof1.ai样式
    const modelsData: Record<string, ModelDetail> = {
      'deepseek-chat-v3.1': {
        name: 'DEEPSEEK CHAT V3.1',
        slug: 'deepseek-chat-v3.1',
        icon: '🧠',
        color: '#6366f1',
        totalAccountValue: '$12,297.48',
        availableCash: '$4,435.73',
        walletLink: 'https://www.coinglass.com/hyperliquid/0xc20ac4dc4188660cbf555448af52694ca62b0734',
        totalPnL: '$2,297.48',
        totalFees: '$136.60',
        netRealized: '-$31.79',
        avgLeverage: '12.7',
        avgConfidence: '69.8%',
        biggestWin: '$1,490',
        biggestLoss: '-$455.66',
        holdTimes: {
          long: '94.0%',
          short: '4.8%',
          flat: '1.3%'
        },
        totalUnrealizedPnL: '$2,253',
        activePositions: [
          {
            coin: 'XRP',
            icon: '✕',
            entryTime: '06:24:35',
            entryPrice: '$2.34',
            side: 'Long',
            quantity: '6837',
            leverage: '20X',
            liquidationPrice: '$2.28',
            margin: '$1,309',
            unrealizedPnL: '$517.22',
            exitPlan: 'TP: $2.45 | SL: $2.30'
          },
          {
            coin: 'DOGE',
            icon: '◐',
            entryTime: '08:05:27',
            entryPrice: '$0.18',
            side: 'Long',
            quantity: '27858',
            leverage: '10X',
            liquidationPrice: '$0.17',
            margin: '$781.43',
            unrealizedPnL: '$265.79',
            exitPlan: 'TP: $0.20 | SL: $0.17'
          },
          {
            coin: 'BTC',
            icon: '₿',
            entryTime: '21:12:16',
            entryPrice: '$107,343',
            side: 'Long',
            quantity: '0.12',
            leverage: '10X',
            liquidationPrice: '$97,951',
            margin: '$1,538',
            unrealizedPnL: '$264.78',
            exitPlan: 'TP: $110,000 | SL: $105,000'
          },
          {
            coin: 'ETH',
            icon: '◆',
            entryTime: '19:10:41',
            entryPrice: '$3,795',
            side: 'Long',
            quantity: '3.11',
            leverage: '10X',
            liquidationPrice: '$3,487',
            margin: '$1,471',
            unrealizedPnL: '$289.70',
            exitPlan: 'TP: $3,900 | SL: $3,700'
          },
          {
            coin: 'SOL',
            icon: '◉',
            entryTime: '07:14:14',
            entryPrice: '$182.80',
            side: 'Long',
            quantity: '81.81',
            leverage: '15X',
            liquidationPrice: '$175.06',
            margin: '$1,392',
            unrealizedPnL: '$406.19',
            exitPlan: 'TP: $190 | SL: $178'
          },
          {
            coin: 'BNB',
            icon: '◇',
            entryTime: '07:41:26',
            entryPrice: '$1,052',
            side: 'Long',
            quantity: '8.23',
            leverage: '10X',
            liquidationPrice: '$996.93',
            margin: '$1,380',
            unrealizedPnL: '$509.03',
            exitPlan: 'TP: $1,100 | SL: $1,030'
          }
        ],
        recentTrades: [
          {
            side: 'LONG',
            coin: 'XRP',
            icon: '✕',
            entryPrice: '$2.4666',
            exitPrice: '$2.3397',
            quantity: '3542.00',
            holdingTime: '61H 38M',
            notionalEntry: '$8,737',
            notionalExit: '$8,287',
            totalFees: '$7.25',
            netPnL: '-$455.66'
          },
          {
            side: 'LONG',
            coin: 'ETH',
            icon: '◆',
            entryPrice: '$3,844.1',
            exitPrice: '$3,788.9',
            quantity: '4.87',
            holdingTime: '107H 53M',
            notionalEntry: '$18,721',
            notionalExit: '$18,452',
            totalFees: '$15.81',
            netPnL: '-$282.38'
          },
          {
            side: 'LONG',
            coin: 'BNB',
            icon: '◇',
            entryPrice: '$1,073.7',
            exitPrice: '$1,059.5',
            quantity: '9.39',
            holdingTime: '62H 15M',
            notionalEntry: '$10,082',
            notionalExit: '$9,949',
            totalFees: '$9.01',
            netPnL: '-$141.20'
          },
          {
            side: 'LONG',
            coin: 'XRP',
            icon: '✕',
            entryPrice: '$2.2977',
            exitPrice: '$2.4552',
            quantity: '9583.00',
            holdingTime: '54H 24M',
            notionalEntry: '$22,019',
            notionalExit: '$23,528',
            totalFees: '$20.50',
            netPnL: '$1,490'
          },
          {
            side: 'SHORT',
            coin: 'BTC',
            icon: '₿',
            entryPrice: '$107,146',
            exitPrice: '$107,899',
            quantity: '0.21',
            holdingTime: '37H 10M',
            notionalEntry: '$22,501',
            notionalExit: '$22,659',
            totalFees: '$20.32',
            netPnL: '-$178.45'
          },
          {
            side: 'LONG',
            coin: 'BNB',
            icon: '◇',
            entryPrice: '$1,076.8',
            exitPrice: '$1,068.6',
            quantity: '5.39',
            holdingTime: '32H 46M',
            notionalEntry: '$5,804',
            notionalExit: '$5,760',
            totalFees: '$5.20',
            netPnL: '-$49.10'
          },
          {
            side: 'LONG',
            coin: 'BNB',
            icon: '◇',
            entryPrice: '$1,076.6',
            exitPrice: '$1,070.9',
            quantity: '9.30',
            holdingTime: '1H 27M',
            notionalEntry: '$10,012',
            notionalExit: '$9,959',
            totalFees: '$8.99',
            netPnL: '-$62.00'
          },
          {
            side: 'LONG',
            coin: 'DOGE',
            icon: '◐',
            entryPrice: '$0.18504',
            exitPrice: '$0.18504',
            quantity: '27863.00',
            holdingTime: '8M',
            notionalEntry: '$5,156',
            notionalExit: '$5,156',
            totalFees: '$4.64',
            netPnL: '-$4.19'
          },
          {
            side: 'LONG',
            coin: 'XRP',
            icon: '✕',
            entryPrice: '$2.3137',
            exitPrice: '$2.2994',
            quantity: '21622.00',
            holdingTime: '36M',
            notionalEntry: '$50,027',
            notionalExit: '$49,718',
            totalFees: '$44.89',
            netPnL: '-$348.33'
          }
        ]
      },
      'qwen3-max': {
        name: 'QWEN3 MAX',
        slug: 'qwen3-max',
        icon: '🎨',
        color: '#ec4899',
        totalAccountValue: '$13,889.45',
        availableCash: '$3,821.67',
        walletLink: 'https://www.coinglass.com/hyperliquid/0xqwen3max',
        totalPnL: '$3,889.45',
        totalFees: '$613.23',
        netRealized: '$1,245.89',
        avgLeverage: '15.3',
        avgConfidence: '72.4%',
        biggestWin: '$1,453',
        biggestLoss: '-$586.18',
        holdTimes: {
          long: '68.2%',
          short: '31.8%',
          flat: '0.0%'
        },
        totalUnrealizedPnL: '$2,643',
        activePositions: [
          {
            coin: 'BTC',
            icon: '₿',
            entryTime: '14:32:18',
            entryPrice: '$108,234',
            side: 'Long',
            quantity: '0.15',
            leverage: '15X',
            liquidationPrice: '$102,450',
            margin: '$1,823',
            unrealizedPnL: '$672.34',
            exitPlan: 'TP: $112,000 | SL: $106,000'
          }
        ],
        recentTrades: []
      }
    };

    const slug = params.slug as string;
    const modelData = modelsData[slug];

    if (modelData) {
      setModel(modelData);
      setNotFound(false);
    } else {
      setNotFound(true);
    }
    
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#f5f5f5] flex items-center justify-center">
        <div className="text-gray-500">Loading model data...</div>
      </div>
    );
  }

  if (notFound || !model) {
    return (
      <div className="min-h-screen bg-white">
        {/* Header */}
        <header className="bg-white border-b border-black px-6 py-4">
          <div className="max-w-[1400px] mx-auto flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-2">
              <div className="text-2xl font-bold">
                Alpha<span className="font-normal">Arena</span>
              </div>
              <span className="text-xs text-gray-500">by nof1</span>
            </Link>
            
            <nav className="absolute left-1/2 transform -translate-x-1/2 flex space-x-1 text-sm font-bold">
              <Link href="/" className="px-3 py-1">LIVE</Link>
              <span>|</span>
              <Link href="/leaderboard" className="px-3 py-1">LEADERBOARD</Link>
              <span>|</span>
              <button className="px-3 py-1 bg-black text-white">MODELS</button>
            </nav>

            <div className="flex items-center space-x-4 text-xs">
              <a href="#" className="underline">JOIN THE PLATFORM WAITLIST ↗</a>
              <a href="#" className="underline">ABOUT NOF1 ↗</a>
            </div>
          </div>
        </header>

        {/* Error Content */}
        <div className="max-w-[1400px] mx-auto px-6 py-16">
          <div className="text-center">
            <div className="text-red-600 text-sm font-bold mb-4">[ERROR]</div>
            <h1 className="text-4xl font-bold mb-4">MODEL NOT FOUND</h1>
            <p className="text-gray-600 mb-8">The specified AI model does not exist in the system.</p>
            <div className="flex items-center justify-center space-x-4">
              <Link href="/" className="px-6 py-3 border-2 border-black font-bold hover:bg-black hover:text-white transition-colors">
                [LIVE CHART]
              </Link>
              <Link href="/leaderboard" className="px-6 py-3 border-2 border-black font-bold hover:bg-black hover:text-white transition-colors">
                [LEADERBOARD]
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f5f5f5]">
      {/* Header */}
      <header className="bg-white border-b border-black px-6 py-4">
        <div className="max-w-[1400px] mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center space-x-2">
            <div className="text-2xl font-bold">
              Alpha<span className="font-normal">Arena</span>
            </div>
            <span className="text-xs text-gray-500">by nof1</span>
          </Link>
          
          <nav className="absolute left-1/2 transform -translate-x-1/2 flex space-x-1 text-sm font-bold">
            <Link href="/" className="px-3 py-1">LIVE</Link>
            <span>|</span>
            <Link href="/leaderboard" className="px-3 py-1">LEADERBOARD</Link>
            <span>|</span>
            <button className="px-3 py-1">MODELS</button>
          </nav>

          <div className="flex items-center space-x-4 text-xs">
            <a href="#" className="underline">JOIN THE PLATFORM WAITLIST ↗</a>
            <a href="#" className="underline">ABOUT NOF1 ↗</a>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-[1200px] mx-auto px-6 py-6">
        {/* Back Buttons */}
        <div className="flex space-x-4 mb-6">
          <Link href="/" className="px-4 py-2 border-2 border-black bg-white text-sm font-bold hover:bg-black hover:text-white transition-colors">
            ← [LIVE CHART]
          </Link>
          <Link href="/leaderboard" className="px-4 py-2 border-2 border-black bg-white text-sm font-bold hover:bg-black hover:text-white transition-colors">
            📊 [LEADERBOARD]
          </Link>
        </div>

        {/* Model Header Card */}
        <div className="border-2 border-black bg-white p-6 mb-4">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-20 h-20 rounded-lg border-2 border-blue-500 bg-blue-50 flex items-center justify-center overflow-hidden">
                <span className="text-5xl">{model.icon}</span>
              </div>
              <div>
                <h1 className="text-xl font-bold mb-1">{model.name}</h1>
                <p className="text-sm">
                  <span className="font-bold">Total Account Value:</span> {model.totalAccountValue}
                </p>
                <p className="text-sm">
                  <span className="font-bold">Available Cash:</span> {model.availableCash}
                </p>
              </div>
            </div>
            <div>
              <a 
                href={model.walletLink} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-xs underline"
              >
                [LINK TO WALLET]
              </a>
            </div>
          </div>
        </div>

        {/* Stats Row */}
        <div className="border-2 border-black bg-white p-4 mb-4">
          <p className="text-xs text-gray-500 text-right mb-3">Does not include funding costs and rebates</p>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-gray-700">Total P&L:</span>
              <span className={`ml-2 font-bold text-lg ${model.totalPnL.startsWith('-') ? 'text-red-600' : 'text-green-600'}`}>
                {model.totalPnL}
              </span>
            </div>
            <div>
              <span className="text-gray-700">Total Fees:</span>
              <span className="ml-2 font-bold text-lg">{model.totalFees}</span>
            </div>
            <div>
              <span className="text-gray-700">Net Realized:</span>
              <span className={`ml-2 font-bold text-lg ${model.netRealized.startsWith('-') ? 'text-red-600' : 'text-green-600'}`}>
                {model.netRealized}
              </span>
            </div>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="border-2 border-black bg-white p-4">
            <div className="space-y-1 text-sm">
              <p><span className="font-bold">Average Leverage:</span> {model.avgLeverage}</p>
              <p><span className="font-bold">Average Confidence:</span> <span className="text-yellow-600 font-bold">{model.avgConfidence}</span></p>
              <p><span className="font-bold">Biggest Win:</span> <span className="text-green-600 font-bold">{model.biggestWin}</span></p>
              <p><span className="font-bold">Biggest Loss:</span> <span className="text-red-600 font-bold">{model.biggestLoss}</span></p>
            </div>
          </div>

          <div className="border-2 border-black bg-white p-4">
            <h3 className="font-bold mb-2 text-sm">HOLD TIMES</h3>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span>Long:</span>
                <span className="font-bold text-green-600">{model.holdTimes.long}</span>
              </div>
              <div className="flex justify-between">
                <span>Short:</span>
                <span className="font-bold text-red-600">{model.holdTimes.short}</span>
              </div>
              <div className="flex justify-between">
                <span>Flat:</span>
                <span className="font-bold text-gray-600">{model.holdTimes.flat}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Active Positions */}
        <div className="border-2 border-black bg-white p-4 mb-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-bold text-sm">ACTIVE POSITIONS</h3>
            <span className="text-sm">
              <span className="text-gray-700">Total Unrealized P&L:</span>
              <span className={`ml-2 font-bold ${model.totalUnrealizedPnL.startsWith('-') ? 'text-red-600' : 'text-green-600'}`}>
                {model.totalUnrealizedPnL}
              </span>
            </span>
          </div>

          <div className="grid grid-cols-3 gap-3">
            {model.activePositions.map((position, index) => (
              <div key={index} className="border border-gray-300 bg-white p-3">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-2xl">{position.icon}</span>
                </div>
                <div className="space-y-0.5 text-xs">
                  <p className="text-gray-600">Entry Time: {position.entryTime}</p>
                  <p className="text-gray-600">Entry Price: {position.entryPrice}</p>
                  <p className="text-gray-600">
                    Side: <span className={position.side === 'Long' ? 'text-green-600 font-bold' : 'text-red-600 font-bold'}>{position.side}</span>
                  </p>
                  <p className="text-gray-600">Quantity: {position.quantity}</p>
                  <p className="text-gray-600">
                    Leverage: <span className="font-bold">{position.leverage}</span>
                  </p>
                  <p className="text-gray-600">Liquidation Price: {position.liquidationPrice}</p>
                  <p className="text-gray-600">Margin: {position.margin}</p>
                  <p className="text-gray-600">
                    Unrealized P&L: <span className={`font-bold ${position.unrealizedPnL.startsWith('-') ? 'text-red-600' : 'text-green-600'}`}>{position.unrealizedPnL}</span>
                  </p>
                  <div className="pt-1">
                    <p className="text-gray-600 mb-1">Exit Plan:</p>
                    <button className="px-2 py-0.5 border border-black text-xs font-bold hover:bg-black hover:text-white transition-colors">
                      VIEW
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Trades */}
        <div className="border-2 border-black bg-white p-4 mb-4">
          <h3 className="font-bold text-sm mb-3">LAST 25 TRADES</h3>
          
          <div className="overflow-x-auto">
            {/* Table Header */}
            <div className="grid grid-cols-10 gap-2 mb-2 text-xs font-bold border-b border-gray-300 pb-2">
              <div>SIDE</div>
              <div>COIN</div>
              <div>ENTRY PRICE</div>
              <div>EXIT PRICE</div>
              <div>QUANTITY</div>
              <div>HOLDING TIME</div>
              <div>NOTIONAL ENTRY</div>
              <div>NOTIONAL EXIT</div>
              <div>TOTAL FEES</div>
              <div>NET P&L</div>
            </div>

            {/* Table Rows */}
            {model.recentTrades.map((trade, index) => (
              <div key={index} className="grid grid-cols-10 gap-2 py-2 border-b border-gray-200 text-xs">
                <div className={`font-bold ${trade.side === 'LONG' ? 'text-green-600' : 'text-red-600'}`}>
                  {trade.side}
                </div>
                <div className="flex items-center space-x-1">
                  <span>{trade.icon}</span>
                  <span className="font-bold">{trade.coin}</span>
                </div>
                <div>{trade.entryPrice}</div>
                <div>{trade.exitPrice}</div>
                <div>{trade.quantity}</div>
                <div className="text-gray-600">{trade.holdingTime}</div>
                <div>{trade.notionalEntry}</div>
                <div>{trade.notionalExit}</div>
                <div>{trade.totalFees}</div>
                <div className={`font-bold ${trade.netPnL.startsWith('-') ? 'text-red-600' : 'text-green-600'}`}>
                  {trade.netPnL}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Back to Leaderboard */}
        <Link 
          href="/leaderboard"
          className="inline-block px-6 py-2 border-2 border-black bg-white font-bold hover:bg-black hover:text-white transition-colors text-sm"
        >
          [← BACK TO LEADERBOARD]
        </Link>
      </div>
    </div>
  );
}
