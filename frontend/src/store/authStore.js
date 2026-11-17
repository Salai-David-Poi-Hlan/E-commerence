import {create} from 'zustand'

const useAuthStore=create((set)=>({
    accessToken:localStorage.getItem('accessToken') || null,
    refreshToken:localStorage.getItem('refreshToken') || null,
    
    setTokens:(access,refresh)=>{
        localStorage.setItem('accessToken',access)
        localStorage.setItem('refreshToken',refresh)

        set ({accessToken:access,refreshToken:refresh})
    },


    logout:()=>{
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        set({accessToken:null,refreshToken:null})
    },
    isAuthenticated:()=>!!get().accessToken
}))


export default useAuthStore