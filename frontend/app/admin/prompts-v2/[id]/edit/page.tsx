"use client"

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'

export default function PromptEditPage() {
  const params = useParams()
  const router = useRouter()
  const promptId = params.id
  
  const [promptInfo, setPromptInfo] = useState<any>(null)
  const [originalContent, setOriginalContent] = useState('')
  const [optimizedContent, setOptimizedContent] = useState('')
  const [currentContent, setCurrentContent] = useState('')
  const [loading, setLoading] = useState(false)
  const [optimizing, setOptimizing] = useState(false)

  useEffect(() => {
    fetchPrompt()
  }, [])

  const fetchPrompt = async () => {
    try {
      const response = await fetch(`/api/v1/prompts/v2/${promptId}`)
      const data = await response.json()
      setPromptInfo(data)
      setOriginalContent(data.content)
      setCurrentContent(data.content)
    } catch (error) {
      console.error('获取Prompt失败:', error)
    }
  }

  const handleOptimize = async () => {
    try {
      setOptimizing(true)
      const response = await fetch('/api/v1/prompts/v2/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          template_id: promptId,
          optimization_goal: '提高决策准确率，降低误判风险'
        })
      })
      const data = await response.json()
      setOptimizedContent(data.optimized_content)
      setCurrentContent(data.optimized_content)
    } catch (error) {
      alert('❌ DeepSeek优化失败')
    } finally {
      setOptimizing(false)
    }
  }

  const handleSave = async (content: string, summary: string) => {
    try {
      setLoading(true)
      await fetch(`/api/v1/prompts/v2/${promptId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content,
          change_summary: summary
        })
      })
      alert('✅ 保存成功')
      router.push('/admin/prompts-v2')
    } catch (error) {
      alert('❌ 保存失败')
    } finally {
      setLoading(false)
    }
  }

  // 获取类别样式
  const getCategoryStyle = (category: string) => {
    const styles = {
      decision: { icon: '🎯', color: 'from-blue-50 to-cyan-50', border: 'border-blue-200' },
      debate: { icon: '⚔️', color: 'from-purple-50 to-pink-50', border: 'border-purple-200' },
      intelligence: { icon: '🔍', color: 'from-green-50 to-emerald-50', border: 'border-green-200' }
    }
    return styles[category as keyof typeof styles] || styles.decision
  }

  const categoryStyle = promptInfo ? getCategoryStyle(promptInfo.category) : getCategoryStyle('decision')

  return (
    <div className="space-y-6">
      {/* 页面标题和操作区 */}
      <div className={`bg-gradient-to-r ${categoryStyle.color} border-2 ${categoryStyle.border} rounded-xl p-6`}>
        <div className="flex justify-between items-center">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="text-3xl">{categoryStyle.icon}</span>
              <h1 className="text-3xl font-bold text-gray-900">智能编辑 Prompt</h1>
              {promptInfo && (
                <span className="px-3 py-1 rounded-full text-sm font-semibold bg-white/80 text-gray-700">
                  {promptInfo.name}
                </span>
              )}
            </div>
            <p className="text-gray-600">使用 DeepSeek 智能优化 Prompt 模板，提升决策准确率</p>
          </div>
          <button
            onClick={handleOptimize}
            disabled={optimizing}
            className="px-6 py-3 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition-all transform hover:scale-105 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {optimizing ? '🤖 优化中...' : '🤖 DeepSeek智能优化'}
          </button>
        </div>
      </div>

      {/* 双栏对比编辑区 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 原始版本 */}
        <div className="bg-gradient-to-br from-gray-50 to-slate-50 border-2 border-gray-200 rounded-xl p-6 hover:shadow-xl transition-all">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">📄 原始版本</h2>
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-gray-200 text-gray-700">
              只读
            </span>
          </div>
          
          <textarea
            value={originalContent}
            readOnly
            className="w-full h-96 px-4 py-3 border-2 border-gray-300 rounded-xl font-mono text-sm text-gray-700 bg-white/50 focus:outline-none resize-none"
          />
          
          <button
            onClick={() => handleSave(originalContent, '保留原始版本')}
            disabled={loading}
            className="mt-4 w-full px-6 py-3 bg-white border-2 border-gray-300 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            💾 保存原始版本
          </button>
        </div>

        {/* DeepSeek优化版本 */}
        <div className="bg-gradient-to-br from-indigo-50 to-purple-50 border-2 border-indigo-200 rounded-xl p-6 hover:shadow-xl transition-all">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">✨ DeepSeek优化版本</h2>
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-indigo-200 text-indigo-800">
              可编辑
            </span>
          </div>
          
          <textarea
            value={currentContent}
            onChange={(e) => setCurrentContent(e.target.value)}
            placeholder="点击「DeepSeek智能优化」按钮生成优化版本，或手动编辑..."
            className="w-full h-96 px-4 py-3 border-2 border-indigo-300 rounded-xl font-mono text-sm text-gray-900 bg-white focus:outline-none focus:border-indigo-500 transition-colors resize-none"
          />
          
          <div className="mt-4 grid grid-cols-2 gap-3">
            <button
              onClick={() => handleSave(optimizedContent, 'DeepSeek自动优化')}
              disabled={loading || !optimizedContent}
              className="px-6 py-3 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition-all transform hover:scale-105 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              💾 保存优化版本
            </button>
            <button
              onClick={() => handleSave(currentContent, '手动编辑后保存')}
              disabled={loading}
              className="px-6 py-3 bg-white border-2 border-indigo-300 text-indigo-700 rounded-xl font-semibold hover:bg-indigo-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              ✏️ 保存手动编辑
            </button>
          </div>
        </div>
      </div>

      {/* 底部操作栏 */}
      <div className="flex justify-between items-center bg-white border-2 border-gray-200 rounded-xl p-4">
        <button
          onClick={() => router.push('/admin/permissions')}
          className="px-6 py-3 bg-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-300 transition-all"
        >
          ← 返回权限管理
        </button>
        
        {promptInfo && (
          <div className="text-sm text-gray-600">
            <span className="font-semibold">最后更新：</span>
            {new Date(promptInfo.updated_at).toLocaleString('zh-CN')}
          </div>
        )}
      </div>
    </div>
  )
}

