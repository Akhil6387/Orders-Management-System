import { useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, Typography, Space } from 'antd'
import {
  DashboardOutlined,
  AppstoreOutlined,
  TeamOutlined,
  ShoppingCartOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons'

const { Sider, Content, Header } = Layout
const { Text } = Typography

const NAV = [
  { key: '/dashboard', icon: <DashboardOutlined />, label: 'Dashboard' },
  { key: '/products',  icon: <AppstoreOutlined />,  label: 'Products' },
  { key: '/customers', icon: <TeamOutlined />,       label: 'Customers' },
  { key: '/orders',    icon: <ShoppingCartOutlined />, label: 'Orders' },
]

const PAGE_TITLES = {
  '/dashboard': 'Dashboard',
  '/products':  'Products',
  '/customers': 'Customers',
  '/orders':    'Orders',
}

export default function MainLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const activeKey = '/' + pathname.split('/')[1]

  return (
    <Layout style={{ height: '100vh', overflow: 'hidden' }}>
      {/* ── SIDEBAR ── */}
      <Sider
        collapsible
        collapsed={collapsed}
        trigger={null}
        width={220}
        collapsedWidth={64}
        style={{ overflow: 'auto', display: 'flex', flexDirection: 'column' }}
      >
        {/* Logo */}
        <div style={{
          padding: collapsed ? '20px 16px' : '20px 20px 16px',
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          transition: 'padding 0.2s',
        }}>
          <LogoMark />
          {!collapsed && (
            <div>
              <Text style={{ color: 'var(--text-primary)', fontWeight: 700, fontSize: 16, letterSpacing: '-0.02em', display: 'block' }}>
                Stockflow
              </Text>
              <Text style={{ color: 'var(--text-muted)', fontSize: 10, letterSpacing: '0.08em', textTransform: 'uppercase' }}>
                Inventory Suite
              </Text>
            </div>
          )}
        </div>

        {/* Navigation */}
        <Menu
          mode="inline"
          selectedKeys={[activeKey]}
          onClick={({ key }) => navigate(key)}
          style={{ padding: '8px 0', flex: 1 }}
          items={NAV.map(({ key, icon, label }) => ({ key, icon, label }))}
        />

        {/* Collapse trigger */}
        <div
          onClick={() => setCollapsed(!collapsed)}
          style={{
            padding: '14px 20px',
            cursor: 'pointer',
            color: 'var(--text-muted)',
            borderTop: '1px solid var(--border)',
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            transition: 'color 0.15s',
          }}
          onMouseEnter={(e) => e.currentTarget.style.color = 'var(--text-primary)'}
          onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-muted)'}
        >
          {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          {!collapsed && <Text style={{ color: 'inherit', fontSize: 13 }}>Collapse</Text>}
        </div>
      </Sider>

      {/* ── MAIN ── */}
      <Layout>
        {/* Header */}
        <Header style={{
          height: 56,
          lineHeight: '56px',
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <Text style={{ color: 'var(--text-primary)', fontWeight: 600, fontSize: 18, letterSpacing: '-0.01em' }}>
            {PAGE_TITLES[activeKey] || 'Stockflow'}
          </Text>

          <Space>
            <div style={{
              width: 8, height: 8, borderRadius: '50%',
              background: 'var(--green)',
              boxShadow: '0 0 6px var(--green)',
            }} />
            <Text style={{ color: 'var(--text-muted)', fontSize: 12 }}>API Connected</Text>
          </Space>
        </Header>

        {/* Content */}
        <Content style={{
          overflow: 'auto',
          padding: 24,
          background: 'var(--bg-base)',
        }}>
          <div className="page-enter">
            <Outlet />
          </div>
        </Content>
      </Layout>
    </Layout>
  )
}

function LogoMark() {
  return (
    <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
      <rect width="28" height="28" rx="7" fill="#0F172A"/>
      <rect x="5" y="7" width="7" height="7" rx="1" fill="#38BDF8"/>
      <rect x="16" y="7" width="7" height="7" rx="1" fill="#38BDF8" opacity="0.45"/>
      <rect x="5" y="16" width="7" height="7" rx="1" fill="#38BDF8" opacity="0.45"/>
      <rect x="16" y="16" width="7" height="7" rx="1" fill="#F472B6"/>
    </svg>
  )
}
