/**
 * Mock Data Service for generating synthetic real-time data
 * This provides live data when backend is not available or for development
 */

interface SensorReading {
  sensor_id: string
  well_id: string
  sensor_type: string
  sensor_value: number
  unit: string
  timestamp: string
  data_quality: number
}

interface Well {
  well_id: string
  well_name: string
  status: 'active' | 'maintenance' | 'inactive'
  location: {
    latitude: number
    longitude: number
  }
  production_rate?: number
  last_update?: string
}

interface Alert {
  alert_id: string
  well_id: string
  alert_type: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  message: string
  timestamp: string
  resolved: boolean
}

// Sensor specifications
const sensorSpecs: Record<string, { min: number; max: number; unit: string; mean: number; std: number }> = {
  motor_temperature: { min: 65, max: 120, unit: '°C', mean: 75, std: 3 },
  intake_pressure: { min: 450, max: 600, unit: 'psi', mean: 525, std: 25 },
  discharge_pressure: { min: 800, max: 1200, unit: 'psi', mean: 1000, std: 50 },
  vibration: { min: 0.5, max: 5.0, unit: 'g', mean: 2.0, std: 0.3 },
  current: { min: 30, max: 80, unit: 'A', mean: 50, std: 5 },
  flow_rate: { min: 1500, max: 2500, unit: 'bpd', mean: 2000, std: 100 },
}

// Generate well IDs
const wellIds = Array.from({ length: 10 }, (_, i) => `Well_${String(i + 1).padStart(2, '0')}`)

// Generate well names
const wellNames = [
  'North Field A-01',
  'South Platform B-02',
  'East Well C-03',
  'West Production D-04',
  'Central Hub E-05',
  'Alpha Site F-06',
  'Beta Platform G-07',
  'Gamma Field H-08',
  'Delta Well I-09',
  'Epsilon Site J-10',
]

// Generate random value within normal distribution
function generateSensorValue(sensorType: string, baseValue?: number): number {
  const spec = sensorSpecs[sensorType]
  if (!spec) return 0

  // Use base value if provided, otherwise generate new
  const value = baseValue !== undefined
    ? baseValue + (Math.random() - 0.5) * spec.std * 0.5
    : spec.mean + (Math.random() - 0.5) * spec.std * 2

  // Add some variation
  const variation = Math.sin(Date.now() / 10000) * spec.std * 0.3
  const finalValue = value + variation

  return Math.max(spec.min, Math.min(spec.max, finalValue))
}

// Generate well data
export function generateWells(): Well[] {
  const statuses: Array<'active' | 'maintenance' | 'inactive'> = ['active', 'maintenance', 'inactive']
  
  return wellIds.map((wellId, index) => {
    const status = statuses[Math.floor(Math.random() * 10)] || 'active'
    if (Math.random() > 0.8) {
      // 20% chance of maintenance or inactive
      return statuses[Math.floor(Math.random() * 2) + 1] as 'maintenance' | 'inactive'
    }
    return 'active'
  }).map((status, index) => ({
    well_id: wellIds[index],
    well_name: wellNames[index] || `Well ${index + 1}`,
    status,
    location: {
      latitude: 29.5 + Math.random() * 2,
      longitude: 47.5 + Math.random() * 2,
    },
    production_rate: status === 'active' ? 1500 + Math.random() * 1000 : 0,
    last_update: new Date().toISOString(),
  }))
}

// Generate real-time sensor data
export function generateRealtimeSensorData(wellId?: string): Record<string, Record<string, SensorReading>> {
  const data: Record<string, Record<string, SensorReading>> = {}
  const targetWells = wellId ? [wellId] : wellIds

  targetWells.forEach((wId) => {
    data[wId] = {}
    Object.keys(sensorSpecs).forEach((sensorType) => {
      const spec = sensorSpecs[sensorType]
      const value = generateSensorValue(sensorType)
      
      data[wId][sensorType] = {
        sensor_id: `${wId}_${sensorType}`,
        well_id: wId,
        sensor_type: sensorType,
        sensor_value: Math.round(value * 100) / 100,
        unit: spec.unit,
        timestamp: new Date().toISOString(),
        data_quality: 85 + Math.random() * 15,
      }
    })
  })

  return data
}

// Generate latest sensor readings
export function generateLatestReadings(wellId?: string, limit: number = 100): SensorReading[] {
  const readings: SensorReading[] = []
  const targetWells = wellId ? [wellId] : wellIds.slice(0, 3) // Limit to 3 wells for latest

  targetWells.forEach((wId) => {
    Object.keys(sensorSpecs).forEach((sensorType) => {
      const spec = sensorSpecs[sensorType]
      const value = generateSensorValue(sensorType)
      
      readings.push({
        sensor_id: `${wId}_${sensorType}`,
        well_id: wId,
        sensor_type: sensorType,
        sensor_value: Math.round(value * 100) / 100,
        unit: spec.unit,
        timestamp: new Date(Date.now() - Math.random() * 3600000).toISOString(),
        data_quality: 85 + Math.random() * 15,
      })
    })
  })

  return readings.slice(0, limit).sort((a, b) => 
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  )
}

