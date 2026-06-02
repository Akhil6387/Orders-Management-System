import { Empty, Button } from 'antd'
import { PlusOutlined } from '@ant-design/icons'

export default function EmptyState({ description = 'No data', actionLabel, onAction }) {
  return (
    <div style={{ padding: '48px 0', textAlign: 'center' }}>
      <Empty
        image={Empty.PRESENTED_IMAGE_SIMPLE}
        description={<span style={{ color: 'var(--text-muted)' }}>{description}</span>}
      />
      {actionLabel && onAction && (
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={onAction}
          style={{ marginTop: 16 }}
        >
          {actionLabel}
        </Button>
      )}
    </div>
  )
}
