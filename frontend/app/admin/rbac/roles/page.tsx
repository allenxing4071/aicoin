'use client';

import { useState, useEffect } from 'react';
import { usePermissions } from '../../PermissionsProvider';
import PageHeader from '../../../components/common/PageHeader';

interface Permission {
  id: number;
  code: string;
  name: string;
}

interface Role {
  id: number;
  code: string;
  name: string;
  description?: string;
  is_system: boolean;
  parent_role_id?: number;
  permissions?: Permission[];
  permission_count?: number;
}

export default function RolesManagementPage() {
  const { loading: permLoading } = usePermissions();
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showPermissionsModal, setShowPermissionsModal] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [managingRole, setManagingRole] = useState<Role | null>(null);
  const [selectedPermissions, setSelectedPermissions] = useState<number[]>([]);
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    description: '',
    parent_role_id: null as number | null,
  });

  // 加载角色列表
  const loadRoles = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch('/api/v1/admin/rbac/roles?include_permissions=true', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setRoles(data.data.roles);
        }
      }
    } catch (error) {
      console.error('加载角色列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 加载所有权限
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
    }
  };

  useEffect(() => {
    if (!permLoading) {
      loadRoles();
      loadPermissions();
    }
  }, [permLoading]);

  // 打开新建/编辑角色模态框
  const openModal = (role?: Role) => {
    if (role) {
      setEditingRole(role);
      setFormData({
        code: role.code,
        name: role.name,
        description: role.description || '',
        parent_role_id: role.parent_role_id || null,
      });
    } else {
      setEditingRole(null);
      setFormData({
        code: '',
        name: '',
        description: '',
        parent_role_id: null,
      });
    }
    setShowModal(true);
  };

  // 打开权限管理模态框
  const openPermissionsModal = (role: Role) => {
    setManagingRole(role);
    const permIds = role.permissions?.map(p => p.id) || [];
    setSelectedPermissions(permIds);
    setShowPermissionsModal(true);
  };

  // 保存角色
  const handleSave = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      const url = editingRole
        ? `/api/v1/admin/rbac/roles/${editingRole.id}`
        : '/api/v1/admin/rbac/roles';
      
      const method = editingRole ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });
      
      if (response.ok) {
        alert(editingRole ? '角色更新成功' : '角色创建成功');
        setShowModal(false);
        loadRoles();
      } else {
        const data = await response.json();
        alert(`操作失败: ${data.detail || '未知错误'}`);
      }
    } catch (error) {
      console.error('保存角色失败:', error);
      alert('保存失败');
    }
  };

  // 保存角色权限
  const handleSavePermissions = async () => {
    if (!managingRole) return;
    
    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch(`/api/v1/admin/rbac/roles/${managingRole.id}/permissions`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          permission_ids: selectedPermissions,
        }),
      });
      
      if (response.ok) {
        alert('角色权限更新成功');
        setShowPermissionsModal(false);
        loadRoles();
      } else {
        const data = await response.json();
        alert(`更新失败: ${data.detail || '未知错误'}`);
      }
    } catch (error) {
      console.error('保存权限失败:', error);
      alert('保存失败');
    }
  };

  // 删除角色
  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除此角色吗？删除后不可恢复。')) return;
    
    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch(`/api/v1/admin/rbac/roles/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (response.ok) {
        alert('角色删除成功');
        loadRoles();
      } else {
        const data = await response.json();
        alert(`删除失败: ${data.detail || '未知错误'}`);
      }
    } catch (error) {
      console.error('删除角色失败:', error);
      alert('删除失败');
    }
  };

  // 切换权限选择
  const togglePermission = (permId: number) => {
    if (selectedPermissions.includes(permId)) {
      setSelectedPermissions(selectedPermissions.filter(id => id !== permId));
    } else {
      setSelectedPermissions([...selectedPermissions, permId]);
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
        title="角色管理"
        description="管理系统角色，配置角色权限，支持角色继承"
        icon="👥"
        actions={
          <button
            onClick={() => openModal()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            ➕ 新建角色
          </button>
        }
      />

      {/* 角色统计 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">总角色数</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{roles.length}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">系统角色</div>
          <div className="text-2xl font-bold text-blue-600 mt-1">
            {roles.filter(r => r.is_system).length}
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">自定义角色</div>
          <div className="text-2xl font-bold text-green-600 mt-1">
            {roles.filter(r => !r.is_system).length}
          </div>
        </div>
      </div>

      {/* 角色列表 */}
      <div className="bg-white rounded-lg border">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">角色代码</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">角色名称</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">描述</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">类型</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">权限数</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {roles.map((role) => (
                <tr key={role.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <code className="text-sm text-gray-900 bg-gray-100 px-2 py-1 rounded">{role.code}</code>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{role.name}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{role.description || '-'}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      role.is_system ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                    }`}>
                      {role.is_system ? '系统角色' : '自定义'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {role.permission_count || role.permissions?.length || 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                    <button
                      onClick={() => openPermissionsModal(role)}
                      className="text-purple-600 hover:text-purple-900"
                    >
                      权限
                    </button>
                    {!role.is_system && (
                      <>
                        <button
                          onClick={() => openModal(role)}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          编辑
                        </button>
                        <button
                          onClick={() => handleDelete(role.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          删除
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 新建/编辑角色模态框 */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">
              {editingRole ? '编辑角色' : '新建角色'}
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">角色代码 *</label>
                <input
                  type="text"
                  value={formData.code}
                  onChange={(e) => setFormData({...formData, code: e.target.value})}
                  disabled={!!editingRole}
                  placeholder="例如: custom_admin"
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">角色名称 *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  placeholder="例如: 自定义管理员"
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">父角色（继承权限）</label>
                <select
                  value={formData.parent_role_id || ''}
                  onChange={(e) => setFormData({...formData, parent_role_id: e.target.value ? parseInt(e.target.value) : null})}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">无</option>
                  {roles.filter(r => r.id !== editingRole?.id).map(r => (
                    <option key={r.id} value={r.id}>{r.name}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">描述</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  rows={3}
                  placeholder="角色的详细描述"
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

      {/* 权限管理模态框 */}
      {showPermissionsModal && managingRole && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4">
              管理角色权限: {managingRole.name}
            </h3>
            
            <div className="mb-4 text-sm text-gray-600">
              已选择 {selectedPermissions.length} / {permissions.length} 个权限
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {permissions.map((permission) => (
                <div key={permission.id} className="border rounded-lg p-3 hover:bg-gray-50">
                  <label className="flex items-start cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedPermissions.includes(permission.id)}
                      onChange={() => togglePermission(permission.id)}
                      className="mt-1 mr-3"
                    />
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">{permission.name}</div>
                      <code className="text-xs text-gray-500">{permission.code}</code>
                    </div>
                  </label>
                </div>
              ))}
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowPermissionsModal(false)}
                className="px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                取消
              </button>
              <button
                onClick={handleSavePermissions}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                保存权限
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

