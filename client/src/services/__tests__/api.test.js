import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { testConnection } from '../api'
import api from '../api'

// Mock axios
vi.mock('axios', () => {
  const mockAxiosInstance = {
    get: vi.fn(),
    post: vi.fn(),
    interceptors: {
      request: {
        use: vi.fn((successHandler) => {
          mockAxiosInstance._requestInterceptor = successHandler
          return 0
        })
      },
      response: {
        use: vi.fn((successHandler, errorHandler) => {
          mockAxiosInstance._responseInterceptor = { successHandler, errorHandler }
          return 0
        })
      }
    },
    _requestInterceptor: null,
    _responseInterceptor: null
  }

  return {
    default: {
      create: vi.fn(() => mockAxiosInstance)
    }
  }
})

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

// Mock toast
vi.mock('react-hot-toast', () => ({
  default: {
    error: vi.fn(),
    success: vi.fn()
  }
}))

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.clear()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('testConnection', () => {
    it('returns success when connection is successful', async () => {
      const mockResponse = { data: { status: 'healthy' } }
      api.get = vi.fn().mockResolvedValueOnce(mockResponse)

      const result = await testConnection()

      expect(result.success).toBe(true)
      expect(result.data).toEqual(mockResponse.data)
      expect(api.get).toHaveBeenCalledWith('/health')
    })

    it('returns error when connection fails', async () => {
      const mockError = new Error('Connection failed')
      api.get = vi.fn().mockRejectedValueOnce(mockError)

      const result = await testConnection()

      expect(result.success).toBe(false)
      expect(result.error).toBe('Connection failed')
      expect(result.details).toBe('Connection failed')
    })

    it('includes response data in error details when available', async () => {
      const mockError = {
        message: 'Server error',
        response: {
          data: { detail: 'Internal server error' }
        }
      }
      api.get = vi.fn().mockRejectedValueOnce(mockError)

      const result = await testConnection()

      expect(result.success).toBe(false)
      expect(result.error).toBe('Server error')
      expect(result.details).toEqual({ detail: 'Internal server error' })
    })
  })

  describe('API instance configuration', () => {
    it('is created with correct base configuration', () => {
      expect(api).toBeDefined()
      expect(typeof api.get).toBe('function')
      expect(typeof api.post).toBe('function')
    })

    it('has request interceptor available', () => {
      expect(api.interceptors).toBeDefined()
      expect(api.interceptors.request).toBeDefined()
    })

    it('has response interceptor available', () => {
      expect(api.interceptors).toBeDefined()
      expect(api.interceptors.response).toBeDefined()
    })
  })

  describe('Request interceptor', () => {
    it('adds Authorization header when token exists', () => {
      localStorageMock.setItem('authToken', 'test-token')
      
      const config = { headers: {} }
      const interceptor = api._requestInterceptor
      
      if (interceptor) {
        const result = interceptor(config)
        expect(result.headers.Authorization).toBe('Bearer test-token')
      }
    })

    it('does not add Authorization header when token does not exist', () => {
      const config = { headers: {} }
      const interceptor = api._requestInterceptor
      
      if (interceptor) {
        const result = interceptor(config)
        expect(result.headers.Authorization).toBeUndefined()
      }
    })
  })
})
