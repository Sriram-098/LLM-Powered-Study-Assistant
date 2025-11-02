import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import { AuthProvider, useAuth } from '../AuthContext'

// Mock toast before importing anything else
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  }
}))

// Mock api service
vi.mock('../../services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  }
}))

// Import after mocking
import api from '../../services/api'
import toast from 'react-hot-toast'

// Mock localStorage
const localStorageMock = (() => {
  let store = {}
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => {
      store[key] = value.toString()
    },
    removeItem: (key) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    }
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.clear()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('useAuth hook', () => {
    it('throws error when used outside AuthProvider', () => {
      // Suppress console.error for this test
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      expect(() => {
        renderHook(() => useAuth())
      }).toThrow('useAuth must be used within an AuthProvider')
      
      consoleError.mockRestore()
    })

    it('returns auth context when used within AuthProvider', () => {
      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>
      const { result } = renderHook(() => useAuth(), { wrapper })

      expect(result.current).toHaveProperty('user')
      expect(result.current).toHaveProperty('loading')
      expect(result.current).toHaveProperty('isAuthenticated')
      expect(result.current).toHaveProperty('login')
      expect(result.current).toHaveProperty('register')
      expect(result.current).toHaveProperty('logout')
      expect(result.current).toHaveProperty('checkAuth')
    })
  })

  describe('Initial state', () => {
    it('initializes with correct default values', () => {
      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>
      const { result } = renderHook(() => useAuth(), { wrapper })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
    })

    it('checks authentication on mount when token exists', async () => {
      const mockUser = { id: 1, email: 'test@example.com', username: 'testuser' }
      localStorageMock.setItem('authToken', 'test-token')
      api.get.mockResolvedValueOnce({ data: mockUser })

      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>
      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(api.get).toHaveBeenCalledWith('/auth/me')
      expect(result.current.user).toEqual(mockUser)
      expect(result.current.isAuthenticated).toBe(true)
    })

    it('sets unauthenticated state when no token exists', async () => {
      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>
      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
    })

    it('handles authentication check failure', async () => {
      localStorageMock.setItem('authToken', 'invalid-token')
      api.get.mockRejectedValueOnce(new Error('Unauthorized'))

      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>
      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(localStorageMock.getItem('authToken')).toBeNull()
    })
  })

  describe('login', () => {
    it('successfully logs in user', async () => {
      const mockUser = { id: 1, email: 'test@example.com', username: 'testuser' }
      const credentials = { email: 'test@example.com', password: 'password123' }
      
      api.post.mockResolvedValueOnce({ data: { access_token: 'new-token' } })
      api.get.mockResolvedValueOnce({ data: mockUser })

      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>
      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      let loginResult
      await act(async () => {
        loginResult = await result.current.login(credentials)
      })

      expect(loginResult.success).toBe(true)
      expect(api.post).toHaveBeenCalledWith('/auth/login', credentials)
      expect(api.get).toHaveBeenCalledWith('/auth/me')
      expect(result.current.user).toEqual(mockUser)
      expect(result.current.isAuthenticated).toBe(true)
      expect(localStorageMock.getItem('authToken')).toBe('new-token')
      expect(toast.success).toHaveBeenCalledWith('Welcome back!')
    })

    it('handles login failure', async () => {
      const credentials = { email: 'test@example.com', password: 'wrong-password' }
      const errorMessage = 'Invalid credentials'
      
      api.post.mockRejectedValueOnce({
        response: { data: { detail: errorMessage } }
      })

      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>
      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      let loginResult
      await act(async () => {
        loginResult = await result.current.login(credentials)
      })

      expect(loginResult.success).toBe(false)
      expect(loginResult.error).toBe(errorMessage)
      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(toast.error).toHaveBeenCalledWith(errorMessage)
    })

    it('handles login with token but user fetch failure', async () => {
      const credentials = { email: 'test@example.com', password: 'password123' }
      
      api.post.mockResolvedValueOnce({ data: { access_token: 'new-token' } })
      api.get.mockRejectedValueOnce(new Error('User fetch failed'))

      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>
      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      let loginResult
      await act(async () => {
        loginResult = await result.current.login(credentials)
      })

      expect(loginResult.success).toBe(true)
      expect(result.current.isAuthenticated).toBe(true)
      expect(localStorageMock.getItem('authToken')).toBe('new-token')
    })
  })

  describe('register', () => {
    it('has register function available', () => {
      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>
      const { result } = renderHook(() => useAuth(), { wrapper })

      expect(result.current.register).toBeDefined()
      expect(typeof result.current.register).toBe('function')
    })

    // Note: Full register testing is complex due to axios.create usage
    // Better tested in integration/E2E tests
  })

  describe('logout', () => {
    it('successfully logs out user', async () => {
      const mockUser = { id: 1, email: 'logout@example.com', username: 'logoutuser' }
      localStorageMock.clear()
      localStorageMock.setItem('authToken', 'logout-token')
      
      api.get.mockResolvedValue({ data: mockUser })
      api.post.mockResolvedValue({})

      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>
      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.user).toEqual(mockUser)
        expect(result.current.isAuthenticated).toBe(true)
      })

      await act(async () => {
        await result.current.logout()
      })

      expect(api.post).toHaveBeenCalledWith('/auth/logout')
      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(localStorageMock.getItem('authToken')).toBeNull()
      expect(toast.success).toHaveBeenCalledWith('Logged out successfully')
    })

    it('logs out even if API call fails', async () => {
      const mockUser = { id: 1, email: 'test@example.com', username: 'testuser' }
      localStorageMock.setItem('authToken', 'test-token')
      
      api.get.mockResolvedValueOnce({ data: mockUser })
      api.post.mockRejectedValueOnce(new Error('Logout failed'))

      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>
      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.user).toEqual(mockUser)
      })

      await act(async () => {
        await result.current.logout()
      })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(localStorageMock.getItem('authToken')).toBeNull()
      expect(toast.success).toHaveBeenCalledWith('Logged out successfully')
    })
  })

  describe('checkAuth', () => {
    it('successfully checks authentication', async () => {
      const mockUser = { id: 2, email: 'checkauth@example.com', username: 'checkauthuser' }
      localStorageMock.clear()
      localStorageMock.setItem('authToken', 'checkauth-token')
      
      // Clear all previous mocks
      vi.clearAllMocks()
      api.get.mockResolvedValue({ data: mockUser })

      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>
      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      await act(async () => {
        await result.current.checkAuth()
      })

      expect(api.get).toHaveBeenCalledWith('/auth/me')
      expect(result.current.user).toEqual(mockUser)
      expect(result.current.isAuthenticated).toBe(true)
    })

    it('handles checkAuth when no token exists', async () => {
      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>
      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      await act(async () => {
        await result.current.checkAuth()
      })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
    })

    it('handles checkAuth failure', async () => {
      localStorageMock.setItem('authToken', 'invalid-token')
      api.get.mockRejectedValueOnce(new Error('Unauthorized'))

      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>
      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      await act(async () => {
        await result.current.checkAuth()
      })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(localStorageMock.getItem('authToken')).toBeNull()
    })
  })

  describe('Loading states', () => {
    it('sets loading to true during login', async () => {
      const credentials = { email: 'test@example.com', password: 'password123' }
      
      api.post.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))

      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>
      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.login(credentials)
      })

      expect(result.current.loading).toBe(true)
    })

    it('sets loading to false after login completes', async () => {
      const mockUser = { id: 1, email: 'test@example.com', username: 'testuser' }
      const credentials = { email: 'test@example.com', password: 'password123' }
      
      api.post.mockResolvedValueOnce({ data: { access_token: 'new-token' } })
      api.get.mockResolvedValueOnce({ data: mockUser })

      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>
      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      await act(async () => {
        await result.current.login(credentials)
      })

      expect(result.current.loading).toBe(false)
    })
  })
})
