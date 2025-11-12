'use client'

import { useQuery } from 'react-query'
import { apiClient } from '@/lib/api'
import * as mockData from '@/lib/mockData'
import { Activity, CheckCircle, AlertTriangle, XCircle } from 'lucide-react'

export default function SensorStatusWidget() {
  const { data: sensors, isLoading } = useQuery(
    'sensor-status',
    async () => {
      try {
        const response = await apiClient.get('/sensors/realtime')
        return response.data
      } catch (error) {
        console.warn('Using mock sensor status data')
        return { data: mockData.generateRealtimeSensorData(), timestamp: new Date().toISOString() }
      }
    },
    {
      refetchInterval: 10000,
    }
  )

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-8 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  // Count sensors by status (based on data quality)
  const sensorCounts: { [key: string]: number } = {
    healthy: 0,
    warning: 0,
    critical: 0,
    offline: 0,
  }

  if (sensors?.data) {
    Object.values(sensors.data).forEach((wellSensors: any) => {
      Object.values(wellSensors).forEach((sensor: any) => {
        const quality = sensor.data_quality || sensor.quality || 0
        if (!sensor || quality === 0) {
          sensorCounts.offline++
        } else if (quality >= 80) {
          sensorCounts.healthy++
        } else if (quality >= 60) {
          sensorCounts.warning++
        } else {
          sensorCounts.critical++
        }
      })
    })
  }

  const totalSensors =
    sensorCounts.healthy + sensorCounts.warning + sensorCounts.critical + sensorCounts.offline

  const statusItems = [
    {
      label: 'Healthy',
      count: sensorCounts.healthy,
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      label: 'Warning',
      count: sensorCounts.warning,
      icon: AlertTriangle,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
    },
    {
      label: 'Critical',
      count: sensorCounts.critical,
      icon: XCircle,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
    },
    {
      label: 'Offline',
      count: sensorCounts.offline,
      icon: Activity,
      color: 'text-gray-600',
      bgColor: 'bg-gray-50',
    },
  ]

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Sensor Status</h2>
        <p className="text-sm text-gray-500 mt-1">
          {totalSensors} total sensors monitored
        </p>
      </div>
      <div className="p-6">
        <div className="space-y-3">
          {statusItems.map((item) => {
            const Icon = item.icon
            const percentage =
              totalSensors > 0 ? ((item.count / totalSensors) * 100).toFixed(1) : 0
            return (
              <div key={item.label} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${item.bgColor}`}>
                    <Icon className={`h-5 w-5 ${item.color}`} />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{item.label}</p>
                    <p className="text-xs text-gray-500">{item.count} sensors</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${item.bgColor.replace('50', '500')}`}
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-600 w-12 text-right">
                    {percentage}%
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

