import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import AuthCard from '../AuthCard'

describe('AuthCard', () => {
  it('renders with title, subtitle, and children', () => {
    render(
      <AuthCard title="Welcome Back" subtitle="Sign in to continue">
        <div>Form content</div>
      </AuthCard>
    )

    expect(screen.getByText('Welcome Back')).toBeInTheDocument()
    expect(screen.getByText('Sign in to continue')).toBeInTheDocument()
    expect(screen.getByText('Form content')).toBeInTheDocument()
  })
})
