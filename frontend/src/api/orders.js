import apiClient from './client'

export const ordersApi = {
  getAll: (params = {}) =>
    apiClient.get('/orders', { params }).then((r) => r.data),

  getById: (id) =>
    apiClient.get(`/orders/${id}`).then((r) => r.data),

  create: (data) =>
    apiClient.post('/orders', data).then((r) => r.data),

  delete: (id) =>
    apiClient.delete(`/orders/${id}`).then((r) => r.data),
}
