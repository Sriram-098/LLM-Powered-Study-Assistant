import { Link } from 'react-router-dom'
import Card from './Card'

const QuickActions = () => {
  const actions = [
    {
      title: 'Add Material',
      description: 'Upload files or enter text content',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      ),
      href: '/upload',
      color: 'bg-black'
    },
    {
      title: 'View History',
      description: 'Browse your uploaded materials',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      href: '/history',
      color: 'bg-gray-600'
    },
    {
      title: 'Generate Quiz',
      description: 'Create quiz from your materials',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      href: '/history',
      color: 'bg-gray-800'
    }
  ]

  return (
    <Card>
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Quick Actions</h3>
      <div className="space-y-4">
        {actions.map((action, index) => (
          <Link
            key={index}
            to={action.href}
            className="flex items-center p-4 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors group cursor-pointer"
          >
            <div className={`p-3 rounded-lg ${action.color} text-white mr-4 transition-transform`}>
              {action.icon}
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 group-hover:text-black transition-colors">
                {action.title}
              </h4>
              <p className="text-sm text-gray-600">{action.description}</p>
            </div>
            <svg className="w-5 h-5 text-gray-400 ml-auto group-hover:text-black transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        ))}
      </div>
    </Card>
  )
}

export default QuickActions