'use client'

import { useQuery } from 'react-query'
import { apiClient } from '@/lib/api'
import * as mockData from '@/lib/mockData'

export function useKPIs(options: {
  wellId?: string
  startTime?: string
  endTime?: string
}) {
  const { wellId, startTime, endTime } = options

  return useQuery(
    ['analytics', 'kpi', wellId, startTime, endTime],
    async () => {
      try {
        const params = new URLSearchParams()
        if (wellId) params.append('well_id', wellId)
        if (startTime) params.append('start_time', startTime)
        if (endTime) params.append('end_time', endTime)

        const response = await apiClient.get(`/analytics/kpi?${params.toString()}`)
        return response.data
      } catch (error) {
        console.warn('Using mock KPI data')
        return { kpis: mockData.generateKPIs() }
      }
    },
    {
      refetchInterval: 60000,
    }
  )
}

export function useTrends(wellId: string, metric: string, days: number = 30) {
  return useQuery(
    ['analytics', 'trends', wellId, metric, days],
    async () => {
      try {
        const response = await apiClient.get(
          `/analytics/trends?well_id=${wellId}&metric=${metric}&days=${days}`
        )
        return response.data
      } catch (error) {
        console.warn('Using mock trends data')
        const timeSeries = mockData.generateTimeSeriesData(metric, days * 24, 60)
        return {
          well_id: wellId,
          metric,
          data_points: timeSeries.map((point) => ({
            date: point.timestamp,
            avg: point.value,
            min: point.value * 0.9,
            max: point.value * 1.1,
          })),
        }
      }
    },
    {
      refetchInterval: 60000,
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

