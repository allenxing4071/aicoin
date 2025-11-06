'use client';

/**
 * AI工作日记 - Qwen情报官与DeepSeek交易官的每日记录
 * 
 * 路径: /admin/trading
 * 
 * 功能:
 * - 展示Qwen情报官的每日情报收集日记
 * - 展示DeepSeek交易官的每日交易日记
 * - 查看历史日记
 * - 展开查看原始数据统计
 */

import { useEffect, useState } from "react";
import PageHeader from '../../components/common/PageHeader';

interface JournalData {
  success: boolean;
  date: string;
  qwen_journal: string;
  deepseek_journal: string;
  data_summary: {
    qwen_reports_count: number;
    news_count: number;
    whale_signals_count: number;
    decisions_count: number;
    trades_count: number;
    total_pnl: number;
    executed_decisions: number;
    rejected_decisions: number;
  };
}

export default function AIJournalPage() {
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [journal, setJournal] = useState<JournalData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statsOpen, setStatsOpen] = useState(true); // 数据统计默认展开

  useEffect(() => {
    fetchJournal();
  }, [date]);

  const fetchJournal = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(
        `http://localhost:8000/api/v1/ai-journal/daily-journal?target_date=${date}`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setJournal(data);
    } catch (error: any) {
      console.error("获取日记失败:", error);
      setError(error.message || "获取日记失败");
    } finally {
      setLoading(false);
    }
  };

  const goToToday = () => {
    setDate(new Date().toISOString().split('T')[0]);
  };

  const goToPrevDay = () => {
    const prevDate = new Date(date);
    prevDate.setDate(prevDate.getDate() - 1);
    setDate(prevDate.toISOString().split('T')[0]);
  };

  const goToNextDay = () => {
    const nextDate = new Date(date);
    nextDate.setDate(nextDate.getDate() + 1);
    const today = new Date().toISOString().split('T')[0];
    const newDate = nextDate.toISOString().split('T')[0];
    if (newDate <= today) {
      setDate(newDate);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader
          icon="📖"
          title="AI工作日记"
          description="Qwen情报官与DeepSeek交易官的每日记录"
          color="pink"
        />
        <div className="flex items-center justify-center p-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600 mx-auto mb-4"></div>
            <div className="text-gray-600">加载日记中...</div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <PageHeader
          icon="📖"
          title="AI工作日记"
          description="Qwen情报官与DeepSeek交易官的每日记录"
          color="pink"
        />
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
          <div className="text-red-600 mb-2">❌ 加载失败</div>
          <div className="text-sm text-red-500">{error}</div>
          <button
            onClick={fetchJournal}
            className="mt-4 px-4 py-2 bg-red-100 text-red-900 rounded-lg hover:bg-red-200 transition-colors"
          >
            重试
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        icon="📖"
        title="AI工作日记"
        description="Qwen情报官与DeepSeek交易官的每日记录"
        color="pink"
      />

      {/* 日期选择器 */}
      <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
        <div className="flex items-center gap-4">
          <button
            onClick={goToPrevDay}
            className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
            title="前一天"
          >
            ← 前一天
          </button>
          
          <input
            type="date"
            value={date}
            max={new Date().toISOString().split('T')[0]}
            onChange={(e) => setDate(e.target.value)}
            className="px-4 py-2 border border-pink-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent transition-all font-medium"
          />
          
          <button
            onClick={goToToday}
            className="px-4 py-2 bg-gradient-to-r from-pink-500 to-pink-600 text-white rounded-lg hover:shadow-lg transition-all font-medium"
          >
            📅 今天
          </button>
          
          <button
            onClick={goToNextDay}
            disabled={date >= new Date().toISOString().split('T')[0]}
            className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            title="后一天"
          >
            后一天 →
          </button>

          <div className="ml-auto text-sm text-gray-600">
            {new Date(date).toLocaleDateString('zh-CN', { 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric',
              weekday: 'long'
            })}
          </div>
        </div>
      </div>

      {/* 数据统计（可折叠） - 移到顶部，默认展开 */}
      {journal?.data_summary && (
        <div className="bg-white rounded-xl p-6 shadow border border-gray-200 mb-4">
          <div 
            className="cursor-pointer text-gray-900 font-bold text-lg hover:text-pink-600 transition-colors flex items-center justify-between"
            onClick={() => setStatsOpen(!statsOpen)}
          >
            <span>📊 查看原始数据统计</span>
            <span className="text-gray-500">{statsOpen ? '▼' : '▶'}</span>
          </div>
          {statsOpen && (
          <div className="mt-4">
            <div className="grid grid-cols-8 gap-3">
              <StatCard 
                label="情报报告" 
                value={journal.data_summary.qwen_reports_count} 
                icon="📋"
                color="orange"
              />
              <StatCard 
                label="收集新闻" 
                value={journal.data_summary.news_count} 
                icon="📰"
                color="orange"
              />
              <StatCard 
                label="巨鲸活动" 
                value={journal.data_summary.whale_signals_count} 
                icon="🐋"
                color="orange"
              />
              <StatCard 
                label="AI决策" 
                value={journal.data_summary.decisions_count} 
                icon="🤔"
                color="purple"
              />
              <StatCard 
                label="执行交易" 
                value={journal.data_summary.trades_count} 
                icon="📈"
                color="purple"
              />
              <StatCard 
                label="已执行决策" 
                value={journal.data_summary.executed_decisions} 
                icon="✅"
                color="green"
              />
              <StatCard 
                label="被拒决策" 
                value={journal.data_summary.rejected_decisions} 
                icon="❌"
                color="red"
              />
              <StatCard 
                label="总盈亏" 
                value={`$${journal.data_summary.total_pnl.toFixed(2)}`}
                icon="💰"
                color={journal.data_summary.total_pnl >= 0 ? 'green' : 'red'}
              />
            </div>
          </div>
          )}
        </div>
      )}

      {/* 日记区域 - 左右结构 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Qwen情报官的日记 - 左侧 */}
        <div className="bg-gradient-to-br from-orange-50 to-yellow-50 rounded-xl p-6 shadow-lg border border-orange-200">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-3xl">🕵️</span>
            <h3 className="text-xl font-bold text-orange-900">Qwen情报官的日记</h3>
          </div>
          <div className="prose prose-orange max-w-none">
            <pre className="whitespace-pre-wrap font-sans text-gray-800 leading-relaxed">
{journal?.qwen_journal || "今天没有记录"}
            </pre>
          </div>
        </div>

        {/* DeepSeek交易官的日记 - 右侧 */}
        <div className="bg-gradient-to-br from-pink-50 to-purple-50 rounded-xl p-6 shadow-lg border border-pink-200">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-3xl">🤖</span>
            <h3 className="text-xl font-bold text-pink-900">DeepSeek交易官的日记</h3>
          </div>
          <div className="prose prose-pink max-w-none">
            <pre className="whitespace-pre-wrap font-sans text-gray-800 leading-relaxed">
{journal?.deepseek_journal || "今天没有记录"}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}

interface StatCardProps {
  label: string;
  value: number | string;
  icon: string;
  color: string;
}

function StatCard({ label, value, icon, color }: StatCardProps) {
  const colorClasses = {
    orange: 'bg-orange-50 border-orange-200 text-orange-900',
    purple: 'bg-purple-50 border-purple-200 text-purple-900',
    green: 'bg-green-50 border-green-200 text-green-900',
    red: 'bg-red-50 border-red-200 text-red-900',
    gray: 'bg-gray-50 border-gray-200 text-gray-900',
  };

  const textColorClasses = {
    orange: 'text-orange-600',
    purple: 'text-purple-600',
    green: 'text-green-600',
    red: 'text-red-600',
    gray: 'text-gray-600',
  };

  return (
    <div className={`rounded-lg p-4 border ${colorClasses[color as keyof typeof colorClasses] || colorClasses.gray}`}>
      <div className="flex items-center gap-2 mb-2">
        <span className="text-2xl">{icon}</span>
        <div className="text-sm text-gray-600">{label}</div>
      </div>
      <div className={`text-2xl font-bold ${textColorClasses[color as keyof typeof textColorClasses] || textColorClasses.gray}`}>
        {value || 0}
      </div>
    </div>
  );
}
