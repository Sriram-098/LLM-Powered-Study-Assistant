import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { AuthCard, RegisterForm } from '../components'

const Register = () => {
  const { register, loading } = useAuth()
  const navigate = useNavigate()

  const handleRegister = async (formData) => {
    const result = await register(formData)
    if (result.success && result.redirectToLogin) {
      // Redirect to login page after successful registration
      setTimeout(() => {
        navigate('/login')
      }, 1500) // Small delay to show success message
    }
    return result
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <AuthCard
        title="Create Account"
        subtitle="Join us and start your learning journey"
      >
        <RegisterForm onSubmit={handleRegister} loading={loading} />
      </AuthCard>
    </div>
  )
}

export default Register