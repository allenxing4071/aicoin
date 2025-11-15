"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

interface PromptTemplate {
  id: number
  name: string
  category: string
  permission_level: string | null
  content: string
  version: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export default function PromptsV2Page() {
  const router = useRouter()
  const [prompts, setPrompts] = useState<PromptTemplate[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedLevel, setSelectedLevel] = useState<string>('all')

  useEffect(() => {
    fetchPrompts()
  }, [selectedCategory, selectedLevel])

  const fetchPrompts = async () => {
    try {
      setLoading(true)
      let url = '/api/v1/prompts/v2/'
      const params = new URLSearchParams()
      
      if (selectedCategory !== 'all') params.append('category', selectedCategory)
      if (selectedLevel !== 'all') params.append('permission_level', selectedLevel)
      
      if (params.toString()) url += `?${params.toString()}`
      
      const response = await fetch(url)
      const data = await response.json()
      setPrompts(data)
    } catch (error) {
      console.error('获取Prompt列表失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleReload = async () => {
    try {
      await fetch('/api/v1/prompts/v2/reload', { method: 'POST' })
      alert('✅ Prompt已重载')
      fetchPrompts()
    } catch (error) {
      alert('❌ 重载失败')
    }
  }

  // 获取类别图标和颜色
  const getCategoryStyle = (category: string) => {
    const styles = {
      decision: { icon: '🎯', color: 'from-blue-50 to-cyan-50', border: 'border-blue-200', badge: 'bg-blue-100 text-blue-800' },
      debate: { icon: '⚔️', color: 'from-purple-50 to-pink-50', border: 'border-purple-200', badge: 'bg-purple-100 text-purple-800' },
      intelligence: { icon: '🔍', color: 'from-green-50 to-emerald-50', border: 'border-green-200', badge: 'bg-green-100 text-green-800' }
    }
    return styles[category as keyof typeof styles] || styles.decision
  }

  // 获取权限等级颜色
  const getLevelColor = (level: string) => {
    const colors = {
      L0: 'bg-gray-100 text-gray-800',
      L1: 'bg-blue-100 text-blue-800',
      L2: 'bg-green-100 text-green-800',
      L3: 'bg-yellow-100 text-yellow-800',
      L4: 'bg-orange-100 text-orange-800',
      L5: 'bg-red-100 text-red-800'
    }
    return colors[level as keyof typeof colors] || 'bg-gray-100 text-gray-800'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">加载中...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 页面标题和操作区 */}
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border-2 border-indigo-200 rounded-xl p-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">📝 Prompt模板管理 v2</h1>
            <p className="text-gray-600">管理AI决策、辩论和情报系统的Prompt模板</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleReload}
              className="px-6 py-3 bg-white border-2 border-indigo-300 text-indigo-700 rounded-xl font-semibold hover:bg-indigo-50 transition-all transform hover:scale-105 shadow-sm"
            >
              🔄 热重载
            </button>
            <button
              onClick={() => router.push('/admin/prompts-v2/create')}
              className="px-6 py-3 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition-all transform hover:scale-105 shadow-lg"
            >
              ➕ 创建Prompt
            </button>
          </div>
        </div>
      </div>

      {/* 筛选器 */}
      <div className="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-sm">
        <div className="flex gap-6">
          <div className="flex-1">
            <label className="block text-sm font-semibold text-gray-900 mb-2">📂 类别筛选</label>
            <select 
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl font-medium text-gray-900 focus:outline-none focus:border-indigo-500 transition-colors"
            >
              <option value="all">全部类别</option>
              <option value="decision">🎯 决策</option>
              <option value="debate">⚔️ 辩论</option>
              <option value="intelligence">🔍 情报</option>
            </select>
          </div>
          
          <div className="flex-1">
            <label className="block text-sm font-semibold text-gray-900 mb-2">🔑 权限等级</label>
            <select 
              value={selectedLevel}
              onChange={(e) => setSelectedLevel(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl font-medium text-gray-900 focus:outline-none focus:border-indigo-500 transition-colors"
            >
              <option value="all">全部等级</option>
              <option value="L0">L0 - 极度保守</option>
              <option value="L1">L1 - 保守稳健</option>
              <option value="L2">L2 - 平衡型</option>
              <option value="L3">L3 - 积极进取</option>
              <option value="L4">L4 - 高风险</option>
              <option value="L5">L5 - 极限激进</option>
            </select>
          </div>
        </div>
        
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            共找到 <span className="font-bold text-indigo-600">{prompts.length}</span> 个Prompt模板
          </p>
        </div>
      </div>

      {/* Prompt列表 */}
      {prompts.length === 0 ? (
        <div className="bg-white border-2 border-gray-200 rounded-xl p-12 text-center">
          <div className="text-6xl mb-4">📭</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">暂无Prompt模板</h3>
          <p className="text-gray-600">点击上方"创建Prompt"按钮添加新模板</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {prompts.map((prompt) => {
            const categoryStyle = getCategoryStyle(prompt.category)
            return (
              <div 
                key={prompt.id} 
                className={`bg-gradient-to-r ${categoryStyle.color} border-2 ${categoryStyle.border} rounded-xl p-6 hover:shadow-xl transition-all transform hover:scale-[1.01]`}
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-2xl">{categoryStyle.icon}</span>
                      <h3 className="text-xl font-bold text-gray-900">{prompt.name}</h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${categoryStyle.badge}`}>
                        {prompt.category}
                      </span>
                      {prompt.permission_level && (
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getLevelColor(prompt.permission_level)}`}>
                          {prompt.permission_level}
                        </span>
                      )}
                      <span className="px-3 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-800">
                        v{prompt.version}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">
                      更新时间: {new Date(prompt.updated_at).toLocaleString('zh-CN')}
                    </p>
                  </div>
                  
                  <div className="flex gap-2">
                    <button 
                      onClick={() => router.push(`/admin/prompts-v2/${prompt.id}/edit`)}
                      className="px-4 py-2 bg-white border-2 border-indigo-300 text-indigo-700 rounded-lg font-semibold hover:bg-indigo-50 transition-all text-sm"
                    >
                      ✏️ 编辑
                    </button>
                    <button 
                      onClick={() => router.push(`/admin/prompts-v2/${prompt.id}/versions`)}
                      className="px-4 py-2 bg-white border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-all text-sm"
                    >
                      📚 版本
                    </button>
                    <button 
                      onClick={() => router.push(`/admin/prompts-v2/${prompt.id}/metrics`)}
                      className="px-4 py-2 bg-white border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-all text-sm"
                    >
                      📊 指标
                    </button>
                  </div>
                </div>
                
                <div className="bg-white/80 backdrop-blur-sm border border-gray-200 rounded-lg p-4">
                  <pre className="text-sm text-gray-700 font-mono whitespace-pre-wrap max-h-40 overflow-y-auto">
{prompt.content.substring(0, 300)}{prompt.content.length > 300 && '...'}
                  </pre>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

