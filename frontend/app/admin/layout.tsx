"use client";

import React, { ReactNode, useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import AuthGuard from "./AuthGuard";
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
} from "@ant-design/icons";
import type { MenuProps } from "antd";

const { Sider, Content, Header } = Layout;

interface AdminLayoutProps {
  children: ReactNode;
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [username, setUsername] = useState<string | null>(null);
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    const user = localStorage.getItem("admin_user");
    setUsername(user);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("admin_token");
    localStorage.removeItem("admin_user");
    router.push("/admin/login");
  };

  // 如果是登录页面,不显示layout
  if (pathname === "/admin/login") {
    return <AuthGuard>{children}</AuthGuard>;
  }

  // 菜单项配置 - 智能化命名
  const menuItems: MenuProps["items"] = [
    {
      key: "/admin",
      icon: <DashboardOutlined />,
      label: <Link href="/admin">智能驾驶舱</Link>,
    },
    {
      key: "exchange-group",
      icon: <SwapOutlined />,
      label: "交易网关",
      children: [
        {
          key: "/admin/exchanges",
          label: <Link href="/admin/exchanges">交易所接入</Link>,
        },
      ],
    },
    {
      key: "intelligence-group",
      icon: <FileSearchOutlined />,
      label: "情报中枢",
      children: [
        {
          key: "/admin/intelligence",
          label: <Link href="/admin/intelligence">情报源配置</Link>,
        },
      ],
    },
    {
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
    },
    {
      key: "memory-group",
      icon: <BulbOutlined />,
      label: "神经网络",
      children: [
        {
          key: "/admin/memory",
          label: <Link href="/admin/memory">记忆矩阵</Link>,
        },
      ],
    },
    {
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
    },
    {
      key: "data-management-group",
      icon: <DatabaseOutlined />,
      label: "数据湖",
      children: [
        {
          key: "/admin/market-data",
          label: <Link href="/admin/market-data">市场行情</Link>,
        },
      ],
    },
    {
      key: "system-management-group",
      icon: <SettingOutlined />,
      label: "系统控制",
      children: [
        {
          key: "/admin/risk-events",
          label: <Link href="/admin/risk-events">风控预警</Link>,
        },
        {
          key: "/admin/permissions",
          label: <Link href="/admin/permissions">权限矩阵</Link>,
        },
        {
          key: "/admin/users",
          label: <Link href="/admin/users">用户中心</Link>,
        },
      ],
    },
  ];

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
          {/* Logo区域 - 年轻化设计 + 折叠按钮 */}
          <div
            style={{
              height: "64px",
              display: "flex",
              alignItems: "center",
              justifyContent: collapsed ? "center" : "space-between",
              borderBottom: "1px solid #f0f0f0",
              padding: collapsed ? "0 24px" : "0 20px",
              gap: "12px",
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
              onClick={() => setCollapsed(!collapsed)}
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
            defaultOpenKeys={menuItems
              .filter((item: any) => item?.children)
              .map((item: any) => item.key as string)}
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

            {/* 右侧：操作按钮 */}
            <Space size="small">
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
                  console.log("跳转到个人中心");
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
