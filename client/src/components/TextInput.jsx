import { useState } from 'react'

const TextInput = ({ value, onChange, placeholder = "Enter your text content here..." }) => {
  const [charCount, setCharCount] = useState(value?.length || 0)

  const handleChange = (e) => {
    const newValue = e.target.value
    setCharCount(newValue.length)
    onChange(newValue)
  }

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Text Content
      </label>
      <div className="relative">
        <textarea
          value={value}
          onChange={handleChange}
          placeholder={placeholder}
          rows={12}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:border-gray-500 transition-colors resize-vertical min-h-[200px]"
        />
        <div className="absolute bottom-3 right-3 text-xs text-gray-500 bg-white px-2 py-1 rounded">
          {charCount.toLocaleString()} characters
        </div>
      </div>
      <p className="mt-2 text-sm text-gray-500">
        Enter the text content you want to analyze. Minimum 50 characters recommended.
      </p>
    </div>
  )
}

export default TextInput