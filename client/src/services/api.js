import axios from 'axios'
import toast from 'react-hot-toast'

// Create axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  withCredentials: true, // Enable for cookie-based auth
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available (fallback for header-based auth)
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login
      localStorage.removeItem('authToken')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    } else if (error.response?.status === 403) {
      toast.error('Access denied')
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.')
    } else if (error.code === 'ECONNABORTED') {
      toast.error('Request timeout. Please try again.')
    } else if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
      toast.error('Cannot connect to server. Please check if the server is running.')
    } else if (!error.response) {
      toast.error('Network error. Please check your connection.')
    }
    
    return Promise.reject(error)
  }
)

// Add a function to test API connection
export const testConnection = async () => {
  try {
    const response = await api.get('/health')
    return { success: true, data: response.data }
  } catch (error) {
    return { 
      success: false, 
      error: error.message,
      details: error.response?.data || 'Connection failed'
    }
  }
}

export default api