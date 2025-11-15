'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';

interface PromptVersion {
  id: number;
  template_id: number;
  version: number;
  content: string;
  change_summary: string;
  created_at: string;
  created_by?: string;
}

export default function PromptVersionsPage() {
  const params = useParams();
  const router = useRouter();
  const promptId = params.id;
  
  const [versions, setVersions] = useState<PromptVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [promptName, setPromptName] = useState('');

  useEffect(() => {
    fetchVersions();
  }, []);

  const fetchVersions = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('admin_token');
      
      // 获取 Prompt 基本信息
      const promptResponse = await fetch(`/api/v1/prompts/v2/${promptId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const promptData = await promptResponse.json();
      setPromptName(promptData.name);
      
      // 获取版本列表
      const versionsResponse = await fetch(`/api/v1/prompts/v2/${promptId}/versions`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const versionsData = await versionsResponse.json();
      setVersions(versionsData);
    } catch (error) {
      console.error('获取版本列表失败:', error);
      alert('❌ 获取版本列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleRollback = async (version: number) => {
    if (!confirm(`确定要回滚到版本 ${version} 吗？`)) {
      return;
    }

    try {
      const token = localStorage.getItem('admin_token');
      await fetch(`/api/v1/prompts/v2/${promptId}/rollback/${version}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      alert('✅ 回滚成功');
      router.push('/admin/permissions');
    } catch (error) {
      alert('❌ 回滚失败');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl text-gray-600">加载中...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-200 rounded-xl p-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">📚 版本历史</h1>
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

      {/* 版本列表 */}
      {versions.length === 0 ? (
        <div className="bg-white border-2 border-gray-200 rounded-xl p-12 text-center">
          <div className="text-6xl mb-4">📭</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">暂无版本历史</h3>
          <p className="text-gray-600">该 Prompt 还没有版本记录</p>
        </div>
      ) : (
        <div className="space-y-4">
          {versions.map((version, index) => (
            <div
              key={version.id}
              className={`bg-white border-2 rounded-xl p-6 transition-all ${
                index === 0
                  ? 'border-green-300 bg-gradient-to-r from-green-50 to-emerald-50'
                  : 'border-gray-200 hover:shadow-lg'
              }`}
            >
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{index === 0 ? '🟢' : '📦'}</span>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">
                      版本 {version.version}
                      {index === 0 && (
                        <span className="ml-3 px-3 py-1 rounded-full text-sm font-semibold bg-green-200 text-green-800">
                          当前版本
                        </span>
                      )}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">
                      {new Date(version.created_at).toLocaleString('zh-CN')}
                      {version.created_by && ` · 创建者: ${version.created_by}`}
                    </p>
                  </div>
                </div>

                {index !== 0 && (
                  <button
                    onClick={() => handleRollback(version.version)}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition-all transform hover:scale-105 shadow-lg"
                  >
                    🔄 回滚到此版本
                  </button>
                )}
              </div>

              {version.change_summary && (
                <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm font-semibold text-blue-900">📝 变更说明：</p>
                  <p className="text-sm text-blue-800 mt-1">{version.change_summary}</p>
                </div>
              )}

              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <p className="text-xs font-semibold text-gray-600 mb-2">Prompt 内容：</p>
                <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono max-h-64 overflow-y-auto">
                  {version.content}
                </pre>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

