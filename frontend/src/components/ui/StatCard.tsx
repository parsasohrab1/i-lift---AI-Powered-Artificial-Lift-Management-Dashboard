'use client'

import { LucideIcon } from 'lucide-react'

interface StatCardProps {
  title: string
  value: string | number
  icon: LucideIcon
  trend?: string
  trendLabel?: string
  severity?: 'normal' | 'warning' | 'critical'
}

export default function StatCard({
  title,
  value,
  icon: Icon,
  trend,
  trendLabel,
  severity = 'normal',
}: StatCardProps) {
  const severityColors = {
    normal: 'bg-green-50 text-green-600',
    warning: 'bg-yellow-50 text-yellow-600',
    critical: 'bg-red-50 text-red-600',
  }

  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <Icon
              className={`h-6 w-6 ${
                severity === 'critical'
                  ? 'text-red-600'
                  : severity === 'warning'
                  ? 'text-yellow-600'
                  : 'text-gray-400'
              }`}
            />
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">
                {title}
              </dt>
              <dd className="flex items-baseline">
                <div className="text-2xl font-semibold text-gray-900">
                  {value}
                </div>
                {trend && (
                  <div className="ml-2 flex items-baseline text-sm font-semibold text-green-600">
                    {trend}
                    {trendLabel && (
                      <span className="ml-1 text-xs text-gray-500">
                        {trendLabel}
                      </span>
                    )}
                  </div>
                )}
              </dd>
            </dl>
          </div>
        </div>
      </div>
      {severity !== 'normal' && (
        <div className={`${severityColors[severity]} px-5 py-3`}>
          <div className="text-sm">
            {severity === 'critical' && 'Immediate attention required'}
            {severity === 'warning' && 'Attention recommended'}
          </div>
        </div>
      )}
    </div>
  )
}

