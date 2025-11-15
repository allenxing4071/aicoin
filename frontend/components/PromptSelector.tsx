'use client';

import { useMemo } from 'react';

interface PromptTemplate {
  id: number;
  name: string;
  category: string;
  permission_level: string | null;
  version: number;
}

interface PromptSelectorProps {
  category: 'decision' | 'debate' | 'intelligence';
  selectedPromptId?: number;
  onSelect: (promptId: number | null) => void;
  permissionLevel?: string;
  // 新增：接收预加载的 prompts 数据
  allPrompts?: PromptTemplate[];
  loading?: boolean;
}

export default function PromptSelector({ 
  category, 
  selectedPromptId, 
  onSelect,
  permissionLevel,
  allPrompts = [],
  loading = false
}: PromptSelectorProps) {
  // 使用 useMemo 过滤数据，避免重复计算
  const filteredPrompts = useMemo(() => {
    return allPrompts.filter(p => {
      const matchCategory = p.category === category;
      const matchLevel = !permissionLevel || p.permission_level === permissionLevel || !p.permission_level;
      return matchCategory && matchLevel;
    });
  }, [allPrompts, category, permissionLevel]);

  const getCategoryIcon = (cat: string) => {
    const icons = {
      decision: '🎯',
      debate: '⚔️',
      intelligence: '🔍'
    };
    return icons[cat as keyof typeof icons] || '📝';
  };

  // 获取 Prompt 名称的中文备注
  const getPromptNameWithChinese = (name: string) => {
    const nameMap: Record<string, string> = {
      // 辩论系统
      'bear_analyst': 'bear_analyst (空头分析师)',
      'bull_analyst': 'bull_analyst (多头分析师)',
      'research_manager': 'research_manager (研究经理)',
      // 决策系统 - 旧版本
      'default': 'default (默认策略)',
      'decision_base': 'decision_base (决策基础模板)',
      'conservative_decision': 'conservative_decision (保守型)',
      'l0_conservative': 'l0_conservative (L0-极度保守)',
      'l1_moderate': 'l1_moderate (L1-保守稳健)',
      'l2_balanced': 'l2_balanced (L2-平衡型)',
      'l3_aggressive': 'l3_aggressive (L3-积极进取)',
      'l4_high_risk': 'l4_high_risk (L4-高风险)',
      'l5_extreme': 'l5_extreme (L5-极限激进)',
      // 决策系统 - 新版本 (L0-L5)
      'decision_l0_conservative': 'L0 极度保守型决策',
      'decision_l1_stable': 'L1 保守稳健型决策',
      'decision_l2_balanced': 'L2 平衡型决策',
      'decision_l3_aggressive': 'L3 积极进取型决策',
      'decision_l4_high_risk': 'L4 高风险型决策',
      'decision_l5_extreme': 'L5 极限激进型决策',
      // 情报系统
      'intelligence_analysis': 'intelligence_analysis (情报分析)',
      'multi_platform_synthesis': 'multi_platform_synthesis (多平台综合)',
    };
    
    // 如果在映射表中找到，直接返回
    if (nameMap[name]) {
      return nameMap[name];
    }
    
    // 否则，尝试智能生成中文备注
    if (name.includes('l0') || name.includes('L0')) return `${name} (L0-极度保守型)`;
    if (name.includes('l1') || name.includes('L1')) return `${name} (L1-保守稳健型)`;
    if (name.includes('l2') || name.includes('L2')) return `${name} (L2-平衡型)`;
    if (name.includes('l3') || name.includes('L3')) return `${name} (L3-积极进取型)`;
    if (name.includes('l4') || name.includes('L4')) return `${name} (L4-高风险型)`;
    if (name.includes('l5') || name.includes('L5')) return `${name} (L5-极限激进型)`;
    if (name.includes('conservative')) return `${name} (保守型)`;
    if (name.includes('aggressive')) return `${name} (激进型)`;
    if (name.includes('balanced')) return `${name} (平衡型)`;
    if (name.includes('stable') || name.includes('moderate')) return `${name} (稳健型)`;
    if (name.includes('base')) return `${name} (基础模板)`;
    if (name.includes('decision')) return `${name} (决策模板)`;
    if (name.includes('debate')) return `${name} (辩论模板)`;
    if (name.includes('intelligence')) return `${name} (情报模板)`;
    
    // 默认返回原名称
    return name;
  };

  if (loading) {
    return (
      <select className="w-full px-3 py-2 border-2 border-gray-300 rounded-lg text-sm" disabled>
        <option>加载中...</option>
      </select>
    );
  }

  return (
    <select
      value={selectedPromptId || ''}
      onChange={(e) => onSelect(e.target.value ? parseInt(e.target.value) : null)}
      className="w-full px-3 py-2 border-2 border-gray-300 rounded-lg text-sm focus:outline-none focus:border-indigo-500 transition-colors"
    >
      <option value="">未选择</option>
      {filteredPrompts.map((prompt) => (
        <option key={prompt.id} value={prompt.id}>
          {getCategoryIcon(prompt.category)} {getPromptNameWithChinese(prompt.name)} (v{prompt.version})
        </option>
      ))}
    </select>
  );
}

