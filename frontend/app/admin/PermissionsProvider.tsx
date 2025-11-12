"use client";

import React, { createContext, useContext } from 'react';
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
  const permissions = usePermissionsHook();
  
  return (
    <PermissionsContext.Provider value={permissions}>
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

