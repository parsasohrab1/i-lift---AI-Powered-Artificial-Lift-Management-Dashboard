'use client'

import { useQuery, useMutation, useQueryClient } from 'react-query'
import { apiClient } from '@/lib/api'
import toast from 'react-hot-toast'

interface UseAlertsOptions {
  wellId?: string
  severity?: string
  resolved?: boolean
  limit?: number
}

export function useAlerts(options: UseAlertsOptions = {}) {
  const { wellId, severity, resolved, limit = 100 } = options

  return useQuery(
    ['alerts', wellId, severity, resolved, limit],
    async () => {
      const params = new URLSearchParams()
      if (wellId) params.append('well_id', wellId)
      if (severity) params.append('severity', severity)
      if (resolved !== undefined) params.append('resolved', resolved.toString())
      params.append('limit', limit.toString())

      const response = await apiClient.get(`/alerts/?${params.toString()}`)
      return response.data
    },
    {
      refetchInterval: 10000, // Refresh every 10 seconds
    }
  )
}

export function useCriticalAlerts(wellId?: string) {
  return useQuery(
    ['alerts', 'critical', wellId],
    async () => {
      const params = wellId ? `?well_id=${wellId}` : ''
      const response = await apiClient.get(`/alerts/critical${params}`)
      return response.data
    },
    {
      refetchInterval: 10000,
    }
  )
}

export function useResolveAlert() {
  const queryClient = useQueryClient()

  return useMutation(
    async (alertId: string) => {
      const response = await apiClient.post(`/alerts/${alertId}/resolve`)
      return response.data
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('alerts')
        toast.success('Alert resolved')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to resolve alert')
      },
    }
  )
}

