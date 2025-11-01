import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import Card from './Card'
import LoadingSpinner from './LoadingSpinner'
import EmptyState from './EmptyState'

const RecentUploads = () => {
  const [materials, setMaterials] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchRecentMaterials()
  }, [])

  const fetchRecentMaterials = async () => {
    try {
      setError(null)
      const response = await api.get('/materials/get-history')
      const materials = response.data || []
      setMaterials(materials.slice(0, 5)) // Show only 5 recent items
    } catch (error) {
      console.error('Failed to fetch materials:', error)
      
      // Set user-friendly error message
      let errorMessage = 'Failed to load recent uploads'
      
      if (error.code === 'ERR_NETWORK' || error.code === 'ECONNREFUSED') {
        errorMessage = 'Cannot connect to server. Please check if the backend is running.'
      } else if (error.response?.status === 401) {
        errorMessage = 'Please log in to view your materials'
      } else if (error.response?.status === 500) {
        errorMessage = 'Server error. Please try again later.'
      } else if (error.code === 'ECONNABORTED') {
        errorMessage = 'Request timeout. Please try again.'
      }
      
      setError(errorMessage)
      setMaterials([])
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }

  const getFileIcon = (fileType) => {
    if (fileType === 'pdf') {
      return (
        <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
        </svg>
      )
    }
    return (
      <svg className="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
        <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
      </svg>
    )
  }

  if (loading) {
    return (
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Recent Uploads</h3>
        <div className="py-8">
          <LoadingSpinner />
        </div>
      </Card>
    )
  }

  return (
    <Card>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Recent Uploads</h3>
        <Link
          to="/history"
          className="text-sm text-blue-600 hover:text-blue-700 font-medium cursor-pointer"
        >
          View all
        </Link>
      </div>

      {error ? (
        <EmptyState
          icon={
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          }
          title="Connection Error"
          description={error}
          actionButton={
            <button
              onClick={fetchRecentMaterials}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors cursor-pointer"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Retry
            </button>
          }
        />
      ) : materials.length === 0 ? (
        <EmptyState
          icon={
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          }
          title="No materials yet"
          description="Upload your first document to get started"
          actionButton={
            <Link
              to="/upload"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors cursor-pointer"
            >
              Upload Material
            </Link>
          }
        />
      ) : (
        <div className="space-y-3">
          {materials.map((item) => {
            // Handle both data structures: item.material or direct item
            const material = item.material || item
            const generatedData = item.generated_data || {}
            
            return (
              <Link
                key={material.id}
                to={`/material/${material.id}`}
                className="flex items-center p-3 rounded-xl hover:bg-gray-50 transition-colors group cursor-pointer"
              >
                <div className="flex-shrink-0 mr-3">
                  {getFileIcon(material.file_type)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate group-hover:text-blue-600 transition-colors">
                    {material.title}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatDate(material.uploaded_at)}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  {generatedData?.summary && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Summary
                    </span>
                  )}
                  {generatedData?.quiz_questions && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                      Quiz
                    </span>
                  )}
                  <svg className="w-4 h-4 text-gray-400 group-hover:text-blue-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </Link>
            )
          })}
        </div>
      )}
    </Card>
  )
}

export default RecentUploads