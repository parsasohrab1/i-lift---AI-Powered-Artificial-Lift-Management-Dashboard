/**
 * Hook for using mock data when API is unavailable
 */
import { useQuery } from 'react-query'
import { apiClient } from '@/lib/api'
import * as mockData from '@/lib/mockData'

interface UseMockDataOptions {
  apiEndpoint: string
  mockDataFn: () => any
  refetchInterval?: number
  enabled?: boolean
}

export function useMockData<T = any>(
  queryKey: string | string[],
  apiEndpoint: string,
  mockDataFn: () => T,
  options: {
    refetchInterval?: number
    enabled?: boolean
    onError?: (error: any) => void
  } = {}
) {
  return useQuery(
    queryKey,
    async () => {
      try {
        // Try to fetch from API
        const response = await apiClient.get(apiEndpoint)
        return response.data
      } catch (error: any) {
        // If API fails, use mock data
        console.warn(`API call failed for ${apiEndpoint}, using mock data:`, error.message)
        return mockDataFn()
      }
    },
    {
      refetchInterval: options.refetchInterval,
      enabled: options.enabled !== false,
      retry: false, // Don't retry, just use mock data
      ...options,
    }
  )
}

