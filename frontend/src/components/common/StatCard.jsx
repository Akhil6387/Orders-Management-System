import { Statistic, Skeleton } from 'antd'
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons'

export default function StatCard({ title, value, icon, color, prefix, suffix, loading, trend }) {
  return (
    <div style={{
      background: 'var(--bg-surface)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius-lg)',
      padding: '20px 24px',
      display: 'flex',
      flexDirection: 'column',
      gap: 12,
      position: 'relative',
      overflow: 'hidden',
      transition: 'border-color 0.2s, box-shadow 0.2s',
    }}
    onMouseEnter={e => {
      e.currentTarget.style.borderColor = color || 'var(--border-bright)'
      e.currentTarget.style.boxShadow = `0 4px 24px rgba(0,0,0,0.4)`
    }}
    onMouseLeave={e => {
      e.currentTarget.style.borderColor = 'var(--border)'
      e.currentTarget.style.boxShadow = 'none'
    }}
    >
      {/* Glow accent */}
      <div style={{
        position: 'absolute', top: 0, right: 0,
        width: 80, height: 80,
        background: `radial-gradient(circle at top right, ${color}22, transparent 70%)`,
        pointerEvents: 'none',
      }} />

      {/* Icon + Title row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <span style={{ color: 'var(--text-muted)', fontSize: 11, fontWeight: 600, letterSpacing: '0.07em', textTransform: 'uppercase' }}>
          {title}
        </span>
        <div style={{
          width: 36, height: 36, borderRadius: 10,
          background: `${color}1A`,
          border: `1px solid ${color}33`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 16, color,
        }}>
          {icon}
        </div>
      </div>

      {/* Value */}
      {loading ? (
        <Skeleton.Input active size="large" style={{ width: 100, background: 'var(--bg-elevated)' }} />
      ) : (
        <Statistic
          value={value}
          prefix={prefix}
          suffix={suffix}
          valueStyle={{ color: 'var(--text-primary)', fontSize: 28, fontWeight: 700, letterSpacing: '-0.03em' }}
        />
      )}

      {/* Trend badge */}
      {trend !== undefined && !loading && (
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 4,
          fontSize: 12, fontWeight: 500,
          color: trend >= 0 ? 'var(--green)' : 'var(--red)',
        }}>
          {trend >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
          {Math.abs(trend)}% from last month
        </div>
      )}
    </div>
  )
}
