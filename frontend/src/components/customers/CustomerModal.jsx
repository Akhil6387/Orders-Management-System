import { useEffect } from 'react'
import { Modal, Form, Input, Button, Space } from 'antd'
import { UserOutlined, MailOutlined, PhoneOutlined } from '@ant-design/icons'

export default function CustomerModal({ open, onClose, onSubmit, loading }) {
  const [form] = Form.useForm()

  useEffect(() => {
    if (open) form.resetFields()
  }, [open, form])

  const handleOk = () => {
    form.validateFields().then(values => onSubmit(values))
  }

  return (
    <Modal
      open={open}
      onCancel={onClose}
      title="Add Customer"
      footer={
        <Space>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="primary" onClick={handleOk} loading={loading}>
            Add Customer
          </Button>
        </Space>
      }
      destroyOnClose
    >
      <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
        <Form.Item
          name="full_name"
          label="Full Name"
          rules={[{ required: true, message: 'Full name is required' }]}
        >
          <Input prefix={<UserOutlined style={{ color: 'var(--text-muted)' }} />} placeholder="Jane Doe" />
        </Form.Item>

        <Form.Item
          name="email"
          label="Email"
          rules={[
            { required: true, message: 'Email is required' },
            { type: 'email', message: 'Enter a valid email address' },
          ]}
        >
          <Input prefix={<MailOutlined style={{ color: 'var(--text-muted)' }} />} placeholder="jane@example.com" />
        </Form.Item>

        <Form.Item
          name="phone_number"
          label="Phone Number"
          rules={[{ required: true, message: 'Phone number is required' }]}
        >
          <Input prefix={<PhoneOutlined style={{ color: 'var(--text-muted)' }} />} placeholder="+1 (555) 000-0000" />
        </Form.Item>
      </Form>
    </Modal>
  )
}
