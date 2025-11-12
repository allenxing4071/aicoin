"use client";

import React, { createContext, useContext, useMemo } from 'react';
import { usePermissions as usePermissionsHook } from '../hooks/usePermissions';

interface PermissionsContextType {
  user: any;
  permissions: string[];
  loading: boolean;
  hasPermission: (permission: string) => boolean;
  hasAnyPermission: (...perms: string[]) => boolean;
  hasAllPermissions: (...perms: string[]) => boolean;
  isRole: (role: string) => boolean;
  isAnyRole: (...roles: string[]) => boolean;
  refresh: () => void;
  userRole: string | undefined;
}

const PermissionsContext = createContext<PermissionsContextType | undefined>(undefined);

export function PermissionsProvider({ children }: { children: React.ReactNode }) {
  const permissionsData = usePermissionsHook();
  
  // 使用useMemo稳定整个context value，避免不必要的重渲染
  // 由于所有函数都已经用useCallback包装，它们的引用是稳定的
  const value = useMemo(() => ({
    ...permissionsData,
    permissions: permissionsData.permissions || []
  }), [
    permissionsData.user,
    permissionsData.permissions?.join(','), // 使用字符串作为稳定依赖
    permissionsData.loading,
    permissionsData.userRole,
    permissionsData.hasPermission,
    permissionsData.hasAnyPermission,
    permissionsData.hasAllPermissions,
    permissionsData.isRole,
    permissionsData.isAnyRole,
    permissionsData.refresh
  ]);
  
  return (
    <PermissionsContext.Provider value={value}>
      {children}
    </PermissionsContext.Provider>
  );
}

export function usePermissions() {
  const context = useContext(PermissionsContext);
  if (context === undefined) {
    throw new Error('usePermissions must be used within a PermissionsProvider');
  }
  return context;
}

