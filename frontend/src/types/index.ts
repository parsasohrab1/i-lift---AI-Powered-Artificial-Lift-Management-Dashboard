/**
 * TypeScript type definitions
 */

export interface SensorReading {
  reading_id: string;
  well_id: string;
  sensor_type: string;
  sensor_value: number;
  measurement_unit?: string;
  data_quality?: number;
  timestamp: string;
  created_at: string;
}

export interface Well {
  well_id: string;
  well_name: string;
  location_lat: number;
  location_lon: number;
  equipment_type: string;
  installation_date?: string;
  status: string;
  last_maintenance?: string;
}

export interface Alert {
  alert_id: string;
  well_id: string;
  alert_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  sensor_type?: string;
  resolved: boolean;
  created_at: string;
  resolved_at?: string;
}

export interface MLPrediction {
  prediction_id: string;
  well_id: string;
  model_type: string;
  prediction_value?: number;
  confidence_score?: number;
  prediction_type: string;
  timestamp: string;
}

export interface User {
  user_id: string;
  username: string;
  email: string;
  full_name?: string;
  role: string;
  is_active: boolean;
}

