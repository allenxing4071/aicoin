/**
 * AIcoin 管理后台设计系统 v2.0
 * 年轻化、清爽、有活力的配色方案
 */

export const designSystem = {
  // 🎨 主题色 - 更年轻更有活力
  colors: {
    // 主色调 - 明亮的蓝色
    primary: {
      50: '#e6f4ff',
      100: '#bae0ff',
      200: '#91caff',
      300: '#69b1ff',
      400: '#4096ff',
      500: '#1677ff',  // 主色 - 更鲜艳的蓝
      600: '#0958d9',
      700: '#003eb3',
      800: '#002c8c',
      900: '#001d66',
    },
    
    // 成功色 - 清新的绿
    success: {
      50: '#f6ffed',
      500: '#52c41a',
      600: '#389e0d',
    },
    
    // 警告色 - 活力的橙
    warning: {
      50: '#fff7e6',
      500: '#fa8c16',
      600: '#d46b08',
    },
    
    // 错误色 - 鲜艳的红
    error: {
      50: '#fff1f0',
      500: '#ff4d4f',
      600: '#cf1322',
    },
    
    // 中性色 - 更柔和
    neutral: {
      0: '#ffffff',
      50: '#fafafa',
      100: '#f5f5f5',
      200: '#e8e8e8',
      300: '#d9d9d9',
      400: '#bfbfbf',
      500: '#8c8c8c',
      600: '#595959',
      700: '#434343',
      800: '#262626',
      900: '#141414',
    },
  },
  
  // 📏 间距 - 更舒适
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
    xxl: '48px',
  },
  
  // 🔤 圆角 - 更圆润
  radius: {
    sm: '6px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    full: '9999px',
  },
  
  // 🌟 阴影 - 更轻盈
  shadow: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.03), 0 1px 6px -1px rgba(0, 0, 0, 0.02)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.06), 0 4px 6px -2px rgba(0, 0, 0, 0.03)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 10px 10px -5px rgba(0, 0, 0, 0.02)',
  },
};

// 组件样式 - 年轻化设计
export const componentStyles = {
  // 侧边栏
  sider: {
    background: '#ffffff',
    borderRight: '1px solid #f0f0f0',
    logoArea: 'h-16 flex items-center justify-center border-b border-gray-100',
    menu: 'py-4',
  },
  
  // 顶部栏
  header: {
    background: '#ffffff',
    borderBottom: '1px solid #f0f0f0',
    height: '64px',
  },
  
  // 内容区
  content: {
    background: '#f5f5f5',  // 浅灰背景
    padding: '24px',
    borderRadius: '0',
  },
  
  // 卡片 - 更圆润
  card: {
    background: '#ffffff',
    border: '1px solid #f0f0f0',
    borderRadius: '12px',
    padding: '24px',
    shadow: '0 2px 8px rgba(0,0,0,0.04)',
  },
  
  // 表格 - 更清爽
  table: {
    headerBg: '#fafafa',
    headerText: '#262626',
    rowHover: '#f5f5f5',
    border: '#f0f0f0',
  },
  
  // 按钮 - 更活泼
  button: {
    primary: 'bg-blue-500 hover:bg-blue-600 text-white rounded-lg px-4 py-2 transition-all duration-200 shadow-sm hover:shadow-md',
    secondary: 'bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 rounded-lg px-4 py-2 transition-all duration-200',
  },
  
  // Tab - 更现代
  tab: {
    container: 'flex gap-2 border-b border-gray-200',
    active: 'px-4 py-3 text-blue-600 border-b-2 border-blue-600 font-medium transition-all',
    inactive: 'px-4 py-3 text-gray-600 border-b-2 border-transparent hover:text-blue-600 transition-all',
  },
};

export default designSystem;
