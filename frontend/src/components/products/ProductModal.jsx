import { useEffect } from 'react'
import { Modal, Form, Input, InputNumber, Button, Space } from 'antd'

export default function ProductModal({ open, onClose, onSubmit, initialValues, loading }) {
  const [form] = Form.useForm()
  const isEdit = !!initialValues

  useEffect(() => {
    if (open) {
      form.resetFields()
      if (initialValues) form.setFieldsValue(initialValues)
    }
  }, [open, initialValues, form])

  const handleOk = () => {
    form.validateFields().then(values => {
      onSubmit(values)
    })
  }

  return (
    <Modal
      open={open}
      onCancel={onClose}
      title={isEdit ? 'Edit Product' : 'Add Product'}
      footer={
        <Space>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="primary" onClick={handleOk} loading={loading}>
            {isEdit ? 'Save Changes' : 'Add Product'}
          </Button>
        </Space>
      }
      destroyOnClose
    >
      <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
        <Form.Item
          name="product_name"
          label="Product Name"
          rules={[{ required: true, message: 'Product name is required' }]}
        >
          <Input placeholder="e.g. Wireless Headphones" />
        </Form.Item>

        <Form.Item
          name="sku"
          label="SKU"
          rules={[{ required: true, message: 'SKU is required' }]}
        >
          <Input
            placeholder="e.g. WH-1000XM5"
            style={{ fontFamily: 'var(--font-mono)' }}
          />
        </Form.Item>

        <Form.Item
          name="price"
          label="Price ($)"
          rules={[{ required: true, message: 'Price is required' }, { type: 'number', min: 0.01, message: 'Price must be positive' }]}
        >
          <InputNumber min={0.01} step={0.01} precision={2} placeholder="0.00" />
        </Form.Item>

        <Form.Item
          name="quantity_in_stock"
          label="Quantity in Stock"
          rules={[{ required: true, message: 'Quantity is required' }, { type: 'number', min: 0, message: 'Quantity cannot be negative' }]}
        >
          <InputNumber min={0} precision={0} placeholder="0" />
        </Form.Item>
      </Form>
    </Modal>
  )
}
