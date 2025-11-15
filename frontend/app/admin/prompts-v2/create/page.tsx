'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function CreatePromptPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: '',
    category: 'decision',
    permission_level: '',
    content: ''
  });
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [showAIPanel, setShowAIPanel] = useState(false);
  const [aiRequirement, setAiRequirement] = useState('');

  const handleAIGenerate = async () => {
    if (!aiRequirement.trim()) {
      alert('请输入需求描述');
      return;
    }

    if (!formData.name || !formData.category) {
      alert('请先填写模板名称和类别');
      return;
    }

    try {
      setGenerating(true);
      const token = localStorage.getItem('admin_token');
      
      const response = await fetch('/api/v1/prompts/v2/generate', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: formData.name,
          category: formData.category,
          permission_level: formData.permission_level || null,
          requirement: aiRequirement
        })
      });

      if (!response.ok) {
        throw new Error('AI 生成失败');
      }

      const data = await response.json();
      setFormData({ ...formData, content: data.generated_content });
      setShowAIPanel(false);
      alert('✅ AI 生成成功！请检查并修改内容');
    } catch (error: any) {
      console.error('❌ AI 生成失败:', error);
      alert(`❌ AI 生成失败: ${error.message}`);
    } finally {
      setGenerating(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name || !formData.content) {
      alert('请填写名称和内容');
      return;
    }

    try {
      setLoading(true);
      
      console.log('📤 提交数据:', {
        name: formData.name,
        category: formData.category,
        permission_level: formData.permission_level || null,
        content: formData.content
      });
      
      const token = localStorage.getItem('admin_token');
      const response = await fetch('/api/v1/prompts/v2/', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: formData.name,
          category: formData.category,
          permission_level: formData.permission_level || null,
          content: formData.content
        })
      });

      console.log('📥 响应状态:', response.status);

      if (!response.ok) {
        let errorMsg = '创建失败';
        try {
          const error = await response.json();
          console.error('❌ 错误详情:', error);
          errorMsg = error.detail || JSON.stringify(error);
        } catch (e) {
          const text = await response.text();
          console.error('❌ 错误文本:', text);
          errorMsg = text || `HTTP ${response.status}`;
        }
        throw new Error(errorMsg);
      }

      const result = await response.json();
      console.log('✅ 创建成功:', result);
      alert('✅ Prompt 创建成功！');
      router.push('/admin/permissions');
    } catch (error: any) {
      console.error('❌ 创建失败:', error);
      alert(`❌ 创建失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border-2 border-indigo-200 rounded-xl p-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">➕ 创建 Prompt 模板</h1>
            <p className="text-gray-600">创建新的 AI 决策、辩论或情报系统的 Prompt 模板</p>
          </div>
          <button
            onClick={() => router.push('/admin/permissions')}
            className="px-6 py-3 bg-white border-2 border-gray-300 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition-all"
          >
            ← 返回
          </button>
        </div>
      </div>

      {/* 创建表单 */}
      <form onSubmit={handleSubmit} className="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-sm space-y-6">
        {/* 基本信息 */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900 border-b pb-2">基本信息</h2>
          
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              📝 模板名称 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="例如: bear_analyst, bull_analyst"
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl font-medium text-gray-900 focus:outline-none focus:border-indigo-500 transition-colors"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                📂 类别 <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl font-medium text-gray-900 focus:outline-none focus:border-indigo-500 transition-colors"
              >
                <option value="decision">🎯 决策 (Decision)</option>
                <option value="debate">⚔️ 辩论 (Debate)</option>
                <option value="intelligence">🔍 情报 (Intelligence)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                🔑 权限等级 (可选)
              </label>
              <select
                value={formData.permission_level}
                onChange={(e) => setFormData({ ...formData, permission_level: e.target.value })}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl font-medium text-gray-900 focus:outline-none focus:border-indigo-500 transition-colors"
              >
                <option value="">通用 (所有等级)</option>
                <option value="L0">L0 - 极度保守</option>
                <option value="L1">L1 - 保守稳健</option>
                <option value="L2">L2 - 平衡型</option>
                <option value="L3">L3 - 积极进取</option>
                <option value="L4">L4 - 高风险</option>
                <option value="L5">L5 - 极限激进</option>
              </select>
            </div>
          </div>
        </div>

        {/* Prompt 内容 */}
        <div className="space-y-4">
          <div className="flex justify-between items-center border-b pb-2">
            <h2 className="text-xl font-bold text-gray-900">Prompt 内容</h2>
            <button
              type="button"
              onClick={() => setShowAIPanel(!showAIPanel)}
              className="px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl font-semibold hover:from-purple-600 hover:to-pink-600 transition-all transform hover:scale-105 shadow-lg"
            >
              {showAIPanel ? '✏️ 手动编辑' : '🤖 DeepSeek智能生成'}
            </button>
          </div>

          {/* AI 生成面板 */}
          {showAIPanel && (
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-200 rounded-xl p-6 space-y-4">
              <div className="flex items-center gap-3 mb-4">
                <span className="text-3xl">🤖</span>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">DeepSeek 智能生成</h3>
                  <p className="text-sm text-gray-600">描述你的需求，AI 将自动生成 Prompt 模板</p>
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2">
                  💬 需求描述
                </label>
                <textarea
                  value={aiRequirement}
                  onChange={(e) => setAiRequirement(e.target.value)}
                  placeholder="例如：我需要一个保守型的决策 Prompt，重点关注风险控制，避免高风险交易，适合 L0-L1 权限等级..."
                  rows={6}
                  className="w-full px-4 py-3 border-2 border-purple-300 rounded-xl text-sm text-gray-900 focus:outline-none focus:border-purple-500 transition-colors"
                />
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={handleAIGenerate}
                  disabled={generating}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-semibold hover:from-purple-700 hover:to-pink-700 transition-all transform hover:scale-105 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {generating ? '🤖 生成中...' : '✨ 立即生成'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowAIPanel(false);
                    setAiRequirement('');
                  }}
                  className="px-6 py-3 bg-white border-2 border-purple-300 text-purple-700 rounded-xl font-semibold hover:bg-purple-50 transition-all"
                >
                  取消
                </button>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-xs text-yellow-800">
                  <strong>💡 提示：</strong>请先填写"模板名称"和"类别"，然后描述你的需求。AI 将根据你的描述生成专业的 Prompt 模板。
                </p>
              </div>
            </div>
          )}
          
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              📄 模板内容 <span className="text-red-500">*</span>
            </label>
            <textarea
              value={formData.content}
              onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              placeholder="输入 Prompt 模板内容，或使用 DeepSeek 智能生成..."
              rows={20}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl font-mono text-sm text-gray-900 focus:outline-none focus:border-indigo-500 transition-colors"
              required
            />
            <p className="text-sm text-gray-500 mt-2">
              💡 提示：可以使用变量如 {`{{ market_data }}`}, {`{{ intelligence_report }}`} 等
            </p>
          </div>
        </div>

        {/* 操作按钮 */}
        <div className="flex gap-4 pt-4 border-t">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 px-6 py-3 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition-all transform hover:scale-105 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? '⏳ 创建中...' : '✅ 创建 Prompt'}
          </button>
          <button
            type="button"
            onClick={() => router.push('/admin/permissions')}
            className="px-6 py-3 bg-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-300 transition-all"
          >
            取消
          </button>
        </div>
      </form>
    </div>
  );
}

