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
      'bear_analyst': 'bear_analyst (空头分析师)',
      'bull_analyst': 'bull_analyst (多头分析师)',
      'research_manager': 'research_manager (研究经理)',
      'default': 'default (默认策略)',
      'l0_conservative': 'l0_conservative (L0-极度保守)',
      'l1_moderate': 'l1_moderate (L1-保守稳健)',
      'l2_balanced': 'l2_balanced (L2-平衡型)',
      'l3_aggressive': 'l3_aggressive (L3-积极进取)',
      'l4_high_risk': 'l4_high_risk (L4-高风险)',
      'l5_extreme': 'l5_extreme (L5-极限激进)',
    };
    return nameMap[name] || name;
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

