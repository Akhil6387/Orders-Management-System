import { useState } from 'react'
import { Table, Button, Space, Popconfirm, Typography, Tooltip } from 'antd'
import {
  PlusOutlined, DeleteOutlined, EyeOutlined,
} from '@ant-design/icons'
import dayjs from 'dayjs'
import PageHeader from '../components/common/PageHeader'
import StatusBadge from '../components/common/StatusBadge'
import CreateOrderModal from '../components/orders/CreateOrderModal'
import OrderDetailDrawer from '../components/orders/OrderDetailDrawer'
import { useOrders, useCreateOrder, useDeleteOrder } from '../hooks/useOrders'

const { Text } = Typography

export default function Orders() {
  const [page, setPage]               = useState(1)
  const [createOpen, setCreateOpen]   = useState(false)
  const [detailOrderId, setDetailOrderId] = useState(null)

  const PAGE_SIZE = 10
  const { data, isLoading } = useOrders({ skip: (page - 1) * PAGE_SIZE, limit: PAGE_SIZE })
  const createOrder = useCreateOrder()
  const deleteOrder = useDeleteOrder()

  const orders = data?.items || data || []
  const total  = data?.total || orders.length

  const handleCreateSubmit = async (values) => {
    await createOrder.mutateAsync(values)
    setCreateOpen(false)
  }

  const columns = [
    {
      title: 'Order ID',
      dataIndex: 'id',
      key: 'id',
      render: (v) => (
        <Text
          className="mono"
          style={{ color: 'var(--accent)', fontSize: 12, cursor: 'pointer' }}
          onClick={() => setDetailOrderId(v)}
        >
          #{String(v).padStart(5, '0')}
        </Text>
      ),
    },
    {
      title: 'Customer',
      dataIndex: 'customer_id',
      key: 'customer_id',
      render: (v, r) => (
        <Text style={{ color: 'var(--text-primary)' }}>
          {r.customer_name || `Customer #${String(v).padStart(4, '0')}`}
        </Text>
      ),
    },
    {
      title: 'Items',
      dataIndex: 'items',
      key: 'items',
      render: (items) => (
        <Text className="mono" style={{ color: 'var(--text-muted)' }}>
          {Array.isArray(items) ? items.length : '—'}
        </Text>
      ),
    },
    {
      title: 'Total',
      dataIndex: 'total_amount',
      key: 'total',
      render: (v) => (
        <Text style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--text-primary)' }}>
          ${Number(v).toFixed(2)}
        </Text>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (s) => <StatusBadge status={s} />,
    },
    {
      title: 'Date',
      dataIndex: 'created_at',
      key: 'date',
      render: (v) => (
        <Text style={{ color: 'var(--text-muted)', fontSize: 12 }}>
          {dayjs(v).format('MMM D, YYYY')}
        </Text>
      ),
    },
    {
      title: '',
      key: 'actions',
      width: 90,
      render: (_, record) => (
        <Space>
          <Tooltip title="View Details">
            <Button
              type="text"
              icon={<EyeOutlined />}
              size="small"
              style={{ color: 'var(--text-muted)' }}
              onClick={() => setDetailOrderId(record.id)}
            />
          </Tooltip>
          <Popconfirm
            title="Delete Order"
            description="Are you sure you want to delete this order?"
            onConfirm={() => deleteOrder.mutate(record.id)}
            okText="Delete"
            okButtonProps={{ danger: true }}
            cancelText="Cancel"
          >
            <Tooltip title="Delete">
              <Button
                type="text"
                icon={<DeleteOutlined />}
                size="small"
                style={{ color: 'var(--text-muted)' }}
                danger
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <PageHeader
        title="Orders"
        subtitle={`${total} total order${total !== 1 ? 's' : ''}`}
        actions={
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateOpen(true)}>
            New Order
          </Button>
        }
      />

      <div style={{ background: 'var(--bg-surface)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border)', overflow: 'hidden' }}>
        <Table
          dataSource={orders}
          columns={columns}
          rowKey="id"
          loading={isLoading}
          pagination={{
            current: page,
            pageSize: PAGE_SIZE,
            total,
            onChange: setPage,
            showSizeChanger: false,
            showTotal: (t) => <Text style={{ color: 'var(--text-muted)' }}>Total {t} orders</Text>,
          }}
          size="middle"
          onRow={(record) => ({
            style: { cursor: 'pointer' },
            onClick: (e) => {
              if (!e.target.closest('.ant-btn') && !e.target.closest('.ant-popconfirm')) {
                setDetailOrderId(record.id)
              }
            },
          })}
        />
      </div>

      {/* Create Order Modal */}
      <CreateOrderModal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onSubmit={handleCreateSubmit}
        loading={createOrder.isPending}
      />

      {/* Order Detail Drawer */}
      <OrderDetailDrawer
        orderId={detailOrderId}
        onClose={() => setDetailOrderId(null)}
      />
    </div>
  )
}
