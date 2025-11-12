/**
 * 权限管理 Hook
 * 提供权限检查和角色判断功能
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { jwtDecode } from 'jwt-decode';

interface User {
  username: string;
  role: string;
  email?: string;
}

interface JWTPayload {
  sub: string;  // username
  role: string;
  exp: number;
}

export function usePermissions() {
  const [user, setUser] = useState<User | null>(null);
  const [permissions, setPermissions] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    let isMounted = true;
    
    const loadUserInfo = async () => {
      try {
        const token = localStorage.getItem('admin_token');
        if (!token) {
          if (isMounted) {
            setUser(null);
            setPermissions([]);
            setLoading(false);
          }
          return;
        }
        
        // 解析JWT获取用户信息
        const decoded = jwtDecode<JWTPayload>(token);
        const userInfo: User = {
          username: decoded.sub,
          role: decoded.role,
        };
        if (isMounted) {
          setUser(userInfo);
        }
        
        // 从API获取角色的权限列表
        try {
          const response = await fetch(
            `/api/v1/admin/users/roles/${decoded.role}/permissions`,
            {
              headers: {
                'Authorization': `Bearer ${token}`
              }
            }
          );
          
          if (response.ok && isMounted) {
            const data = await response.json();
            if (data.success && data.data.permissions) {
              setPermissions(data.data.permissions);
            }
          }
        } catch (error) {
          console.error('获取权限列表失败:', error);
        }
        
        if (isMounted) {
          setLoading(false);
        }
      } catch (error) {
        console.error('解析用户信息失败:', error);
        if (isMounted) {
          setUser(null);
          setPermissions([]);
          setLoading(false);
        }
      }
    };
    
    loadUserInfo();
    
    return () => {
      isMounted = false;
    };
  }, []); // 只在组件挂载时执行一次
  
  /**
   * 检查是否有指定权限
   */
  const hasPermission = useCallback((permission: string): boolean => {
    // 加载中时，默认返回 true 避免重定向循环
    if (loading) return true;
    if (!user) return false;
    // super_admin 拥有所有权限
    if (user?.role === 'super_admin') return true;
    return permissions.includes(permission);
  }, [loading, user, permissions]);
  
  /**
   * 检查是否有任意一个指定权限
   */
  const hasAnyPermission = useCallback((...perms: string[]): boolean => {
    if (loading) return true; // 加载中默认允许
    if (!user) return false;
    if (user.role === 'super_admin') return true;
    return perms.some(p => permissions.includes(p));
  }, [loading, user, permissions]);
  
  /**
   * 检查是否有所有指定权限
   */
  const hasAllPermissions = useCallback((...perms: string[]): boolean => {
    if (loading) return true; // 加载中默认允许
    if (!user) return false;
    if (user.role === 'super_admin') return true;
    return perms.every(p => permissions.includes(p));
  }, [loading, user, permissions]);
  
  /**
   * 检查是否是指定角色
   */
  const isRole = useCallback((role: string): boolean => {
    if (loading) return true; // 加载中默认允许
    return user?.role === role;
  }, [loading, user]);
  
  /**
   * 检查是否是任意一个指定角色
   */
  const isAnyRole = useCallback((...roles: string[]): boolean => {
    if (loading) return true; // 加载中默认允许
    if (!user) return false;
    return roles.includes(user.role);
  }, [loading, user]);
  
  /**
   * 刷新权限信息
   */
  const refresh = useCallback(() => {
    // 强制刷新：清空状态并重新加载
    setLoading(true);
    setTimeout(() => {
      window.location.reload();
    }, 100);
  }, []);
  
  return {
    user,
    permissions,
    loading,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    isRole,
    isAnyRole,
    refresh,
    // 导出 user.role 供 useMemo 使用
    userRole: user?.role,
  };
}

