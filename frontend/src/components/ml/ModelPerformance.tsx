'use client'

import { useQuery } from 'react-query'
import { apiClient } from '@/lib/api'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

export default function ModelPerformance() {
  const { data: anomalyPerformance, isLoading: anomalyLoading } = useQuery(
    'ml-performance-anomaly',
    async () => {
      const response = await apiClient.get('/ml/models/anomaly_detection/performance')
      return response.data
    }
  )

  const { data: maintenancePerformance, isLoading: maintenanceLoading } = useQuery(
    'ml-performance-maintenance',
    async () => {
      const response = await apiClient.get('/ml/models/predictive_maintenance/performance')
      return response.data
    }
  )

  if (anomalyLoading || maintenanceLoading) {
    return <div className="text-center py-8">Loading performance data...</div>
  }

  const chartData = [
    {
      model: 'Anomaly Detection',
      predictions: anomalyPerformance?.total_predictions || 0,
      confidence: ((anomalyPerformance?.average_confidence || 0) * 100).toFixed(1),
    },
    {
      model: 'Predictive Maintenance',
      predictions: maintenancePerformance?.total_predictions || 0,
      confidence: ((maintenancePerformance?.average_confidence || 0) * 100).toFixed(1),
    },
  ]

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Anomaly Detection Performance */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Anomaly Detection Model
          </h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Total Predictions</span>
              <span className="text-sm font-semibold text-gray-900">
                {anomalyPerformance?.total_predictions || 0}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Average Confidence</span>
              <span className="text-sm font-semibold text-gray-900">
                {((anomalyPerformance?.average_confidence || 0) * 100).toFixed(1)}%
              </span>
            </div>
            {anomalyPerformance?.predictions_by_well && (
              <div className="mt-4">
                <p className="text-xs text-gray-500 mb-2">Predictions by Well</p>
                <div className="space-y-1">
                  {Object.entries(anomalyPerformance.predictions_by_well)
                    .slice(0, 5)
                    .map(([wellId, count]: [string, any]) => (
                      <div key={wellId} className="flex justify-between text-xs">
                        <span className="text-gray-600">{wellId}</span>
                        <span className="text-gray-900">{count}</span>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Predictive Maintenance Performance */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Predictive Maintenance Model
          </h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Total Predictions</span>
              <span className="text-sm font-semibold text-gray-900">
                {maintenancePerformance?.total_predictions || 0}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Average Confidence</span>
              <span className="text-sm font-semibold text-gray-900">
                {((maintenancePerformance?.average_confidence || 0) * 100).toFixed(1)}%
              </span>
            </div>
            {maintenancePerformance?.predictions_by_well && (
              <div className="mt-4">
                <p className="text-xs text-gray-500 mb-2">Predictions by Well</p>
                <div className="space-y-1">
                  {Object.entries(maintenancePerformance.predictions_by_well)
                    .slice(0, 5)
                    .map(([wellId, count]: [string, any]) => (
                      <div key={wellId} className="flex justify-between text-xs">
                        <span className="text-gray-600">{wellId}</span>
                        <span className="text-gray-900">{count}</span>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Model Performance Comparison
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="model" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="predictions" fill="#3b82f6" name="Total Predictions" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

