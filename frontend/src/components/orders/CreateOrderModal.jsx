import { useState, useEffect } from 'react'
import {
  Modal, Form, Select, InputNumber, Button, Space,
  Divider, Typography, Tooltip,
} from 'antd'
import { PlusOutlined, DeleteOutlined, ShoppingCartOutlined } from '@ant-design/icons'
import { useCustomers } from '../../hooks/useCustomers'
import { useProducts } from '../../hooks/useProducts'

const { Text } = Typography
const { Option } = Select

const EMPTY_ITEM = { product_id: null, quantity: 1 }

export default function CreateOrderModal({ open, onClose, onSubmit, loading }) {
  const [form] = Form.useForm()
  const [items, setItems] = useState([{ ...EMPTY_ITEM }])

  const { data: customersData } = useCustomers({ limit: 500 })
  const { data: productsData }  = useProducts({ limit: 500 })

  const customers = customersData?.items || customersData || []
  const products  = productsData?.items  || productsData  || []

  useEffect(() => {
    if (open) {
      form.resetFields()
      setItems([{ ...EMPTY_ITEM }])
    }
  }, [open, form])

  const getProduct = (id) => products.find(p => p.id === id)

  const updateItem = (idx, field, value) => {
    setItems(prev => prev.map((it, i) => i === idx ? { ...it, [field]: value } : it))
  }

  const addItem = () => setItems(prev => [...prev, { ...EMPTY_ITEM }])
  const removeItem = (idx) => setItems(prev => prev.filter((_, i) => i !== idx))

  const calcTotal = () => {
    return items.reduce((sum, it) => {
      const p = getProduct(it.product_id)
      return sum + (p ? p.price * (it.quantity || 0) : 0)
    }, 0)
  }

  const handleOk = () => {
    form.validateFields().then(values => {
      const validItems = items.filter(it => it.product_id && it.quantity > 0)
      if (validItems.length === 0) return
      onSubmit({
        customer_id: values.customer_id,
        items: validItems.map(it => ({
          product_id: it.product_id,
          quantity: it.quantity,
        })),
      })
    })
  }

  const usedProductIds = items.map(i => i.product_id).filter(Boolean)

  return (
    <Modal
      open={open}
      onCancel={onClose}
      title={
        <Space>
          <ShoppingCartOutlined style={{ color: 'var(--accent)' }} />
          <span>Create New Order</span>
        </Space>
      }
      footer={
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <Text style={{ color: 'var(--text-muted)', fontSize: 12 }}>Estimated Total: </Text>
            <Text style={{ color: 'var(--accent)', fontWeight: 700, fontFamily: 'var(--font-mono)', fontSize: 16 }}>
              ${calcTotal().toFixed(2)}
            </Text>
          </div>
          <Space>
            <Button onClick={onClose}>Cancel</Button>
            <Button
              type="primary"
              onClick={handleOk}
              loading={loading}
              disabled={items.every(i => !i.product_id)}
            >
              Place Order
            </Button>
          </Space>
        </div>
      }
      width={580}
      destroyOnClose
    >
      <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
        <Form.Item
          name="customer_id"
          label="Customer"
          rules={[{ required: true, message: 'Please select a customer' }]}
        >
          <Select
            showSearch
            placeholder="Select customer…"
            filterOption={(input, option) =>
              option?.label?.toLowerCase().includes(input.toLowerCase())
            }
            options={customers.map(c => ({
              value: c.id,
              label: `${c.full_name} — ${c.email}`,
            }))}
          />
        </Form.Item>
      </Form>

      <Divider style={{ borderColor: 'var(--border)', margin: '8px 0 16px' }}>
        <Text style={{ color: 'var(--text-muted)', fontSize: 11, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
          Order Items
        </Text>
      </Divider>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {items.map((item, idx) => {
          const product = getProduct(item.product_id)
          const lineTotal = product ? product.price * (item.quantity || 0) : 0
          const maxQty = product?.quantity_in_stock ?? 9999

          return (
            <div key={idx} style={{
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius)',
              padding: '12px 14px',
            }}>
              <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <Text style={{ color: 'var(--text-muted)', fontSize: 11, fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase', display: 'block', marginBottom: 4 }}>
                    Product
                  </Text>
                  <Select
                    showSearch
                    placeholder="Select product…"
                    style={{ width: '100%' }}
                    value={item.product_id}
                    onChange={(v) => updateItem(idx, 'product_id', v)}
                    filterOption={(input, option) =>
                      option?.label?.toLowerCase().includes(input.toLowerCase())
                    }
                    options={products.map(p => ({
                      value: p.id,
                      label: p.product_name,
                      disabled: usedProductIds.includes(p.id) && p.id !== item.product_id,
                    }))}
                  />
                </div>

                <div style={{ width: 90 }}>
                  <Text style={{ color: 'var(--text-muted)', fontSize: 11, fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase', display: 'block', marginBottom: 4 }}>
                    Qty
                  </Text>
                  <InputNumber
                    min={1}
                    max={maxQty || 9999}
                    value={item.quantity}
                    onChange={(v) => updateItem(idx, 'quantity', v)}
                    style={{ width: '100%' }}
                  />
                </div>

                {items.length > 1 && (
                  <Tooltip title="Remove item">
                    <Button
                      type="text"
                      icon={<DeleteOutlined />}
                      size="small"
                      danger
                      onClick={() => removeItem(idx)}
                      style={{ marginTop: 22 }}
                    />
                  </Tooltip>
                )}
              </div>

              {product && (
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, paddingTop: 8, borderTop: '1px solid var(--border)' }}>
                  <Text style={{ color: 'var(--text-muted)', fontSize: 12 }}>
                    ${product.price.toFixed(2)} × {item.quantity} · Stock: {product.quantity_in_stock}
                  </Text>
                  <Text style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-mono)', fontWeight: 600, fontSize: 12 }}>
                    ${lineTotal.toFixed(2)}
                  </Text>
                </div>
              )}
            </div>
          )
        })}
      </div>

      <Button
        type="dashed"
        icon={<PlusOutlined />}
        onClick={addItem}
        style={{ width: '100%', marginTop: 10, borderColor: 'var(--border)', color: 'var(--text-muted)' }}
      >
        Add Item
      </Button>
    </Modal>
  )
}
