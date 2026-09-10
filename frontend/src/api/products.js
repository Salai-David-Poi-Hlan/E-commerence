import apiClient from "./client"


export const getProducts=apiClient.get('/products')
export const getProduct=apiClient.get(`/products/${id}/`)