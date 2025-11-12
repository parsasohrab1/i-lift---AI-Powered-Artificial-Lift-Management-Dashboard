'use client'

import { useState } from 'react'
import DashboardLayout from '@/components/layouts/DashboardLayout'
import { useQuery } from 'react-query'
import { apiClient } from '@/lib/api'
import WellsList from '@/components/wells/WellsList'
import WellMap from '@/components/wells/WellMap'
import { Database, MapPin, Activity } from 'lucide-react'

export default function WellsPage() {
  const [viewMode, setViewMode] = useState<'list' | 'map'>('list')
  const [selectedWell, setSelectedWell] = useState<string | null>(null)

  const { data: wells, isLoading } = useQuery(
    'wells',
    async () => {
      const response = await apiClient.get('/wells/')
      return response.data
    },
    {
      refetchInterval: 60000, // Refresh every minute
    }
  )

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Wells Management</h1>
            <p className="mt-1 text-sm text-gray-500">
              Monitor and manage artificial lift wells
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setViewMode('list')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'list'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              <Database className="h-4 w-4 inline mr-2" />
              List View
            </button>
            <button
              onClick={() => setViewMode('map')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'map'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              <MapPin className="h-4 w-4 inline mr-2" />
              Map View
            </button>
          </div>
        </div>

        {/* Stats */}
        {!isLoading && wells && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Database className="h-8 w-8 text-primary-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Total Wells</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {wells.length || 0}
                  </p>
                </div>
              </div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Activity className="h-8 w-8 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Active Wells</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {wells.filter((w: any) => w.status === 'active').length || 0}
                  </p>
                </div>
              </div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Activity className="h-8 w-8 text-yellow-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Maintenance Due</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {wells.filter((w: any) => {
                      if (!w.last_maintenance) return true
                      const lastMaintenance = new Date(w.last_maintenance)
                      const daysSince = (Date.now() - lastMaintenance.getTime()) / (1000 * 60 * 60 * 24)
                      return daysSince > 90
                    }).length || 0}
                  </p>
                </div>
              </div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <MapPin className="h-8 w-8 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Locations</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {new Set(wells.map((w: any) => w.location?.split(',')[0])).size || 0}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Content */}
        {viewMode === 'list' ? (
          <WellsList wells={wells} isLoading={isLoading} onSelectWell={setSelectedWell} />
        ) : (
          <WellMap wells={wells} isLoading={isLoading} selectedWell={selectedWell} />
        )}
      </div>
    </DashboardLayout>
  )
}

