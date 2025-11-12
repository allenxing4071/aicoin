'use client';

import { useState } from 'react';
import PageHeader from '../../components/common/PageHeader';

export default function ApiDocsPage() {
  // 使用生产环境的API地址
  const API_BASE_URL = 'https://jifenpay.cc';

  const openSwagger = () => {
    window.open(`${API_BASE_URL}/docs`, '_blank', 'noopener,noreferrer');
  };

  const openRedoc = () => {
    window.open(`${API_BASE_URL}/redoc`, '_blank', 'noopener,noreferrer');
  };

  return (
    <div className="p-6">
      <PageHeader
        icon="📚"
        title="API文档"
        description="查看完整的API接口文档和在线测试"
        color="blue"
      />

      {/* 文档类型选择 */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={openSwagger}
          className="px-6 py-3 rounded-xl font-medium transition-all bg-blue-500 hover:bg-blue-600 text-white shadow-lg"
        >
          📖 打开 Swagger UI
        </button>
        <button
          onClick={openRedoc}
          className="px-6 py-3 rounded-xl font-medium transition-all bg-blue-500 hover:bg-blue-600 text-white shadow-lg"
        >
          📄 打开 ReDoc
        </button>
      </div>

      {/* 文档信息卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white p-4 rounded-xl border border-gray-200">
          <div className="text-sm text-gray-600 mb-1">API版本</div>
          <div className="text-xl font-bold text-blue-600">v3.2.0</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-gray-200">
          <div className="text-sm text-gray-600 mb-1">接口协议</div>
          <div className="text-xl font-bold text-green-600">REST API</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-gray-200">
          <div className="text-sm text-gray-600 mb-1">认证方式</div>
          <div className="text-xl font-bold text-purple-600">Token</div>
        </div>
      </div>

      {/* 安全说明 */}
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-300 p-6 mb-4">
        <h3 className="text-lg font-bold text-green-900 mb-3">🔒 安全保护</h3>
        <div className="space-y-2 text-sm text-green-800">
          <div className="flex items-start gap-2">
            <span className="text-green-600">✅</span>
            <div>
              <strong>权限控制：</strong>只有登录的管理员才能访问API文档
            </div>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-green-600">✅</span>
            <div>
              <strong>自动认证：</strong>使用您当前的登录凭证，无需额外输入Token
            </div>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-green-600">✅</span>
            <div>
              <strong>安全隔离：</strong>未登录用户无法查看任何API信息
            </div>
          </div>
        </div>
      </div>

      {/* 文档说明 */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200 p-6 mb-6">
        <h3 className="text-lg font-bold text-blue-900 mb-4">📌 使用说明</h3>
        <ul className="text-sm text-blue-800 space-y-2">
          <li>• <strong>Swagger UI</strong>: 提供交互式API测试，可以直接在浏览器中测试接口</li>
          <li>• <strong>ReDoc</strong>: 提供更清晰的文档阅读体验，适合查看接口详情</li>
          <li>• 点击上方按钮将在新标签页中打开文档（需要保持登录状态）</li>
          <li>• 测试接口时需要在请求头中携带 <code className="bg-blue-100 px-2 py-0.5 rounded">Authorization: Bearer &lt;token&gt;</code></li>
        </ul>
      </div>

      {/* 快速链接 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white p-6 rounded-xl border border-gray-200 hover:shadow-lg transition-shadow">
          <h3 className="text-lg font-bold text-gray-900 mb-3">📖 Swagger UI</h3>
          <p className="text-sm text-gray-600 mb-4">
            交互式API文档，支持在线测试所有接口。适合开发人员进行API调试和测试。
          </p>
          <div className="space-y-2 text-sm text-gray-700 mb-4">
            <div>✅ 在线测试接口</div>
            <div>✅ 查看请求/响应示例</div>
            <div>✅ 支持Token认证</div>
          </div>
          <button
            onClick={openSwagger}
            className="w-full px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors"
          >
            打开 Swagger UI →
          </button>
        </div>

        <div className="bg-white p-6 rounded-xl border border-gray-200 hover:shadow-lg transition-shadow">
          <h3 className="text-lg font-bold text-gray-900 mb-3">📄 ReDoc</h3>
          <p className="text-sm text-gray-600 mb-4">
            清晰美观的API文档，提供更好的阅读体验。适合查看完整的接口说明和参数定义。
          </p>
          <div className="space-y-2 text-sm text-gray-700 mb-4">
            <div>✅ 清晰的文档结构</div>
            <div>✅ 详细的参数说明</div>
            <div>✅ 响应模型展示</div>
          </div>
          <button
            onClick={openRedoc}
            className="w-full px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors"
          >
            打开 ReDoc →
          </button>
        </div>
      </div>

      {/* 直接链接 */}
      <div className="mt-6 bg-gray-50 p-4 rounded-xl border border-gray-200">
        <h3 className="text-sm font-bold text-gray-700 mb-2">🔗 直接访问链接</h3>
        <div className="space-y-2 text-sm">
          <div className="flex items-center gap-2">
            <span className="text-gray-600">Swagger UI:</span>
            <a 
              href={`${API_BASE_URL}/docs`} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 underline"
            >
              {API_BASE_URL}/docs
            </a>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-gray-600">ReDoc:</span>
            <a 
              href={`${API_BASE_URL}/redoc`} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 underline"
            >
              {API_BASE_URL}/redoc
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

