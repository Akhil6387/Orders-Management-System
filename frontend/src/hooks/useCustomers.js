import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { message } from 'antd'
import { customersApi } from '../api/customers'

export const CUSTOMERS_KEY = ['customers']

export function useCustomers(params) {
  return useQuery({
    queryKey: [...CUSTOMERS_KEY, params],
    queryFn: () => customersApi.getAll(params),
  })
}

export function useCustomer(id) {
  return useQuery({
    queryKey: [...CUSTOMERS_KEY, id],
    queryFn: () => customersApi.getById(id),
    enabled: !!id,
  })
}

export function useCreateCustomer() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: customersApi.create,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: CUSTOMERS_KEY })
      message.success('Customer added successfully')
    },
    onError: (err) => message.error(err.userMessage || 'Failed to add customer'),
  })
}

export function useDeleteCustomer() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: customersApi.delete,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: CUSTOMERS_KEY })
      message.success('Customer deleted')
    },
    onError: (err) => message.error(err.userMessage || 'Failed to delete customer'),
  })
}
