'use client'

import { useState } from 'react'
import DashboardLayout from '@/components/layouts/DashboardLayout'
import { useAlerts, useResolveAlert } from '@/hooks/useAlerts'
import { CheckCircle, XCircle, AlertTriangle } from 'lucide-react'
import toast from 'react-hot-toast'

export default function AlertsPage() {
  const [filters, setFilters] = useState({
    severity: '',
    resolved: false,
  })

  const { data, isLoading } = useAlerts({
    severity: filters.severity || undefined,
    resolved: filters.resolved,
    limit: 100,
  })

  const resolveMutation = useResolveAlert()

  const handleResolve = async (alertId: string) => {
    await resolveMutation.mutateAsync(alertId)
  }

  const alerts = data?.alerts || []

  const severityColors = {
    critical: 'bg-red-50 border-red-200',
    high: 'bg-orange-50 border-orange-200',
    medium: 'bg-yellow-50 border-yellow-200',
    low: 'bg-blue-50 border-blue-200',
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Alerts</h1>
          <p className="mt-1 text-sm text-gray-500">
            Monitor and manage system alerts
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center space-x-4">
            <select
              value={filters.severity}
              onChange={(e) =>
                setFilters({ ...filters, severity: e.target.value })
              }
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500"
            >
              <option value="">All Severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>

            <label className="flex items-center">
              <input
                type="checkbox"
                checked={filters.resolved}
                onChange={(e) =>
                  setFilters({ ...filters, resolved: e.target.checked })
                }
                className="mr-2"
              />
              <span className="text-sm text-gray-700">Show resolved</span>
            </label>
          </div>
        </div>

        {/* Alerts list */}
        <div className="bg-white rounded-lg shadow">
          {isLoading ? (
            <div className="p-6 text-center">Loading...</div>
          ) : alerts.length === 0 ? (
            <div className="p-6 text-center text-gray-500">No alerts found</div>
          ) : (
            <div className="divide-y divide-gray-200">
              {alerts.map((alert: any) => (
                <div
                  key={alert.alert_id}
                  className={`p-6 border-l-4 ${
                    severityColors[alert.severity as keyof typeof severityColors]
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center">
                        <AlertTriangle
                          className={`h-5 w-5 mr-2 ${
                            alert.severity === 'critical'
                              ? 'text-red-600'
                              : alert.severity === 'high'
                              ? 'text-orange-600'
                              : 'text-yellow-600'
                          }`}
                        />
                        <span className="text-sm font-medium text-gray-900 capitalize">
                          {alert.severity} - {alert.alert_type}
                        </span>
                      </div>
                      <p className="mt-1 text-sm text-gray-600">
                        {alert.message}
                      </p>
                      <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                        <span>Well: {alert.well_id}</span>
                        {alert.sensor_type && (
                          <span>Sensor: {alert.sensor_type}</span>
                        )}
                        <span>
                          {new Date(alert.created_at).toLocaleString()}
                        </span>
                      </div>
                    </div>
                    {!alert.resolved && (
                      <button
                        onClick={() => handleResolve(alert.alert_id)}
                        className="ml-4 flex items-center px-3 py-1 text-sm font-medium text-green-700 bg-green-50 rounded-md hover:bg-green-100"
                      >
                        <CheckCircle className="h-4 w-4 mr-1" />
                        Resolve
                      </button>
                    )}
                    {alert.resolved && (
                      <span className="ml-4 flex items-center text-sm text-gray-500">
                        <CheckCircle className="h-4 w-4 mr-1" />
                        Resolved
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  )
}

