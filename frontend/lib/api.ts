/**
 * API Configuration
 * 统一的API配置文件
 */

// 🎯 统一的 API 配置
// 使用相对路径，通过 Nginx 反向代理访问后端，避免 CORS 问题

/**
 * API Base URL - 使用相对路径通过 Nginx 代理
 * Nginx 配置:
 *   location /api/ { proxy_pass http://localhost:8000/api/; }
 */
export const API_BASE = '/api/v1';

/**
 * API Server URL - 用于非 API 端点（如 /docs, /health）
 * Nginx 配置:
 *   location ~ ^/(docs|redoc|health|openapi\.json)$ { proxy_pass http://localhost:8000; }
 */
export const API_SERVER = '';

// API Endpoints
export const API_ENDPOINTS = {
  // Market Data
  MARKET_TICKERS: `${API_BASE}/market/tickers`,
  MARKET_TICKER: (symbol: string) => `${API_BASE}/market/ticker/${symbol}`,
  
  // Account
  ACCOUNT_INFO: `${API_BASE}/account/info`,
  ACCOUNT_POSITIONS: `${API_BASE}/account/positions`,
  ACCOUNT_HISTORY: `${API_BASE}/account/history`,
  
  // AI
  AI_STATUS: `${API_BASE}/status`,
  AI_DECISIONS: `${API_BASE}/ai/decisions`,
  AI_CHAT: `${API_BASE}/ai/chat`,
  AI_PERMISSION: `${API_BASE}/ai/permission`,
  
  // Admin
  ADMIN_TABLES: `${API_BASE}/admin/tables`,
  ADMIN_STATS: `${API_BASE}/admin/stats`,
  ADMIN_VERIFY: `${API_BASE}/admin/verify`,
  
  // Admin - Database
  ADMIN_DB_STATS: `${API_BASE}/admin/database/stats`,
  ADMIN_DB_TABLES: `${API_BASE}/admin/database/tables`,
  ADMIN_DB_TABLE_DATA: (tableName: string) => `${API_BASE}/admin/database/tables/${tableName}/data`,
  ADMIN_DB_TABLE_SCHEMA: (tableName: string) => `${API_BASE}/admin/database/tables/${tableName}/schema`,
  
  // Admin - Permissions
  ADMIN_PERMISSIONS: `${API_BASE}/admin/permissions/levels`,
  ADMIN_PERMISSION: (level: string) => `${API_BASE}/admin/permissions/levels/${level}`,
  ADMIN_PERMISSION_SET_DEFAULT: (level: string) => `${API_BASE}/admin/permissions/levels/${level}/set-default`,
  ADMIN_PERMISSION_INIT: `${API_BASE}/admin/permissions/levels/init-defaults`,
  
  // Performance
  PERFORMANCE_METRICS: `${API_BASE}/performance/metrics`,
  
  // Constraints
  CONSTRAINTS_STATUS: `${API_BASE}/constraints/status`,
  
  // Health Check
  HEALTH: `${API_BASE.replace('/api/v1', '')}/health`,
};

// Helper function to build URL with query params
export function buildUrl(baseUrl: string, params?: Record<string, any>): string {
  if (!params) return baseUrl;
  
  const queryString = Object.entries(params)
    .filter(([_, value]) => value !== undefined && value !== null)
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join('&');
  
  return queryString ? `${baseUrl}?${queryString}` : baseUrl;
}

// Default axios config
export const axiosConfig = {
  timeout: 10000, // 10 seconds
  headers: {
    'Content-Type': 'application/json',
  },
};

