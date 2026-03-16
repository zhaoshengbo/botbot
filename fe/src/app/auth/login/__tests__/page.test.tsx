import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import LoginPage from '../page'
import { apiClient } from '@/lib/api'

// Mock the API client
jest.mock('@/lib/api', () => ({
  apiClient: {
    directLogin: jest.fn(),
  },
}))

const mockPush = jest.fn()
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

describe('LoginPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders login form', () => {
    render(<LoginPage />)

    expect(screen.getByText('🦞')).toBeInTheDocument()
    expect(screen.getByText('Welcome to BotBot')).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/phone number/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument()
  })

  it('allows user to input phone number', () => {
    render(<LoginPage />)

    const input = screen.getByPlaceholderText(/phone number/i) as HTMLInputElement
    fireEvent.change(input, { target: { value: '+8613800138000' } })

    expect(input.value).toBe('+8613800138000')
  })

  it('submits form and redirects on successful login', async () => {
    const mockResponse = {
      access_token: 'test_token',
      refresh_token: 'refresh_token',
      token_type: 'bearer',
      user: {
        id: '123',
        phone_number: '+8613800138000',
        username: 'test_user',
      },
    }

    ;(apiClient.directLogin as jest.Mock).mockResolvedValueOnce(mockResponse)

    render(<LoginPage />)

    const input = screen.getByPlaceholderText(/phone number/i)
    const button = screen.getByRole('button', { name: /login/i })

    fireEvent.change(input, { target: { value: '+8613800138000' } })
    fireEvent.click(button)

    await waitFor(() => {
      expect(apiClient.directLogin).toHaveBeenCalledWith('+8613800138000')
      expect(mockPush).toHaveBeenCalledWith('/')
    })
  })

  it('displays error message on login failure', async () => {
    const mockError = new Error('Login failed')
    ;(apiClient.directLogin as jest.Mock).mockRejectedValueOnce(mockError)

    render(<LoginPage />)

    const input = screen.getByPlaceholderText(/phone number/i)
    const button = screen.getByRole('button', { name: /login/i })

    fireEvent.change(input, { target: { value: '+8613800138000' } })
    fireEvent.click(button)

    await waitFor(() => {
      expect(screen.getByText(/failed/i)).toBeInTheDocument()
    })
  })

  it('disables button while loading', async () => {
    ;(apiClient.directLogin as jest.Mock).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 1000))
    )

    render(<LoginPage />)

    const input = screen.getByPlaceholderText(/phone number/i)
    const button = screen.getByRole('button', { name: /login/i }) as HTMLButtonElement

    fireEvent.change(input, { target: { value: '+8613800138000' } })
    fireEvent.click(button)

    await waitFor(() => {
      expect(button.disabled).toBe(true)
    })
  })

  it('validates phone number format', () => {
    render(<LoginPage />)

    const input = screen.getByPlaceholderText(/phone number/i)
    const button = screen.getByRole('button', { name: /login/i })

    // Try with empty input
    fireEvent.click(button)

    // Form should not submit with empty input
    expect(apiClient.directLogin).not.toHaveBeenCalled()
  })
})
