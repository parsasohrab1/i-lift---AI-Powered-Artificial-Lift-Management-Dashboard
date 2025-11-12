'use client'

import { useQuery } from 'react-query'
import { apiClient } from '@/lib/api'
import { SensorReading } from '@/types'

interface UseSensorsOptions {
  wellId?: string
  sensorType?: string
  startTime?: string
  endTime?: string
  limit?: number
  enabled?: boolean
}

export function useSensors(options: UseSensorsOptions = {}) {
  const {
    wellId,
    sensorType,
    startTime,
    endTime,
    limit = 100,
    enabled = true,
  } = options

  return useQuery(
    ['sensors', wellId, sensorType, startTime, endTime, limit],
    async () => {
      const params = new URLSearchParams()
      if (wellId) params.append('well_id', wellId)
      if (sensorType) params.append('sensor_type', sensorType)
      if (startTime) params.append('start_time', startTime)
      if (endTime) params.append('end_time', endTime)
      params.append('limit', limit.toString())

      const response = await apiClient.get(`/sensors/?${params.toString()}`)
      return response.data
    },
    {
      enabled,
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  )
}

export function useRealtimeSensors(wellId?: string) {
  return useQuery(
    ['sensors', 'realtime', wellId],
    async () => {
      const params = wellId ? `?well_id=${wellId}` : ''
      const response = await apiClient.get(`/sensors/realtime${params}`)
      return response.data
    },
    {
      refetchInterval: 5000, // Refresh every 5 seconds
    }
  )
}

export function useSensorStatistics(options: {
  wellId?: string
  sensorType?: string
  startTime?: string
  endTime?: string
}) {
  const { wellId, sensorType, startTime, endTime } = options

  return useQuery(
    ['sensors', 'statistics', wellId, sensorType, startTime, endTime],
    async () => {
      const params = new URLSearchParams()
      if (wellId) params.append('well_id', wellId)
      if (sensorType) params.append('sensor_type', sensorType)
      if (startTime) params.append('start_time', startTime)
      if (endTime) params.append('end_time', endTime)

      const response = await apiClient.get(
        `/sensors/statistics?${params.toString()}`
      )
      return response.data
    }
  )
}

