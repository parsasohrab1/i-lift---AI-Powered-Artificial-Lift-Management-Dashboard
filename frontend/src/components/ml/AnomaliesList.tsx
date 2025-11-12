'use client'

import { AlertTriangle, TrendingUp } from 'lucide-react'

interface AnomaliesListProps {
  anomalies: any[]
  isLoading: boolean
}

export default function AnomaliesList({ anomalies, isLoading }: AnomaliesListProps) {
  if (isLoading) {
    return <div className="text-center py-8">Loading anomalies...</div>
  }

  if (anomalies.length === 0) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No anomalies detected</h3>
        <p className="text-gray-500">All systems operating normally.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {anomalies.map((anomaly: any) => (
        <div
          key={anomaly.prediction_id}
          className="bg-red-50 border border-red-200 rounded-lg p-4"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5 text-red-600" />
                <h4 className="text-sm font-semibold text-red-900">
                  Anomaly Detected
                </h4>
                <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded">
                  {anomaly.well_id}
                </span>
              </div>
              <div className="mt-2">
                <p className="text-sm text-red-800">
                  Anomaly Score: <span className="font-semibold">
                    {(anomaly.anomaly_score * 100).toFixed(1)}%
                  </span>
                </p>
                {anomaly.confidence && (
                  <p className="text-xs text-red-700 mt-1">
                    Confidence: {(anomaly.confidence * 100).toFixed(1)}%
                  </p>
                )}
              </div>
              {anomaly.features && (
                <div className="mt-3 text-xs text-red-700">
                  <p className="font-medium mb-1">Key Indicators:</p>
                  <ul className="list-disc list-inside space-y-1">
                    {Object.entries(anomaly.features)
                      .slice(0, 3)
                      .map(([key, value]: [string, any]) => (
                        <li key={key}>
                          {key.replace('_', ' ')}: {typeof value === 'number' ? value.toFixed(2) : value}
                        </li>
                      ))}
                  </ul>
                </div>
              )}
              <p className="text-xs text-red-600 mt-2">
                {new Date(anomaly.timestamp).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

