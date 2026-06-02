import { useState } from 'react'
import { Table, Button, Input, Space, Popconfirm, Typography, Avatar, Tooltip } from 'antd'
import { PlusOutlined, SearchOutlined, DeleteOutlined, UserOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import PageHeader from '../components/common/PageHeader'
import CustomerModal from '../components/customers/CustomerModal'
import { useCustomers, useCreateCustomer, useDeleteCustomer } from '../hooks/useCustomers'

const { Text } = Typography

function getInitials(name = '') {
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

const AVATAR_COLORS = [
  '#38BDF8', '#F472B6', '#34D399', '#FBBF24', '#818CF8', '#FB923C',
]

export default function Customers() {
  const [search, setSearch]   = useState('')
  const [page, setPage]       = useState(1)
  const [modalOpen, setModalOpen] = useState(false)

  const PAGE_SIZE = 10
  const { data, isLoading } = useCustomers({ skip: (page - 1) * PAGE_SIZE, limit: PAGE_SIZE, search })
  const createCustomer = useCreateCustomer()
  const deleteCustomer = useDeleteCustomer()

  const customers = data?.items || data || []
  const total     = data?.total || customers.length

  const handleSubmit = async (values) => {
    await createCustomer.mutateAsync(values)
    setModalOpen(false)
  }

  const columns = [
    {
      title: 'Customer',
      key: 'customer',
      render: (_, r) => {
        const color = AVATAR_COLORS[r.id % AVATAR_COLORS.length]
        return (
          <Space>
            <Avatar
              style={{ background: `${color}22`, color, border: `1px solid ${color}44`, fontWeight: 600, fontSize: 13 }}
              size={36}
            >
              {getInitials(r.full_name)}
            </Avatar>
            <div>
              <Text style={{ color: 'var(--text-primary)', fontWeight: 500, display: 'block' }}>{r.full_name}</Text>
              <Text style={{ color: 'var(--text-muted)', fontSize: 12 }}>#{String(r.id).padStart(4, '0')}</Text>
            </div>
          </Space>
        )
      },
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
      render: v => <Text style={{ color: 'var(--text-secondary)' }}>{v}</Text>,
    },
    {
      title: 'Phone',
      dataIndex: 'phone_number',
      key: 'phone',
      render: v => <Text className="mono" style={{ color: 'var(--text-secondary)', fontSize: 13 }}>{v}</Text>,
    },
    {
      title: 'Joined',
      dataIndex: 'created_at',
      key: 'joined',
      render: v => <Text style={{ color: 'var(--text-muted)', fontSize: 12 }}>{dayjs(v).format('MMM D, YYYY')}</Text>,
    },
    {
      title: '',
      key: 'actions',
      width: 60,
      render: (_, record) => (
        <Popconfirm
          title="Delete Customer"
          description="This will permanently delete the customer."
          onConfirm={() => deleteCustomer.mutate(record.id)}
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
      ),
    },
  ]

  return (
    <div>
      <PageHeader
        title="Customers"
        subtitle={`${total} registered customer${total !== 1 ? 's' : ''}`}
        actions={
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
            Add Customer
          </Button>
        }
      />

      <div style={{ marginBottom: 16 }}>
        <Input
          prefix={<SearchOutlined style={{ color: 'var(--text-muted)' }} />}
          placeholder="Search by name or email…"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1) }}
          style={{ maxWidth: 320 }}
          allowClear
        />
      </div>

      <div style={{ background: 'var(--bg-surface)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border)', overflow: 'hidden' }}>
        <Table
          dataSource={customers}
          columns={columns}
          rowKey="id"
          loading={isLoading}
          pagination={{
            current: page,
            pageSize: PAGE_SIZE,
            total,
            onChange: setPage,
            showSizeChanger: false,
            showTotal: (t) => <Text style={{ color: 'var(--text-muted)' }}>Total {t} customers</Text>,
          }}
          size="middle"
        />
      </div>

      <CustomerModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={handleSubmit}
        loading={createCustomer.isPending}
      />
    </div>
  )
}
