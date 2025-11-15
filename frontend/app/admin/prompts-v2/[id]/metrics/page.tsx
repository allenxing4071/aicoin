"use client"

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

interface RiskMetrics {
  total_decisions: number
  win_rate: number
  total_pnl: number
  sharpe_ratio: number | null
  sortino_ratio: number | null
  max_drawdown: number | null
  calmar_ratio: number | null
  var_95: number | null
  cvar_95: number | null
}

export default function PromptMetricsPage() {
  const params = useParams()
  const promptId = params.id
  
  const [metrics, setMetrics] = useState<RiskMetrics | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchMetrics()
  }, [])

  const fetchMetrics = async () => {
    try {
      const response = await fetch(`/api/v1/prompts/v2/${promptId}/risk-metrics`)
      const data = await response.json()
      setMetrics(data)
    } catch (error) {
      console.error('获取风险指标失败:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="p-6">加载中...</div>

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Prompt 风险指标仪表盘</h1>

      <div className="grid grid-cols-3 gap-4 mb-6">
        {/* 基础指标 */}
        <Card>
          <CardHeader>
            <CardTitle>总决策次数</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold">{metrics?.total_decisions || 0}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>胜率</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold">
              {((metrics?.win_rate || 0) * 100).toFixed(2)}%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>总盈亏</CardTitle>
          </CardHeader>
          <CardContent>
            <p className={`text-4xl font-bold ${(metrics?.total_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              ${(metrics?.total_pnl || 0).toFixed(2)}
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* 风险调整后收益 */}
        <Card>
          <CardHeader>
            <CardTitle>风险调整后收益</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>夏普比率:</span>
                <span className="font-bold">{metrics?.sharpe_ratio?.toFixed(2) || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span>索提诺比率:</span>
                <span className="font-bold">{metrics?.sortino_ratio?.toFixed(2) || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span>卡玛比率:</span>
                <span className="font-bold">{metrics?.calmar_ratio?.toFixed(2) || 'N/A'}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 风险指标 */}
        <Card>
          <CardHeader>
            <CardTitle>风险指标</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>最大回撤:</span>
                <span className="font-bold text-red-600">
                  {((metrics?.max_drawdown || 0) * 100).toFixed(2)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span>VaR(95%):</span>
                <span className="font-bold">{metrics?.var_95?.toFixed(2) || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span>CVaR(95%):</span>
                <span className="font-bold">{metrics?.cvar_95?.toFixed(2) || 'N/A'}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

