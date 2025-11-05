/**
 * 管理后台统一样式配置
 * 确保所有页面使用一致的白色主题
 */

export const adminStyles = {
  // 页面容器
  page: "space-y-6",
  
  // 页头标题
  pageTitle: "text-2xl font-semibold text-gray-900 mb-2",
  pageSubtitle: "text-gray-600",
  
  // Tab切换
  tabContainer: "flex gap-2 border-b border-gray-200",
  tab: "px-4 py-3 font-medium text-sm transition-colors border-b-2",
  tabActive: "text-blue-600 border-blue-600",
  tabInactive: "text-gray-600 border-transparent hover:text-blue-600",
  
  // 卡片
  card: "bg-white rounded-lg shadow-sm border border-gray-200 p-6",
  cardTitle: "text-lg font-semibold text-gray-900 mb-4",
  
  // 按钮
  btnPrimary: "px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors",
  btnSecondary: "px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors",
  
  // 文字颜色
  textPrimary: "text-gray-900",
  textSecondary: "text-gray-600",
  textMuted: "text-gray-500",
  
  // 状态颜色
  statusSuccess: "text-green-600 bg-green-50",
  statusWarning: "text-yellow-600 bg-yellow-50",
  statusError: "text-red-600 bg-red-50",
  statusInfo: "text-blue-600 bg-blue-50",
};
