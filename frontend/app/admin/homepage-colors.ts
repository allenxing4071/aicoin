/**
 * 首页配色方案 - 应用到所有页面
 * 清爽、活泼的彩色卡片风格
 */

export const homepageColors = {
  // 蓝色系 - 用于交易所、API、技术相关
  blue: {
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    title: 'text-blue-900',
    text: 'text-blue-700',
    accent: 'text-blue-600',
    button: 'bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700',
  },
  
  // 绿色系 - 用于数据、成功状态、环境
  green: {
    bg: 'bg-green-50',
    border: 'border-green-200',
    title: 'text-green-900',
    text: 'text-green-700',
    accent: 'text-green-600',
    button: 'bg-green-600 hover:bg-green-700',
  },
  
  // 紫色系 - 用于权限、AI、模型
  purple: {
    bg: 'bg-purple-50',
    border: 'border-purple-200',
    title: 'text-purple-900',
    text: 'text-purple-700',
    accent: 'text-purple-600',
    button: 'bg-purple-600 hover:bg-purple-700',
  },
  
  // 橙色系 - 用于情报、记忆、Qwen
  orange: {
    bg: 'bg-orange-50',
    border: 'border-orange-200',
    title: 'text-orange-900',
    text: 'text-orange-700',
    accent: 'text-orange-600',
    button: 'bg-orange-600 hover:bg-orange-700',
  },
  
  // 粉色系 - 用于交易、订单
  pink: {
    bg: 'bg-pink-50',
    border: 'border-pink-200',
    title: 'text-pink-900',
    text: 'text-pink-700',
    accent: 'text-pink-600',
    button: 'bg-pink-600 hover:bg-pink-700',
  },
  
  // 青色系 - 用于监控、统计
  cyan: {
    bg: 'bg-cyan-50',
    border: 'border-cyan-200',
    title: 'text-cyan-900',
    text: 'text-cyan-700',
    accent: 'text-cyan-600',
    button: 'bg-cyan-600 hover:bg-cyan-700',
  },
};

// 页面配色映射
export const pageColorMap = {
  exchanges: 'blue',      // 交易所 - 蓝色
  intelligence: 'orange', // 情报 - 橙色
  trading: 'pink',        // 交易 - 粉色
  memory: 'purple',       // 记忆 - 紫色
  'ai-decisions': 'purple', // AI决策 - 紫色
  'model-performance': 'cyan', // 模型性能 - 青色
  'market-data': 'green',  // 数据 - 绿色
};
