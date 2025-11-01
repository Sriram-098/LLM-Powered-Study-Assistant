import { useState } from 'react'
import { testConnection } from '../services/api'

const ConnectionTest = () => {
  const [testing, setTesting] = useState(false)
  const [result, setResult] = useState(null)

  const handleTest = async () => {
    setTesting(true)
    setResult(null)
    
    try {
      const connectionResult = await testConnection()
      setResult(connectionResult)
    } catch (error) {
      setResult({
        success: false,
        error: error.message,
        details: 'Failed to test connection'
      })
    } finally {
      setTesting(false)
    }
  }

  return (
    <div className="p-4 border border-gray-200 rounded-lg">
      <h3 className="text-lg font-semibold mb-4">Connection Test</h3>
      
      <button
        onClick={handleTest}
        disabled={testing}
        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 cursor-pointer"
      >
        {testing ? 'Testing...' : 'Test Connection'}
      </button>

      {result && (
        <div className={`mt-4 p-3 rounded-lg ${
          result.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
        }`}>
          <div className={`font-semibold ${result.success ? 'text-green-800' : 'text-red-800'}`}>
            {result.success ? '✅ Connection Successful' : '❌ Connection Failed'}
          </div>
          
          {result.success && result.data && (
            <div className="mt-2 text-sm text-green-700">
              <div>Status: {result.data.status}</div>
              {result.data.storage && (
                <div>Storage: {result.data.storage.configured ? 'Connected' : 'Not configured'}</div>
              )}
            </div>
          )}
          
          {!result.success && (
            <div className="mt-2 text-sm text-red-700">
              <div>Error: {result.error}</div>
              {result.details && <div>Details: {JSON.stringify(result.details)}</div>}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ConnectionTest