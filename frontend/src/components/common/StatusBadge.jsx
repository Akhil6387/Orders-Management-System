import { Tag } from 'antd'

const STATUS_CONFIG = {
  pending:    { color: '#FBBF24', bg: 'rgba(251,191,36,0.12)',   label: 'Pending' },
  processing: { color: '#38BDF8', bg: 'rgba(56,189,248,0.12)',  label: 'Processing' },
  completed:  { color: '#34D399', bg: 'rgba(52,211,153,0.12)',  label: 'Completed' },
  cancelled:  { color: '#F87171', bg: 'rgba(248,113,113,0.12)', label: 'Cancelled' },
}

export default function StatusBadge({ status }) {
  const cfg = STATUS_CONFIG[status?.toLowerCase()] || STATUS_CONFIG.pending
  return (
    <Tag style={{
      background: cfg.bg,
      color: cfg.color,
      border: `1px solid ${cfg.color}55`,
      borderRadius: 20,
      padding: '1px 10px',
      fontSize: 11,
      fontWeight: 600,
      letterSpacing: '0.04em',
      textTransform: 'capitalize',
    }}>
      {cfg.label}
    </Tag>
  )
}
