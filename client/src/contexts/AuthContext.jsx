import { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'
import api from '../services/api'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  // Check if user is authenticated on app load
  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('authToken')
      if (!token) {
        setUser(null)
        setIsAuthenticated(false)
        return
      }

      const response = await api.get('/auth/me')
      setUser(response.data)
      setIsAuthenticated(true)
    } catch (error) {
      setUser(null)
      setIsAuthenticated(false)
      localStorage.removeItem('authToken')
    } finally {
      setLoading(false)
    }
  }

  const login = async (credentials) => {
    try {
      setLoading(true)
      
      const response = await api.post('/auth/login', credentials)

      // Store token if provided (fallback for header-based auth)
      if (response.data.access_token) {
        localStorage.setItem('authToken', response.data.access_token)
      }

      // Get user profile with the new token
      try {
        const userResponse = await api.get('/auth/me')
        setUser(userResponse.data)
        setIsAuthenticated(true)
      } catch (userError) {
        // Still consider login successful if we got a token
        setIsAuthenticated(true)
      }

      toast.success('Welcome back!')
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.detail || error.message || 'Login failed'
      toast.error(message)
      return { success: false, error: message }
    } finally {
      setLoading(false)
    }
  }

  const register = async (userData) => {
    try {
      setLoading(true)

      // Use a separate axios instance without credentials for registration
      const registerApi = axios.create({
        baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json',
        },
      })

      await registerApi.post('/auth/register', userData)

      // Registration successful - redirect to login
      toast.success('Account created successfully! Please login to continue.')
      return { success: true, redirectToLogin: true }
    } catch (error) {
      const message = error.response?.data?.detail || 'Registration failed'
      toast.error(message)
      return { success: false, error: message }
    } finally {
      setLoading(false)
    }
  }

  const logout = async () => {
    try {
      await api.post('/auth/logout')
    } catch (error) {
      // Ignore logout errors
    } finally {
      setUser(null)
      setIsAuthenticated(false)
      localStorage.removeItem('authToken')
      toast.success('Logged out successfully')
    }
  }

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    checkAuth,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}