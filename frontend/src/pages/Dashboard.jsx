import { Row, Col, Card, Typography, Table, Tag, Spin } from 'antd'
import {
  AppstoreOutlined,
  TeamOutlined,
  ShoppingCartOutlined,
  WarningOutlined,
} from '@ant-design/icons'
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import dayjs from 'dayjs'
import StatCard from '../components/common/StatCard'
import StockBadge from '../components/common/StockBadge'
import StatusBadge from '../components/common/StatusBadge'
import { useProducts } from '../hooks/useProducts'
import { useCustomers } from '../hooks/useCustomers'
import { useOrders } from '../hooks/useOrders'

const { Text } = Typography

// Custom chart tooltip
const ChartTooltip = ({ active, payload, label, prefix = '' }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background: 'var(--bg-elevated)',
      border: '1px solid var(--border)',
      borderRadius: 8,
      padding: '8px 12px',
    }}>
      <Text style={{ color: 'var(--text-muted)', fontSize: 11, display: 'block' }}>{label}</Text>
      <Text style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
        {prefix}{payload[0].value?.toLocaleString()}
      </Text>
    </div>
  )
}

function buildOrderTimeline(orders = []) {
  const map = {}
  orders.forEach(o => {
    const day = dayjs(o.created_at).format('MMM D')
    map[day] = (map[day] || 0) + 1
  })
  return Object.entries(map).slice(-7).map(([day, count]) => ({ day, count }))
}

function buildRevenueTimeline(orders = []) {
  const map = {}
  orders.forEach(o => {
    const day = dayjs(o.created_at).format('MMM D')
    map[day] = (map[day] || 0) + (o.total_amount || 0)
  })
  return Object.entries(map).slice(-7).map(([day, revenue]) => ({ day, revenue: +revenue.toFixed(2) }))
}

