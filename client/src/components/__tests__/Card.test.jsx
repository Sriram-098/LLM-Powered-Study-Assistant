import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import Card from '../Card'

describe('Card', () => {
  it('renders children content', () => {
    render(
      <Card>
        <div>Card content</div>
      </Card>
    )
    expect(screen.getByText('Card content')).toBeInTheDocument()
  })

  it('applies default medium padding', () => {
    const { container } = render(<Card>Content</Card>)
    const card = container.firstChild
    expect(card).toHaveClass('p-6')
  })

  it('applies small padding when specified', () => {
    const { container } = render(<Card padding="sm">Content</Card>)
    const card = container.firstChild
    expect(card).toHaveClass('p-4')
  })

  it('applies large padding when specified', () => {
    const { container } = render(<Card padding="lg">Content</Card>)
    const card = container.firstChild
    expect(card).toHaveClass('p-8')
  })

  it('applies hover effect when hover prop is true', () => {
    const { container } = render(<Card hover>Content</Card>)
    const card = container.firstChild
    expect(card).toHaveClass('hover:border-gray-300')
  })

  it('applies custom className', () => {
    const { container } = render(<Card className="custom-class">Content</Card>)
    const card = container.firstChild
    expect(card).toHaveClass('custom-class')
  })
})
