import { useAuth } from '../contexts/AuthContext'

const WelcomeSection = () => {
  const { user } = useAuth()
  
  const currentHour = new Date().getHours()
  const getGreeting = () => {
    if (currentHour < 12) return 'Good morning'
    if (currentHour < 18) return 'Good afternoon'
    return 'Good evening'
  }

  return (
    <div className="bg-black rounded-lg p-8 text-white mb-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-semibold mb-2">
            {getGreeting()}, {user?.username || 'there'}!
          </h2>
          <p className="text-gray-300 text-lg">
            Ready to enhance your learning experience with AI-powered tools?
          </p>
        </div>
        <div className="hidden md:block">
          <div className="w-16 h-16 bg-gray-800 rounded-lg flex items-center justify-center">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  )
}

export default WelcomeSection