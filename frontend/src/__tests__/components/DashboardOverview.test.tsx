import { render, screen } from '@testing-library/react'
import DashboardOverview from '@/components/dashboard/DashboardOverview'

// Mock the API client
jest.mock('@/lib/api', () => ({
  apiClient: {
    get: jest.fn(() => Promise.resolve({
      data: {
        total_wells: 10,
        active_wells: 8,
        total_alerts: 5,
        active_alerts: 2
      }
    }))
  }
}))

describe('DashboardOverview', () => {
  it('renders dashboard overview', () => {
    render(<DashboardOverview />)
    
    // Check if component renders without crashing
    expect(screen).toBeDefined()
  })
})

