import apiClient from "./client"


export const getProducts=()=>apiClient.get('/products')
export const getProduct=(id)=>apiClient.get(`/products/${id}/`)
export const createProduct=(data)=>apiClient.post('/products/',data)
