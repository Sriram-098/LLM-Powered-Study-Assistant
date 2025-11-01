const EmptyState = ({ 
  icon, 
  title, 
  description, 
  actionButton,
  className = "" 
}) => {
  return (
    <div className={`text-center py-12 ${className}`}>
      {icon && (
        <div className="mx-auto h-12 w-12 text-gray-400 mb-4">
          {icon}
        </div>
      )}
      <h3 className="mt-2 text-sm font-semibold text-gray-900">{title}</h3>
      {description && (
        <p className="mt-1 text-sm text-gray-500">{description}</p>
      )}
      {actionButton && (
        <div className="mt-6">
          {actionButton}
        </div>
      )}
    </div>
  )
}

export default EmptyState