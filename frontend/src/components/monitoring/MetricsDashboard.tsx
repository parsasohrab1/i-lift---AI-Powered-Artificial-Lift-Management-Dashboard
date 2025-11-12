'use client'

import { useQuery } from 'react-query'
import { apiClient } from '@/lib/api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts'
import { Activity, TrendingUp, AlertTriangle, Database } from 'lucide-react'

export default function MetricsDashboard() {
  const { data: metrics, isLoading } = useQuery(
    'metrics-summary',
    async () => {
      const response = await apiClient.get('/monitoring/metrics/summary')
      return response.data
    },
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  )

  const { data: businessMetrics } = useQuery(
    'business-metrics',
    async () => {
      const response = await apiClient.get('/monitoring/metrics/business?hours=24')
      return response.data
    },
    {
      refetchInterval: 60000, // Refresh every minute
    }
  )

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  const alertsData = metrics?.active_alerts_by_severity
    ? Object.entries(metrics.active_alerts_by_severity).map(([severity, count]) => ({
        severity: severity.toUpperCase(),
        count,
      }))
    : []

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Active Wells</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {metrics?.active_wells || 0}
              </p>
            </div>
            <Database className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Active Sensors</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {metrics?.active_sensors || 0}
              </p>
            </div>
            <Activity className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Sensor Readings (1h)</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {metrics?.sensor_readings_last_hour || 0}
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-purple-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Alerts (1h)</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {metrics?.alerts_last_hour || 0}
              </p>
            </div>
            <AlertTriangle className="w-8 h-8 text-red-500" />
          </div>
        </div>
      </div>

      {/* Business Metrics */}
      {businessMetrics && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Business Metrics (24h)</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-500">Sensor Readings</p>
              <p className="text-2xl font-bold text-blue-600 mt-1">
                {businessMetrics.sensor_readings || 0}
              </p>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <p className="text-sm text-gray-500">Alerts</p>
              <p className="text-2xl font-bold text-yellow-600 mt-1">
                {businessMetrics.alerts || 0}
              </p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-gray-500">ML Predictions</p>
              <p className="text-2xl font-bold text-green-600 mt-1">
                {businessMetrics.ml_predictions || 0}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Alerts by Severity Chart */}
      {alertsData.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Active Alerts by Severity</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={alertsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="severity" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

