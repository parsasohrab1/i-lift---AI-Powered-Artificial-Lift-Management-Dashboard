'use client'

import { useQuery } from 'react-query'
import { apiClient } from '@/lib/api'

export function useKPIs(options: {
  wellId?: string
  startTime?: string
  endTime?: string
}) {
  const { wellId, startTime, endTime } = options

  return useQuery(
    ['analytics', 'kpi', wellId, startTime, endTime],
    async () => {
      const params = new URLSearchParams()
      if (wellId) params.append('well_id', wellId)
      if (startTime) params.append('start_time', startTime)
      if (endTime) params.append('end_time', endTime)

      const response = await apiClient.get(`/analytics/kpi?${params.toString()}`)
      return response.data
    }
  )
}

export function useTrends(wellId: string, metric: string, days: number = 30) {
  return useQuery(
    ['analytics', 'trends', wellId, metric, days],
    async () => {
      const response = await apiClient.get(
        `/analytics/trends?well_id=${wellId}&metric=${metric}&days=${days}`
      )
      return response.data
    }
  )
}

export function useComparison(wellIds: string[], metric: string) {
  return useQuery(
    ['analytics', 'comparison', wellIds, metric],
    async () => {
      const params = new URLSearchParams()
      wellIds.forEach((id) => params.append('well_ids', id))
      params.append('metric', metric)

      const response = await apiClient.get(
        `/analytics/comparison?${params.toString()}`
      )
      return response.data
    },
    {
      enabled: wellIds.length >= 2,
    }
  )
}

