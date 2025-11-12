'use client'

import { useQuery } from 'react-query'
import { apiClient } from '@/lib/api'
import { AlertTriangle, CheckCircle, Activity, TrendingUp } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

export default function ActivityFeed() {
  // Fetch recent alerts
  const { data: alerts } = useQuery(
    'recent-alerts',
    async () => {
      const response = await apiClient.get('/alerts/?limit=10&resolved=false')
      return response.data
    },
    {
      refetchInterval: 30000,
    }
  )

  // Fetch recent predictions
  const { data: predictions } = useQuery(
    'recent-predictions',
    async () => {
      const response = await apiClient.get('/ml/predictions/latest?limit=5')
      return response.data
    },
    {
      refetchInterval: 60000,
    }
  )

  const activities: any[] = []

  // Add alerts as activities
  if (alerts?.alerts) {
    alerts.alerts.forEach((alert: any) => {
      activities.push({
        id: alert.alert_id,
        type: 'alert',
        severity: alert.severity,
        title: alert.message,
        wellId: alert.well_id,
        timestamp: alert.created_at,
        icon: AlertTriangle,
        color:
          alert.severity === 'critical'
            ? 'text-red-600'
            : alert.severity === 'high'
            ? 'text-orange-600'
            : 'text-yellow-600',
      })
    })
  }

  // Add predictions as activities
  if (predictions) {
    predictions.forEach((prediction: any) => {
      activities.push({
        id: prediction.prediction_id,
        type: 'prediction',
        title: `${prediction.model_type.replace('_', ' ')} prediction`,
        wellId: prediction.well_id,
        timestamp: prediction.timestamp,
        icon: TrendingUp,
        color: 'text-blue-600',
        value: prediction.prediction_value,
      })
    })
  }

  // Sort by timestamp (newest first)
  activities.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
        <p className="text-sm text-gray-500 mt-1">Latest alerts and predictions</p>
      </div>
      <div className="p-6">
        {activities.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Activity className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p>No recent activity</p>
          </div>
        ) : (
          <div className="space-y-4">
            {activities.slice(0, 10).map((activity) => {
              const Icon = activity.icon
              return (
                <div
                  key={activity.id}
                  className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className={`flex-shrink-0 ${activity.color}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                    <div className="mt-1 flex items-center space-x-2">
                      <span className="text-xs text-gray-500">{activity.wellId}</span>
                      {activity.value !== undefined && (
                        <span className="text-xs text-gray-500">
                          • Value: {activity.value.toFixed(4)}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-gray-400 mt-1">
                      {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
                    </p>
                  </div>
                  {activity.type === 'alert' && activity.severity === 'critical' && (
                    <span className="flex-shrink-0 px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                      Critical
                    </span>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

