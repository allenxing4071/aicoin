/**
 * 统一的 Prompt 数据获取 Hook
 * 使用缓存和批量请求优化性能
 */

import { useState, useEffect, useCallback } from 'react';
import { promptCache } from '@/lib/promptCache';

interface PromptTemplate {
  id: number;
  name: string;
  category: string;
  permission_level: string | null;
  content: string;
  version: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface UsePromptsOptions {
  category?: string;
  permissionLevel?: string;
  enabled?: boolean; // 是否启用自动请求
}

interface UsePromptsResult {
  prompts: PromptTemplate[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/**
 * 使用 Prompts Hook
 */
export function usePrompts(options: UsePromptsOptions = {}): UsePromptsResult {
  const { category = 'all', permissionLevel = 'all', enabled = true } = options;
  
  const [prompts, setPrompts] = useState<PromptTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 生成缓存 key
  const getCacheKey = useCallback(() => {
    return `prompts_${category}_${permissionLevel}`;
  }, [category, permissionLevel]);

  // 获取 Prompts
  const fetchPrompts = useCallback(async () => {
    if (!enabled) return;

    const cacheKey = getCacheKey();
    
    // 先尝试从缓存获取
    const cached = promptCache.get<PromptTemplate[]>(cacheKey);
    if (cached) {
      setPrompts(cached);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      let url = '/api/v1/prompts/v2/';
      const params = new URLSearchParams();

      if (category !== 'all') params.append('category', category);
      if (permissionLevel !== 'all') params.append('permission_level', permissionLevel);

      if (params.toString()) url += `?${params.toString()}`;

      const token = localStorage.getItem('admin_token');
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      
      // 存入缓存（5分钟）
      promptCache.set(cacheKey, data, 5 * 60 * 1000);
      
      setPrompts(data);
    } catch (err: any) {
      console.error('获取Prompt列表失败:', err);
      setError(err.message || '获取失败');
    } finally {
      setLoading(false);
    }
  }, [category, permissionLevel, enabled, getCacheKey]);

  useEffect(() => {
    fetchPrompts();
  }, [fetchPrompts]);

  return {
    prompts,
    loading,
    error,
    refetch: fetchPrompts
  };
}

/**
 * 批量获取所有 Prompts（用于页面初始化）
 */
export function useAllPrompts() {
  return usePrompts({ category: 'all', permissionLevel: 'all' });
}

/**
 * 按类别获取 Prompts
 */
export function usePromptsByCategory(category: 'decision' | 'debate' | 'intelligence') {
  return usePrompts({ category });
}

