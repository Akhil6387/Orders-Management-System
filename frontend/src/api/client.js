import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://backend-production-f7907.up.railway.app/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

// Response interceptor – normalize errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred'
    return Promise.reject({ ...error, userMessage: message })
  },
)

export default apiClient
