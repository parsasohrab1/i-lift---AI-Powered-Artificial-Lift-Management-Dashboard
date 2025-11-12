import { apiClient } from '@/lib/api'

describe('API Client', () => {
  it('has base URL configured', () => {
    expect(apiClient.defaults.baseURL).toBeDefined()
  })

  it('has timeout configured', () => {
    expect(apiClient.defaults.timeout).toBeDefined()
  })
})

