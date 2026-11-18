import apiClient from './client'

const toPayload=(items)=>
    items.map((i)=>({
        product:i.id,quantity:i.quantity
    }))

export const validateCart=(items)=>
    apiClient.post('/cart/validate/',{items:toPayload(items)})

export const createOrder=(items,shippingAddress)=>

    apiClient.post('/orders/',{
        shipping_address:shippingAddress,
        items:toPayload(items)
    })

export const payOrder=(orderId)=>
    apiClient.post(`/orders/${orderId}/pay/`)

export const getOrder=(orderId)=>
    apiClient.get(`/orders/${orderId}/`)


export const getMyOrders = () =>apiClient.get('/orders/')

export const cancelOrder = (orderId) => 
    apiClient.post(`/orders/${orderId}/status`,{status:'cancelled'})