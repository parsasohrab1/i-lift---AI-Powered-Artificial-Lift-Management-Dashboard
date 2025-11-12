'use client'

import SystemHealth from '@/components/monitoring/SystemHealth'
import MetricsDashboard from '@/components/monitoring/MetricsDashboard'

export default function MonitoringPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Monitoring & Observability</h1>
        <p className="text-gray-500 mt-1">System health, metrics, and performance monitoring</p>
      </div>

      <SystemHealth />
      <MetricsDashboard />
    </div>
  )
}

