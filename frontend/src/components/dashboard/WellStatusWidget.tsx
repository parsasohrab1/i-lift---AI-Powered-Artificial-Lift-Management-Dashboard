'use client'

import { useQuery } from 'react-query'
import { apiClient } from '@/lib/api'
import * as mockData from '@/lib/mockData'
import Link from 'next/link'
import { CheckCircle, XCircle, AlertCircle, ArrowRight } from 'lucide-react'

export default function WellStatusWidget() {
  const { data: wells, isLoading } = useQuery(
    'wells-status',
    async () => {
      try {
        const response = await apiClient.get('/wells/')
        return response.data
      } catch (error) {
        console.warn('Using mock wells data')
        return mockData.generateWells()
      }
    },
    {
      refetchInterval: 60000,
    }
  )

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-200 rounded w-1/3"></div>
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-12 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    )
  }

  const wellsList = wells || []
  const activeWells = wellsList.filter((w: any) => w.status === 'active')
  const maintenanceWells = wellsList.filter((w: any) => w.status === 'maintenance')
  const inactiveWells = wellsList.filter((w: any) => w.status === 'inactive')

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'maintenance':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />
      case 'inactive':
        return <XCircle className="h-5 w-5 text-red-500" />
      default:
        return <AlertCircle className="h-5 w-5 text-gray-500" />
    }
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Well Status</h2>
          <p className="text-sm text-gray-500 mt-1">
            {activeWells.length} active, {maintenanceWells.length} maintenance,{' '}
            {inactiveWells.length} inactive
          </p>
        </div>
        <Link
          href="/dashboard/wells"
          className="text-sm text-primary-600 hover:text-primary-700 flex items-center"
        >
          View all
          <ArrowRight className="h-4 w-4 ml-1" />
        </Link>
      </div>
      <div className="p-6">
        {wellsList.length === 0 ? (
          <div className="text-center py-8 text-gray-500">No wells found</div>
        ) : (
          <div className="space-y-3">
            {wellsList.slice(0, 5).map((well: any) => (
              <div
                key={well.well_id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  {getStatusIcon(well.status)}
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {well.well_name}
                    </p>
                    <p className="text-xs text-gray-500">{well.well_id}</p>
                  </div>
                </div>
                <span
                  className={`px-2 py-1 text-xs font-semibold rounded-full ${
                    well.status === 'active'
                      ? 'bg-green-100 text-green-800'
                      : well.status === 'maintenance'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {well.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

