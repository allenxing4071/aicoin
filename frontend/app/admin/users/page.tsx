"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import PageHeader from '../../components/common/PageHeader';
import { PermissionGuard } from '../../components/auth/PermissionGuard';
import { usePermissions } from '../PermissionsProvider';

interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

interface RoleInfo {
  value: string;
  label: string;
  description: string;
  permission_count: number;
}

interface RolePermissions {
  role: string;
  display_name: string;
  permissions: string[];
}

export default function UsersPage() {
  const router = useRouter();
  const { hasPermission, loading: permLoading } = usePermissions();
  
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  
  // 角色信息
  const [roles, setRoles] = useState<RoleInfo[]>([]);
  const [selectedRolePermissions, setSelectedRolePermissions] = useState<RolePermissions | null>(null);
  
  // 表单状态
  const [formData, setFormData] = useState({
    username: "",
    password: "",
    email: "",
    role: "viewer",
    is_active: true,
  });

  // 模拟数据 - 后续会连接真实API
  const mockUsers: User[] = [
    {
      id: 1,
      username: "admin",
      email: "admin@aicoin.com",
      role: "admin",
      is_active: true,
      created_at: "2025-01-01T00:00:00Z",
      last_login: "2025-11-04T15:30:00Z",
    },
    {
      id: 2,
      username: "trader",
      email: "trader@aicoin.com",
      role: "trader",
      is_active: true,
      created_at: "2025-02-15T10:20:00Z",
      last_login: "2025-11-03T09:15:00Z",
    },
    {
      id: 3,
      username: "viewer",
      email: "viewer@aicoin.com",
      role: "viewer",
      is_active: true,
      created_at: "2025-03-20T14:30:00Z",
      last_login: "2025-11-02T16:45:00Z",
    },
  ];

  // 加载数据
  useEffect(() => {
    loadUsers();
    loadRoles();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // 组件挂载时加载一次

  const loadRoles = async () => {
    try {
      const token = localStorage.getItem("admin_token");
      if (!token) return;
      
      const response = await fetch("/api/v1/admin/users/roles", {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.data) {
          setRoles(data.data);
        }
      }
    } catch (error) {
      console.error("加载角色列表失败:", error);
    }
  };

  const loadRolePermissions = async (role: string) => {
    try {
      const token = localStorage.getItem("admin_token");
      if (!token) return;
      
      const response = await fetch(`/api/v1/admin/users/roles/${role}/permissions`, {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.data) {
          setSelectedRolePermissions(data.data);
        }
      }
    } catch (error) {
      console.error("加载角色权限失败:", error);
    }
  };

  const loadUsers = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("admin_token");
      
      // 如果没有token，重定向到登录页
      if (!token) {
        console.warn("未登录，重定向到登录页面");
        router.push("/admin/login");
        return;
      }
      
      const response = await fetch("/api/v1/admin/users", {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      } else if (response.status === 401) {
        // Token过期或无效，清除并重定向到登录页
        console.warn("Token无效或已过期，重定向到登录页面");
        localStorage.removeItem("admin_token");
        router.push("/admin/login");
      } else {
        console.error("加载用户列表失败");
        // 如果API失败，使用模拟数据
        setUsers(mockUsers);
      }
      setLoading(false);
    } catch (error) {
      console.error("加载用户列表失败:", error);
      // 如果API失败，使用模拟数据
      setUsers(mockUsers);
      setLoading(false);
    }
  };

  const handleAddUser = () => {
    setEditingUser(null);
    setFormData({
      username: "",
      password: "",
      email: "",
      role: "viewer",
      is_active: true,
    });
    setShowAddModal(true);
  };

  const handleEditUser = (user: User) => {
    setEditingUser(user);
    setFormData({
      username: user.username,
      password: "",
      email: user.email,
      role: user.role,
      is_active: user.is_active,
    });
    setShowAddModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem("admin_token");
      
      if (!token) {
        router.push("/admin/login");
        return;
      }
      
      if (editingUser) {
        // 更新用户
        const response = await fetch(`/api/v1/admin/users/${editingUser.id}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
          },
          body: JSON.stringify(formData)
        });
        
        if (response.status === 401) {
          localStorage.removeItem("admin_token");
          router.push("/admin/login");
          return;
        }
        
        if (!response.ok) {
          throw new Error("更新失败");
        }
      } else {
        // 创建用户
        const response = await fetch("/api/v1/admin/users", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
          },
          body: JSON.stringify(formData)
        });
        
        if (response.status === 401) {
          localStorage.removeItem("admin_token");
          router.push("/admin/login");
          return;
        }
        
        if (!response.ok) {
          throw new Error("创建失败");
        }
      }
      
      setShowAddModal(false);
      loadUsers();
    } catch (error) {
      console.error("操作失败:", error);
      alert("操作失败，请重试");
    }
  };

  const handleToggleActive = async (user: User) => {
    // 不允许禁用默认管理员
    if (user.username === "admin" && user.is_active) {
      alert("⚠️ 不能禁用默认管理员账户");
      return;
    }
    
    try {
      const token = localStorage.getItem("admin_token");
      
      if (!token) {
        router.push("/admin/login");
        return;
      }
      
      const response = await fetch(`/api/v1/admin/users/${user.id}/toggle-active`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      
      if (response.status === 401) {
        localStorage.removeItem("admin_token");
        router.push("/admin/login");
        return;
      }
      
      if (response.status === 403) {
        alert("⚠️ 权限不足或不能禁用默认管理员账户");
        return;
      }
      
      if (!response.ok) {
        throw new Error("切换状态失败");
      }
      
      // 重新加载用户列表
      loadUsers();
    } catch (error) {
      console.error("切换状态失败:", error);
      alert("切换状态失败，请重试");
    }
  };

  const handleDeleteUser = async (user: User) => {
    if (!confirm(`确定要删除用户 "${user.username}" 吗？`)) {
      return;
    }
    
    try {
      const token = localStorage.getItem("admin_token");
      
      if (!token) {
        router.push("/admin/login");
        return;
      }
      
      const response = await fetch(`/api/v1/admin/users/${user.id}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      
      if (response.status === 401) {
        localStorage.removeItem("admin_token");
        router.push("/admin/login");
        return;
      }
      
      if (!response.ok) {
        throw new Error("删除用户失败");
      }
      
      // 重新加载用户列表
      loadUsers();
    } catch (error) {
      console.error("删除用户失败:", error);
      alert("删除用户失败，请重试");
    }
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case "admin":
        return "bg-red-100 text-red-800";
      case "trader":
        return "bg-blue-100 text-blue-800";
      case "viewer":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case "admin":
        return "管理员";
      case "trader":
        return "交易员";
      case "viewer":
        return "观察者";
      default:
        return role;
    }
  };

  const formatDateTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString("zh-CN");
  };

  // 移除页面级权限检查，由菜单控制访问

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 - 统一风格 */}
      <PageHeader
        icon="👥"
        title="用户管理"
        description="管理系统用户和账户"
        color="blue"
        actions={
          <PermissionGuard permission="users:create">
            <button
              onClick={handleAddUser}
              className="px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white shadow-sm hover:shadow-md rounded-xl transition-all flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span>添加用户</span>
            </button>
          </PermissionGuard>
        }
      />

      {/* 用户统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">总用户数</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{users.length}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-xl">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">活跃用户</p>
              <p className="text-2xl font-bold text-green-600 mt-1">
                {users.filter(u => u.is_active).length}
              </p>
            </div>
            <div className="p-3 bg-green-100 rounded-xl">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">管理员</p>
              <p className="text-2xl font-bold text-red-600 mt-1">
                {users.filter(u => u.role === "admin").length}
              </p>
            </div>
            <div className="p-3 bg-red-100 rounded-xl">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">交易员</p>
              <p className="text-2xl font-bold text-blue-600 mt-1">
                {users.filter(u => u.role === "trader").length}
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-xl">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* 用户列表表格 */}
      <div className="bg-white rounded-xl shadow border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  用户
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  角色
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  状态
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  最后登录
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  创建时间
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  操作
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10">
                        <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                          <span className="text-blue-600 font-medium text-sm">
                            {user.username.charAt(0).toUpperCase()}
                          </span>
                        </div>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {user.username}
                        </div>
                        <div className="text-sm text-gray-500">{user.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getRoleBadgeColor(user.role)}`}>
                      {getRoleLabel(user.role)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      user.is_active 
                        ? "bg-green-100 text-green-800" 
                        : "bg-gray-100 text-gray-800"
                    }`}>
                      {user.is_active ? "活跃" : "禁用"}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {user.last_login ? formatDateTime(user.last_login) : "从未登录"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDateTime(user.created_at)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end space-x-2">
                      <PermissionGuard permission="users:update">
                        <button
                          onClick={() => handleEditUser(user)}
                          className="text-blue-600 hover:text-blue-900"
                          title="编辑"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                      </PermissionGuard>
                      
                      <PermissionGuard permission="users:update">
                        {!(user.username === "admin" && user.is_active) && (
                          <button
                            onClick={() => handleToggleActive(user)}
                            className={user.is_active ? "text-yellow-600 hover:text-yellow-900" : "text-green-600 hover:text-green-900"}
                            title={user.is_active ? "禁用" : "启用"}
                          >
                            {user.is_active ? (
                              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                              </svg>
                            ) : (
                              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                            )}
                          </button>
                        )}
                      </PermissionGuard>
                      
                      <PermissionGuard permission="users:delete">
                        {user.username !== "admin" && (
                          <button
                            onClick={() => handleDeleteUser(user)}
                            className="text-red-600 hover:text-red-900"
                            title="删除"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        )}
                      </PermissionGuard>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 添加/编辑用户模态框 */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full mx-4">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">
                {editingUser ? "编辑用户" : "添加用户"}
              </h2>
            </div>
            
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  用户名 *
                </label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                  disabled={!!editingUser}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  密码 {editingUser ? "(留空则不修改)" : "*"}
                </label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required={!editingUser}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  邮箱 *
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  角色 *
                </label>
                <div className="grid grid-cols-2 gap-3 mb-3">
                  {roles.map((role) => (
                    <div
                      key={role.value}
                      onClick={() => {
                        setFormData({ ...formData, role: role.value });
                        loadRolePermissions(role.value);
                      }}
                      className={`p-3 border-2 rounded-xl cursor-pointer transition-all ${
                        formData.role === role.value
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="font-medium text-sm text-gray-900">{role.label}</div>
                      <div className="text-xs text-gray-600 mt-1">{role.description}</div>
                      <div className="text-xs text-blue-600 mt-1">
                        {role.permission_count} 项权限
                      </div>
                    </div>
                  ))}
                </div>
                
                {/* 权限预览 */}
                {selectedRolePermissions && formData.role === selectedRolePermissions.role && (
                  <div className="bg-gray-50 border border-gray-200 rounded-xl p-3 max-h-40 overflow-y-auto">
                    <div className="text-xs font-medium text-gray-700 mb-2">
                      {selectedRolePermissions.display_name} 的权限：
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {selectedRolePermissions.permissions.map((perm) => (
                        <span
                          key={perm}
                          className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded"
                        >
                          {perm}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="is_active" className="ml-2 block text-sm text-gray-700">
                  启用用户
                </label>
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-xl text-gray-700 hover:bg-gray-50"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white shadow-sm hover:shadow-md rounded-xl"
                >
                  {editingUser ? "更新" : "创建"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

