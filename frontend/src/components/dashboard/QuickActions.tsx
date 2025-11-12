'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation } from 'react-query'
import { apiClient } from '@/lib/api'
import {
  Plus,
  Search,
  Download,
  Settings,
  AlertCircle,
  TrendingUp,
  Database,
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function QuickActions() {
  const router = useRouter()
  const [isCreatingPrediction, setIsCreatingPrediction] = useState(false)

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
        setIsCreatingPrediction(false)
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to create prediction')
        setIsCreatingPrediction(false)
      },
    }
  )

  const actions = [
    {
      label: 'View Sensors',
      icon: Database,
      onClick: () => router.push('/dashboard/sensors'),
      color: 'bg-blue-50 text-blue-600 hover:bg-blue-100',
    },
    {
      label: 'View Wells',
      icon: Database,
      onClick: () => router.push('/dashboard/wells'),
      color: 'bg-green-50 text-green-600 hover:bg-green-100',
    },
    {
      label: 'View Alerts',
      icon: AlertCircle,
      onClick: () => router.push('/dashboard/alerts'),
      color: 'bg-red-50 text-red-600 hover:bg-red-100',
    },
    {
      label: 'Analytics',
      icon: TrendingUp,
      onClick: () => router.push('/dashboard/analytics'),
      color: 'bg-purple-50 text-purple-600 hover:bg-purple-100',
    },
    {
      label: 'Export Data',
      icon: Download,
      onClick: async () => {
        try {
          const response = await apiClient.get('/sensors/export?format=csv&limit=1000', {
            responseType: 'blob',
          })
          const url = window.URL.createObjectURL(new Blob([response.data]))
          const link = document.createElement('a')
          link.href = url
          link.setAttribute('download', `sensor_data_${new Date().toISOString()}.csv`)
          document.body.appendChild(link)
          link.click()
          link.remove()
          toast.success('Data exported successfully')
        } catch (error: any) {
          toast.error('Failed to export data')
        }
      },
      color: 'bg-yellow-50 text-yellow-600 hover:bg-yellow-100',
    },
    {
      label: 'Settings',
      icon: Settings,
      onClick: () => router.push('/dashboard/settings'),
      color: 'bg-gray-50 text-gray-600 hover:bg-gray-100',
    },
  ]

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Quick Actions</h2>
        <p className="text-sm text-gray-500 mt-1">Common tasks and shortcuts</p>
      </div>
      <div className="p-6">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {actions.map((action) => {
            const Icon = action.icon
            return (
              <button
                key={action.label}
                onClick={action.onClick}
                className={`flex flex-col items-center justify-center p-4 rounded-lg transition-colors ${action.color}`}
              >
                <Icon className="h-6 w-6 mb-2" />
                <span className="text-sm font-medium">{action.label}</span>
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}

