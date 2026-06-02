import { useState } from 'react'
import { Table, Button, Input, Space, Popconfirm, Typography, Tooltip } from 'antd'
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
} from '@ant-design/icons'
import PageHeader from '../components/common/PageHeader'
import StockBadge from '../components/common/StockBadge'
import ProductModal from '../components/products/ProductModal'
import { useProducts, useCreateProduct, useUpdateProduct, useDeleteProduct } from '../hooks/useProducts'

const { Text } = Typography

export default function Products() {
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [modalOpen, setModalOpen] = useState(false)
  const [editTarget, setEditTarget] = useState(null)

  const PAGE_SIZE = 10

  const { data, isLoading } = useProducts({ skip: (page - 1) * PAGE_SIZE, limit: PAGE_SIZE, search })
  const createProduct = useCreateProduct()
  const updateProduct = useUpdateProduct()
  const deleteProduct = useDeleteProduct()

  const products = data?.items || data || []
  const total    = data?.total || products.length

  const openAdd  = () => { setEditTarget(null); setModalOpen(true) }
  const openEdit = (record) => { setEditTarget(record); setModalOpen(true) }
  const closeModal = () => { setModalOpen(false); setEditTarget(null) }

  const handleSubmit = async (values) => {
    if (editTarget) {
      await updateProduct.mutateAsync({ id: editTarget.id, data: values })
    } else {
      await createProduct.mutateAsync(values)
    }
    closeModal()
  }

  const columns = [
    {
      title: 'Product Name',
      dataIndex: 'product_name',
      key: 'product_name',
      render: (v) => <Text style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{v}</Text>,
    },
    {
      title: 'SKU',
      dataIndex: 'sku',
      key: 'sku',
      render: (v) => (
        <Text className="mono" style={{ color: 'var(--accent)', fontSize: 12, background: 'var(--accent-dim)', padding: '2px 8px', borderRadius: 4 }}>
          {v}
        </Text>
      ),
    },
    {
      title: 'Price',
      dataIndex: 'price',
      key: 'price',
      render: (v) => <Text style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>${Number(v).toFixed(2)}</Text>,
    },
    {
      title: 'Stock',
      dataIndex: 'quantity_in_stock',
      key: 'stock',
      render: (qty) => (
        <Space>
          <Text style={{
            fontFamily: 'var(--font-mono)',
            fontWeight: 600,
            color: qty === 0 ? 'var(--red)' : qty <= 10 ? 'var(--amber)' : 'var(--text-primary)',
            minWidth: 28,
            display: 'inline-block',
          }}>
            {qty}
          </Text>
          <StockBadge qty={qty} />
        </Space>
      ),
    },
    {
      title: '',
      key: 'actions',
      width: 100,
      render: (_, record) => (
        <Space>
          <Tooltip title="Edit">
            <Button
              type="text"
              icon={<EditOutlined />}
              size="small"
              onClick={() => openEdit(record)}
              style={{ color: 'var(--text-muted)' }}
            />
          </Tooltip>
          <Popconfirm
            title="Delete Product"
            description="Are you sure you want to delete this product?"
            onConfirm={() => deleteProduct.mutate(record.id)}
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
        title="Products"
        subtitle={`${total} product${total !== 1 ? 's' : ''} in inventory`}
        actions={
          <Button type="primary" icon={<PlusOutlined />} onClick={openAdd}>
            Add Product
          </Button>
        }
      />

      {/* Search bar */}
      <div style={{ marginBottom: 16 }}>
        <Input
          prefix={<SearchOutlined style={{ color: 'var(--text-muted)' }} />}
          placeholder="Search by name or SKU…"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1) }}
          style={{ maxWidth: 320 }}
          allowClear
        />
      </div>

      {/* Table */}
      <div style={{ background: 'var(--bg-surface)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border)', overflow: 'hidden' }}>
        <Table
          dataSource={products}
          columns={columns}
          rowKey="id"
          loading={isLoading}
          pagination={{
            current: page,
            pageSize: PAGE_SIZE,
            total,
            onChange: setPage,
            showSizeChanger: false,
            showTotal: (t) => <Text style={{ color: 'var(--text-muted)' }}>Total {t} products</Text>,
          }}
          size="middle"
        />
      </div>

      {/* Modal */}
      <ProductModal
        open={modalOpen}
        onClose={closeModal}
        onSubmit={handleSubmit}
        initialValues={editTarget}
        loading={createProduct.isPending || updateProduct.isPending}
      />
    </div>
  )
}
