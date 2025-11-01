import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import toast from 'react-hot-toast'
import { PageHeader, Card, FormInput, FileUpload, Button, InputTypeSelector, TextInput, AIProcessingAnimation } from '../components'

const Upload = () => {
  const [inputType, setInputType] = useState('file')
  const [file, setFile] = useState(null)
  const [textContent, setTextContent] = useState('')
  const [title, setTitle] = useState('')
  const [loading, setLoading] = useState(false)
  const [showAIAnimation, setShowAIAnimation] = useState(false)
  const [materialId, setMaterialId] = useState(null)
  const navigate = useNavigate()

  const handleFileSelect = (selectedFile) => {
    if (validateFile(selectedFile)) {
      setFile(selectedFile)
      if (!title) {
        setTitle(selectedFile.name.replace(/\.[^/.]+$/, ''))
      }
    }
  }

  const validateFile = (file) => {
    const allowedTypes = ['application/pdf', 'text/plain']
    const maxSize = 10 * 1024 * 1024 // 10MB

    if (!allowedTypes.includes(file.type)) {
      toast.error('Please upload only PDF or text files')
      return false
    }

    if (file.size > maxSize) {
      toast.error('File size must be less than 10MB')
      return false
    }

    return true
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    // Validation based on input type
    if (inputType === 'file') {
      if (!file || !title.trim()) {
        toast.error('Please provide both a title and file')
        return
      }
    } else {
      if (!textContent.trim() || !title.trim()) {
        toast.error('Please provide both a title and text content')
        return
      }
      if (textContent.trim().length < 50) {
        toast.error('Text content should be at least 50 characters long')
        return
      }
    }

    setLoading(true)
    setShowAIAnimation(true)

    try {
      let response

      if (inputType === 'file') {
        // File upload
        const formData = new FormData()
        formData.append('file', file)
        
        response = await api.post(`/materials/upload-material?title=${encodeURIComponent(title.trim())}`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
      } else {
        // Text upload
        response = await api.post('/materials/upload-text', {
          title: title.trim(),
          content: textContent.trim()
        })
      }

      // Set the material ID for polling
      setMaterialId(response.data.id)
    } catch (error) {
      setShowAIAnimation(false)
      const message = error.response?.data?.detail || 'Upload failed'
      toast.error(message)
      setLoading(false)
    }
  }

  const removeFile = () => {
    setFile(null)
    setTitle('')
  }

  const handleInputTypeChange = (type) => {
    setInputType(type)
    // Clear previous inputs when switching
    setFile(null)
    setTextContent('')
    setTitle('')
  }

  const handleAnimationComplete = () => {
    setShowAIAnimation(false)
    setLoading(false)
    
    // Navigate to the material page after backend processing completes
    if (materialId) {
      toast.success('Material uploaded successfully! AI processing complete!')
      navigate(`/material/${materialId}`)
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <PageHeader
        title="Add Study Material"
        subtitle="Upload files or enter text content. Our AI will automatically generate summaries, quiz questions, and extract key concepts!"
        centered
      />

      {/* Automatic Processing Info */}
      <div className="max-w-2xl mx-auto mb-6">
        <div className="bg-gradient-to-r from-gray-50 to-gray-100 border border-gray-200 rounded-xl p-6">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="w-6 h-6 text-gray-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Automatic AI Processing</h3>
              <p className="text-gray-700 text-sm leading-relaxed mb-3">
                Once you upload your material, our Large Language Model (LLM) will automatically:
              </p>
              <ul className="text-sm text-gray-600 space-y-2">
                <li className="flex items-start">
                  <svg className="w-4 h-4 mr-2 text-gray-900 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  <span><strong>Generate concise summaries</strong> with key points and takeaways</span>
                </li>
                <li className="flex items-start">
                  <svg className="w-4 h-4 mr-2 text-gray-900 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span><strong>Create quiz questions for revision</strong> including multiple-choice, true/false, and short-answer questions</span>
                </li>
                <li className="flex items-start">
                  <svg className="w-4 h-4 mr-2 text-gray-900 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  <span><strong>Extract key concepts and terms</strong> in a neat, structured format</span>
                </li>
              </ul>
              <div className="mt-3 text-xs text-gray-500">
                ⚡ All processing happens automatically - no manual steps required!
              </div>
            </div>
          </div>
        </div>
      </div>

      <Card className="max-w-2xl mx-auto">
        <form onSubmit={handleSubmit} className="space-y-6">
          <InputTypeSelector
            selectedType={inputType}
            onTypeChange={handleInputTypeChange}
          />

          <FormInput
            id="title"
            name="title"
            type="text"
            label="Material Title"
            placeholder="Enter a descriptive title for your material"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />

          {inputType === 'file' ? (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Upload File
              </label>
              <FileUpload
                onFileSelect={handleFileSelect}
                file={file}
                onRemoveFile={removeFile}
                loading={loading}
              />
            </div>
          ) : (
            <TextInput
              value={textContent}
              onChange={setTextContent}
              placeholder="Enter your text content here. This could be lecture notes, article text, study material, or any content you want to analyze..."
            />
          )}

          <div className="flex justify-end space-x-4 pt-4">
            <Button
              type="button"
              variant="secondary"
              onClick={() => navigate('/history')}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={
                loading || (inputType === 'file' 
                  ? (!file || !title.trim()) 
                  : (!textContent.trim() || !title.trim() || textContent.trim().length < 50))
              }
              loading={loading}
            >
              {loading ? 'Uploading & Processing with AI...' : 'Upload & Process with AI'}
            </Button>
          </div>
        </form>

        {/* AI Processing Animation - Shows below the form */}
        <AIProcessingAnimation 
          isVisible={showAIAnimation} 
          materialId={materialId}
          onComplete={handleAnimationComplete}
        />
      </Card>
    </div>
  )
}

export default Upload