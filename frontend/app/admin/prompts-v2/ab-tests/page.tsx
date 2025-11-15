"use client"

import { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

interface ABTest {
  id: number
  test_name: string
  status: string
  prompt_a_id: number
  prompt_b_id: number
  a_stats: {
    total_decisions: number
    win_rate: number
    total_pnl: number
  }
  b_stats: {
    total_decisions: number
    win_rate: number
    total_pnl: number
  }
  p_value: number | null
  is_significant: boolean
  winner: string | null
}

export default function ABTestsPage() {
  const [tests, setTests] = useState<ABTest[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // TODO: 实现获取A/B测试列表
    setLoading(false)
  }, [])

  const handleStopTest = async (testId: number) => {
    try {
      await fetch(`/api/prompts/v2/ab-tests/${testId}/stop`, { method: 'POST' })
      alert('✅ 测试已停止')
      // 刷新列表
    } catch (error) {
      alert('❌ 停止失败')
    }
  }

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">A/B 测试管理</h1>
        <Button onClick={() => window.location.href = '/admin/prompts-v2/ab-tests/create'}>
          ➕ 创建测试
        </Button>
      </div>

      <div className="grid gap-4">
        {tests.map((test) => (
          <Card key={test.id}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle>{test.test_name}</CardTitle>
                  <Badge className="mt-2">{test.status}</Badge>
                </div>
                {test.status === 'RUNNING' && (
                  <Button size="sm" onClick={() => handleStopTest(test.id)}>
                    ⏹️ 停止测试
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                {/* A组 */}
                <div className="border p-4 rounded">
                  <h3 className="font-bold mb-2">A组（对照组）</h3>
                  <p>决策次数: {test.a_stats.total_decisions}</p>
                  <p>胜率: {(test.a_stats.win_rate * 100).toFixed(2)}%</p>
                  <p>总盈亏: ${test.a_stats.total_pnl.toFixed(2)}</p>
                </div>

                {/* B组 */}
                <div className="border p-4 rounded">
                  <h3 className="font-bold mb-2">B组（实验组）</h3>
                  <p>决策次数: {test.b_stats.total_decisions}</p>
                  <p>胜率: {(test.b_stats.win_rate * 100).toFixed(2)}%</p>
                  <p>总盈亏: ${test.b_stats.total_pnl.toFixed(2)}</p>
                </div>
              </div>

              {test.is_significant && (
                <div className="mt-4 p-4 bg-green-50 rounded">
                  <p className="font-bold">✅ 统计显著（p={test.p_value?.toFixed(4)}）</p>
                  <p>获胜者: {test.winner}</p>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

