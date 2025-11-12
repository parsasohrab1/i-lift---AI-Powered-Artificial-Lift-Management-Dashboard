import { render, screen } from '@testing-library/react'
import StatCard from '@/components/ui/StatCard'

describe('StatCard', () => {
  it('renders with title and value', () => {
    render(<StatCard title="Test Title" value="100" />)
    
    expect(screen.getByText('Test Title')).toBeInTheDocument()
    expect(screen.getByText('100')).toBeInTheDocument()
  })

  it('renders with icon', () => {
    const Icon = () => <div data-testid="icon">Icon</div>
    render(<StatCard title="Test" value="100" icon={<Icon />} />)
    
    expect(screen.getByTestId('icon')).toBeInTheDocument()
  })

  it('renders with trend', () => {
    render(<StatCard title="Test" value="100" trend="up" />)
    
    expect(screen.getByText('Test')).toBeInTheDocument()
  })
})

