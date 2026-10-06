import {create} from 'zustand'

const useAuthStore=create((set)=>({
    accessToken:localStorage.getItem('accessToken') || null,
    
    setToken:(token)=>{
        localStorage.setItem('accessToken',token)
        set ({accessToken:token})
    },


    logout:()=>{
        localStorage.removeItem('accessToken');

        set({accessToken:null})
    },


    isAuthenticated:()=>!localStorage.getItem('accessToken')
}))


export default useAuthStore