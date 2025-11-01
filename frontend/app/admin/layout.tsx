"use client";

import { ReactNode, useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import AuthGuard from "./AuthGuard";

interface AdminLayoutProps {
  children: ReactNode;
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [username, setUsername] = useState<string | null>(null);

  useEffect(() => {
    const user = localStorage.getItem("admin_user");
    setUsername(user);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("admin_token");
    localStorage.removeItem("admin_user");
    router.push("/admin/login");
  };

  const navItems = [
    { name: "概览", path: "/admin" },
    { name: "三层记忆", path: "/admin/memory" },
    { name: "交易记录", path: "/admin/trades" },
    { name: "订单记录", path: "/admin/orders" },
    { name: "账户快照", path: "/admin/accounts" },
    { name: "AI决策", path: "/admin/ai-decisions" },
    { name: "K线数据", path: "/admin/market-data" },
    { name: "风控事件", path: "/admin/risk-events" },
  ];

  // 如果是登录页面,不显示layout
  if (pathname === "/admin/login") {
    return <AuthGuard>{children}</AuthGuard>;
  }

  return (
    <AuthGuard>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center space-x-4">
                <h1 className="text-2xl font-bold text-gray-900">
                  AIcoin 管理后台
                </h1>
                <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                  只读模式
                </span>
              </div>
              <div className="flex items-center space-x-4">
                {username && (
                  <span className="text-sm text-gray-600">
                    欢迎, <span className="font-medium">{username}</span>
                  </span>
                )}
                <Link
                  href="/"
                  className="text-sm text-gray-600 hover:text-gray-900"
                >
                  返回主页
                </Link>
                <button
                  onClick={handleLogout}
                  className="text-sm text-red-600 hover:text-red-700 font-medium"
                >
                  退出登录
                </button>
              </div>
            </div>
          </div>
        </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8 overflow-x-auto">
            {navItems.map((item) => {
              const isActive = pathname === item.path;
              return (
                <Link
                  key={item.path}
                  href={item.path}
                  className={`
                    py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap
                    ${
                      isActive
                        ? "border-blue-500 text-blue-600"
                        : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    }
                  `}
                >
                  {item.name}
                </Link>
              );
            })}
          </div>
        </div>
      </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
      </div>
    </AuthGuard>
  );
}

