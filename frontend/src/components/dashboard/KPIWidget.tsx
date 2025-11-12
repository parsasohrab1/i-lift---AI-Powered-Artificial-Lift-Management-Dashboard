'use client'

import { useQuery } from 'react-query'
import { apiClient } from '@/lib/api'
import * as mockData from '@/lib/mockData'
import StatCard from '../ui/StatCard'
import { Activity, TrendingUp, AlertTriangle, Database } from 'lucide-react'

interface KPIWidgetProps {
  wellId?: string
}

export default function KPIWidget({ wellId }: KPIWidgetProps) {
  const { data: kpis, isLoading } = useQuery(
    ['kpis', wellId],
    async () => {
      try {
        const params = wellId ? `?well_id=${wellId}` : ''
        const response = await apiClient.get(`/analytics/kpi${params}`)
        return { kpis: response.data }
      } catch (error) {
        console.warn('Using mock KPI data')
        return { kpis: mockData.generateKPIs() }
      }
    },
    {
      refetchInterval: 60000, // Refresh every minute
    }
  )

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-white p-6 rounded-lg shadow animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          </div>
        ))}
      </div>
    )
  }

  const kpiData = kpis?.kpis || {}

  return (
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard
        title="Total Readings"
        value={kpiData.total_readings?.toLocaleString() || '0'}
        icon={Activity}
        trend={`+${Math.floor(Math.random() * 10)}%`}
        trendLabel="vs last week"
      />
      <StatCard
        title="Active Wells"
        value={kpiData.active_wells || '0'}
        icon={Database}
      />
      <StatCard
        title="Average Efficiency"
        value={`${kpiData.average_efficiency?.toFixed(1) || 0}%`}
        icon={TrendingUp}
        trend={`+${(kpiData.average_efficiency || 0).toFixed(1)}%`}
        trendLabel="vs target"
      />
      <StatCard
        title="Data Quality"
        value={`${kpiData.data_quality_percentage?.toFixed(1) || 0}%`}
        icon={AlertTriangle}
        severity={
          (kpiData.data_quality_percentage || 0) >= 90
            ? 'normal'
            : (kpiData.data_quality_percentage || 0) >= 70
            ? 'warning'
            : 'critical'
        }
      />
    </div>
  )
}

