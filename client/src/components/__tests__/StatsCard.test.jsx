import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import StatsCard from '../StatsCard'

describe('StatsCard', () => {
  it('renders title and value', () => {
    render(<StatsCard title="Total Users" value="1,234" />)
    expect(screen.getByText('Total Users')).toBeInTheDocument()
    expect(screen.getByText('1,234')).toBeInTheDocument()
  })

  it('renders icon when provided', () => {
    const icon = <svg data-testid="stats-icon">Icon</svg>
    render(<StatsCard title="Total" value="100" icon={icon} />)
    expect(screen.getByTestId('stats-icon')).toBeInTheDocument()
  })

  it('renders upward trend', () => {
    const trend = { direction: 'up', value: '+12%' }
    render(<StatsCard title="Sales" value="$5,000" trend={trend} />)
    expect(screen.getByText(/\+12%/)).toBeInTheDocument()
    expect(screen.getByText('vs last month')).toBeInTheDocument()
  })

  it('renders downward trend', () => {
    const trend = { direction: 'down', value: '-5%' }
    render(<StatsCard title="Sales" value="$4,000" trend={trend} />)
    expect(screen.getByText(/-5%/)).toBeInTheDocument()
    expect(screen.getByText('vs last month')).toBeInTheDocument()
  })

  it('renders without trend when not provided', () => {
    render(<StatsCard title="Total" value="100" />)
    expect(screen.queryByText('vs last month')).not.toBeInTheDocument()
  })
})
