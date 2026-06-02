import apiClient from './client'

export const productsApi = {
  getAll: (params = {}) =>
    apiClient.get('/products', { params }).then((r) => r.data),

  getById: (id) =>
    apiClient.get(`/products/${id}`).then((r) => r.data),

  create: (data) =>
    apiClient.post('/products', data).then((r) => r.data),

  update: (id, data) =>
    apiClient.put(`/products/${id}`, data).then((r) => r.data),

  delete: (id) =>
    apiClient.delete(`/products/${id}`).then((r) => r.data),
}
