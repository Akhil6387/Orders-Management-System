import { describe, it, expect, vi, beforeEach } from 'vitest'
import apiClient from '../api/client'

// ── API Client ────────────────────────────────────────────────
describe('API client', () => {
  it('has correct baseURL', () => {
    expect(apiClient.defaults.baseURL).toBeTruthy()
  })

  it('sets JSON content-type header', () => {
    expect(apiClient.defaults.headers['Content-Type']).toBe('application/json')
  })
})

// ── Products API ──────────────────────────────────────────────
describe('productsApi', async () => {
  const { productsApi } = await import('../api/products')

  beforeEach(() => vi.restoreAllMocks())

  it('getAll calls /products endpoint', () => {
    const spy = vi.spyOn(apiClient, 'get').mockResolvedValue({ data: [] })
    productsApi.getAll()
    expect(spy).toHaveBeenCalledWith('/products', { params: {} })
  })

  it('create calls POST /products', () => {
    const spy = vi.spyOn(apiClient, 'post').mockResolvedValue({ data: {} })
    productsApi.create({ product_name: 'Test', sku: 'T-001', price: 10, quantity_in_stock: 5 })
    expect(spy).toHaveBeenCalledWith('/products', expect.objectContaining({ sku: 'T-001' }))
  })

  it('update calls PUT /products/{id}', () => {
    const spy = vi.spyOn(apiClient, 'put').mockResolvedValue({ data: {} })
    productsApi.update(1, { product_name: 'Updated' })
    expect(spy).toHaveBeenCalledWith('/products/1', expect.any(Object))
  })

  it('delete calls DELETE /products/{id}', () => {
    const spy = vi.spyOn(apiClient, 'delete').mockResolvedValue({ data: {} })
    productsApi.delete(1)
    expect(spy).toHaveBeenCalledWith('/products/1')
  })
})

// ── Customers API ─────────────────────────────────────────────
describe('customersApi', async () => {
  const { customersApi } = await import('../api/customers')

  beforeEach(() => vi.restoreAllMocks())

  it('getAll calls /customers endpoint', () => {
    const spy = vi.spyOn(apiClient, 'get').mockResolvedValue({ data: [] })
    customersApi.getAll()
    expect(spy).toHaveBeenCalledWith('/customers', { params: {} })
  })

  it('create calls POST /customers', () => {
    const spy = vi.spyOn(apiClient, 'post').mockResolvedValue({ data: {} })
    customersApi.create({ full_name: 'Alice', email: 'alice@test.com', phone_number: '555-1234' })
    expect(spy).toHaveBeenCalledWith('/customers', expect.objectContaining({ email: 'alice@test.com' }))
  })
})

// ── Orders API ────────────────────────────────────────────────
describe('ordersApi', async () => {
  const { ordersApi } = await import('../api/orders')

  beforeEach(() => vi.restoreAllMocks())

  it('getAll calls /orders endpoint', () => {
    const spy = vi.spyOn(apiClient, 'get').mockResolvedValue({ data: [] })
    ordersApi.getAll()
    expect(spy).toHaveBeenCalledWith('/orders', { params: {} })
  })

  it('create calls POST /orders with items', () => {
    const spy = vi.spyOn(apiClient, 'post').mockResolvedValue({ data: {} })
    ordersApi.create({ customer_id: 1, items: [{ product_id: 2, quantity: 3 }] })
    expect(spy).toHaveBeenCalledWith('/orders', expect.objectContaining({ customer_id: 1 }))
  })
})
