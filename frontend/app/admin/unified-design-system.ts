/**
 * 统一设计系统 - 基于AI工作日志的风格
 * 
 * 设计原则：
 * 1. 渐变背景卡片
 * 2. 圆角阴影
 * 3. 柔和的色彩
 * 4. 统一的间距
 * 5. 清晰的层次结构
 */

export const unifiedDesignSystem = {
  // 页面容器
  page: {
    container: "space-y-6",
    background: "#f8f9fa",
  },

  // 页头样式（带渐变背景）
  pageHeader: {
    // 不同颜色主题的页头
    pink: "bg-gradient-to-r from-pink-50 to-pink-100 rounded-xl p-6 border border-pink-200 shadow-sm",
    purple: "bg-gradient-to-r from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200 shadow-sm",
    blue: "bg-gradient-to-r from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200 shadow-sm",
    green: "bg-gradient-to-r from-green-50 to-green-100 rounded-xl p-6 border border-green-200 shadow-sm",
    orange: "bg-gradient-to-r from-orange-50 to-orange-100 rounded-xl p-6 border border-orange-200 shadow-sm",
    yellow: "bg-gradient-to-r from-yellow-50 to-yellow-100 rounded-xl p-6 border border-yellow-200 shadow-sm",
    red: "bg-gradient-to-r from-red-50 to-red-100 rounded-xl p-6 border border-red-200 shadow-sm",
    indigo: "bg-gradient-to-r from-indigo-50 to-indigo-100 rounded-xl p-6 border border-indigo-200 shadow-sm",
    
    // 页头内容布局
    content: "flex items-center justify-between",
    titleSection: "flex items-center gap-4",
    icon: "text-4xl",
    titleWrapper: "",
    title: "text-2xl font-bold text-gray-900",
    description: "text-sm text-gray-600 mt-1",
  },

  // 统计卡片样式（方形卡片 - 图1样式）
  statCard: {
    container: "rounded-lg p-4 border",
    // 不同颜色的背景和边框（完整方形卡片）
    backgrounds: {
      pink: "bg-pink-50 border-pink-200",
      purple: "bg-purple-50 border-purple-200",
      blue: "bg-blue-50 border-blue-200",
      green: "bg-green-50 border-green-200",
      orange: "bg-orange-50 border-orange-200",
      yellow: "bg-yellow-50 border-yellow-200",
      red: "bg-red-50 border-red-200",
      indigo: "bg-indigo-50 border-indigo-200",
      gray: "bg-gray-50 border-gray-200",
    },
    label: "text-sm text-gray-600",
    value: "text-2xl font-bold",
    // 不同颜色的值
    valueColors: {
      pink: "text-pink-600",
      purple: "text-purple-600",
      blue: "text-blue-600",
      green: "text-green-600",
      orange: "text-orange-600",
      yellow: "text-yellow-600",
      red: "text-red-600",
      indigo: "text-indigo-600",
      gray: "text-gray-600",
    },
    icon: "text-2xl",
  },

  // 内容卡片样式（带渐变背景）
  contentCard: {
    // 不同颜色主题的卡片
    pink: "bg-gradient-to-br from-pink-50 to-purple-50 rounded-xl p-6 shadow-lg border border-pink-200",
    purple: "bg-gradient-to-br from-purple-50 to-indigo-50 rounded-xl p-6 shadow-lg border border-purple-200",
    blue: "bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-6 shadow-lg border border-blue-200",
    green: "bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 shadow-lg border border-green-200",
    orange: "bg-gradient-to-br from-orange-50 to-yellow-50 rounded-xl p-6 shadow-lg border border-orange-200",
    yellow: "bg-gradient-to-br from-yellow-50 to-amber-50 rounded-xl p-6 shadow-lg border border-yellow-200",
    red: "bg-gradient-to-br from-red-50 to-pink-50 rounded-xl p-6 shadow-lg border border-red-200",
    indigo: "bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-6 shadow-lg border border-indigo-200",
    
    // 卡片标题
    titleSection: "flex items-center gap-2 mb-4",
    icon: "text-3xl",
    title: "text-xl font-bold",
    titleColors: {
      pink: "text-pink-900",
      purple: "text-purple-900",
      blue: "text-blue-900",
      green: "text-green-900",
      orange: "text-orange-900",
      yellow: "text-yellow-900",
      red: "text-red-900",
      indigo: "text-indigo-900",
    },
    content: "prose max-w-none",
  },

  // 列表卡片样式（白色背景，带彩色边框）
  listCard: {
    container: "bg-white rounded-xl shadow-sm p-6 border-l-4",
    borderColors: {
      pink: "border-pink-500",
      purple: "border-purple-500",
      blue: "border-blue-500",
      green: "border-green-500",
      orange: "border-orange-500",
      yellow: "border-yellow-500",
      red: "border-red-500",
      indigo: "border-indigo-500",
    },
    header: "flex items-start justify-between mb-4",
    titleSection: "flex items-center gap-3",
    icon: "text-3xl",
    titleWrapper: "",
    title: "text-lg font-semibold text-gray-900",
    subtitle: "text-sm text-gray-500",
  },

  // 按钮样式
  button: {
    // 主要按钮（带渐变）
    primary: {
      pink: "px-6 py-3 bg-gradient-to-r from-pink-500 to-pink-600 text-white rounded-lg font-medium hover:shadow-lg transition-all",
      purple: "px-6 py-3 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-lg font-medium hover:shadow-lg transition-all",
      blue: "px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg font-medium hover:shadow-lg transition-all",
      green: "px-6 py-3 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg font-medium hover:shadow-lg transition-all",
      orange: "px-6 py-3 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-lg font-medium hover:shadow-lg transition-all",
      red: "px-6 py-3 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg font-medium hover:shadow-lg transition-all",
    },
    // 次要按钮
    secondary: "px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium",
    // 小按钮
    small: "px-3 py-1.5 text-sm rounded-lg font-medium transition-colors",
  },

  // 徽章样式
  badge: {
    success: "px-3 py-1 text-xs rounded-full font-medium bg-green-100 text-green-800",
    warning: "px-3 py-1 text-xs rounded-full font-medium bg-yellow-100 text-yellow-800",
    error: "px-3 py-1 text-xs rounded-full font-medium bg-red-100 text-red-800",
    info: "px-3 py-1 text-xs rounded-full font-medium bg-blue-100 text-blue-800",
    default: "px-3 py-1 text-xs rounded-full font-medium bg-gray-100 text-gray-600",
  },

  // 输入框样式
  input: {
    base: "px-4 py-2 border rounded-lg focus:ring-2 focus:border-transparent transition-all font-medium",
    colors: {
      pink: "border-pink-300 focus:ring-pink-500",
      purple: "border-purple-300 focus:ring-purple-500",
      blue: "border-blue-300 focus:ring-blue-500",
      green: "border-green-300 focus:ring-green-500",
      orange: "border-orange-300 focus:ring-orange-500",
    },
  },

  // 日期选择器容器
  dateSelector: {
    container: "bg-white rounded-xl border border-gray-200 p-4 shadow-sm",
    controls: "flex items-center gap-4",
  },

  // 折叠面板
  collapsible: {
    container: "bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden",
    header: "flex items-center justify-between p-6 cursor-pointer hover:bg-gray-50 transition-colors",
    title: "text-lg font-semibold text-gray-900",
    content: "p-6 border-t border-gray-200",
  },

  // 网格布局
  grid: {
    cols1: "grid grid-cols-1 gap-4",
    cols2: "grid grid-cols-1 md:grid-cols-2 gap-4",
    cols3: "grid grid-cols-1 md:grid-cols-3 gap-4",
    cols4: "grid grid-cols-1 md:grid-cols-4 gap-4",
    cols2Lg: "grid grid-cols-1 lg:grid-cols-2 gap-6",
  },

  // 文本样式
  text: {
    primary: "text-gray-900",
    secondary: "text-gray-600",
    muted: "text-gray-500",
    heading1: "text-2xl font-bold text-gray-900",
    heading2: "text-xl font-bold text-gray-900",
    heading3: "text-lg font-semibold text-gray-900",
  },

  // 状态指示器
  status: {
    online: "w-2 h-2 bg-green-500 rounded-full",
    offline: "w-2 h-2 bg-gray-400 rounded-full",
    warning: "w-2 h-2 bg-yellow-500 rounded-full",
    error: "w-2 h-2 bg-red-500 rounded-full",
  },

  // 模态框样式
  modal: {
    overlay: "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4",
    container: "bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl",
    header: "sticky top-0 bg-white border-b border-gray-200 p-6 flex items-start justify-between",
    title: "text-xl font-bold text-gray-900",
    closeButton: "text-gray-500 hover:text-gray-700 text-2xl font-bold",
    content: "p-6",
    footer: "sticky bottom-0 bg-white border-t border-gray-200 p-6 flex items-center justify-end gap-3",
  },
};

