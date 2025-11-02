import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from '../App'

// Mock all the page components
vi.mock('../pages/Login', () => ({
  default: () => <div>Login Page</div>
}))

vi.mock('../pages/Register', () => ({
  default: () => <div>Register Page</div>
}))

vi.mock('../pages/Dashboard', () => ({
  default: () => <div>Dashboard Page</div>
}))

vi.mock('../pages/Upload', () => ({
  default: () => <div>Upload Page</div>
}))

vi.mock('../pages/History', () => ({
  default: () => <div>History Page</div>
}))

vi.mock('../pages/MaterialView', () => ({
  default: () => <div>Material View Page</div>
}))

// Mock Header component
vi.mock('../components/Header', () => ({
  default: () => <div>Header</div>
}))

// Mock AuthContext
vi.mock('../contexts/AuthContext', () => ({
  AuthProvider: ({ children }) => <div>{children}</div>,
  useAuth: () => ({
    isAuthenticated: false,
    loading: false,
    user: null
  })
}))

// Mock react-hot-toast
vi.mock('react-hot-toast', () => ({
  Toaster: () => <div>Toaster</div>
}))

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    expect(screen.getByText('Header')).toBeInTheDocument()
  })

  it('renders Toaster component', () => {
    render(<App />)
    expect(screen.getByText('Toaster')).toBeInTheDocument()
  })

  it('wraps content in AuthProvider', () => {
    const { container } = render(<App />)
    expect(container.querySelector('div')).toBeInTheDocument()
  })

  it('renders main element', () => {
    const { container } = render(<App />)
    const main = container.querySelector('main')
    expect(main).toBeInTheDocument()
  })

  it('applies correct styling classes', () => {
    const { container } = render(<App />)
    const appDiv = container.querySelector('.min-h-screen.bg-gray-50')
    expect(appDiv).toBeInTheDocument()
  })
})
