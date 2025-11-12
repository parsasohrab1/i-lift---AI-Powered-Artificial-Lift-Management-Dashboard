'use client'

import { useState } from 'react'
import DashboardLayout from '@/components/layouts/DashboardLayout'
import { useQuery, useMutation } from 'react-query'
import { apiClient } from '@/lib/api'
import { Brain, AlertTriangle, TrendingUp, Activity } from 'lucide-react'
import toast from 'react-hot-toast'
import PredictionsList from '@/components/ml/PredictionsList'
import AnomaliesList from '@/components/ml/AnomaliesList'
import ModelPerformance from '@/components/ml/ModelPerformance'

export default function MLPredictionsPage() {
  const [activeTab, setActiveTab] = useState<'predictions' | 'anomalies' | 'performance'>('predictions')

  // Fetch predictions
  const { data: predictions, isLoading: predictionsLoading } = useQuery(
    'ml-predictions',
    async () => {
      const response = await apiClient.get('/ml/predictions?limit=50')
      return response.data
    },
    {
      refetchInterval: 30000,
    }
  )

  // Fetch anomalies
  const { data: anomalies, isLoading: anomaliesLoading } = useQuery(
    'ml-anomalies',
    async () => {
      const response = await apiClient.get('/ml/anomalies?threshold=0.5')
      return response.data
    },
    {
      refetchInterval: 10000,
    }
  )

  // Fetch models
  const { data: models } = useQuery('ml-models', async () => {
    const response = await apiClient.get('/ml/models')
    return response.data
  })

  // Create prediction mutation
  const createPredictionMutation = useMutation(
    async ({ wellId, modelType }: { wellId: string; modelType: string }) => {
      const response = await apiClient.post('/ml/predict', {
        well_id: wellId,
        model_type: modelType,
      })
      return response.data
    },
    {
      onSuccess: () => {
        toast.success('Prediction created successfully')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to create prediction')
      },
    }
  )

  const handleCreatePrediction = async (wellId: string, modelType: string) => {
    await createPredictionMutation.mutateAsync({ wellId, modelType })
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">ML Predictions</h1>
          <p className="mt-1 text-sm text-gray-500">
            Machine learning predictions and anomaly detection
          </p>
        </div>

        {/* Models Overview */}
        {models && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {models.map((model: any) => (
              <div key={model.model_type} className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {model.model_name}
                    </h3>
                    <p className="text-sm text-gray-500 mt-1">{model.description}</p>
                  </div>
                  <Brain className="h-8 w-8 text-primary-600" />
                </div>
                <div className="mt-4 flex items-center justify-between">
                  <div>
                    <p className="text-xs text-gray-500">Accuracy</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {(model.accuracy * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Status</p>
                    <span
                      className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        model.status === 'active'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {model.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('predictions')}
                className={`px-6 py-4 text-sm font-medium border-b-2 ${
                  activeTab === 'predictions'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <TrendingUp className="h-4 w-4 inline mr-2" />
                Predictions
              </button>
              <button
                onClick={() => setActiveTab('anomalies')}
                className={`px-6 py-4 text-sm font-medium border-b-2 ${
                  activeTab === 'anomalies'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <AlertTriangle className="h-4 w-4 inline mr-2" />
                Anomalies ({anomalies?.length || 0})
              </button>
              <button
                onClick={() => setActiveTab('performance')}
                className={`px-6 py-4 text-sm font-medium border-b-2 ${
                  activeTab === 'performance'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Activity className="h-4 w-4 inline mr-2" />
                Performance
              </button>
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'predictions' && (
              <PredictionsList
                predictions={predictions || []}
                isLoading={predictionsLoading}
                onCreatePrediction={handleCreatePrediction}
              />
            )}
            {activeTab === 'anomalies' && (
              <AnomaliesList
                anomalies={anomalies || []}
                isLoading={anomaliesLoading}
              />
            )}
            {activeTab === 'performance' && <ModelPerformance />}
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}

