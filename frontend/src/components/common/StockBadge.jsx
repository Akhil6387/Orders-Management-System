import { Tag } from 'antd'

export default function StockBadge({ qty }) {
  let color, bg, label
  if (qty === 0) {
    color = '#F87171'; bg = 'rgba(248,113,113,0.12)'; label = 'Out of Stock'
  } else if (qty <= 10) {
    color = '#FBBF24'; bg = 'rgba(251,191,36,0.12)'; label = 'Low Stock'
  } else {
    color = '#34D399'; bg = 'rgba(52,211,153,0.12)'; label = 'In Stock'
  }

  return (
    <Tag style={{
      background: bg,
      color,
      border: `1px solid ${color}55`,
      borderRadius: 20,
      padding: '1px 10px',
      fontSize: 11,
      fontWeight: 600,
    }}>
      {label}
    </Tag>
  )
}
