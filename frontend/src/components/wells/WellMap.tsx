'use client'

import { useEffect, useState } from 'react'
import dynamic from 'next/dynamic'

// Dynamically import MapContainer to avoid SSR issues
const MapContainer = dynamic(
  () => import('react-leaflet').then((mod) => mod.MapContainer),
  { ssr: false }
)
const TileLayer = dynamic(
  () => import('react-leaflet').then((mod) => mod.TileLayer),
  { ssr: false }
)
const Marker = dynamic(
  () => import('react-leaflet').then((mod) => mod.Marker),
  { ssr: false }
)
const Popup = dynamic(
  () => import('react-leaflet').then((mod) => mod.Popup),
  { ssr: false }
)

interface WellMapProps {
  wells: any[]
  isLoading: boolean
  selectedWell: string | null
}

export default function WellMap({ wells, isLoading, selectedWell }: WellMapProps) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  if (!mounted) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="h-96 flex items-center justify-center">
          <p className="text-gray-500">Loading map...</p>
        </div>
      </div>
    )
  }

  // Parse well locations
  const wellsWithLocations = wells?.filter((well: any) => {
    if (!well.location) return false
    try {
      const [lat, lon] = well.location.split(',').map(Number)
      return !isNaN(lat) && !isNaN(lon)
    } catch {
      return false
    }
  }) || []

  // Default center (can be calculated from wells)
  const defaultCenter: [number, number] = [29.0, 48.0] // Approximate Middle East

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">
          Wells Map ({wellsWithLocations.length} locations)
        </h2>
      </div>
      <div className="h-[600px] relative">
        <MapContainer
          center={defaultCenter}
          zoom={6}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {wellsWithLocations.map((well: any) => {
            const [lat, lon] = well.location.split(',').map(Number)
            return (
              <Marker
                key={well.well_id}
                position={[lat, lon]}
              >
                <Popup>
                  <div className="p-2">
                    <h3 className="font-semibold text-gray-900">{well.well_name}</h3>
                    <p className="text-sm text-gray-600">ID: {well.well_id}</p>
                    <p className="text-sm text-gray-600">Status: {well.status}</p>
                    <p className="text-sm text-gray-600">
                      Equipment: {well.equipment_type || 'N/A'}
                    </p>
                  </div>
                </Popup>
              </Marker>
            )
          })}
        </MapContainer>
      </div>
    </div>
  )
}

