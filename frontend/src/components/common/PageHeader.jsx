import { Typography, Space } from 'antd'

const { Title, Text } = Typography

export default function PageHeader({ title, subtitle, actions }) {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'flex-start',
      marginBottom: 24,
      flexWrap: 'wrap',
      gap: 12,
    }}>
      <div>
        <Title level={4} style={{ margin: 0, color: 'var(--text-primary)', fontWeight: 700, letterSpacing: '-0.02em' }}>
          {title}
        </Title>
        {subtitle && (
          <Text style={{ color: 'var(--text-muted)', fontSize: 13, marginTop: 2, display: 'block' }}>
            {subtitle}
          </Text>
        )}
      </div>
      {actions && <Space wrap>{actions}</Space>}
    </div>
  )
}
