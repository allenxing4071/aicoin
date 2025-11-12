/**
 * 权限保护组件
 * 根据用户权限控制子组件的显示
 */

import { ReactNode } from 'react';
import { usePermissions } from '../../hooks/usePermissions';

interface PermissionGuardProps {
  /** 需要的权限（单个或多个） */
  permission?: string | string[];
  /** 需要的角色（单个或多个） */
  role?: string | string[];
  /** 权限检查模式：'all' 需要所有权限，'any' 需要任意一个权限 */
  mode?: 'all' | 'any';
  /** 没有权限时显示的内容 */
  fallback?: ReactNode;
  /** 子组件 */
  children: ReactNode;
}

export function PermissionGuard({ 
  permission, 
  role,
  mode = 'all',
  fallback = null, 
  children 
}: PermissionGuardProps) {
  const { hasPermission, hasAnyPermission, hasAllPermissions, isRole, isAnyRole, loading } = usePermissions();
  
  // 加载中不显示任何内容
  if (loading) {
    return null;
  }
  
  let hasAccess = true;
  
  // 检查角色
  if (role) {
    if (Array.isArray(role)) {
      hasAccess = isAnyRole(...role);
    } else {
      hasAccess = isRole(role);
    }
  }
  
  // 检查权限
  if (hasAccess && permission) {
    if (Array.isArray(permission)) {
      if (mode === 'all') {
        hasAccess = hasAllPermissions(...permission);
      } else {
        hasAccess = hasAnyPermission(...permission);
      }
    } else {
      hasAccess = hasPermission(permission);
    }
  }
  
  if (!hasAccess) {
    return <>{fallback}</>;
  }
  
  return <>{children}</>;
}


/**
 * 权限按钮组件
 * 自动根据权限显示/隐藏按钮
 */
interface PermissionButtonProps {
  permission?: string | string[];
  role?: string | string[];
  mode?: 'all' | 'any';
  onClick?: () => void;
  className?: string;
  children: ReactNode;
  disabled?: boolean;
}

export function PermissionButton({
  permission,
  role,
  mode = 'all',
  onClick,
  className = '',
  children,
  disabled = false,
}: PermissionButtonProps) {
  return (
    <PermissionGuard permission={permission} role={role} mode={mode}>
      <button
        onClick={onClick}
        className={className}
        disabled={disabled}
      >
        {children}
      </button>
    </PermissionGuard>
  );
}

