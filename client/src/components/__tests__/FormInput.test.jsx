import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import FormInput from '../FormInput'

describe('FormInput', () => {
  it('renders input with label', () => {
    render(
      <FormInput 
        label="Email" 
        name="email" 
        value="" 
        onChange={() => {}} 
      />
    )
    expect(screen.getByLabelText('Email')).toBeInTheDocument()
  })

  it('shows required asterisk when required is true', () => {
    render(
      <FormInput 
        label="Email" 
        name="email" 
        value="" 
        onChange={() => {}} 
        required 
      />
    )
    expect(screen.getByText('*')).toBeInTheDocument()
  })

  it('displays error message when error prop is provided', () => {
    render(
      <FormInput 
        label="Email" 
        name="email" 
        value="" 
        onChange={() => {}} 
        error="Email is required" 
      />
    )
    expect(screen.getByText('Email is required')).toBeInTheDocument()
  })

  it('applies error styling when error exists', () => {
    render(
      <FormInput 
        label="Email" 
        name="email" 
        value="" 
        onChange={() => {}} 
        error="Invalid email" 
      />
    )
    const input = screen.getByLabelText('Email')
    expect(input).toHaveClass('border-red-500', 'bg-red-50')
  })

  it('calls onChange handler when input value changes', () => {
    const handleChange = vi.fn()
    render(
      <FormInput 
        label="Email" 
        name="email" 
        value="" 
        onChange={handleChange} 
      />
    )
    const input = screen.getByLabelText('Email')
    fireEvent.change(input, { target: { value: 'test@example.com' } })
    expect(handleChange).toHaveBeenCalled()
  })

  it('disables input when disabled prop is true', () => {
    render(
      <FormInput 
        label="Email" 
        name="email" 
        value="" 
        onChange={() => {}} 
        disabled 
      />
    )
    expect(screen.getByLabelText('Email')).toBeDisabled()
  })

  it('renders with placeholder', () => {
    render(
      <FormInput 
        label="Email" 
        name="email" 
        value="" 
        onChange={() => {}} 
        placeholder="Enter your email" 
      />
    )
    expect(screen.getByPlaceholderText('Enter your email')).toBeInTheDocument()
  })
})
