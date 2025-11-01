const PageHeader = ({ title, subtitle, children, centered = false, className = '' }) => {
  if (centered) {
    return (
      <div className={`mb-8 text-center ${className}`}>
        <h1 className="text-3xl font-semibold text-gray-900 mb-3">{title}</h1>
        {subtitle && (
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">{subtitle}</p>
        )}
        {children && (
          <div className="mt-6">
            {children}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className={`bg-white border-b border-gray-200 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">{title}</h1>
            {subtitle && (
              <p className="mt-1 text-sm text-gray-600">{subtitle}</p>
            )}
          </div>
          {children && (
            <div className="flex items-center space-x-3">
              {children}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default PageHeader