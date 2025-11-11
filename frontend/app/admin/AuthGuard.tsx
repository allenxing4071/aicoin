"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // 如果是登录页面,直接显示,不需要认证
    if (pathname === "/admin/login") {
      setIsAuthenticated(true);
      setIsLoading(false);
      return;
    }

    // 检查是否有token
    const token = localStorage.getItem("admin_token");
    
    // 正式模式：没有token直接跳转登录页
    if (!token) {
      router.push("/admin/login");
      setIsLoading(false);
      return;
    }

    // 只在首次加载时验证token，不在每次路由变化时验证
    if (isLoading) {
      validateToken(token);
    } else {
      // 已经验证过，直接设置为已认证
      setIsAuthenticated(true);
    }
  }, [pathname, router, isLoading]);

  const validateToken = async (token: string) => {
    try {
      // 正式模式：向后端验证 token 是否有效
      const response = await fetch("/api/v1/admin/verify", {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (response.ok) {
      setIsAuthenticated(true);
      } else {
        // token无效，清除并跳转到登录页
        console.warn("Token验证失败，跳转到登录页");
        localStorage.removeItem("admin_token");
        localStorage.removeItem("admin_user");
        router.push("/admin/login");
      }
    } catch (error) {
      console.error("Token validation failed:", error);
      // 网络错误时也跳转到登录页（安全优先）
      localStorage.removeItem("admin_token");
      localStorage.removeItem("admin_user");
      router.push("/admin/login");
    } finally {
      setIsLoading(false);
    }
  };

  // 登录页面直接显示
  if (pathname === "/admin/login") {
    return <>{children}</>;
  }

  // 加载中显示loading
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-gray-600">验证登录状态...</p>
        </div>
      </div>
    );
  }

  // 已认证显示内容
  if (isAuthenticated) {
    return <>{children}</>;
  }

  // 未认证不显示任何内容(会被重定向)
  return null;
}

