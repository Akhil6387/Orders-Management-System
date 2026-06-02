import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { message } from 'antd'
import { ordersApi } from '../api/orders'

export const ORDERS_KEY = ['orders']

export function useOrders(params) {
  return useQuery({
    queryKey: [...ORDERS_KEY, params],
    queryFn: () => ordersApi.getAll(params),
  })
}

export function useOrder(id) {
  return useQuery({
    queryKey: [...ORDERS_KEY, id],
    queryFn: () => ordersApi.getById(id),
    enabled: !!id,
  })
}

export function useCreateOrder() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ordersApi.create,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ORDERS_KEY })
      // Invalidate products because stock changes
      qc.invalidateQueries({ queryKey: ['products'] })
      message.success('Order placed successfully')
    },
    onError: (err) => message.error(err.userMessage || 'Failed to create order'),
  })
}

export function useDeleteOrder() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ordersApi.delete,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ORDERS_KEY })
      message.success('Order deleted')
    },
    onError: (err) => message.error(err.userMessage || 'Failed to delete order'),
  })
}
