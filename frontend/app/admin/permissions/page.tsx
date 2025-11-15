'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import PageHeader from '../../components/common/PageHeader';
import { API_BASE } from '../../../lib/api';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import PromptSelector from '@/components/PromptSelector';
import { useAllPrompts } from '@/hooks/usePrompts';

interface TradingParams {
  max_position_pct: number;
  max_leverage: number;
  confidence_threshold: number;
  max_daily_trades: number;
}

interface UpgradeConditions {
  win_rate_7d?: number;
  win_rate_30d?: number;
  sharpe_ratio?: number;
  min_trades?: number;
  min_days?: number;
}

interface DowngradeConditions {
  max_drawdown?: number;
  consecutive_losses?: number;
  win_rate_7d?: number;
}

interface PermissionLevel {
  id: number;
  level: string;
  name: string;
  description?: string;
  trading_params: TradingParams;
  upgrade_conditions: UpgradeConditions;
  downgrade_conditions: DowngradeConditions;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
  updated_at: string;
  // 新增：关联的 Prompt
  prompts?: {
    decision_prompt_id?: number;
    debate_prompt_id?: number;
    intelligence_prompt_id?: number;
  };
}

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

export default function PermissionsAdmin() {
  const router = useRouter();
  const [levels, setLevels] = useState<PermissionLevel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingLevel, setEditingLevel] = useState<PermissionLevel | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [currentAILevel, setCurrentAILevel] = useState<string>('L1'); // AI当前使用的权限等级
  
  // Prompt 模板相关状态 - 使用优化的 Hook
  const { prompts: allPrompts, loading: promptsLoading, refetch: refetchPrompts } = useAllPrompts();
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedLevel, setSelectedLevel] = useState<string>('all');

  // 使用 useMemo 过滤 Prompts，避免重复计算
  const filteredPrompts = useMemo(() => {
    return allPrompts.filter(p => {
      const matchCategory = selectedCategory === 'all' || p.category === selectedCategory;
      const matchLevel = selectedLevel === 'all' || p.permission_level === selectedLevel;
      return matchCategory && matchLevel;
    });
  }, [allPrompts, selectedCategory, selectedLevel]);

  useEffect(() => {
    fetchLevels();
    fetchCurrentAILevel();
    // 优化：延长轮询间隔到 30 秒，减少服务器压力
    const interval = setInterval(fetchCurrentAILevel, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchLevels = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/admin/permissions/levels`);
      setLevels(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.message || '获取权限配置失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchCurrentAILevel = async () => {
    try {
      const response = await axios.get(`${API_BASE}/ai/status`);
      if (response.data?.orchestrator?.permission_level) {
        setCurrentAILevel(response.data.orchestrator.permission_level);
      }
    } catch (err) {
      console.error('获取AI当前权限等级失败:', err);
    }
  };
  
  const handleReloadPrompts = async () => {
    try {
      await fetch('/api/v1/prompts/v2/reload', { method: 'POST' });
      alert('✅ Prompt已重载');
      // 清除缓存并重新获取
      await refetchPrompts();
    } catch (error) {
      alert('❌ 重载失败');
    }
  };
  
  // 获取类别图标和颜色
  const getCategoryStyle = (category: string) => {
    const styles = {
      decision: { icon: '🎯', color: 'from-blue-50 to-cyan-50', border: 'border-blue-200', badge: 'bg-blue-100 text-blue-800' },
      debate: { icon: '⚔️', color: 'from-purple-50 to-pink-50', border: 'border-purple-200', badge: 'bg-purple-100 text-purple-800' },
      intelligence: { icon: '🔍', color: 'from-green-50 to-emerald-50', border: 'border-green-200', badge: 'bg-green-100 text-green-800' }
    };
    return styles[category as keyof typeof styles] || styles.decision;
  };
  
  // 获取权限等级颜色
  const getPromptLevelColor = (level: string) => {
    const colors = {
      L0: 'bg-gray-100 text-gray-800',
      L1: 'bg-blue-100 text-blue-800',
      L2: 'bg-green-100 text-green-800',
      L3: 'bg-yellow-100 text-yellow-800',
      L4: 'bg-orange-100 text-orange-800',
      L5: 'bg-red-100 text-red-800'
    };
    return colors[level as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const handleEdit = (level: PermissionLevel) => {
    setEditingLevel({ ...level });
    setShowEditModal(true);
  };

  const handleSave = async () => {
    if (!editingLevel) return;

    try {
      await axios.put(
        `${API_BASE}/admin/permissions/levels/${editingLevel.level}`,
        {
          name: editingLevel.name,
          description: editingLevel.description,
          trading_params: editingLevel.trading_params,
          upgrade_conditions: editingLevel.upgrade_conditions,
          downgrade_conditions: editingLevel.downgrade_conditions,
          is_active: editingLevel.is_active,
          is_default: editingLevel.is_default
        }
      );
      setShowEditModal(false);
      setEditingLevel(null);
      fetchLevels();
    } catch (err: any) {
      alert(`保存失败: ${err.message}`);
    }
  };

  const handleSetDefault = async (level: string) => {
    try {
      await axios.post(`${API_BASE}/admin/permissions/levels/${level}/set-default`);
      fetchLevels();
    } catch (err: any) {
      alert(`设置默认等级失败: ${err.message}`);
    }
  };

  const handleInitDefaults = async () => {
    if (!confirm('确认初始化默认权限配置？这将创建L0-L5的默认配置。')) return;

    try {
      await axios.post(`${API_BASE}/admin/permissions/levels/init-defaults`);
      fetchLevels();
      alert('默认配置初始化成功！');
    } catch (err: any) {
      alert(`初始化失败: ${err.message}`);
    }
  };

  const getLevelColor = (level: string) => {
    const colors: { [key: string]: string } = {
      'L0': 'bg-gray-100 text-gray-800',
      'L1': 'bg-green-100 text-green-800',
      'L2': 'bg-blue-100 text-blue-800',
      'L3': 'bg-purple-100 text-purple-800',
      'L4': 'bg-orange-100 text-orange-800',
      'L5': 'bg-red-100 text-red-800',
    };
    return colors[level] || 'bg-gray-100 text-gray-800';
  };

  if (loading) return <div className="p-6">加载中...</div>;
  if (error) return <div className="p-6 text-red-500">错误: {error}</div>;

  const currentLevelData = levels.find(l => l.level === currentAILevel);

  return (
    <div className="space-y-6">
      <PageHeader
        icon="🔐"
        title="权限管理"
        description="管理用户角色、权限配置和 Prompt 模板"
        color="purple"
        actions={
          <button
            onClick={handleInitDefaults}
            className="px-4 py-2 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-xl hover:from-purple-600 hover:to-purple-700 shadow-sm hover:shadow-md transition-all"
          >
            初始化默认配置
          </button>
        }
      />
      
      {/* Tabs 布局 */}
      <Tabs defaultValue="levels" className="w-full">
        <TabsList className="grid w-full grid-cols-2 max-w-md">
          <TabsTrigger value="levels">权限等级配置</TabsTrigger>
          <TabsTrigger value="prompts">Prompt 模板库</TabsTrigger>
        </TabsList>
        
        {/* Tab 1: 权限等级配置 */}
        <TabsContent value="levels" className="space-y-6">

      {/* 当前AI使用的权限等级指示器 */}
      {currentLevelData && (
        <div className="mb-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-xl p-6 shadow-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="text-2xl">🤖</span>
                <div>
                  <div className="text-sm text-gray-600 font-medium">AI当前使用的权限等级</div>
                  <div className="flex items-center gap-3 mt-1">
                    <span className={`px-4 py-2 rounded-full font-bold text-lg ${getLevelColor(currentAILevel)}`}>
                      {currentAILevel}
                    </span>
                    <span className="text-xl font-bold text-gray-900">{currentLevelData.name}</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="grid grid-cols-4 gap-4 text-center">
              <div className="bg-white rounded-xl p-3 shadow">
                <div className="text-xs text-gray-600">最大仓位</div>
                <div className="text-lg font-bold text-blue-700">{(currentLevelData.trading_params.max_position_pct * 100).toFixed(0)}%</div>
              </div>
              <div className="bg-white rounded-xl p-3 shadow">
                <div className="text-xs text-gray-600">最大杠杆</div>
                <div className="text-lg font-bold text-blue-700">{currentLevelData.trading_params.max_leverage}x</div>
              </div>
              <div className="bg-white rounded-xl p-3 shadow">
                <div className="text-xs text-gray-600">置信度阈值</div>
                <div className="text-lg font-bold text-blue-700">{(currentLevelData.trading_params.confidence_threshold * 100).toFixed(0)}%</div>
              </div>
              <div className="bg-white rounded-xl p-3 shadow">
                <div className="text-xs text-gray-600">每日最大交易</div>
                <div className="text-lg font-bold text-blue-700">{currentLevelData.trading_params.max_daily_trades}</div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="mb-4">
        <h2 className="text-xl font-bold text-gray-900">所有权限等级配置</h2>
        <p className="text-sm text-gray-600 mt-1">以下是系统中所有权限等级的配置，可以编辑每个等级的参数</p>
      </div>

      <div className="grid gap-6">
        {levels.map((level) => (
          <div
            key={level.id}
            className={`bg-white rounded-xl shadow-md p-6 border-l-4 ${
              level.level === currentAILevel ? 'ring-2 ring-blue-400' : ''
            }`}
            style={{
              borderLeftColor: level.level === currentAILevel ? '#3b82f6' : level.is_default ? '#10b981' : '#e5e7eb'
            }}
          >
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center gap-3">
                <span className={`px-3 py-1 rounded-full font-bold ${getLevelColor(level.level)}`}>
                  {level.level}
                </span>
                <div>
                  <h3 className="text-xl font-bold">{level.name}</h3>
                  {level.description && (
                    <p className="text-gray-600 text-sm">{level.description}</p>
                  )}
                </div>
                {level.level === currentAILevel && (
                  <span className="px-3 py-1 bg-blue-500 text-white text-xs rounded font-bold animate-pulse">
                    ⚡ 当前使用
                  </span>
                )}
                {level.is_default && (
                  <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                    默认等级
                  </span>
                )}
                {!level.is_active && (
                  <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded">
                    已禁用
                  </span>
                )}
              </div>
              <div className="flex gap-2">
                {!level.is_default && (
                  <button
                    onClick={() => handleSetDefault(level.level)}
                    className="px-3 py-1 text-sm text-green-600 hover:text-green-700 border border-green-600 rounded"
                  >
                    设为默认
                  </button>
                )}
                <button
                  onClick={() => handleEdit(level)}
                  className="px-3 py-1 text-sm text-blue-600 hover:text-blue-700 border border-blue-600 rounded"
                >
                  编辑
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500">最大仓位</div>
                <div className="text-lg font-bold">{(level.trading_params.max_position_pct * 100).toFixed(0)}%</div>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500">最大杠杆</div>
                <div className="text-lg font-bold">{level.trading_params.max_leverage}x</div>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500">置信度门槛</div>
                <div className="text-lg font-bold">{(level.trading_params.confidence_threshold * 100).toFixed(0)}%</div>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500">每日交易限制</div>
                <div className="text-lg font-bold">{level.trading_params.max_daily_trades}</div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <h4 className="font-semibold text-gray-700 mb-2">🔼 升级条件</h4>
                <div className="space-y-1 text-gray-600">
                  {level.upgrade_conditions.win_rate_7d && (
                    <div>• 7日胜率 ≥ {(level.upgrade_conditions.win_rate_7d * 100).toFixed(0)}%</div>
                  )}
                  {level.upgrade_conditions.win_rate_30d && (
                    <div>• 30日胜率 ≥ {(level.upgrade_conditions.win_rate_30d * 100).toFixed(0)}%</div>
                  )}
                  {level.upgrade_conditions.sharpe_ratio && (
                    <div>• 夏普比率 ≥ {level.upgrade_conditions.sharpe_ratio.toFixed(1)}</div>
                  )}
                  {level.upgrade_conditions.min_trades && (
                    <div>• 最少交易 {level.upgrade_conditions.min_trades} 笔</div>
                  )}
                  {level.upgrade_conditions.min_days && (
                    <div>• 运行天数 ≥ {level.upgrade_conditions.min_days} 天</div>
                  )}
                  {!level.upgrade_conditions.win_rate_7d && !level.upgrade_conditions.win_rate_30d && (
                    <div className="text-gray-600">无升级条件</div>
                  )}
                </div>
              </div>
              <div>
                <h4 className="font-semibold text-gray-700 mb-2">🔽 降级条件</h4>
                <div className="space-y-1 text-gray-600">
                  {level.downgrade_conditions.max_drawdown && (
                    <div>• 最大回撤 {'>'} {(level.downgrade_conditions.max_drawdown * 100).toFixed(0)}%</div>
                  )}
                  {level.downgrade_conditions.consecutive_losses && (
                    <div>• 连续亏损 {'>'} {level.downgrade_conditions.consecutive_losses} 次</div>
                  )}
                  {level.downgrade_conditions.win_rate_7d && (
                    <div>• 7日胜率 {'<'} {(level.downgrade_conditions.win_rate_7d * 100).toFixed(0)}%</div>
                  )}
                  {!level.downgrade_conditions.max_drawdown && !level.downgrade_conditions.consecutive_losses && (
                    <div className="text-gray-600">无降级条件</div>
                  )}
                </div>
              </div>
            </div>
            
            {/* 关联 Prompt 模板 */}
            <div className="mt-4 pt-4 border-t border-gray-200">
              <h4 className="font-semibold text-gray-700 mb-3">📝 关联 Prompt 模板</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">🎯 决策 Prompt</label>
                  <PromptSelector
                    category="decision"
                    selectedPromptId={level.prompts?.decision_prompt_id}
                    onSelect={(promptId) => {
                      // TODO: 保存关联
                      console.log(`关联决策Prompt ${promptId} 到 ${level.level}`);
                    }}
                    permissionLevel={level.level}
                    allPrompts={allPrompts}
                    loading={promptsLoading}
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">⚔️ 辩论 Prompt</label>
                  <PromptSelector
                    category="debate"
                    selectedPromptId={level.prompts?.debate_prompt_id}
                    onSelect={(promptId) => {
                      // TODO: 保存关联
                      console.log(`关联辩论Prompt ${promptId} 到 ${level.level}`);
                    }}
                    permissionLevel={level.level}
                    allPrompts={allPrompts}
                    loading={promptsLoading}
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">🔍 情报 Prompt</label>
                  <PromptSelector
                    category="intelligence"
                    selectedPromptId={level.prompts?.intelligence_prompt_id}
                    onSelect={(promptId) => {
                      // TODO: 保存关联
                      console.log(`关联情报Prompt ${promptId} 到 ${level.level}`);
                    }}
                    permissionLevel={level.level}
                    allPrompts={allPrompts}
                    loading={promptsLoading}
                  />
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                💡 提示：为每个权限等级选择对应的 Prompt 模板，AI 将根据当前权限等级使用相应的 Prompt
              </p>
            </div>
          </div>
        ))}
      </div>
        </TabsContent>
        
        {/* Tab 2: Prompt 模板库 */}
        <TabsContent value="prompts" className="space-y-6">
          {/* 页面标题和操作区 */}
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border-2 border-indigo-200 rounded-xl p-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">📝 Prompt 模板库</h2>
                <p className="text-gray-600">管理 AI 决策、辩论和情报系统的 Prompt 模板</p>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={handleReloadPrompts}
                  className="px-6 py-3 bg-white border-2 border-indigo-300 text-indigo-700 rounded-xl font-semibold hover:bg-indigo-50 transition-all transform hover:scale-105 shadow-sm"
                >
                  🔄 热重载
                </button>
                <button
                  onClick={() => router.push('/admin/prompts-v2/create')}
                  className="px-6 py-3 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition-all transform hover:scale-105 shadow-lg"
                >
                  ➕ 创建 Prompt
                </button>
              </div>
            </div>
          </div>

          {/* 筛选器 */}
          <div className="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-sm">
            <div className="flex gap-6">
              <div className="flex-1">
                <label className="block text-sm font-semibold text-gray-900 mb-2">📂 类别筛选</label>
                <select 
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl font-medium text-gray-900 focus:outline-none focus:border-indigo-500 transition-colors"
                >
                  <option value="all">全部类别</option>
                  <option value="decision">🎯 决策</option>
                  <option value="debate">⚔️ 辩论</option>
                  <option value="intelligence">🔍 情报</option>
                </select>
              </div>
              
              <div className="flex-1">
                <label className="block text-sm font-semibold text-gray-900 mb-2">🔑 权限等级</label>
                <select 
                  value={selectedLevel}
                  onChange={(e) => setSelectedLevel(e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl font-medium text-gray-900 focus:outline-none focus:border-indigo-500 transition-colors"
                >
                  <option value="all">全部等级</option>
                  <option value="L0">L0 - 极度保守</option>
                  <option value="L1">L1 - 保守稳健</option>
                  <option value="L2">L2 - 平衡型</option>
                  <option value="L3">L3 - 积极进取</option>
                  <option value="L4">L4 - 高风险</option>
                  <option value="L5">L5 - 极限激进</option>
                </select>
              </div>
            </div>
            
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-600">
                共找到 <span className="font-bold text-indigo-600">{filteredPrompts.length}</span> 个 Prompt 模板
              </p>
            </div>
          </div>

          {/* Prompt 列表 */}
          {promptsLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-gray-500">加载中...</div>
            </div>
          ) : filteredPrompts.length === 0 ? (
            <div className="bg-white border-2 border-gray-200 rounded-xl p-12 text-center">
              <div className="text-6xl mb-4">📭</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">暂无 Prompt 模板</h3>
              <p className="text-gray-600">点击上方"创建 Prompt"按钮添加新模板</p>
            </div>
          ) : (
            <div className="grid gap-4">
              {filteredPrompts.map((prompt) => {
                const categoryStyle = getCategoryStyle(prompt.category);
                return (
                  <div 
                    key={prompt.id} 
                    className={`bg-gradient-to-r ${categoryStyle.color} border-2 ${categoryStyle.border} rounded-xl p-6 hover:shadow-xl transition-all transform hover:scale-[1.01]`}
                  >
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="text-2xl">{categoryStyle.icon}</span>
                          <h3 className="text-xl font-bold text-gray-900">{prompt.name}</h3>
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${categoryStyle.badge}`}>
                            {prompt.category}
                          </span>
                          {prompt.permission_level && (
                            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getPromptLevelColor(prompt.permission_level)}`}>
                              {prompt.permission_level}
                            </span>
                          )}
                          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-800">
                            v{prompt.version}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600">
                          更新时间: {new Date(prompt.updated_at).toLocaleString('zh-CN')}
                        </p>
                      </div>
                      
                      <div className="flex gap-2">
                        <button 
                          onClick={() => router.push(`/admin/prompts-v2/${prompt.id}/edit`)}
                          className="px-4 py-2 bg-white border-2 border-indigo-300 text-indigo-700 rounded-lg font-semibold hover:bg-indigo-50 transition-all text-sm"
                        >
                          ✏️ 编辑
                        </button>
                        <button 
                          onClick={() => router.push(`/admin/prompts-v2/${prompt.id}/versions`)}
                          className="px-4 py-2 bg-white border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-all text-sm"
                        >
                          📚 版本
                        </button>
                        <button 
                          onClick={() => router.push(`/admin/prompts-v2/${prompt.id}/metrics`)}
                          className="px-4 py-2 bg-white border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-all text-sm"
                        >
                          📊 指标
                        </button>
                      </div>
                    </div>
                    
                    <div className="bg-white/80 backdrop-blur-sm border border-gray-200 rounded-lg p-4">
                      <pre className="text-sm text-gray-700 font-mono whitespace-pre-wrap max-h-40 overflow-y-auto">
{prompt.content.substring(0, 300)}{prompt.content.length > 300 && '...'}
                      </pre>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* 编辑模态框 */}
      {showEditModal && editingLevel && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">编辑权限等级: {editingLevel.level}</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">等级名称</label>
                <input
                  type="text"
                  value={editingLevel.name}
                  onChange={(e) => setEditingLevel({ ...editingLevel, name: e.target.value })}
                  className="w-full px-3 py-2 border rounded"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">描述</label>
                <textarea
                  value={editingLevel.description || ''}
                  onChange={(e) => setEditingLevel({ ...editingLevel, description: e.target.value })}
                  className="w-full px-3 py-2 border rounded"
                  rows={2}
                />
              </div>

              <div className="border-t pt-4">
                <h3 className="font-semibold mb-3">交易参数</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">最大仓位 (%)</label>
                    <input
                      type="number"
                      value={(editingLevel.trading_params.max_position_pct * 100).toFixed(0)}
                      onChange={(e) => setEditingLevel({
                        ...editingLevel,
                        trading_params: {
                          ...editingLevel.trading_params,
                          max_position_pct: parseFloat(e.target.value) / 100
                        }
                      })}
                      className="w-full px-3 py-2 border rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">最大杠杆</label>
                    <input
                      type="number"
                      value={editingLevel.trading_params.max_leverage}
                      onChange={(e) => setEditingLevel({
                        ...editingLevel,
                        trading_params: {
                          ...editingLevel.trading_params,
                          max_leverage: parseInt(e.target.value)
                        }
                      })}
                      className="w-full px-3 py-2 border rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">置信度门槛 (%)</label>
                    <input
                      type="number"
                      value={(editingLevel.trading_params.confidence_threshold * 100).toFixed(0)}
                      onChange={(e) => setEditingLevel({
                        ...editingLevel,
                        trading_params: {
                          ...editingLevel.trading_params,
                          confidence_threshold: parseFloat(e.target.value) / 100
                        }
                      })}
                      className="w-full px-3 py-2 border rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">每日交易限制</label>
                    <input
                      type="number"
                      value={editingLevel.trading_params.max_daily_trades}
                      onChange={(e) => setEditingLevel({
                        ...editingLevel,
                        trading_params: {
                          ...editingLevel.trading_params,
                          max_daily_trades: parseInt(e.target.value)
                        }
                      })}
                      className="w-full px-3 py-2 border rounded"
                    />
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={editingLevel.is_active}
                    onChange={(e) => setEditingLevel({ ...editingLevel, is_active: e.target.checked })}
                  />
                  <span>启用此等级</span>
                </label>
              </div>
            </div>

            <div className="flex gap-2 mt-6">
              <button
                onClick={handleSave}
                className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-gray-900 rounded hover:from-blue-600 hover:to-blue-700"
              >
                保存
              </button>
              <button
                onClick={() => {
                  setShowEditModal(false);
                  setEditingLevel(null);
                }}
                className="flex-1 px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

