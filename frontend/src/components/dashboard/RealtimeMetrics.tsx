'use client'

import { useQuery } from 'react-query'
import { apiClient } from '@/lib/api'
import { Activity, Thermometer, Gauge, Zap } from 'lucide-react'

export default function RealtimeMetrics() {
  const { data: realtimeData, isLoading } = useQuery(
    'realtime-metrics',
    async () => {
      const response = await apiClient.get('/sensors/realtime')
      return response.data
    },
    {
      refetchInterval: 5000, // Refresh every 5 seconds
    }
  )

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-2 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-20 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  // Aggregate metrics from all wells
  const metrics: any[] = []
  if (realtimeData?.data) {
    Object.entries(realtimeData.data).forEach(([wellId, sensors]: [string, any]) => {
      Object.entries(sensors).forEach(([sensorType, sensorData]: [string, any]) => {
        const existing = metrics.find((m) => m.type === sensorType)
        if (existing) {
          existing.values.push(sensorData.value)
          existing.wells.add(wellId)
        } else {
          metrics.push({
            type: sensorType,
            values: [sensorData.value],
            wells: new Set([wellId]),
            unit: sensorData.unit,
          })
        }
      })
    })
  }

  const getIcon = (type: string) => {
    if (type.includes('temperature')) return Thermometer
    if (type.includes('pressure')) return Gauge
    if (type.includes('current')) return Zap
    return Activity
  }

  const getAverage = (values: number[]) => {
    return values.reduce((a, b) => a + b, 0) / values.length
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Real-time Metrics</h2>
        <p className="text-sm text-gray-500 mt-1">Live sensor data across all wells</p>
      </div>
      <div className="p-6">
        {metrics.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No real-time data available
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {metrics.map((metric) => {
              const Icon = getIcon(metric.type)
              const avg = getAverage(metric.values)
              return (
                <div
                  key={metric.type}
                  className="p-4 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <div className="flex items-center justify-between mb-2">
                    <Icon className="h-5 w-5 text-primary-600" />
                    <span className="text-xs text-gray-500">
                      {metric.wells.size} well{metric.wells.size !== 1 ? 's' : ''}
                    </span>
                  </div>
                  <p className="text-xs text-gray-600 mb-1">
                    {metric.type.replace('_', ' ')}
                  </p>
                  <p className="text-2xl font-bold text-gray-900">
                    {avg.toFixed(2)}
                    <span className="text-sm font-normal text-gray-500 ml-1">
                      {metric.unit || ''}
                    </span>
                  </p>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

