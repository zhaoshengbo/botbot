import { apiClient, setAuthToken, clearAuthToken } from '../api'
import axios from 'axios'

jest.mock('axios')
const mockedAxios = axios as jest.Mocked<typeof axios>

describe('API Client', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    clearAuthToken()
  })

  describe('setAuthToken', () => {
    it('sets authorization header when token is provided', () => {
      const token = 'test_token_123'
      setAuthToken(token)

      // The actual implementation sets it on axios defaults
      expect(mockedAxios.defaults.headers.common['Authorization']).toBe(
        `Bearer ${token}`
      )
    })

    it('removes authorization header when token is null', () => {
      setAuthToken('test_token')
      clearAuthToken()

      expect(
        mockedAxios.defaults.headers.common['Authorization']
      ).toBeUndefined()
    })
  })

  describe('API methods', () => {
    it('has all required API methods', () => {
      expect(apiClient.sendCode).toBeDefined()
      expect(apiClient.verifyCode).toBeDefined()
      expect(apiClient.directLogin).toBeDefined()
      expect(apiClient.getCurrentUser).toBeDefined()
      expect(apiClient.getTasks).toBeDefined()
      expect(apiClient.getTask).toBeDefined()
      expect(apiClient.createTask).toBeDefined()
      expect(apiClient.createBid).toBeDefined()
      expect(apiClient.analyzeTask).toBeDefined()
    })
  })

  describe('Error handling', () => {
    it('handles API errors gracefully', async () => {
      const mockError = {
        response: {
          status: 401,
          data: { detail: 'Unauthorized' },
        },
      }

      mockedAxios.get.mockRejectedValueOnce(mockError)

      // Test that errors are propagated
      await expect(apiClient.getCurrentUser()).rejects.toEqual(mockError)
    })
  })
})
