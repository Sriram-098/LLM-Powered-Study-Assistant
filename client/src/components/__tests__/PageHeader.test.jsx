import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import PageHeader from '../PageHeader'

describe('PageHeader', () => {
  it('renders title', () => {
    render(<PageHeader title="Dashboard" />)
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })

  it('renders subtitle when provided', () => {
    render(
      <PageHeader 
        title="Dashboard" 
        subtitle="Welcome back to your dashboard" 
      />
    )
    expect(screen.getByText('Welcome back to your dashboard')).toBeInTheDocument()
  })

  it('renders children content', () => {
    render(
      <PageHeader title="Dashboard">
        <button>Action</button>
      </PageHeader>
    )
    expect(screen.getByText('Action')).toBeInTheDocument()
  })

  it('renders centered layout when centered prop is true', () => {
    const { container } = render(
      <PageHeader title="Dashboard" centered />
    )
    expect(container.firstChild).toHaveClass('text-center')
  })

  it('renders default layout when centered is false', () => {
    const { container } = render(
      <PageHeader title="Dashboard" />
    )
    expect(container.firstChild).toHaveClass('bg-white', 'border-b')
  })

  it('applies custom className', () => {
    const { container } = render(
      <PageHeader title="Dashboard" className="custom-header" />
    )
    expect(container.firstChild).toHaveClass('custom-header')
  })
})
