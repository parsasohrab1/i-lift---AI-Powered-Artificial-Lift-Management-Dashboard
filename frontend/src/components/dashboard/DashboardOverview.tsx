'use client'

import { useQuery } from 'react-query'
import { apiClient } from '@/lib/api'
import StatCard from '../ui/StatCard'
import { Activity, AlertTriangle, TrendingUp, Database } from 'lucide-react'
import KPIWidget from './KPIWidget'
import RealtimeMetrics from './RealtimeMetrics'
import WellStatusWidget from './WellStatusWidget'
import SensorStatusWidget from './SensorStatusWidget'
import ActivityFeed from './ActivityFeed'
import QuickActions from './QuickActions'
import PerformanceChart from './PerformanceChart'
import RealtimeChart from './RealtimeChart'
import AlertsList from './AlertsList'

export default function DashboardOverview() {
  // Fetch dashboard summary
  const { data: summary, isLoading } = useQuery(
    'dashboard-summary',
    async () => {
      const response = await apiClient.get('/dashboard/summary')
      return response.data
    },
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  )

  // Fetch real-time alerts count
  const { data: alertsCount } = useQuery(
    'alerts-count',
    async () => {
      const response = await apiClient.get('/alerts/realtime/count')
      return response.data
    },
    {
      refetchInterval: 10000, // Refresh every 10 seconds
    }
  )

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard Overview</h1>
        <p className="mt-1 text-sm text-gray-500">
          Real-time monitoring and analytics
        </p>
      </div>

      {/* KPI Widgets */}
      <KPIWidget />

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Charts */}
        <div className="lg:col-span-2 space-y-6">
          <RealtimeChart />
          <PerformanceChart wellId="Well_01" days={7} />
        </div>

        {/* Right Column - Status & Alerts */}
        <div className="space-y-6">
          <AlertsList />
          <WellStatusWidget />
        </div>
      </div>

      {/* Secondary Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RealtimeMetrics />
        <SensorStatusWidget />
      </div>

      {/* Bottom Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ActivityFeed />
        <QuickActions />
      </div>
    </div>
  )
}
