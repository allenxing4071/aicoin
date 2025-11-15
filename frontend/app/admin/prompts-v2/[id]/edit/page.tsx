"use client"

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

export default function PromptEditPage() {
  const params = useParams()
  const router = useRouter()
  const promptId = params.id
  
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

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">智能编辑 Prompt</h1>

      <div className="mb-4 flex gap-2">
        <Button onClick={handleOptimize} disabled={optimizing}>
          {optimizing ? '🤖 优化中...' : '🤖 DeepSeek智能优化'}
        </Button>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        {/* 原始版本 */}
        <Card>
          <CardHeader>
            <CardTitle>原始版本</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              value={originalContent}
              readOnly
              className="h-96 font-mono text-sm"
            />
            <Button 
              className="mt-4 w-full"
              onClick={() => handleSave(originalContent, '保留原始版本')}
              disabled={loading}
            >
              💾 保存原始版本
            </Button>
          </CardContent>
        </Card>

        {/* DeepSeek优化版本 */}
        <Card>
          <CardHeader>
            <CardTitle>DeepSeek优化版本</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              value={currentContent}
              onChange={(e) => setCurrentContent(e.target.value)}
              className="h-96 font-mono text-sm"
              placeholder="点击「DeepSeek智能优化」按钮生成优化版本"
            />
            <div className="mt-4 flex gap-2">
              <Button 
                className="flex-1"
                onClick={() => handleSave(optimizedContent, 'DeepSeek自动优化')}
                disabled={loading || !optimizedContent}
              >
                💾 保存优化版本
              </Button>
              <Button 
                className="flex-1"
                variant="outline"
                onClick={() => handleSave(currentContent, '手动编辑后保存')}
                disabled={loading}
              >
                ✏️ 保存手动编辑版本
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <Button 
        variant="outline"
        onClick={() => router.push('/admin/prompts-v2')}
      >
        ← 返回列表
      </Button>
    </div>
  )
}

