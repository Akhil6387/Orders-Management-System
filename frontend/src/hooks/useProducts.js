import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { message } from 'antd'
import { productsApi } from '../api/products'

export const PRODUCTS_KEY = ['products']

export function useProducts(params) {
  return useQuery({
    queryKey: [...PRODUCTS_KEY, params],
    queryFn: () => productsApi.getAll(params),
  })
}

export function useProduct(id) {
  return useQuery({
    queryKey: [...PRODUCTS_KEY, id],
    queryFn: () => productsApi.getById(id),
    enabled: !!id,
  })
}

export function useCreateProduct() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: productsApi.create,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: PRODUCTS_KEY })
      message.success('Product created successfully')
    },
    onError: (err) => message.error(err.userMessage || 'Failed to create product'),
  })
}

export function useUpdateProduct() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }) => productsApi.update(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: PRODUCTS_KEY })
      message.success('Product updated successfully')
    },
    onError: (err) => message.error(err.userMessage || 'Failed to update product'),
  })
}

export function useDeleteProduct() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: productsApi.delete,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: PRODUCTS_KEY })
      message.success('Product deleted')
    },
    onError: (err) => message.error(err.userMessage || 'Failed to delete product'),
  })
}
