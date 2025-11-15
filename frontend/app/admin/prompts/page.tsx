'use client'

/**
 * Prompt模板管理页面
 * 
 * 借鉴NOFX的Web UI设计，提供简洁的模板编辑界面
 */

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { RefreshCw, Save, FileText, AlertCircle } from 'lucide-react'

interface PromptTemplate {
  name: string
  category: string
  content: string
  file_path: string
  content_length: number
  created_at: string
  updated_at: string
}

export default function PromptsPage() {
  const [templates, setTemplates] = useState<PromptTemplate[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState<PromptTemplate | null>(null)
  const [editedContent, setEditedContent] = useState('')
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  // 加载所有模板
  const loadTemplates = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/v1/prompts/')
      const data = await response.json()
      setTemplates(data.templates || [])
    } catch (error) {
      console.error('加载模板失败:', error)
      showMessage('error', '加载模板失败')
    } finally {
      setLoading(false)
    }
  }

  // 加载模板详情
  const loadTemplateDetail = async (category: string, name: string) => {
    try {
      const response = await fetch(`/api/v1/prompts/${category}/${name}`)
      const data = await response.json()
      setSelectedTemplate(data)
      setEditedContent(data.content)
    } catch (error) {
      console.error('加载模板详情失败:', error)
      showMessage('error', '加载模板详情失败')
    }
  }

  // 保存模板
  const saveTemplate = async () => {
    if (!selectedTemplate) return

    setSaving(true)
    try {
      const response = await fetch(
        `/api/v1/prompts/${selectedTemplate.category}/${selectedTemplate.name}`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ content: editedContent })
        }
      )

      if (response.ok) {
        showMessage('success', '保存成功！模板已更新')
        loadTemplates() // 重新加载列表
        loadTemplateDetail(selectedTemplate.category, selectedTemplate.name) // 刷新详情
      } else {
        showMessage('error', '保存失败')
      }
    } catch (error) {
      console.error('保存模板失败:', error)
      showMessage('error', '保存失败')
    } finally {
      setSaving(false)
    }
  }

  // 热重载
  const reloadTemplates = async (category?: string) => {
    setLoading(true)
    try {
      const url = category 
        ? `/api/v1/prompts/reload?category=${category}`
        : '/api/v1/prompts/reload'
      
      const response = await fetch(url, { method: 'POST' })
      
      if (response.ok) {
        showMessage('success', '热重载成功！')
        loadTemplates()
      } else {
        showMessage('error', '热重载失败')
      }
    } catch (error) {
      console.error('热重载失败:', error)
      showMessage('error', '热重载失败')
    } finally {
      setLoading(false)
    }
  }

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text })
    setTimeout(() => setMessage(null), 3000)
  }

  useEffect(() => {
    loadTemplates()
  }, [])

  // 按类别分组
  const groupedTemplates = templates.reduce((acc, template) => {
    if (!acc[template.category]) {
      acc[template.category] = []
    }
    acc[template.category].push(template)
    return acc
  }, {} as Record<string, PromptTemplate[]>)

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 头部 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Prompt模板管理</h1>
          <p className="text-muted-foreground mt-2">
            借鉴NOFX设计 - 文件化管理、热重载、多策略支持
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => reloadTemplates()}
            disabled={loading}
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            热重载所有
          </Button>
        </div>
      </div>

      {/* 消息提示 */}
      {message && (
        <div className={`p-4 rounded-lg ${
          message.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
        }`}>
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4" />
            {message.text}
          </div>
        </div>
      )}

      {/* 主内容 */}
      <div className="grid grid-cols-12 gap-6">
        {/* 左侧：模板列表 */}
        <div className="col-span-4">
          <Card>
            <CardHeader>
              <CardTitle>模板列表</CardTitle>
              <CardDescription>共 {templates.length} 个模板</CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="decision" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="decision">Decision</TabsTrigger>
                  <TabsTrigger value="debate">Debate</TabsTrigger>
                  <TabsTrigger value="intelligence">Intelligence</TabsTrigger>
                </TabsList>

                {Object.entries(groupedTemplates).map(([category, categoryTemplates]) => (
                  <TabsContent key={category} value={category} className="space-y-2">
                    {categoryTemplates.map((template) => (
                      <div
                        key={`${template.category}-${template.name}`}
                        className={`p-3 rounded-lg border cursor-pointer hover:bg-accent transition-colors ${
                          selectedTemplate?.name === template.name &&
                          selectedTemplate?.category === template.category
                            ? 'bg-accent border-primary'
                            : ''
                        }`}
                        onClick={() => loadTemplateDetail(template.category, template.name)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <FileText className="h-4 w-4" />
                            <span className="font-medium">{template.name}</span>
                          </div>
                          <Badge variant="outline">{template.content_length} 字符</Badge>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">
                          更新: {new Date(template.updated_at).toLocaleString('zh-CN')}
                        </p>
                      </div>
                    ))}
                  </TabsContent>
                ))}
              </Tabs>
            </CardContent>
          </Card>
        </div>

        {/* 右侧：编辑器 */}
        <div className="col-span-8">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>
                    {selectedTemplate ? (
                      <>
                        {selectedTemplate.category} / {selectedTemplate.name}
                      </>
                    ) : (
                      '请选择模板'
                    )}
                  </CardTitle>
                  {selectedTemplate && (
                    <CardDescription className="mt-2">
                      文件路径: {selectedTemplate.file_path}
                    </CardDescription>
                  )}
                </div>
                {selectedTemplate && (
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => reloadTemplates(selectedTemplate.category)}
                    >
                      <RefreshCw className="mr-2 h-4 w-4" />
                      重载此类别
                    </Button>
                    <Button
                      size="sm"
                      onClick={saveTemplate}
                      disabled={saving || editedContent === selectedTemplate.content}
                    >
                      <Save className="mr-2 h-4 w-4" />
                      {saving ? '保存中...' : '保存'}
                    </Button>
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {selectedTemplate ? (
                <div className="space-y-4">
                  <Textarea
                    value={editedContent}
                    onChange={(e) => setEditedContent(e.target.value)}
                    className="font-mono text-sm min-h-[600px]"
                    placeholder="Prompt内容..."
                  />
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>字符数: {editedContent.length}</span>
                    <span>
                      {editedContent !== selectedTemplate.content && (
                        <Badge variant="outline" className="text-yellow-600">
                          未保存
                        </Badge>
                      )}
                    </span>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center h-[600px] text-muted-foreground">
                  <div className="text-center">
                    <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>请从左侧选择一个模板进行编辑</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* 底部说明 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">使用说明</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>✅ <strong>文件化管理</strong>：Prompt存储为.txt文件，支持版本控制</p>
          <p>🔄 <strong>热重载</strong>：修改后自动生效，无需重启服务</p>
          <p>🎯 <strong>多策略</strong>：可创建多个策略模板（default, conservative, aggressive）</p>
          <p>🛡️ <strong>优雅降级</strong>：模板加载失败时自动回退到硬编码版本</p>
          <p>📝 <strong>借鉴NOFX</strong>：完全参考NOFX的成熟设计</p>
        </CardContent>
      </Card>
    </div>
  )
}

