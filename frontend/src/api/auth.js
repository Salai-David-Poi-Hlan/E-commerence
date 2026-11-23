import apiClient from './client'



export const login=(username,password)=>{
   return  apiClient.post('/token/',{username,password})
}

export const register=(data)=>apiClient.post('/register/',data)

export const revokeToken=(refresh)=>apiClient.post('/token/blacklist/',{refresh})

export const getMe=()=>apiClient.get('/me/')


