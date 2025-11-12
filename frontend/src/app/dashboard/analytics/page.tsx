'use client'

import DashboardLayout from '@/components/layouts/DashboardLayout'
import { useKPIs, useTrends } from '@/hooks/useAnalytics'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

export default function AnalyticsPage() {
  const { data: kpis, isLoading: kpisLoading } = useKPIs({})
  const { data: trends, isLoading: trendsLoading } = useTrends(
    'Well_01',
    'temperature',
    30
  )

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="mt-1 text-sm text-gray-500">
            Performance metrics and trends
          </p>
        </div>

        {/* KPIs */}
        {kpisLoading ? (
          <div className="animate-pulse">Loading KPIs...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-sm font-medium text-gray-500">
                Total Readings
              </h3>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {kpis?.kpis?.total_readings?.toLocaleString() || 0}
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-sm font-medium text-gray-500">
                Active Wells
              </h3>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {kpis?.kpis?.active_wells || 0}
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-sm font-medium text-gray-500">
                Average Efficiency
              </h3>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {kpis?.kpis?.average_efficiency?.toFixed(1) || 0}%
              </p>
            </div>
          </div>
        )}

        {/* Trends Chart */}
        {trendsLoading ? (
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="animate-pulse">Loading trends...</div>
          </div>
        ) : (
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Temperature Trend - {trends?.well_id}
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trends?.data_points || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="avg"
                  stroke="#0ea5e9"
                  name="Average"
                />
                <Line
                  type="monotone"
                  dataKey="min"
                  stroke="#10b981"
                  name="Min"
                />
                <Line
                  type="monotone"
                  dataKey="max"
                  stroke="#ef4444"
                  name="Max"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}

