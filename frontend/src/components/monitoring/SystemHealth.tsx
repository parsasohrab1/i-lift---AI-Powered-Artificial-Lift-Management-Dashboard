'use client'

import { useQuery } from 'react-query'
import { apiClient } from '@/lib/api'
import { Activity, Database, Server, AlertCircle, CheckCircle, XCircle } from 'lucide-react'

export default function SystemHealth() {
  const { data: health, isLoading } = useQuery(
    'system-health',
    async () => {
      const response = await apiClient.get('/monitoring/health/summary')
      return response.data
    },
    {
      refetchInterval: 10000, // Refresh every 10 seconds
    }
  )

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-2 gap-4">
            {[1, 2].map((i) => (
              <div key={i} className="h-20 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'unhealthy':
        return <XCircle className="w-5 h-5 text-red-500" />
      default:
        return <AlertCircle className="w-5 h-5 text-yellow-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-50'
      case 'unhealthy':
        return 'text-red-600 bg-red-50'
      default:
        return 'text-yellow-600 bg-yellow-50'
    }
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">System Health</h2>
        <p className="text-sm text-gray-500 mt-1">
          Overall Status:{' '}
          <span
            className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(
              health?.overall_status || 'unknown'
            )}`}
          >
            {health?.overall_status?.toUpperCase() || 'UNKNOWN'}
          </span>
        </p>
      </div>

      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Database */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Database className="w-5 h-5 text-blue-500" />
                <span className="font-medium text-gray-900">Database</span>
              </div>
              {getStatusIcon(health?.database?.status)}
            </div>
            {health?.database?.response_time_ms && (
              <p className="text-sm text-gray-500">
                Response Time: {health.database.response_time_ms}ms
              </p>
            )}
          </div>

          {/* Redis */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Server className="w-5 h-5 text-red-500" />
                <span className="font-medium text-gray-900">Redis</span>
              </div>
              {getStatusIcon(health?.redis?.status)}
            </div>
            {health?.redis?.response_time_ms && (
              <p className="text-sm text-gray-500">
                Response Time: {health.redis.response_time_ms}ms
              </p>
            )}
          </div>

          {/* System Resources */}
          {health?.system && (
            <>
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Activity className="w-5 h-5 text-purple-500" />
                  <span className="font-medium text-gray-900">CPU Usage</span>
                </div>
                {health.system.cpu_percent !== null && (
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-gray-500">Usage</span>
                      <span className="text-sm font-medium text-gray-900">
                        {health.system.cpu_percent.toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          health.system.cpu_percent > 80
                            ? 'bg-red-500'
                            : health.system.cpu_percent > 60
                            ? 'bg-yellow-500'
                            : 'bg-green-500'
                        }`}
                        style={{ width: `${health.system.cpu_percent}%` }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>

              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Server className="w-5 h-5 text-indigo-500" />
                  <span className="font-medium text-gray-900">Memory Usage</span>
                </div>
                {health.system.memory_percent !== null && (
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-gray-500">Usage</span>
                      <span className="text-sm font-medium text-gray-900">
                        {health.system.memory_percent.toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          health.system.memory_percent > 80
                            ? 'bg-red-500'
                            : health.system.memory_percent > 60
                            ? 'bg-yellow-500'
                            : 'bg-green-500'
                        }`}
                        style={{ width: `${health.system.memory_percent}%` }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

