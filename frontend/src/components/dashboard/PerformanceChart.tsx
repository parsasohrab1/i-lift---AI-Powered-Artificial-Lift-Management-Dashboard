'use client'

import { useQuery } from 'react-query'
import { apiClient } from '@/lib/api'
import * as mockData from '@/lib/mockData'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

interface PerformanceChartProps {
  wellId?: string
  days?: number
}

export default function PerformanceChart({ wellId = 'Well_01', days = 7 }: PerformanceChartProps) {
  const { data: trends, isLoading } = useQuery(
    ['performance-chart', wellId, days],
    async () => {
      try {
        const response = await apiClient.get(
          `/analytics/trends?well_id=${wellId}&metric=flow_rate&days=${days}`
        )
        return response.data
      } catch (error) {
        console.warn('Using mock performance chart data')
        const timeSeries = mockData.generateTimeSeriesData('flow_rate', days * 24, 60)
        return {
          metric: 'flow_rate',
          well_id: wellId,
          data_points: timeSeries.map((point, index) => ({
            date: point.timestamp,
            avg: point.value,
            min: point.value * 0.9,
            max: point.value * 1.1,
          })),
          trend: {
            direction: Math.random() > 0.5 ? 'increasing' : 'decreasing',
            strength: 0.6 + Math.random() * 0.3,
          },
        }
      }
    },
    {
      enabled: true,
      refetchInterval: 60000,
    }
  )

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  if (!trends || !trends.data_points || trends.data_points.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center py-12 text-gray-500">
          No performance data available
        </div>
      </div>
    )
  }

  const chartData = trends.data_points.map((point: any) => ({
    date: new Date(point.date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    }),
    avg: point.avg,
    min: point.min,
    max: point.max,
  }))

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Performance Trend</h2>
        <p className="text-sm text-gray-500 mt-1">
          {trends.metric} - {trends.well_id} (Last {days} days)
        </p>
      </div>
      <div className="p-6">
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorAvg" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Area
              type="monotone"
              dataKey="avg"
              stroke="#3b82f6"
              fillOpacity={1}
              fill="url(#colorAvg)"
              name="Average"
            />
            <Line
              type="monotone"
              dataKey="min"
              stroke="#10b981"
              strokeDasharray="5 5"
              name="Minimum"
            />
            <Line
              type="monotone"
              dataKey="max"
              stroke="#ef4444"
              strokeDasharray="5 5"
              name="Maximum"
            />
          </AreaChart>
        </ResponsiveContainer>
        {trends.trend && (
          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Trend Direction:</span>
              <span
                className={`text-sm font-semibold ${
                  trends.trend.direction === 'increasing'
                    ? 'text-green-600'
                    : trends.trend.direction === 'decreasing'
                    ? 'text-red-600'
                    : 'text-gray-600'
                }`}
              >
                {trends.trend.direction}
              </span>
            </div>
            <div className="flex items-center justify-between mt-2">
              <span className="text-sm text-gray-600">Trend Strength:</span>
              <span className="text-sm font-semibold text-gray-900">
                {(trends.trend.strength * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

