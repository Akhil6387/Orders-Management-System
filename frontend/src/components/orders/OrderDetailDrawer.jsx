import { Drawer, Descriptions, Table, Typography, Space, Divider, Spin } from 'antd'
import dayjs from 'dayjs'
import StatusBadge from '../common/StatusBadge'
import { useOrder } from '../../hooks/useOrders'

const { Text } = Typography

export default function OrderDetailDrawer({ orderId, onClose }) {
  const { data: order, isLoading } = useOrder(orderId)

  const itemColumns = [
    {
      title: 'Product',
      dataIndex: 'product_id',
      render: (v, r) => (
        <Text style={{ color: 'var(--text-primary)' }}>
          {r.product_name || `Product #${v}`}
        </Text>
      ),
    },
    {
      title: 'Unit Price',
      dataIndex: 'unit_price',
      render: v => <Text className="mono" style={{ color: 'var(--text-secondary)' }}>${Number(v).toFixed(2)}</Text>,
    },
    {
      title: 'Qty',
      dataIndex: 'quantity',
      render: v => <Text className="mono" style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{v}</Text>,
    },
    {
      title: 'Subtotal',
      key: 'subtotal',
      render: (_, r) => (
        <Text className="mono" style={{ color: 'var(--accent)', fontWeight: 600 }}>
          ${(r.unit_price * r.quantity).toFixed(2)}
        </Text>
      ),
    },
  ]

  return (
    <Drawer
      open={!!orderId}
      onClose={onClose}
      title={order ? `Order #${String(order.id).padStart(5, '0')}` : 'Order Details'}
      width={480}
      styles={{
        body: { background: 'var(--bg-surface)', padding: 24 },
        header: { background: 'var(--bg-surface)', borderBottom: '1px solid var(--border)', color: 'var(--text-primary)' },
        mask: { backdropFilter: 'blur(2px)' },
      }}
    >
      {isLoading ? (
        <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 48 }}>
          <Spin size="large" />
        </div>
      ) : order ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Summary */}
          <div style={{ background: 'var(--bg-elevated)', borderRadius: 'var(--radius)', padding: 16, border: '1px solid var(--border)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <Text style={{ color: 'var(--text-muted)', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                Order Summary
              </Text>
              <StatusBadge status={order.status} />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <InfoRow label="Customer ID" value={`#${String(order.customer_id).padStart(4, '0')}`} mono />
              <InfoRow label="Created" value={dayjs(order.created_at).format('MMM D, YYYY [at] h:mm A')} />
              <Divider style={{ borderColor: 'var(--border)', margin: '4px 0' }} />
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text style={{ color: 'var(--text-muted)', fontSize: 13 }}>Total Amount</Text>
                <Text style={{ color: 'var(--accent)', fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: 18 }}>
                  ${Number(order.total_amount).toFixed(2)}
                </Text>
              </div>
            </div>
          </div>

          {/* Items */}
          <div>
            <Text style={{ color: 'var(--text-muted)', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', display: 'block', marginBottom: 10 }}>
              Items ({order.items?.length || 0})
            </Text>
            <Table
              dataSource={order.items || []}
              columns={itemColumns}
              rowKey="id"
              pagination={false}
              size="small"
            />
          </div>
        </div>
      ) : (
        <Text style={{ color: 'var(--text-muted)' }}>Order not found</Text>
      )}
    </Drawer>
  )
}

function InfoRow({ label, value, mono }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
      <Text style={{ color: 'var(--text-muted)', fontSize: 13 }}>{label}</Text>
      <Text style={{ color: 'var(--text-secondary)', fontFamily: mono ? 'var(--font-mono)' : 'inherit', fontSize: 13 }}>
        {value}
      </Text>
    </div>
  )
}
