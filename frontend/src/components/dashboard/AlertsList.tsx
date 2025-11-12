'use client'

import { useQuery } from 'react-query'
import { apiClient } from '@/lib/api'
import { AlertTriangle, X } from 'lucide-react'
import Link from 'next/link'

export default function AlertsList() {
  const { data: alerts, isLoading } = useQuery(
    'critical-alerts',
    async () => {
      const response = await apiClient.get('/alerts/critical?limit=5')
      return response.data
    },
    {
      refetchInterval: 10000, // Refresh every 10 seconds
    }
  )

  const severityColors = {
    critical: 'bg-red-50 border-red-200 text-red-800',
    high: 'bg-orange-50 border-orange-200 text-orange-800',
    medium: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    low: 'bg-blue-50 border-blue-200 text-blue-800',
  }

  if (isLoading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            <div className="h-16 bg-gray-200 rounded"></div>
            <div className="h-16 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center">
          <AlertTriangle className="mr-2 h-5 w-5 text-red-600" />
          Critical Alerts
        </h2>
        <Link
          href="/dashboard/alerts"
          className="text-sm text-primary-600 hover:text-primary-700"
        >
          View all
        </Link>
      </div>

      {!alerts || alerts.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500">No critical alerts</p>
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.slice(0, 5).map((alert: any) => (
            <div
              key={alert.alert_id}
              className={`border rounded-lg p-3 ${severityColors[alert.severity as keyof typeof severityColors] || severityColors.low}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-sm font-medium">{alert.well_id}</p>
                  <p className="text-xs mt-1">{alert.message}</p>
                  <p className="text-xs mt-1 opacity-75">
                    {new Date(alert.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

