'use client'

import { useQuery } from 'react-query'
import { apiClient } from '@/lib/api'
import { X, Activity, AlertTriangle, TrendingUp } from 'lucide-react'
import Link from 'next/link'

interface WellDetailsModalProps {
  well: any
  onClose: () => void
}

export default function WellDetailsModal({ well, onClose }: WellDetailsModalProps) {
  // Fetch real-time data for this well
  const { data: realtimeData } = useQuery(
    ['sensors', 'realtime', well.well_id],
    async () => {
      const response = await apiClient.get(`/sensors/realtime?well_id=${well.well_id}`)
      return response.data
    },
    {
      refetchInterval: 5000,
    }
  )

  // Fetch latest alerts
  const { data: alerts } = useQuery(
    ['alerts', well.well_id],
    async () => {
      const response = await apiClient.get(`/alerts/?well_id=${well.well_id}&limit=5`)
      return response.data
    }
  )

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Backdrop */}
        <div
          className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75"
          onClick={onClose}
        />

        {/* Modal */}
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          {/* Header */}
          <div className="bg-white px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <div>
              <h3 className="text-2xl font-bold text-gray-900">{well.well_name}</h3>
              <p className="text-sm text-gray-500 mt-1">ID: {well.well_id}</p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Content */}
          <div className="bg-white px-6 py-4 max-h-[70vh] overflow-y-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Basic Info */}
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h4>
                <dl className="space-y-3">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Equipment Type</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {well.equipment_type || 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Status</dt>
                    <dd className="mt-1">
                      <span
                        className={`px-2 py-1 text-xs font-semibold rounded-full ${
                          well.status === 'active'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {well.status}
                      </span>
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Installation Date</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {well.installation_date
                        ? new Date(well.installation_date).toLocaleDateString()
                        : 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Last Maintenance</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {well.last_maintenance
                        ? new Date(well.last_maintenance).toLocaleDateString()
                        : 'Never'}
                    </dd>
                  </div>
                </dl>
              </div>

              {/* Real-time Data */}
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Activity className="h-5 w-5 mr-2 text-primary-600" />
                  Real-time Data
                </h4>
                {realtimeData?.data?.[well.well_id] ? (
                  <div className="space-y-2">
                    {Object.entries(realtimeData.data[well.well_id]).map(
                      ([sensorType, sensorData]: [string, any]) => (
                        <div
                          key={sensorType}
                          className="flex items-center justify-between p-2 bg-gray-50 rounded"
                        >
                          <span className="text-sm text-gray-600">
                            {sensorType.replace('_', ' ')}
                          </span>
                          <span className="text-sm font-medium text-gray-900">
                            {sensorData.value?.toFixed(2)} {sensorData.unit || ''}
                          </span>
                        </div>
                      )
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No real-time data available</p>
                )}
              </div>
            </div>

            {/* Alerts */}
            {alerts?.alerts && alerts.alerts.length > 0 && (
              <div className="mt-6">
                <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <AlertTriangle className="h-5 w-5 mr-2 text-red-600" />
                  Recent Alerts
                </h4>
                <div className="space-y-2">
                  {alerts.alerts.slice(0, 3).map((alert: any) => (
                    <div
                      key={alert.alert_id}
                      className="p-3 bg-red-50 border border-red-200 rounded"
                    >
                      <p className="text-sm font-medium text-red-900">
                        {alert.alert_type}
                      </p>
                      <p className="text-xs text-red-700 mt-1">{alert.message}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="mt-6 flex items-center space-x-4">
              <Link
                href={`/dashboard/sensors?well_id=${well.well_id}`}
                className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
              >
                View Sensors
              </Link>
              <Link
                href={`/dashboard/analytics?well_id=${well.well_id}`}
                className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              >
                View Analytics
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

