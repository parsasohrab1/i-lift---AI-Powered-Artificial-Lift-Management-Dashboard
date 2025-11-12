'use client'

import { useState } from 'react'
import DashboardLayout from '@/components/layouts/DashboardLayout'
import SensorDataTable from '@/components/sensors/SensorDataTable'
import SensorFilters from '@/components/sensors/SensorFilters'

export default function SensorsPage() {
  const [filters, setFilters] = useState({
    wellId: '',
    sensorType: '',
    startTime: '',
    endTime: '',
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Sensor Data</h1>
          <p className="mt-1 text-sm text-gray-500">
            View and manage sensor readings
          </p>
        </div>

        <SensorFilters filters={filters} onFiltersChange={setFilters} />
        <SensorDataTable filters={filters} />
      </div>
    </DashboardLayout>
  )
}

