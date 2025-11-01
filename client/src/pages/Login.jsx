import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { AuthCard, LoginForm } from '../components'

const Login = () => {
  const { login, loading } = useAuth()
  const navigate = useNavigate()

  const handleLogin = async (formData) => {
    try {
      const result = await login(formData)
      
      if (result.success) {
        navigate('/')
      }
      return result
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <AuthCard
        title="Welcome Back"
        subtitle="Sign in to continue your learning journey"
      >
        <LoginForm onSubmit={handleLogin} loading={loading} />
      </AuthCard>
    </div>
  )
}

export default Login