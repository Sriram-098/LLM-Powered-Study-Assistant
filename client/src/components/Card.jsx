const Card = ({ 
  children, 
  className = '', 
  padding = 'md',
  hover = false 
}) => {
  const paddingClasses = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  }
  
  const hoverClasses = hover ? 'hover:border-gray-300 transition-colors duration-200' : ''

  return (
    <div className={`bg-white rounded-lg border border-gray-200 ${paddingClasses[padding]} ${hoverClasses} ${className}`}>
      {children}
    </div>
  )
}

export default Card