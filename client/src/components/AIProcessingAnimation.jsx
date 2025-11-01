import { useState, useEffect } from 'react'
import api from '../services/api'

const AIProcessingAnimation = ({ isVisible, materialId, onComplete }) => {
  const [percentage, setPercentage] = useState(0)
  const [dots, setDots] = useState('')
  const [isPolling, setIsPolling] = useState(false)

  // Animated dots effect
  useEffect(() => {
    if (!isVisible) return

    const interval = setInterval(() => {
      setDots(prev => {
        if (prev === '...') return ''
        return prev + '.'
      })
    }, 500)

    return () => clearInterval(interval)
  }, [isVisible])

  // Simulate percentage increase until backend completes
  useEffect(() => {
    if (!isVisible) {
      setPercentage(0)
      setIsPolling(false)
      return
    }

    // Start percentage animation
    const percentageInterval = setInterval(() => {
      setPercentage(prev => {
        if (prev >= 95) return 95 // Stop at 95% until backend completes
        return prev + Math.random() * 3 // Increase by 1-3% randomly
      })
    }, 800)

    // Start polling backend after initial upload
    const startPolling = setTimeout(() => {
      setIsPolling(true)
    }, 2000)

    return () => {
      clearInterval(percentageInterval)
      clearTimeout(startPolling)
    }
  }, [isVisible])

  // Poll backend for completion status
  useEffect(() => {
    if (!isPolling || !materialId) return

    const pollBackend = async () => {
      try {
        const response = await api.get(`/materials/${materialId}`)
        const generatedData = response.data.generated_data

        // Check if AI processing is complete (has summary, quiz, or concepts)
        if (generatedData && (generatedData.summary || generatedData.quiz_questions || generatedData.key_concepts)) {
          setPercentage(100)
          setTimeout(() => {
            onComplete?.()
          }, 1000)
          return
        }
      } catch (error) {
        console.log('Polling error:', error)
      }
    }

    // Poll every 2 seconds
    const pollInterval = setInterval(pollBackend, 2000)

    // Initial poll
    pollBackend()

    return () => clearInterval(pollInterval)
  }, [isPolling, materialId, onComplete])

  if (!isVisible) return null

  return (
    <div className="mt-6 bg-gray-50 border border-gray-200 rounded-lg p-4">
      <div className="flex items-center justify-center space-x-3">
        {/* Simple spinning icon */}
        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-600"></div>

        {/* Processing text with percentage */}
        <span className="text-gray-700 font-medium">
          Processing{dots} {Math.round(percentage)}%
        </span>
      </div>
    </div>
  )
}

export default AIProcessingAnimation