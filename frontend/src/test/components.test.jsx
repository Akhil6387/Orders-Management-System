import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import StatCard from '../components/common/StatCard'
import StatusBadge from '../components/common/StatusBadge'
import StockBadge from '../components/common/StockBadge'

// ── StatCard ──────────────────────────────────────────────────
describe('StatCard', () => {
  it('renders title and value', () => {
    render(
      <StatCard title="Total Products" value={42} icon="📦" color="#38BDF8" />
    )
    expect(screen.getByText('Total Products')).toBeInTheDocument()
    expect(screen.getByText('42')).toBeInTheDocument()
  })

  it('renders loading state', () => {
    const { container } = render(
      <StatCard title="Total Products" value={0} icon="📦" color="#38BDF8" loading />
    )
    expect(container.querySelector('.ant-skeleton')).toBeTruthy()
  })

  it('applies prefix', () => {
    render(
      <StatCard title="Revenue" value={1234.56} prefix="$" icon="💰" color="#FBBF24" />
    )
    expect(screen.getByText('$')).toBeInTheDocument()
  })
})

// ── StatusBadge ───────────────────────────────────────────────
describe('StatusBadge', () => {
  it.each([
    ['pending',    'Pending'],
    ['completed',  'Completed'],
    ['cancelled',  'Cancelled'],
    ['processing', 'Processing'],
  ])('renders %s status', (status, label) => {
    render(<StatusBadge status={status} />)
    expect(screen.getByText(label)).toBeInTheDocument()
  })

  it('falls back gracefully for unknown status', () => {
    render(<StatusBadge status="unknown" />)
    // renders without throwing
  })
})

// ── StockBadge ────────────────────────────────────────────────
describe('StockBadge', () => {
  it('shows Out of Stock when qty is 0', () => {
    render(<StockBadge qty={0} />)
    expect(screen.getByText('Out of Stock')).toBeInTheDocument()
  })

  it('shows Low Stock when qty is ≤ 10', () => {
    render(<StockBadge qty={5} />)
    expect(screen.getByText('Low Stock')).toBeInTheDocument()
  })

  it('shows In Stock when qty > 10', () => {
    render(<StockBadge qty={100} />)
    expect(screen.getByText('In Stock')).toBeInTheDocument()
  })
})
