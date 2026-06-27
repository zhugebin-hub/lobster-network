/**
 * 主布局组件
 */

import React from 'react';
import { Layout, Menu, Avatar, Dropdown, Space } from 'antd';
import {
  DashboardOutlined,
  TeamOutlined,
  CheckSquareOutlined,
  SafetyOutlined,
  WalletOutlined,
  UserOutlined,
  MoonOutlined,
  SunOutlined,
} from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';

const { Header, Sider, Content } = Layout;

interface AppLayoutProps {
  children: React.ReactNode;
  darkMode: boolean;
  toggleDarkMode: () => void;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children, darkMode, toggleDarkMode }) => {
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: <Link to="/">仪表盘</Link>,
    },
    {
      key: '/nodes',
      icon: <TeamOutlined />,
      label: <Link to="/nodes">节点管理</Link>,
    },
    {
      key: '/tasks',
      icon: <CheckSquareOutlined />,
      label: <Link to="/tasks">任务管理</Link>,
    },
    {
      key: '/governance',
      icon: <SafetyOutlined />,
      label: <Link to="/governance">治理提案</Link>,
    },
    {
      key: '/wallet',
      icon: <WalletOutlined />,
      label: <Link to="/wallet">钱包</Link>,
    },
  ];

  const userMenu = {
    items: [
      {
        key: 'profile',
        icon: <UserOutlined />,
        label: '个人资料',
      },
      {
        key: 'settings',
        label: '设置',
      },
      {
        type: 'divider' as const,
      },
      {
        key: 'logout',
        label: '退出登录',
      },
    ],
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        theme={darkMode ? 'dark' : 'light'}
        breakpoint="lg"
        collapsedWidth="80"
        style={{
          position: 'sticky',
          top: 0,
          height: '100vh',
          left: 0,
        }}
      >
        <div style={{
          padding: '16px',
          textAlign: 'center',
          fontSize: '18px',
          fontWeight: 'bold',
        }}>
          🦞 小龙虾网络
        </div>
        <Menu
          theme={darkMode ? 'dark' : 'light'}
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
        />
      </Sider>
      <Layout>
        <Header style={{
          padding: '0 24px',
          background: darkMode ? '#141414' : '#fff',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <div />
          <Space>
            <a onClick={toggleDarkMode} style={{ cursor: 'pointer' }}>
              {darkMode ? <SunOutlined /> : <MoonOutlined />}
            </a>
            <Dropdown menu={userMenu}>
              <Avatar icon={<UserOutlined />} style={{ cursor: 'pointer' }} />
            </Dropdown>
          </Space>
        </Header>
        <Content style={{ margin: 24 }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};

export default AppLayout;
