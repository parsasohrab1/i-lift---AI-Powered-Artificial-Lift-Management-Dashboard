'use client'

import { useState } from 'react'
import { useQuery } from 'react-query'
import { apiClient } from '@/lib/api'
import { TrendingUp, Brain, CheckCircle } from 'lucide-react'

interface PredictionsListProps {
  predictions: any[]
  isLoading: boolean
  onCreatePrediction: (wellId: string, modelType: string) => void
}

export default function PredictionsList({
  predictions,
  isLoading,
  onCreatePrediction,
}: PredictionsListProps) {
  const [selectedWell, setSelectedWell] = useState('')
  const [selectedModel, setSelectedModel] = useState('predictive_maintenance')

  // Fetch wells for dropdown
  const { data: wells } = useQuery('wells', async () => {
    const response = await apiClient.get('/wells/')
    return response.data
  })

  const modelTypes = [
    { value: 'anomaly_detection', label: 'Anomaly Detection' },
    { value: 'predictive_maintenance', label: 'Predictive Maintenance' },
    { value: 'production_optimization', label: 'Production Optimization' },
  ]

  if (isLoading) {
    return <div className="text-center py-8">Loading predictions...</div>
  }

  return (
    <div className="space-y-6">
      {/* Create Prediction */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="text-sm font-medium text-gray-900 mb-4">Create New Prediction</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Well ID
            </label>
            <select
              value={selectedWell}
              onChange={(e) => setSelectedWell(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500"
            >
              <option value="">Select a well</option>
              {wells?.map((well: any) => (
                <option key={well.well_id} value={well.well_id}>
                  {well.well_name} ({well.well_id})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Model Type
            </label>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500"
            >
              {modelTypes.map((model) => (
                <option key={model.value} value={model.value}>
                  {model.label}
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={() => {
                if (selectedWell) {
                  onCreatePrediction(selectedWell, selectedModel)
                }
              }}
              disabled={!selectedWell}
              className="w-full px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Create Prediction
            </button>
          </div>
        </div>
      </div>

      {/* Predictions List */}
      {predictions.length === 0 ? (
        <div className="text-center py-12">
          <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No predictions yet</h3>
          <p className="text-gray-500">Create your first prediction above.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {predictions.map((prediction: any) => (
            <div
              key={prediction.prediction_id}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <Brain className="h-5 w-5 text-primary-600" />
                    <h4 className="text-sm font-semibold text-gray-900">
                      {prediction.model_type.replace('_', ' ')}
                    </h4>
                    <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded">
                      {prediction.well_id}
                    </span>
                  </div>
                  {prediction.prediction_value !== null && (
                    <div className="mt-2">
                      <p className="text-sm text-gray-600">
                        Prediction: <span className="font-semibold text-gray-900">
                          {prediction.prediction_value.toFixed(4)}
                        </span>
                      </p>
                      {prediction.confidence_score && (
                        <p className="text-xs text-gray-500 mt-1">
                          Confidence: {(prediction.confidence_score * 100).toFixed(1)}%
                        </p>
                      )}
                    </div>
                  )}
                  <p className="text-xs text-gray-500 mt-2">
                    {new Date(prediction.timestamp).toLocaleString()}
                  </p>
                </div>
                {prediction.confidence_score && prediction.confidence_score > 0.8 && (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

