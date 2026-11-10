import axios from 'axios'
import useAuthStore from '../store/authStore'

const apiClient=axios.create({
    baseURL:import.meta.env.VITE_API
})


apiClient.interceptors.request.use((config)=>{
    const token=useAuthStore.getState().accessToken
    if (token){
        config.headers.Authorization=`Bearer ${token}`
    }

    return config
})


apiClient.interceptors.response.use(
    (res)=>res,
    (err)=>{
        const isLoginCall=err.config?.url?.includes('/token/');
        if (err.response?.status===401 && !isLoginCall){
            useAuthStore.getState().logout()
            window.location.href='/login'
        }
        return Promise.reject(err)
    }
)

export default apiClient 