// Generate alerts
export function generateAlerts(limit: number = 20): Alert[] {
  const alertTypes = [
    'High Temperature',
    'Low Pressure',
    'Vibration Alert',
    'Current Spike',
    'Flow Rate Drop',
    'Equipment Failure',
    'Maintenance Required',
  ]

  const severities: Array<'low' | 'medium' | 'high' | 'critical'> = ['low', 'medium', 'high', 'critical']
  const messages = [
    'Motor temperature exceeded threshold',
    'Intake pressure below normal range',
    'High vibration detected',
    'Current spike detected',
    'Flow rate dropped significantly',
    'Equipment failure detected',
    'Scheduled maintenance required',
  ]

  const alerts: Alert[] = []
  const alertCount = Math.min(limit, Math.floor(Math.random() * 15) + 5)

  for (let i = 0; i < alertCount; i++) {
    const wellId = wellIds[Math.floor(Math.random() * wellIds.length)]
    const alertType = alertTypes[Math.floor(Math.random() * alertTypes.length)]
    const severity = severities[Math.floor(Math.random() * severities.length)]
    const message = messages[Math.floor(Math.random() * messages.length)]
    const resolved = Math.random() > 0.7

    alerts.push({
      alert_id: `alert_${Date.now()}_${i}`,
      well_id,
      alert_type: alertType,
      severity,
      message: `${wellId}: ${message}`,
      timestamp: new Date(Date.now() - Math.random() * 86400000 * 7).toISOString(),
      resolved,
    })
  }

  return alerts.sort((a, b) => 
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  )
}

// Generate KPI data
export function generateKPIs() {
  const activeWells = Math.floor(Math.random() * 8) + 5
  const totalReadings = 150000 + Math.floor(Math.random() * 50000)
  const avgEfficiency = 75 + Math.random() * 15
  const dataQuality = 85 + Math.random() * 10

  return {
    total_readings: totalReadings,
    active_wells: activeWells,
    average_efficiency: Math.round(avgEfficiency * 10) / 10,
    data_quality_percentage: Math.round(dataQuality * 10) / 10,
  }
}

// Generate dashboard summary
export function generateDashboardSummary() {
  const wells = generateWells()
  const activeWells = wells.filter(w => w.status === 'active').length
  const totalProduction = wells.reduce((sum, w) => sum + (w.production_rate || 0), 0)
  const alerts = generateAlerts(10)
  const criticalAlerts = alerts.filter(a => a.severity === 'critical' && !a.resolved).length

  return {
    total_wells: wells.length,
    active_wells: activeWells,
    total_production: Math.round(totalProduction),
    critical_alerts: criticalAlerts,
    total_alerts: alerts.length,
    unresolved_alerts: alerts.filter(a => !a.resolved).length,
  }
}

// Generate time series data for charts
export function generateTimeSeriesData(
  sensorType: string,
  hours: number = 24,
  intervalMinutes: number = 15
): Array<{ timestamp: string; value: number }> {
  const data: Array<{ timestamp: string; value: number }> = []
  const spec = sensorSpecs[sensorType]
  if (!spec) return data

  const now = Date.now()
  const points = (hours * 60) / intervalMinutes

  for (let i = points; i >= 0; i--) {
    const timestamp = new Date(now - i * intervalMinutes * 60000)
    const baseValue = spec.mean
    const trend = Math.sin((i / points) * Math.PI * 2) * spec.std
    const noise = (Math.random() - 0.5) * spec.std
    const value = baseValue + trend + noise

    data.push({
      timestamp: timestamp.toISOString(),
      value: Math.max(spec.min, Math.min(spec.max, Math.round(value * 100) / 100)),
    })
  }

  return data
}

// Generate performance metrics
export function generatePerformanceMetrics(wellId?: string) {
  const targetWells = wellId ? [wellId] : wellIds.slice(0, 5)
  
  return targetWells.map((wId) => {
    const efficiency = 70 + Math.random() * 20
    const uptime = 85 + Math.random() * 10
    const production = 1500 + Math.random() * 1000

    return {
      well_id: wId,
      well_name: wellNames[wellIds.indexOf(wId)] || wId,
      efficiency: Math.round(efficiency * 10) / 10,
      uptime: Math.round(uptime * 10) / 10,
      production_rate: Math.round(production),
      status: Math.random() > 0.2 ? 'active' : 'maintenance',
    }
  })
}

// Generate ML predictions
export function generateMLPredictions(wellId?: string) {
  const predictions = []
  const targetWells = wellId ? [wellId] : wellIds.slice(0, 5)

  targetWells.forEach((wId) => {
    const failureProbability = Math.random() * 30
    const maintenanceDays = Math.floor(Math.random() * 90) + 7

    predictions.push({
      prediction_id: `pred_${wId}_${Date.now()}`,
      well_id: wId,
      well_name: wellNames[wellIds.indexOf(wId)] || wId,
      prediction_type: 'failure_prediction',
      predicted_failure_probability: Math.round(failureProbability * 10) / 10,
      predicted_maintenance_days: maintenanceDays,
      confidence: 75 + Math.random() * 20,
      timestamp: new Date().toISOString(),
    })
  })

  return predictions
}

// Generate anomalies
export function generateAnomalies(wellId?: string) {
  const anomalies = []
  const targetWells = wellId ? [wellId] : wellIds.slice(0, 3)

  targetWells.forEach((wId) => {
    if (Math.random() > 0.5) {
      const sensorType = Object.keys(sensorSpecs)[Math.floor(Math.random() * Object.keys(sensorSpecs).length)]
      const spec = sensorSpecs[sensorType]
      const anomalyValue = spec.mean + (Math.random() > 0.5 ? 1 : -1) * spec.std * 3

      anomalies.push({
        anomaly_id: `anom_${wId}_${Date.now()}`,
        well_id: wId,
        sensor_type: sensorType,
        anomaly_value: Math.round(anomalyValue * 100) / 100,
        normal_range: { min: spec.min, max: spec.max },
        severity: anomalyValue > spec.max * 0.9 ? 'high' : 'medium',
        timestamp: new Date(Date.now() - Math.random() * 3600000).toISOString(),
      })
    }
  })

  return anomalies
}

