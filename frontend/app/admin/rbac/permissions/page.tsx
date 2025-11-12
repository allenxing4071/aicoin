'use client';

import { useState, useEffect } from 'react';
import { usePermissions } from '../../PermissionsProvider';
import PageHeader from '../../../components/common/PageHeader';

interface Permission {
  id: number;
  code: string;
  name: string;
  description?: string;
  resource_type?: string;
  resource_path?: string;
}

export default function PermissionsManagementPage() {
  const { loading: permLoading } = usePermissions();
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingPermission, setEditingPermission] = useState<Permission | null>(null);
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    description: '',
    resource_type: 'page',
    resource_path: '',
  });

  // 加载权限列表
  const loadPermissions = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch('/api/v1/admin/rbac/permissions', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setPermissions(data.data.permissions);
        }
      }
    } catch (error) {
      console.error('加载权限列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!permLoading) {
      loadPermissions();
    }
  }, [permLoading]);

  // 打开新建/编辑模态框
  const openModal = (permission?: Permission) => {
    if (permission) {
      setEditingPermission(permission);
      setFormData({
        code: permission.code,
        name: permission.name,
        description: permission.description || '',
        resource_type: permission.resource_type || 'page',
        resource_path: permission.resource_path || '',
      });
    } else {
      setEditingPermission(null);
      setFormData({
        code: '',
        name: '',
        description: '',
        resource_type: 'page',
        resource_path: '',
      });
    }
    setShowModal(true);
  };

  // 保存权限
  const handleSave = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      const url = editingPermission
        ? `/api/v1/admin/rbac/permissions/${editingPermission.id}`
        : '/api/v1/admin/rbac/permissions';
      
      const method = editingPermission ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });
      
      if (response.ok) {
        alert(editingPermission ? '权限更新成功' : '权限创建成功');
        setShowModal(false);
        loadPermissions();
      } else {
        const data = await response.json();
        alert(`操作失败: ${data.detail || '未知错误'}`);
      }
    } catch (error) {
      console.error('保存权限失败:', error);
      alert('保存失败');
    }
  };

  // 删除权限
  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除此权限吗？删除后不可恢复。')) return;
    
    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch(`/api/v1/admin/rbac/permissions/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (response.ok) {
        alert('权限删除成功');
        loadPermissions();
      } else {
        const data = await response.json();
        alert(`删除失败: ${data.detail || '未知错误'}`);
      }
    } catch (error) {
      console.error('删除权限失败:', error);
      alert('删除失败');
    }
  };

  if (loading || permLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="权限管理"
        description="管理系统所有权限，包括页面、API和按钮级别权限"
        icon="🔐"
        actions={
          <button
            onClick={() => openModal()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            ➕ 新建权限
          </button>
        }
      />

      {/* 权限统计 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">总权限数</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{permissions.length}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">页面权限</div>
          <div className="text-2xl font-bold text-blue-600 mt-1">
            {permissions.filter(p => p.resource_type === 'page').length}
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">API权限</div>
          <div className="text-2xl font-bold text-green-600 mt-1">
            {permissions.filter(p => p.resource_type === 'api').length}
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">按钮权限</div>
          <div className="text-2xl font-bold text-purple-600 mt-1">
            {permissions.filter(p => p.resource_type === 'button').length}
          </div>
        </div>
      </div>

      {/* 权限列表 */}
      <div className="bg-white rounded-lg border">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">权限代码</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">权限名称</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">资源类型</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">资源路径</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">描述</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {permissions.map((permission) => (
                <tr key={permission.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <code className="text-sm text-gray-900 bg-gray-100 px-2 py-1 rounded">{permission.code}</code>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{permission.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      permission.resource_type === 'page' ? 'bg-blue-100 text-blue-800' :
                      permission.resource_type === 'api' ? 'bg-green-100 text-green-800' :
                      'bg-purple-100 text-purple-800'
                    }`}>
                      {permission.resource_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">{permission.resource_path || '-'}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{permission.description || '-'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                    <button
                      onClick={() => openModal(permission)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      编辑
                    </button>
                    <button
                      onClick={() => handleDelete(permission.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      删除
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 新建/编辑模态框 */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">
              {editingPermission ? '编辑权限' : '新建权限'}
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">权限代码 *</label>
                <input
                  type="text"
                  value={formData.code}
                  onChange={(e) => setFormData({...formData, code: e.target.value})}
                  disabled={!!editingPermission}
                  placeholder="例如: users.view"
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">权限名称 *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  placeholder="例如: 查看用户"
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">资源类型</label>
                <select
                  value={formData.resource_type}
                  onChange={(e) => setFormData({...formData, resource_type: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="page">页面</option>
                  <option value="api">API</option>
                  <option value="button">按钮</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">资源路径</label>
                <input
                  type="text"
                  value={formData.resource_path}
                  onChange={(e) => setFormData({...formData, resource_path: e.target.value})}
                  placeholder="例如: /admin/users 或 /api/v1/users"
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">描述</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  rows={3}
                  placeholder="权限的详细描述"
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                取消
              </button>
              <button
                onClick={handleSave}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                保存
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

