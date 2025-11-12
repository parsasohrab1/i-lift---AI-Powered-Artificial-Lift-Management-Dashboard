'use client'

import { useQuery } from 'react-query'
import { apiClient } from '@/lib/api'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

export default function RealtimeChart() {
  const { data, isLoading } = useQuery(
    'realtime-sensor-data',
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
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  // Transform data for chart
  const chartData = data?.data
    ? Object.entries(data.data).flatMap(([wellId, sensors]: [string, any]) =>
        Object.entries(sensors).map(([sensorType, sensorData]: [string, any]) => ({
          well: wellId,
          sensor: sensorType,
          value: sensorData.value,
          timestamp: new Date(sensorData.timestamp).toLocaleTimeString(),
        }))
      )
    : []

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Real-time Sensor Data
      </h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#0ea5e9"
            strokeWidth={2}
            name="Sensor Value"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

