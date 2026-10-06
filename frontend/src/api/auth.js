import apiClient from './client'



export const login=(username,password)=>{
   return  apiClient.post('/token/',{username,password})
}