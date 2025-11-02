import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../services/api'
import toast from 'react-hot-toast'
import { QuizTaker, MarkdownRenderer } from '../components'

const MaterialView = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [material, setMaterial] = useState(null)
  const [generatedData, setGeneratedData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState({
    summary: false,
    quiz: false,
    concepts: false
  })
  const [activeTab, setActiveTab] = useState('content')
  const [showQuizTaker, setShowQuizTaker] = useState(false)
  const [quizScore, setQuizScore] = useState(null)

  useEffect(() => {
    fetchMaterial()
  }, [id])

  const fetchMaterial = async () => {
    try {
      const response = await api.get(`/materials/${id}`)
      setMaterial(response.data.material)
      setGeneratedData(response.data.generated_data)
    } catch (error) {
      toast.error('Failed to load material')
      navigate('/history')
    } finally {
      setLoading(false)
    }
  }

  const generateSummary = async () => {
    setGenerating(prev => ({ ...prev, summary: true }))
    try {
      const response = await api.post(`/llm/generate-summary/${id}`)
      setGeneratedData(prev => ({
        ...prev,
        summary: response.data.summary
      }))
      toast.success('Summary generated successfully!')
    } catch (error) {
      toast.error('Failed to generate summary')
    } finally {
      setGenerating(prev => ({ ...prev, summary: false }))
    }
  }

  const generateQuiz = async () => {
    setGenerating(prev => ({ ...prev, quiz: true }))
    try {
      const response = await api.post(`/llm/generate-quiz/${id}`)
      setGeneratedData(prev => ({
        ...prev,
        quiz_questions: JSON.stringify(response.data.quiz_questions)
      }))
      toast.success('Quiz generated successfully!')
    } catch (error) {
      toast.error('Failed to generate quiz')
    } finally {
      setGenerating(prev => ({ ...prev, quiz: false }))
    }
  }

  const generateConcepts = async () => {
    setGenerating(prev => ({ ...prev, concepts: true }))
    try {
      const response = await api.post(`/llm/extract-concepts/${id}`)
      setGeneratedData(prev => ({
        ...prev,
        key_concepts: JSON.stringify(response.data.key_concepts)
      }))
      toast.success('Concepts extracted successfully!')
    } catch (error) {
      toast.error('Failed to extract concepts')
    } finally {
      setGenerating(prev => ({ ...prev, concepts: false }))
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const handleViewOriginal = () => {
    // Create a new window/tab to display the original content
    const newWindow = window.open('', '_blank')
    if (newWindow) {
      // Clean and normalize the content to fix vertical display issues
      let cleanContent = material.content || 'No content available'

      // Aggressive content cleaning to fix word separation issues
      cleanContent = cleanContent
        .replace(/[\u200B-\u200D\uFEFF]/g, '') // Remove zero-width characters
        .replace(/\r\n/g, '\n') // Normalize line endings
        .replace(/\r/g, '\n') // Convert remaining \r to \n
        .replace(/\t/g, '    ') // Convert tabs to spaces
        .replace(/\u00A0/g, ' ') // Replace non-breaking spaces with regular spaces
        .replace(/\s+/g, ' ') // Replace multiple spaces with single space
        .replace(/\n\s+/g, '\n') // Remove spaces at beginning of lines
        .replace(/\s+\n/g, '\n') // Remove spaces at end of lines
        .replace(/\n{3,}/g, '\n\n') // Replace multiple line breaks with double line breaks
        .trim() // Remove leading/trailing whitespace

      // If content appears to be separated by unusual characters, try to fix it
      if (cleanContent.includes('   ')) {
        // If there are many triple spaces, it might be word separation issue
        cleanContent = cleanContent.replace(/\s{3,}/g, ' ')
      }

      // Properly escape the content to prevent HTML injection and preserve formatting
      const escapedContent = cleanContent
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;')

      const escapedTitle = material.title
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;')

      const htmlContent = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${escapedTitle} - Original Content</title>
  <style>
    * {
      box-sizing: border-box;
    }
    body { 
      font-family: 'Georgia', 'Times New Roman', serif; 
      padding: 20px; 
      line-height: 1.6; 
      max-width: 1000px; 
      margin: 0 auto;
      background-color: #f9fafb;
      color: #1f2937;
      word-spacing: normal;
      letter-spacing: normal;
    }
    .header {
      background: white;
      padding: 25px;
      border-radius: 12px;
      margin-bottom: 25px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      border-left: 4px solid #3b82f6;
    }
    .content {
      background: white;
      padding: 40px;
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      font-size: 16px;
      line-height: 1.6;
      text-align: justify;
      word-spacing: normal;
      letter-spacing: normal;
      white-space: pre-line;
      word-wrap: break-word;
      overflow-wrap: break-word;
      hyphens: auto;
    }
    .content p {
      margin: 1em 0;
      text-indent: 0;
    }
    h1 { 
      color: #1f2937; 
      margin: 0 0 15px 0; 
      font-size: 28px;
      font-weight: 600;
    }
    .meta { 
      color: #6b7280; 
      font-size: 14px;
      font-family: 'Arial', sans-serif;
    }
    .meta span {
      display: inline-block;
      margin-right: 15px;
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>${escapedTitle}</h1>
    <div class="meta">
      <span><strong>Type:</strong> ${material.file_type.toUpperCase()}</span>
      <span><strong>Characters:</strong> ${material.content?.length || 0}</span>
      <span><strong>Uploaded:</strong> ${formatDate(material.uploaded_at)}</span>
    </div>
  </div>
  <div class="content">${escapedContent}</div>
</body>
</html>`

      newWindow.document.open()
      newWindow.document.write(htmlContent)
      newWindow.document.close()
    }
  }

  const handleDownloadOriginal = async () => {
    try {
      if (material.file_url) {
        // For PDF files, get the download URL from backend
        const response = await api.get(`/materials/download/${material.id}`)
        const downloadUrl = response.data.download_url

        // Create a temporary link and click it to download
        const link = document.createElement('a')
        link.href = downloadUrl
        link.download = `${material.title}.${material.file_type}`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)

        toast.success('Download started!')
      } else {
        // For text content, create a downloadable text file
        const blob = new Blob([material.content], { type: 'text/plain' })
        const url = URL.createObjectURL(blob)

        const link = document.createElement('a')
        link.href = url
        link.download = `${material.title}.txt`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)

        URL.revokeObjectURL(url)
        toast.success('Text file downloaded!')
      }
    } catch (error) {
      toast.error('Failed to download file')
      console.error('Download error:', error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!material) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Material not found</h2>
          <button
            onClick={() => navigate('/history')}
            className="text-blue-600 hover:text-blue-800 cursor-pointer"
          >
            Back to History
          </button>
        </div>
      </div>
    )
  }

  const quizQuestions = generatedData?.quiz_questions ? JSON.parse(generatedData.quiz_questions) : []
  const keyConcepts = generatedData?.key_concepts ? JSON.parse(generatedData.key_concepts) : []

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
      {/* Header */}
      <div className="mb-8 animate-slide-up">
        <button
          onClick={() => navigate('/history')}
          className="inline-flex items-center text-gray-600 hover:text-primary-600 mb-6 font-semibold transition-smooth group cursor-pointer"
        >
          <svg className="w-5 h-5 mr-2 group-hover:-translate-x-1 transition-smooth" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to History
        </button>

        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
          <div className="flex-1">
            <h1 className="heading-1 text-gray-900 mb-3">{material.title}</h1>
            <div className="flex flex-wrap items-center gap-3">
              <span className="inline-flex items-center px-4 py-2 rounded-lg text-sm font-semibold bg-gray-100 text-gray-800 border border-gray-300">
                {material.file_type.toUpperCase()}
              </span>
              <span className="body-base text-gray-600 flex items-center">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Uploaded {formatDate(material.uploaded_at)}
              </span>
            </div>
          </div>

          {/* Auto-Processing Status or Manual Action Buttons */}
          <div className="flex flex-wrap gap-3">
            {/* Show auto-processing info if no generated data exists */}
            {!generatedData?.summary && !generatedData?.quiz_questions && !generatedData?.key_concepts && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg px-4 py-3">
                <div className="flex items-center">
                  <svg className="animate-spin w-5 h-5 text-blue-600 mr-2" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span className="text-blue-800 text-sm font-medium">AI is automatically processing your material...</span>
                </div>
              </div>
            )}

            {/* Manual generation buttons (fallback if auto-processing didn't work) */}
            {!generatedData?.summary && (
              <button
                onClick={generateSummary}
                disabled={generating.summary}
                className="inline-flex items-center px-5 py-3 bg-black text-white rounded-lg font-semibold hover:bg-gray-800 disabled:opacity-50 transition-colors cursor-pointer disabled:cursor-not-allowed"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                {generating.summary ? 'Generating...' : 'Generate Summary'}
              </button>
            )}
            {!generatedData?.quiz_questions && (
              <button
                onClick={generateQuiz}
                disabled={generating.quiz}
                className="inline-flex items-center px-5 py-3 bg-black text-white rounded-lg font-semibold hover:bg-gray-800 disabled:opacity-50 transition-colors cursor-pointer disabled:cursor-not-allowed"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {generating.quiz ? 'Generating...' : 'Generate Quiz'}
              </button>
            )}
            {!generatedData?.key_concepts && (
              <button
                onClick={generateConcepts}
                disabled={generating.concepts}
                className="inline-flex items-center px-5 py-3 bg-black text-white rounded-lg font-semibold hover:bg-gray-800 disabled:opacity-50 transition-colors cursor-pointer disabled:cursor-not-allowed"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                {generating.concepts ? 'Extracting...' : 'Extract Concepts'}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-2xl shadow-md border border-gray-200 mb-6 p-2">
        <nav className="flex flex-wrap gap-2">
          <button
            onClick={() => setActiveTab('content')}
            className={`px-6 py-3 rounded-lg font-semibold transition-colors cursor-pointer ${activeTab === 'content'
              ? 'bg-black text-white'
              : 'text-gray-600 hover:bg-gray-100'
              }`}
          >
            <svg className="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Original Content
          </button>
          {generatedData?.summary && (
            <button
              onClick={() => setActiveTab('summary')}
              className={`px-6 py-3 rounded-lg font-semibold transition-colors cursor-pointer ${activeTab === 'summary'
                ? 'bg-black text-white'
                : 'text-gray-600 hover:bg-gray-100'
                }`}
            >
              <svg className="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              Summary
            </button>
          )}
          {generatedData?.quiz_questions && (
            <button
              onClick={() => setActiveTab('quiz')}
              className={`px-6 py-3 rounded-lg font-semibold transition-colors cursor-pointer ${activeTab === 'quiz'
                ? 'bg-black text-white'
                : 'text-gray-600 hover:bg-gray-100'
                }`}
            >
              <svg className="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Quiz ({quizQuestions.length})
            </button>
          )}
          {generatedData?.key_concepts && (
            <button
              onClick={() => setActiveTab('concepts')}
              className={`px-6 py-3 rounded-lg font-semibold transition-colors cursor-pointer ${activeTab === 'concepts'
                ? 'bg-black text-white'
                : 'text-gray-600 hover:bg-gray-100'
                }`}
            >
              <svg className="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              Key Concepts ({keyConcepts.length})
            </button>
          )}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-2xl shadow-xl border border-gray-200 p-8">
        {activeTab === 'content' && (
          <div className="animate-fade-in">
            <h2 className="heading-3 text-gray-900 mb-6 flex items-center">
              <span className="p-2 bg-blue-100 rounded-lg mr-3">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </span>
              Original Content
            </h2>

            <div className="bg-gray-50 rounded-xl p-8 border border-gray-200 text-center">
              <div className="mb-6">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-4-4m4 4l4-4m6-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {material.file_type === 'pdf' ? 'PDF Document' : 'Text Document'}
                </h3>
                <p className="text-gray-600 mb-4">
                  {material.file_type === 'pdf'
                    ? 'View or download the original PDF file'
                    : 'View or download the original text content'
                  }
                </p>
                <div className="text-sm text-gray-500 mb-6">
                  <span className="inline-flex items-center px-3 py-1 bg-gray-100 rounded-full">
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    {material.content?.length || 0} characters
                  </span>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <button
                  onClick={() => handleViewOriginal()}
                  className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors cursor-pointer"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  View Original
                </button>

                {material.file_url && (
                  <button
                    onClick={() => handleDownloadOriginal()}
                    className="inline-flex items-center px-6 py-3 bg-gray-600 text-white rounded-lg font-semibold hover:bg-gray-700 transition-colors cursor-pointer"
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-4-4m4 4l4-4m6-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Download {material.file_type.toUpperCase()}
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'summary' && generatedData?.summary && (
          <div className="animate-fade-in">
            <h2 className="heading-3 text-gray-900 mb-6 flex items-center">
              <span className="p-2 bg-green-100 rounded-lg mr-3">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </span>
              AI-Generated Summary
            </h2>
            <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
              <MarkdownRenderer content={generatedData.summary} />
            </div>
          </div>
        )}

        {activeTab === 'quiz' && quizQuestions.length > 0 && (
          <div className="animate-fade-in">
            {showQuizTaker ? (
              <QuizTaker
                questions={quizQuestions}
                onComplete={(score) => {
                  setQuizScore(score)
                  setShowQuizTaker(false)
                  toast.success(`Quiz completed! You scored ${score.percentage}%`)
                }}
                onCancel={() => setShowQuizTaker(false)}
              />
            ) : (
              <>
                <div className="text-center">
                  <h2 className="heading-3 text-gray-900 mb-6 flex items-center justify-center">
                    <span className="p-2 bg-purple-100 rounded-lg mr-3">
                      <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </span>
                    Quiz Ready
                  </h2>

                  <div className="bg-gray-50 rounded-xl p-8 border border-gray-200 mb-6">
                    <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      Quiz Available
                    </h3>
                    <p className="text-gray-600 mb-6">
                      Test your knowledge with {quizQuestions.length} questions based on this material
                    </p>

                    <button
                      onClick={() => setShowQuizTaker(true)}
                      className="inline-flex items-center px-8 py-4 bg-black text-white rounded-lg font-semibold hover:bg-gray-800 transition-colors text-lg cursor-pointer"
                    >
                      <svg className="w-6 h-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Take Quiz
                    </button>
                  </div>

                  {quizScore && (
                    <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-xl p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="text-lg font-bold text-gray-900 mb-1">Latest Quiz Score</h3>
                          <p className="text-gray-600">
                            You scored {quizScore.correct} out of {quizScore.total} questions correctly
                          </p>
                        </div>
                        <div className="text-right">
                          <div className={`text-3xl font-bold ${quizScore.percentage >= 80 ? 'text-green-600' :
                            quizScore.percentage >= 60 ? 'text-yellow-600' : 'text-red-600'
                            }`}>
                            {quizScore.percentage}%
                          </div>
                          <p className="text-sm text-gray-500">Score</p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        )}

        {activeTab === 'concepts' && keyConcepts.length > 0 && (
          <div className="animate-fade-in">
            <h2 className="heading-3 text-gray-900 mb-6 flex items-center">
              <span className="p-2 bg-blue-100 rounded-lg mr-3">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </span>
              Key Concepts
            </h2>
            <div className="grid grid-cols-1 gap-4">
              {keyConcepts.map((concept, index) => {
                // Parse the concept string to extract name and explanation
                // Format: **Name**\nExplanation
                const lines = concept.split('\n');
                const conceptName = lines[0]?.replace(/\*\*/g, '').trim() || concept;
                const conceptExplanation = lines[1]?.trim() || '';

                return (
                  <div
                    key={index}
                    className="bg-gray-50 border border-gray-200 rounded-lg p-5 hover:border-gray-300 transition-colors"
                  >
                    <div className="flex items-start">
                      <span className="inline-flex items-center justify-center w-8 h-8 bg-black text-white rounded-lg mr-4 flex-shrink-0 text-sm font-bold">
                        {index + 1}
                      </span>
                      <div className="flex-1">
                        <h4 className="text-gray-900 font-bold text-lg mb-2">{conceptName}</h4>
                        {conceptExplanation && (
                          <p className="text-gray-600 leading-relaxed">{conceptExplanation}</p>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default MaterialView