"use client"

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'

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
  const router = useRouter()
  const promptId = params.id
  
  const [metrics, setMetrics] = useState<RiskMetrics | null>(null)
  const [promptName, setPromptName] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      
      // 获取 Prompt 基本信息
      const promptResponse = await fetch(`/api/v1/prompts/v2/${promptId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const promptData = await promptResponse.json()
      setPromptName(promptData.name)
      
      // 获取风险指标
      const metricsResponse = await fetch(`/api/v1/prompts/v2/${promptId}/risk-metrics`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const metricsData = await metricsResponse.json()
      setMetrics(metricsData)
    } catch (error) {
      console.error('获取数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl text-gray-600">加载中...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="bg-gradient-to-r from-blue-50 to-cyan-50 border-2 border-blue-200 rounded-xl p-6">
        <div className="flex justify-between items-center">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="text-3xl">📊</span>
              <h1 className="text-3xl font-bold text-gray-900">Prompt 风险指标仪表盘</h1>
            </div>
            <p className="text-gray-600">Prompt: <span className="font-semibold">{promptName}</span></p>
          </div>
          <button
            onClick={() => router.push('/admin/permissions')}
            className="px-6 py-3 bg-white border-2 border-gray-300 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition-all"
          >
            ← 返回
          </button>
        </div>
      </div>

        {/* 基础指标 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* 总决策次数 */}
        <div className="bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-200 rounded-xl p-6 hover:shadow-xl transition-all">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-900">📈 总决策次数</h3>
            <span className="text-3xl">🎯</span>
          </div>
          <p className="text-5xl font-bold text-purple-600">{metrics?.total_decisions || 0}</p>
          <p className="text-sm text-gray-600 mt-2">累计执行的决策数量</p>
        </div>

        {/* 胜率 */}
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl p-6 hover:shadow-xl transition-all">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-900">🎲 胜率</h3>
            <span className="text-3xl">✅</span>
          </div>
          <p className="text-5xl font-bold text-green-600">
              {((metrics?.win_rate || 0) * 100).toFixed(2)}%
            </p>
          <p className="text-sm text-gray-600 mt-2">成功决策的比例</p>
        </div>

        {/* 总盈亏 */}
        <div className={`bg-gradient-to-br ${(metrics?.total_pnl || 0) >= 0 ? 'from-green-50 to-teal-50 border-green-300' : 'from-red-50 to-orange-50 border-red-300'} border-2 rounded-xl p-6 hover:shadow-xl transition-all`}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-900">💰 总盈亏</h3>
            <span className="text-3xl">{(metrics?.total_pnl || 0) >= 0 ? '📈' : '📉'}</span>
          </div>
          <p className={`text-5xl font-bold ${(metrics?.total_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              ${(metrics?.total_pnl || 0).toFixed(2)}
            </p>
          <p className="text-sm text-gray-600 mt-2">累计盈利或亏损</p>
        </div>
      </div>

      {/* 详细指标 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 风险调整后收益 */}
        <div className="bg-gradient-to-br from-indigo-50 to-purple-50 border-2 border-indigo-200 rounded-xl p-6 hover:shadow-xl transition-all">
          <div className="flex items-center gap-3 mb-6">
            <span className="text-3xl">📊</span>
            <h2 className="text-2xl font-bold text-gray-900">风险调整后收益</h2>
          </div>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center p-4 bg-white rounded-lg border border-indigo-200">
              <div>
                <span className="text-gray-700 font-semibold">夏普比率 (Sharpe Ratio)</span>
                <p className="text-xs text-gray-500 mt-1">衡量每单位风险的超额回报</p>
              </div>
              <span className="text-2xl font-bold text-indigo-600">
                {metrics?.sharpe_ratio?.toFixed(2) || 'N/A'}
              </span>
            </div>
            
            <div className="flex justify-between items-center p-4 bg-white rounded-lg border border-indigo-200">
              <div>
                <span className="text-gray-700 font-semibold">索提诺比率 (Sortino Ratio)</span>
                <p className="text-xs text-gray-500 mt-1">只考虑下行风险的收益指标</p>
              </div>
              <span className="text-2xl font-bold text-indigo-600">
                {metrics?.sortino_ratio?.toFixed(2) || 'N/A'}
              </span>
            </div>
            
            <div className="flex justify-between items-center p-4 bg-white rounded-lg border border-indigo-200">
              <div>
                <span className="text-gray-700 font-semibold">卡玛比率 (Calmar Ratio)</span>
                <p className="text-xs text-gray-500 mt-1">年化收益率与最大回撤的比值</p>
              </div>
              <span className="text-2xl font-bold text-indigo-600">
                {metrics?.calmar_ratio?.toFixed(2) || 'N/A'}
              </span>
            </div>
          </div>
        </div>

        {/* 风险指标 */}
        <div className="bg-gradient-to-br from-red-50 to-orange-50 border-2 border-red-200 rounded-xl p-6 hover:shadow-xl transition-all">
          <div className="flex items-center gap-3 mb-6">
            <span className="text-3xl">⚠️</span>
            <h2 className="text-2xl font-bold text-gray-900">风险指标</h2>
          </div>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center p-4 bg-white rounded-lg border border-red-200">
              <div>
                <span className="text-gray-700 font-semibold">最大回撤 (Max Drawdown)</span>
                <p className="text-xs text-gray-500 mt-1">从峰值到谷底的最大跌幅</p>
              </div>
              <span className="text-2xl font-bold text-red-600">
                  {((metrics?.max_drawdown || 0) * 100).toFixed(2)}%
                </span>
              </div>
            
            <div className="flex justify-between items-center p-4 bg-white rounded-lg border border-red-200">
              <div>
                <span className="text-gray-700 font-semibold">VaR(95%)</span>
                <p className="text-xs text-gray-500 mt-1">95%置信度下的最大损失</p>
              </div>
              <span className="text-2xl font-bold text-red-600">
                {metrics?.var_95?.toFixed(2) || 'N/A'}
              </span>
            </div>
            
            <div className="flex justify-between items-center p-4 bg-white rounded-lg border border-red-200">
              <div>
                <span className="text-gray-700 font-semibold">CVaR(95%)</span>
                <p className="text-xs text-gray-500 mt-1">超过VaR时的平均损失</p>
              </div>
              <span className="text-2xl font-bold text-red-600">
                {metrics?.cvar_95?.toFixed(2) || 'N/A'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 说明信息 */}
      <div className="bg-gradient-to-r from-yellow-50 to-amber-50 border-2 border-yellow-200 rounded-xl p-6">
        <div className="flex items-start gap-3">
          <span className="text-2xl">💡</span>
          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">指标说明</h3>
            <ul className="text-sm text-gray-700 space-y-1">
              <li>• <strong>夏普比率</strong>：通常大于 1 为良好，大于 2 为优秀</li>
              <li>• <strong>索提诺比率</strong>：只关注下行波动，更适合风险厌恶型投资者</li>
              <li>• <strong>卡玛比率</strong>：考虑最大回撤的风险调整收益指标</li>
              <li>• <strong>最大回撤</strong>：越小越好，表示策略的风险控制能力</li>
              <li>• <strong>VaR/CVaR</strong>：衡量极端情况下的潜在损失</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

