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


let refreshPromise=null;


function refreshAccessToken(){
    if(!refreshPromise){
        const {refreshToken} = useAuthStore.getState()
        refreshPromise=axios
        .post(`${import.meta.env.VITE_API}/token/refresh/`,{refresh:refreshToken})
        .then(({data})=>{
            useAuthStore.getState().setToken(data.access,data.refresh??refreshToken)
            return data.access
        })
        .finally(()=>{
            refreshPromise=null
        })
    }
    return refreshPromise
}


apiClient.interceptors.response.use(
    (res)=>res,
    async (error)=>{
        const original=error.config
        const isAuthCall=original?.url?.includes('/token/');

        if(error?.response?.status !==401 || !original || original._retry || isAuthCall){
            return Promise.reject(error)
        }
        if (!useAuthStore.getState().refreshToken){
            return Promise.reject
            (error)
        }

        original._retry=true

        try{
            const newAccess = await refreshAccessToken()
            original.headers.Authorization= `Bearer ${newAccess}`
            return apiClient(original)
        }catch{
            useAuthStore.getState().logout()
            return Promise.reject(error)
        }
    }
)

export default apiClient 