import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import LoadingSpinner from '../LoadingSpinner'

describe('LoadingSpinner', () => {
  it('renders spinner with default medium size', () => {
    const { container } = render(<LoadingSpinner />)
    const spinner = container.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
    expect(spinner).toHaveClass('h-8', 'w-8')
  })

  it('renders small spinner', () => {
    const { container } = render(<LoadingSpinner size="sm" />)
    const spinner = container.querySelector('.animate-spin')
    expect(spinner).toHaveClass('h-4', 'w-4')
  })

  it('renders large spinner', () => {
    const { container } = render(<LoadingSpinner size="lg" />)
    const spinner = container.querySelector('.animate-spin')
    expect(spinner).toHaveClass('h-12', 'w-12')
  })

  it('renders extra large spinner', () => {
    const { container } = render(<LoadingSpinner size="xl" />)
    const spinner = container.querySelector('.animate-spin')
    expect(spinner).toHaveClass('h-16', 'w-16')
  })

  it('applies blue color by default', () => {
    const { container } = render(<LoadingSpinner />)
    const spinner = container.querySelector('.animate-spin')
    expect(spinner).toHaveClass('border-blue-600')
  })

  it('applies custom color', () => {
    const { container } = render(<LoadingSpinner color="purple" />)
    const spinner = container.querySelector('.animate-spin')
    expect(spinner).toHaveClass('border-purple-600')
  })
})
