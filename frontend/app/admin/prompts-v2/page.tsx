"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

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

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Prompt模板管理 v2</h1>
        <div className="flex gap-2">
          <Button onClick={handleReload}>🔄 热重载</Button>
          <Button onClick={() => router.push('/admin/prompts-v2/create')}>
            ➕ 创建Prompt
          </Button>
        </div>
      </div>

      {/* 筛选器 */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">类别</label>
              <select 
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="border rounded px-3 py-2"
              >
                <option value="all">全部</option>
                <option value="decision">决策</option>
                <option value="debate">辩论</option>
                <option value="intelligence">情报</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">权限等级</label>
              <select 
                value={selectedLevel}
                onChange={(e) => setSelectedLevel(e.target.value)}
                className="border rounded px-3 py-2"
              >
                <option value="all">全部</option>
                <option value="L0">L0 - 极度保守</option>
                <option value="L1">L1 - 保守稳健</option>
                <option value="L2">L2 - 平衡型</option>
                <option value="L3">L3 - 积极进取</option>
                <option value="L4">L4 - 高风险</option>
                <option value="L5">L5 - 极限激进</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Prompt列表 */}
      {loading ? (
        <div className="text-center py-12">加载中...</div>
      ) : (
        <div className="grid gap-4">
          {prompts.map((prompt) => (
            <Card key={prompt.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      {prompt.name}
                      <Badge variant="outline">{prompt.category}</Badge>
                      {prompt.permission_level && (
                        <Badge>{prompt.permission_level}</Badge>
                      )}
                      <Badge variant="secondary">v{prompt.version}</Badge>
                    </CardTitle>
                    <p className="text-sm text-gray-500 mt-1">
                      更新时间: {new Date(prompt.updated_at).toLocaleString('zh-CN')}
                    </p>
                  </div>
                  
                  <div className="flex gap-2">
                    <Button 
                      size="sm"
                      onClick={() => router.push(`/admin/prompts-v2/${prompt.id}/edit`)}
                    >
                      ✏️ 编辑
                    </Button>
                    <Button 
                      size="sm"
                      variant="outline"
                      onClick={() => router.push(`/admin/prompts-v2/${prompt.id}/versions`)}
                    >
                      📚 版本
                    </Button>
                    <Button 
                      size="sm"
                      variant="outline"
                      onClick={() => router.push(`/admin/prompts-v2/${prompt.id}/metrics`)}
                    >
                      📊 指标
                    </Button>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent>
                <div className="bg-gray-50 p-4 rounded text-sm font-mono whitespace-pre-wrap max-h-40 overflow-y-auto">
                  {prompt.content.substring(0, 300)}
                  {prompt.content.length > 300 && '...'}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