export default function Dashboard() {
  const { data: products, isLoading: pLoading } = useProducts({ limit: 200 })
  const { data: customers, isLoading: cLoading } = useCustomers({ limit: 200 })
  const { data: orders, isLoading: oLoading } = useOrders({ limit: 200 })

  const productList = products?.items || products || []
  const customerList = customers?.items || customers || []
  const orderList   = orders?.items || orders || []

  const lowStockProducts = productList.filter(p => p.quantity_in_stock <= 10)
  const totalRevenue = orderList.reduce((s, o) => s + (o.total_amount || 0), 0)

  const orderTimeline  = buildOrderTimeline(orderList)
  const revenueTimeline = buildRevenueTimeline(orderList)

  const recentOrders = [...orderList]
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 5)

  const isLoading = pLoading || cLoading || oLoading

  const lowStockColumns = [
    { title: 'Product', dataIndex: 'product_name', key: 'product_name',
      render: v => <Text style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{v}</Text> },
    { title: 'SKU', dataIndex: 'sku', key: 'sku',
      render: v => <Text className="mono" style={{ color: 'var(--text-muted)', fontSize: 12 }}>{v}</Text> },
    { title: 'Stock', dataIndex: 'quantity_in_stock', key: 'qty',
      render: qty => (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Text style={{ color: qty === 0 ? 'var(--red)' : 'var(--amber)', fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
            {qty}
          </Text>
          <StockBadge qty={qty} />
        </div>
      )
    },
  ]

  const recentOrderColumns = [
    { title: 'Order ID', dataIndex: 'id', key: 'id',
      render: v => <Text className="mono" style={{ color: 'var(--accent)', fontSize: 12 }}>#{String(v).padStart(5, '0')}</Text> },
    { title: 'Customer', dataIndex: 'customer_id', key: 'customer_id',
      render: v => <Text style={{ color: 'var(--text-secondary)' }}>Customer #{v}</Text> },
    { title: 'Amount', dataIndex: 'total_amount', key: 'amount',
      render: v => <Text style={{ color: 'var(--text-primary)', fontWeight: 600 }}>${Number(v).toFixed(2)}</Text> },
    { title: 'Status', dataIndex: 'status', key: 'status',
      render: s => <StatusBadge status={s} /> },
    { title: 'Date', dataIndex: 'created_at', key: 'date',
      render: v => <Text style={{ color: 'var(--text-muted)', fontSize: 12 }}>{dayjs(v).format('MMM D, YYYY')}</Text> },
  ]

  return (
    <Spin spinning={isLoading} size="large">
      <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>

        {/* ── STAT CARDS ── */}
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} xl={6}>
            <StatCard
              title="Total Products"
              value={productList.length}
              icon={<AppstoreOutlined />}
              color="var(--accent)"
              loading={pLoading}
            />
          </Col>
          <Col xs={24} sm={12} xl={6}>
            <StatCard
              title="Total Customers"
              value={customerList.length}
              icon={<TeamOutlined />}
              color="var(--pink)"
              loading={cLoading}
            />
          </Col>
          <Col xs={24} sm={12} xl={6}>
            <StatCard
              title="Total Orders"
              value={orderList.length}
              icon={<ShoppingCartOutlined />}
              color="var(--green)"
              loading={oLoading}
            />
          </Col>
          <Col xs={24} sm={12} xl={6}>
            <StatCard
              title="Total Revenue"
              value={totalRevenue.toFixed(2)}
              prefix="$"
              icon={<span style={{ fontSize: 14 }}>💰</span>}
              color="var(--amber)"
              loading={oLoading}
            />
          </Col>
        </Row>

        {/* ── CHARTS ── */}
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={14}>
            <Card title={<ChartTitle>Revenue (Last 7 Days)</ChartTitle>}>
              {revenueTimeline.length === 0 ? (
                <EmptyChartMessage />
              ) : (
                <ResponsiveContainer width="100%" height={200}>
                  <AreaChart data={revenueTimeline} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
                    <defs>
                      <linearGradient id="revenueGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#38BDF8" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#38BDF8" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                    <XAxis dataKey="day" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
                    <Tooltip content={<ChartTooltip prefix="$" />} />
                    <Area type="monotone" dataKey="revenue" stroke="#38BDF8" strokeWidth={2} fill="url(#revenueGrad)" />
                  </AreaChart>
                </ResponsiveContainer>
              )}
            </Card>
          </Col>

          <Col xs={24} lg={10}>
            <Card title={<ChartTitle>Orders (Last 7 Days)</ChartTitle>}>
              {orderTimeline.length === 0 ? (
                <EmptyChartMessage />
              ) : (
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={orderTimeline} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                    <XAxis dataKey="day" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} allowDecimals={false} />
                    <Tooltip content={<ChartTooltip />} />
                    <Bar dataKey="count" fill="#F472B6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </Card>
          </Col>
        </Row>

        {/* ── TABLES ── */}
        <Row gutter={[16, 16]}>
          <Col xs={24} xl={12}>
            <Card
              title={
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <WarningOutlined style={{ color: 'var(--amber)' }} />
                  <ChartTitle>Low Stock Alert</ChartTitle>
                  {lowStockProducts.length > 0 && (
                    <Tag style={{ background: 'var(--amber-dim)', color: 'var(--amber)', border: '1px solid rgba(251,191,36,0.3)', borderRadius: 20, fontSize: 11 }}>
                      {lowStockProducts.length}
                    </Tag>
                  )}
                </div>
              }
            >
              <Table
                dataSource={lowStockProducts.slice(0, 5)}
                columns={lowStockColumns}
                rowKey="id"
                pagination={false}
                size="small"
                locale={{ emptyText: <Text style={{ color: 'var(--text-muted)' }}>All products well-stocked ✓</Text> }}
              />
            </Card>
          </Col>

          <Col xs={24} xl={12}>
            <Card title={<ChartTitle>Recent Orders</ChartTitle>}>
              <Table
                dataSource={recentOrders}
                columns={recentOrderColumns}
                rowKey="id"
                pagination={false}
                size="small"
                locale={{ emptyText: <Text style={{ color: 'var(--text-muted)' }}>No orders yet</Text> }}
              />
            </Card>
          </Col>
        </Row>

      </div>
    </Spin>
  )
}

function ChartTitle({ children }) {
  return <span style={{ color: 'var(--text-primary)', fontWeight: 600, fontSize: 14 }}>{children}</span>
}

function EmptyChartMessage() {
  return (
    <div style={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <Text style={{ color: 'var(--text-muted)' }}>No data available</Text>
    </div>
  )
}
