'use client';

import { useState, useEffect } from 'react';

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
}

export default function PromptSelector({ 
  category, 
  selectedPromptId, 
  onSelect,
  permissionLevel 
}: PromptSelectorProps) {
  const [prompts, setPrompts] = useState<PromptTemplate[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPrompts();
  }, [category, permissionLevel]);

  const fetchPrompts = async () => {
    try {
      setLoading(true);
      let url = `/api/v1/prompts/v2/?category=${category}`;
      if (permissionLevel) {
        url += `&permission_level=${permissionLevel}`;
      }
      
      const response = await fetch(url);
      const data = await response.json();
      setPrompts(data);
    } catch (error) {
      console.error('获取Prompt列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryIcon = (cat: string) => {
    const icons = {
      decision: '🎯',
      debate: '⚔️',
      intelligence: '🔍'
    };
    return icons[cat as keyof typeof icons] || '📝';
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
      {prompts.map((prompt) => (
        <option key={prompt.id} value={prompt.id}>
          {getCategoryIcon(prompt.category)} {prompt.name} (v{prompt.version})
        </option>
      ))}
    </select>
  );
}

