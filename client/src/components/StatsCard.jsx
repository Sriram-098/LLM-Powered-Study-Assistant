const StatsCard = ({ title, value, icon, trend }) => {
  return (
    <div className="bg-white rounded-lg p-6 border border-gray-200 hover:border-gray-300 transition-colors">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-semibold text-gray-900 mt-2">{value}</p>
          {trend && (
            <div className="flex items-center mt-2">
              <span className={`text-sm font-medium ${
                trend.direction === 'up' ? 'text-gray-900' : 'text-gray-600'
              }`}>
                {trend.direction === 'up' ? '↗' : '↘'} {trend.value}
              </span>
              <span className="text-sm text-gray-500 ml-1">vs last month</span>
            </div>
          )}
        </div>
        <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
          <div className="w-6 h-6 text-gray-700">
            {icon}
          </div>
        </div>
      </div>
    </div>
  )
}

export default StatsCard