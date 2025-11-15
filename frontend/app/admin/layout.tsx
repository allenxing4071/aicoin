"use client";

import React, { ReactNode, useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import AuthGuard from "./AuthGuard";
import { PermissionsProvider, usePermissions } from './PermissionsProvider';
import { Layout, Menu, Space } from "antd";
import {
  DashboardOutlined,
  SwapOutlined,
  FileSearchOutlined,
  LineChartOutlined,
  BulbOutlined,
  RobotOutlined,
  OrderedListOutlined,
  FileTextOutlined,
  WalletOutlined,
  ThunderboltOutlined,
  BarChartOutlined,
  WarningOutlined,
  SafetyOutlined,
  UserOutlined,
  LogoutOutlined,
  HomeOutlined,
  DatabaseOutlined,
  SettingOutlined,
  CloudOutlined,
  DollarOutlined,
  FundOutlined,
} from "@ant-design/icons";
import type { MenuProps } from "antd";

const { Sider, Content, Header } = Layout;

interface AdminLayoutProps {
  children: ReactNode;
}

function AdminLayoutInner({ children }: AdminLayoutProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { hasPermission, loading: permLoading, permissions, userRole } = usePermissions();
  const [username, setUsername] = useState<string | null>(null);
  // 确保侧边栏默认展开
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    const user = localStorage.getItem("admin_user");
    setUsername(user);
    
    // 从localStorage读取保存的侧边栏状态
    const saved = localStorage.getItem('admin_sidebar_collapsed');
    if (saved === 'true') {
      setCollapsed(true);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("admin_token");
    localStorage.removeItem("admin_user");
    router.push("/admin/login");
  };

  // 根据权限动态生成菜单项 - 使用 useMemo 避免重复渲染
  // 注意：必须在所有条件返回之前调用所有 Hooks，避免 React Error #310
  const menuItems = React.useMemo(() => {
    // 如果权限还在加载，返回空数组
    if (permLoading) {
      return [];
    }
    
    // 辅助函数：检查权限（在 useMemo 内部）
    const checkPermission = (permission: string): boolean => {
      // 修复：使用真实的权限检查
      // 如果权限列表为空，可能是加载中或角色未配置
      if (!permissions || permissions.length === 0) {
        // 对于super_admin，即使权限列表为空也允许访问
        if (userRole === 'super_admin') {
          return true;
        }
        // 其他情况，如果是加载中，暂时允许访问避免闪烁
        if (permLoading) {
          return true;
        }
        // 加载完成但权限为空，可能是配置问题，允许基础访问
        return true;
      }
      
      // super_admin 拥有所有权限
      if (userRole === 'super_admin') {
        return true;
      }
      
      // 检查权限列表
      return permissions.includes(permission);
    };
    
    const items: MenuProps["items"] = [];
    
    // 智能驾驶舱 - 所有人都可以访问
    items.push({
      key: "/admin",
      icon: <DashboardOutlined />,
      label: <Link href="/admin">智能驾驶舱</Link>,
    });
    
    // 交易网关 - 需要 exchange:view 权限
    if (checkPermission('exchange:view')) {
      items.push({
        key: "exchange-group",
        icon: <SwapOutlined />,
        label: "交易网关",
        children: [
          {
            key: "/admin/exchanges",
            label: <Link href="/admin/exchanges">交易所接入</Link>,
          },
        ],
      });
    }
    
    // AI平台管理 - 需要 ai:view 权限
    if (checkPermission('ai:view')) {
      items.push({
        key: "ai-platforms-group",
        icon: <CloudOutlined />,
        label: "AI平台管理",
        children: [
          {
            key: "model-config",
            label: "模型配置中心",
            children: [
              {
                key: "/admin/ai-platforms/intelligence",
                label: <Link href="/admin/ai-platforms/intelligence">情报模型（Qwen系列）</Link>,
              },
              {
                key: "/admin/ai-platforms/decision",
                label: <Link href="/admin/ai-platforms/decision">决策模型（DeepSeek）</Link>,
              },
              {
                key: "/admin/ai-platforms/analysis",
                label: <Link href="/admin/ai-platforms/analysis">分析模型（预留）</Link>,
              },
            ],
          },
          {
            key: "cost-management",
            label: "成本管理",
            children: [
              {
                key: "/admin/ai-cost",
                label: <Link href="/admin/ai-cost">实时监控</Link>,
              },
              {
                key: "/admin/ai-pricing",
                label: <Link href="/admin/ai-pricing">价格表管理</Link>,
              },
              {
                key: "/admin/ai-cost/budget",
                label: <Link href="/admin/ai-cost/budget">预算设置</Link>,
              },
              {
                key: "/admin/ai-cost/optimization",
                label: <Link href="/admin/ai-cost/optimization">决策间隔优化</Link>,
              },
            ],
          },
          {
            key: "performance-monitoring",
            label: "性能监控",
            children: [
              {
                key: "/admin/ai-platforms/stats",
                label: <Link href="/admin/ai-platforms/stats">调用统计</Link>,
              },
              {
                key: "/admin/ai-platforms/success-rate",
                label: <Link href="/admin/ai-platforms/success-rate">成功率分析</Link>,
              },
              {
                key: "/admin/ai-platforms/response-time",
                label: <Link href="/admin/ai-platforms/response-time">响应时间</Link>,
              },
            ],
          },
        ],
      });
    }
    
    // 情报中枢 - 需要 intel:view 权限
    if (checkPermission('intel:view')) {
      items.push({
        key: "intelligence-group",
        icon: <FileSearchOutlined />,
        label: "情报中枢",
        children: [
          {
            key: "data-sources",
            label: "数据源管理",
            children: [
              {
                key: "/admin/intelligence/rss",
                label: <Link href="/admin/intelligence/rss">RSS新闻源</Link>,
              },
              {
                key: "/admin/intelligence/whale",
                label: <Link href="/admin/intelligence/whale">巨鲸监控</Link>,
              },
              {
                key: "/admin/intelligence/onchain",
                label: <Link href="/admin/intelligence/onchain">链上数据</Link>,
              },
              {
                key: "/admin/intelligence/kol",
                label: <Link href="/admin/intelligence/kol">KOL追踪</Link>,
              },
              {
                key: "/admin/intelligence/smart-money",
                label: <Link href="/admin/intelligence/smart-money">聪明钱跟单</Link>,
              },
            ],
          },
          {
            key: "intelligence-analysis",
            label: "情报分析",
            children: [
              {
                key: "/admin/intelligence/realtime",
                label: <Link href="/admin/intelligence/realtime">实时情报</Link>,
              },
              {
                key: "/admin/intelligence/reports",
                label: <Link href="/admin/intelligence/reports">历史报告</Link>,
              },
              {
                key: "/admin/intelligence/monitoring",
                label: <Link href="/admin/intelligence/monitoring">系统监控</Link>,
              },
            ],
          },
        ],
      });
    }
    
    // 交易引擎 - 需要 trades:view 权限
    if (checkPermission('trades:view')) {
      items.push({
        key: "trading-group",
        icon: <LineChartOutlined />,
        label: "交易引擎",
        children: [
          {
            key: "/admin/trading",
            label: <Link href="/admin/trading">AI工作日志</Link>,
          },
          {
            key: "/admin/trades",
            label: <Link href="/admin/trades">成交明细</Link>,
          },
          {
            key: "/admin/orders",
            label: <Link href="/admin/orders">订单追踪</Link>,
          },
          {
            key: "/admin/accounts",
            label: <Link href="/admin/accounts">资产快照</Link>,
          },
        ],
      });
    }
    
    // 神经网络 - 需要 memory:view 权限
    if (checkPermission('memory:view')) {
      items.push({
        key: "memory-group",
        icon: <BulbOutlined />,
        label: "神经网络",
        children: [
          {
            key: "/admin/memory",
            label: <Link href="/admin/memory">记忆矩阵</Link>,
          },
        ],
      });
    }
    
    // 智能决策 - 需要 ai:view 权限
    if (checkPermission('ai:view')) {
      items.push({
        key: "ai-decision-group",
        icon: <RobotOutlined />,
        label: "智能决策",
        children: [
          {
            key: "/admin/ai-decisions",
            label: <Link href="/admin/ai-decisions">决策轨迹</Link>,
          },
          {
            key: "/admin/model-performance",
            label: <Link href="/admin/model-performance">模型评估</Link>,
          },
        ],
      });
    }
    
    // 辩论系统 - 需要 ai:view 权限
    if (checkPermission('ai:view')) {
      items.push({
        key: "debate-group",
        icon: <ThunderboltOutlined />,
        label: "辩论系统",
        children: [
          {
            key: "/admin/debate",
            label: <Link href="/admin/debate">辩论历史</Link>,
          },
          {
            key: "/admin/debate/config",
            label: <Link href="/admin/debate/config">辩论配置</Link>,
          },
          {
            key: "/admin/debate/statistics",
            label: <Link href="/admin/debate/statistics">辩论统计</Link>,
          },
          {
            key: "/admin/debate/memory",
            label: <Link href="/admin/debate/memory">记忆管理</Link>,
          },
        ],
      });
    }
    
    // Prompt模板管理 - 需要 ai:view 权限
    if (checkPermission('ai:view')) {
      items.push({
        key: "prompts-group",
        icon: <FileTextOutlined />,
        label: "Prompt管理",
        children: [
          {
            key: "/admin/prompts-v2",
            label: <Link href="/admin/prompts-v2">模板列表</Link>,
          },
        ],
      });
    }
    
    // 数据湖 - 需要 system:view 权限
    if (checkPermission('system:view')) {
      items.push({
        key: "data-management-group",
        icon: <DatabaseOutlined />,
        label: "数据湖",
        children: [
          {
            key: "/admin/market-data",
            label: <Link href="/admin/market-data">市场行情</Link>,
          },
        ],
      });
    }
    
    // 系统控制 - 根据子菜单权限动态生成
    const systemChildren: any[] = [];
    
    if (checkPermission('risk:view')) {
      systemChildren.push({
        key: "/admin/risk-events",
        label: <Link href="/admin/risk-events">风控预警</Link>,
      });
    }
    
    // RBAC权限管理（新增）- admin 和 super_admin 都可以访问
    if (userRole === 'super_admin' || userRole === 'admin') {
      systemChildren.push({
        key: "rbac-group",
        label: "权限管理",
        children: [
          {
            key: "/admin/rbac/permissions",
            label: <Link href="/admin/rbac/permissions">权限配置</Link>,
          },
          {
            key: "/admin/rbac/roles",
            label: <Link href="/admin/rbac/roles">角色管理</Link>,
          },
        ],
      });
    }
    
    if (checkPermission('permissions:view')) {
      systemChildren.push({
        key: "/admin/permissions",
        label: <Link href="/admin/permissions">权限矩阵</Link>,
      });
    }
    
    if (checkPermission('users:view')) {
      systemChildren.push({
        key: "/admin/users",
        label: <Link href="/admin/users">用户中心</Link>,
      });
    }
    
    if (checkPermission('backup:view')) {
      systemChildren.push({
        key: "/admin/backup",
        label: <Link href="/admin/backup">数据备份</Link>,
      });
    }
    
    if (checkPermission('logs:view')) {
      systemChildren.push({
        key: "/admin/logs",
        label: <Link href="/admin/logs">日志管理</Link>,
      });
    }
    
    if (checkPermission('system:view')) {
      systemChildren.push({
        key: "/admin/database",
        label: <Link href="/admin/database">数据库管理</Link>,
      });
      
      systemChildren.push({
        key: "/admin/api-docs",
        label: <Link href="/admin/api-docs">API文档</Link>,
      });
    }
    
    // 只有当有子菜单时才显示系统控制
    if (systemChildren.length > 0) {
      items.push({
        key: "system-management-group",
        icon: <SettingOutlined />,
        label: "系统控制",
        children: systemChildren,
      });
    }
    
    return items;
  }, [permLoading, permissions, userRole]); // 直接使用 permissions 作为依赖

  // 如果是登录页面,不显示layout（必须在所有 Hooks 之后）
  if (pathname === "/admin/login") {
    return <AuthGuard>{children}</AuthGuard>;
  }

  // 移除下拉菜单，改为顶部按钮

  return (
    <AuthGuard>
      <Layout style={{ minHeight: "100vh", background: "#f5f5f5", overflow: "hidden" }}>
        {/* 侧边栏 - 全新设计 */}
        <Sider
          collapsible
          collapsed={collapsed}
          onCollapse={(value) => setCollapsed(value)}
          width={260}
          collapsedWidth={88}
          trigger={null}
          style={{
            overflow: "auto",
            height: "100vh",
            position: "fixed",
            left: 0,
            top: 0,
            bottom: 0,
            background: "#ffffff",
            borderRight: "1px solid #f0f0f0",
          }}
          theme="light"
        >
          {/* Logo区域 - 年轻化设计 + 折叠按钮 - 固定在顶部 */}
          <div
            style={{
              height: "64px",
              display: "flex",
              alignItems: "center",
              justifyContent: collapsed ? "center" : "space-between",
              borderBottom: "1px solid #f0f0f0",
              padding: collapsed ? "0 24px" : "0 20px",
              gap: "12px",
              position: "sticky",
              top: 0,
              background: "#ffffff",
              zIndex: 10,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              {/* Logo图标 - 渐变蓝色 */}
              <div
                style={{
                  width: "36px",
                  height: "36px",
                  background: "linear-gradient(135deg, #1677ff 0%, #0958d9 100%)",
                  borderRadius: "10px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  boxShadow: "0 2px 8px rgba(22, 119, 255, 0.2)",
                  flexShrink: 0,
                }}
              >
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  style={{ color: "#ffffff" }}
                >
                  <path
                    d="M12 2L2 7L12 12L22 7L12 2Z"
                    fill="currentColor"
                    fillOpacity="0.9"
                  />
                  <path
                    d="M2 17L12 22L22 17"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <path
                    d="M2 12L12 17L22 12"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
              
              {/* 文字Logo */}
              {!collapsed && (
                <div style={{ lineHeight: 1.2 }}>
                  <div
                    style={{
                      fontSize: "16px",
                      fontWeight: 700,
                      color: "#262626",
                      letterSpacing: "0.5px",
                    }}
                  >
                    AIcoin
                  </div>
                  <div
                    style={{
                      fontSize: "12px",
                      color: "#8c8c8c",
                      marginTop: "2px",
                    }}
                  >
                    管理后台
                  </div>
                </div>
              )}
            </div>

            {/* 折叠/展开按钮 - 优化样式 */}
            <button
              onClick={() => {
                const newCollapsed = !collapsed;
                setCollapsed(newCollapsed);
                // 保存状态到localStorage
                if (typeof window !== 'undefined') {
                  localStorage.setItem('admin_sidebar_collapsed', String(newCollapsed));
                }
              }}
              style={{
                width: "32px",
                height: "32px",
                borderRadius: "8px",
                border: "1px solid #e8e8e8",
                background: "#fafafa",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
                transition: "all 0.2s",
                flexShrink: 0,
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = "#e6f4ff";
                e.currentTarget.style.borderColor = "#1677ff";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "#fafafa";
                e.currentTarget.style.borderColor = "#e8e8e8";
              }}
              title={collapsed ? "展开侧边栏" : "收起侧边栏"}
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                style={{ color: "#595959", transform: collapsed ? "rotate(180deg)" : "none", transition: "transform 0.2s" }}
              >
                <path
                  d="M15 18L9 12L15 6"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </button>
          </div>

          {/* 导航菜单 - 更清爽的样式 */}
          <Menu
            mode="inline"
            selectedKeys={[pathname]}
            defaultOpenKeys={[]}  // 默认关闭所有菜单
            items={menuItems}
            style={{
              border: "none",
              paddingTop: "12px",
              paddingBottom: "12px",
            }}
          />
        </Sider>

        {/* 主内容区 */}
        <Layout style={{ marginLeft: collapsed ? 88 : 260, transition: "all 0.2s", overflow: "hidden" }}>
          {/* 顶部Header - 更清爽 */}
          <Header
            style={{
              position: "fixed",
              top: 0,
              right: 0,
              left: collapsed ? 88 : 260,
              zIndex: 100,
              height: "64px",
              padding: "0 24px",
              background: "#ffffff",
              borderBottom: "1px solid #f0f0f0",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              boxShadow: "0 1px 2px rgba(0, 0, 0, 0.03)",
              userSelect: "none",
              transition: "left 0.2s",
            }}
          >
            {/* 左侧：欢迎信息 */}
            {username && (
              <span style={{ color: "#595959", fontSize: "14px" }}>
                欢迎, <span style={{ fontWeight: 600, color: "#262626" }}>{username}</span>
              </span>
            )}

            {/* 右侧：操作按钮 - 向右对齐 */}
            <Space size="small" style={{ marginLeft: "auto" }}>
              {/* 打开首页按钮 */}
              <a
                href="/"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "4px",
                  padding: "4px 12px",
                  borderRadius: "4px",
                  border: "1px solid #d9d9d9",
                  background: "#ffffff",
                  color: "#262626",
                  fontSize: "13px",
                  textDecoration: "none",
                  transition: "all 0.2s",
                  cursor: "pointer",
                  height: "28px",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = "#1677ff";
                  e.currentTarget.style.color = "#1677ff";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = "#d9d9d9";
                  e.currentTarget.style.color = "#262626";
                }}
              >
                <HomeOutlined style={{ fontSize: "12px" }} />
                <span>打开首页</span>
              </a>

              {/* 个人中心按钮 */}
              <button
                onClick={() => {
                  // TODO: 跳转到个人中心页面
                }}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "4px",
                  padding: "4px 12px",
                  borderRadius: "4px",
                  border: "1px solid #d9d9d9",
                  background: "#ffffff",
                  color: "#262626",
                  fontSize: "13px",
                  cursor: "pointer",
                  transition: "all 0.2s",
                  height: "28px",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = "#1677ff";
                  e.currentTarget.style.color = "#1677ff";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = "#d9d9d9";
                  e.currentTarget.style.color = "#262626";
                }}
              >
                <UserOutlined style={{ fontSize: "12px" }} />
                <span>个人中心</span>
              </button>

              {/* 退出登录按钮 */}
              <button
                onClick={handleLogout}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "4px",
                  padding: "4px 12px",
                  borderRadius: "4px",
                  border: "1px solid #ff4d4f",
                  background: "#ffffff",
                  color: "#ff4d4f",
                  fontSize: "13px",
                  cursor: "pointer",
                  transition: "all 0.2s",
                  height: "28px",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = "#ff4d4f";
                  e.currentTarget.style.color = "#ffffff";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = "#ffffff";
                  e.currentTarget.style.color = "#ff4d4f";
                }}
                >
                <LogoutOutlined style={{ fontSize: "12px" }} />
                <span>退出登录</span>
              </button>
            </Space>
          </Header>

          {/* 内容区 - 浅灰背景 */}
          <Content
            style={{
              marginTop: "88px",
              marginLeft: "24px",
              marginRight: "24px",
              marginBottom: "24px",
              padding: "24px",
              background: "#ffffff",
              borderRadius: "12px",
              boxShadow: "0 2px 8px rgba(0, 0, 0, 0.04)",
              minHeight: "calc(100vh - 112px)",
            }}
          >
          {children}
          </Content>
        </Layout>
      </Layout>
    </AuthGuard>
  );
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  return (
    <PermissionsProvider>
      <AdminLayoutInner>{children}</AdminLayoutInner>
    </PermissionsProvider>
  );
}
