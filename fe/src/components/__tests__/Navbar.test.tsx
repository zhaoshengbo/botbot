import { render, screen, fireEvent } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import Navbar from '../Navbar'
import { useAuth } from '@/contexts/AuthContext'

// Mock the AuthContext
jest.mock('@/contexts/AuthContext', () => ({
  useAuth: jest.fn(),
}))

const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>
const mockPush = jest.fn()

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

describe('Navbar', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders logo and brand name', () => {
    mockUseAuth.mockReturnValue({
      user: null,
      loading: false,
      login: jest.fn(),
      logout: jest.fn(),
      refreshUser: jest.fn(),
    })

    render(<Navbar />)
    expect(screen.getByText('🦞')).toBeInTheDocument()
    expect(screen.getByText('BotBot')).toBeInTheDocument()
  })

  it('shows login button when user is not authenticated', () => {
    mockUseAuth.mockReturnValue({
      user: null,
      loading: false,
      login: jest.fn(),
      logout: jest.fn(),
      refreshUser: jest.fn(),
    })

    render(<Navbar />)
    expect(screen.getByText('Login')).toBeInTheDocument()
  })

  it('shows user info and navigation when authenticated', () => {
    const mockUser = {
      id: '123',
      phone_number: '+8613800138000',
      username: 'test_user',
      level: 'bronze',
      shrimp_food_balance: 150.5,
      frozen_balance: 0,
      total_earned: 500,
      total_spent: 100,
      tasks_published: 5,
      tasks_completed: 10,
      rating_as_publisher: 4.5,
      rating_as_claimer: 4.8,
      rating_count_as_publisher: 5,
      rating_count_as_claimer: 8,
      ai_preferences: {},
      is_active: true,
      is_admin: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }

    mockUseAuth.mockReturnValue({
      user: mockUser,
      loading: false,
      login: jest.fn(),
      logout: jest.fn(),
      refreshUser: jest.fn(),
    })

    render(<Navbar />)

    // Check navigation links
    expect(screen.getByText('Tasks')).toBeInTheDocument()
    expect(screen.getByText('Post Task')).toBeInTheDocument()
    expect(screen.getByText('My Contracts')).toBeInTheDocument()

    // Check user info
    expect(screen.getByText(/150.5kg/)).toBeInTheDocument()
    expect(screen.getByText(/test_user/)).toBeInTheDocument()
    expect(screen.getByText(/bronze/)).toBeInTheDocument()
    expect(screen.getByText('Logout')).toBeInTheDocument()
  })

  it('calls logout and redirects when logout button is clicked', () => {
    const mockLogout = jest.fn()
    const mockUser = {
      id: '123',
      username: 'test_user',
      shrimp_food_balance: 100,
      level: 'bronze',
    } as any

    mockUseAuth.mockReturnValue({
      user: mockUser,
      loading: false,
      login: jest.fn(),
      logout: mockLogout,
      refreshUser: jest.fn(),
    })

    render(<Navbar />)

    const logoutButton = screen.getByText('Logout')
    fireEvent.click(logoutButton)

    expect(mockLogout).toHaveBeenCalledTimes(1)
    expect(mockPush).toHaveBeenCalledWith('/auth/login')
  })

  it('displays balance with shrimp emoji', () => {
    const mockUser = {
      id: '123',
      username: 'test_user',
      shrimp_food_balance: 99.9,
      level: 'silver',
    } as any

    mockUseAuth.mockReturnValue({
      user: mockUser,
      loading: false,
      login: jest.fn(),
      logout: jest.fn(),
      refreshUser: jest.fn(),
    })

    render(<Navbar />)
    expect(screen.getByText(/99.9kg 🦐/)).toBeInTheDocument()
  })
})