// 辅助函数：根据颜色主题获取样式
export function getThemeStyles(color: string = 'blue') {
  return {
    pageHeader: unifiedDesignSystem.pageHeader[color as keyof typeof unifiedDesignSystem.pageHeader] || unifiedDesignSystem.pageHeader.blue,
    contentCard: unifiedDesignSystem.contentCard[color as keyof typeof unifiedDesignSystem.contentCard] || unifiedDesignSystem.contentCard.blue,
    button: unifiedDesignSystem.button.primary[color as keyof typeof unifiedDesignSystem.button.primary] || unifiedDesignSystem.button.primary.blue,
    statCardBackground: unifiedDesignSystem.statCard.backgrounds[color as keyof typeof unifiedDesignSystem.statCard.backgrounds] || unifiedDesignSystem.statCard.backgrounds.blue,
    statCardValue: unifiedDesignSystem.statCard.valueColors[color as keyof typeof unifiedDesignSystem.statCard.valueColors] || unifiedDesignSystem.statCard.valueColors.blue,
    listCardBorder: unifiedDesignSystem.listCard.borderColors[color as keyof typeof unifiedDesignSystem.listCard.borderColors] || unifiedDesignSystem.listCard.borderColors.blue,
    contentCardTitle: unifiedDesignSystem.contentCard.titleColors[color as keyof typeof unifiedDesignSystem.contentCard.titleColors] || unifiedDesignSystem.contentCard.titleColors.blue,
    input: `${unifiedDesignSystem.input.base} ${unifiedDesignSystem.input.colors[color as keyof typeof unifiedDesignSystem.input.colors] || unifiedDesignSystem.input.colors.blue}`,
  };
}

export default unifiedDesignSystem;

