"use client";

/**
 * 绩效分析面板
 * 
 * 功能:
 * - 收益曲线
 * - 胜率统计
 * - 夏普比率
 * - 策略对比
 */

export default function PerformanceAnalysisPanel() {
  return (
    <div className="space-y-6">
      {/* 开发中提示 */}
      <div className="bg-white/50 backdrop-blur-sm rounded-lg border border-gray-200 p-12 text-center">
        <div className="text-4xl mb-4">📉</div>
        <h3 className="text-lg font-medium text-pink-900 mb-2">绩效分析模块</h3>
        <p className="text-sm text-pink-700 mb-6">
          该模块正在开发中...<br/>
          将提供收益分析、胜率统计、风险收益比
        </p>
        
        {/* 预览功能列表 */}
        <div className="max-w-2xl mx-auto mt-8 grid grid-cols-2 gap-4 text-left">
          <div className="bg-gray-700/30 rounded-lg p-4">
            <div className="text-purple-400 mb-2">📈 收益曲线</div>
            <div className="text-xs text-pink-700">累计收益和净值走势</div>
          </div>
          <div className="bg-gray-700/30 rounded-lg p-4">
            <div className="text-purple-400 mb-2">🎯 胜率统计</div>
            <div className="text-xs text-pink-700">盈利交易占比和平均盈亏</div>
          </div>
          <div className="bg-gray-700/30 rounded-lg p-4">
            <div className="text-purple-400 mb-2">📊 夏普比率</div>
            <div className="text-xs text-pink-700">风险调整后的收益评估</div>
          </div>
          <div className="bg-gray-700/30 rounded-lg p-4">
            <div className="text-purple-400 mb-2">🔄 策略对比</div>
            <div className="text-xs text-pink-700">多策略绩效横向对比</div>
          </div>
        </div>
      </div>
    </div>
  );
}

