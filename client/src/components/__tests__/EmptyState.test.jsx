import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import EmptyState from '../EmptyState'

describe('EmptyState', () => {
  it('renders title', () => {
    render(<EmptyState title="No items found" />)
    expect(screen.getByText('No items found')).toBeInTheDocument()
  })

  it('renders description when provided', () => {
    render(
      <EmptyState 
        title="No items" 
        description="Try adding some items to get started"
      />
    )
    expect(screen.getByText('Try adding some items to get started')).toBeInTheDocument()
  })

  it('renders icon when provided', () => {
    const icon = <svg data-testid="test-icon">Icon</svg>
    render(<EmptyState title="Empty" icon={icon} />)
    expect(screen.getByTestId('test-icon')).toBeInTheDocument()
  })

  it('renders action button when provided', () => {
    const button = <button>Add Item</button>
    render(<EmptyState title="Empty" actionButton={button} />)
    expect(screen.getByText('Add Item')).toBeInTheDocument()
  })

  it('applies custom className', () => {
    const { container } = render(
      <EmptyState title="Empty" className="custom-empty" />
    )
    expect(container.firstChild).toHaveClass('custom-empty')
  })
})
