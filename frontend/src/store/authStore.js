import {create} from 'zustand'

const useAuthStore=create((set)=>({
    accessToken:localStorage.getItem('accessToken') || null,
    refreshToken:localStorage.getItem('refreshToken') || null,
    me:null,
    setTokens:(access,refresh)=>{
        localStorage.setItem('accessToken',access)
        localStorage.setItem('refreshToken',refresh)
        set ({accessToken:access,refreshToken:refresh})

    },

    setMe: (me) => set({me}),
    
    logout:()=>{
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        set({accessToken:null,refreshToken:null,me:null})
    },
    isAuthenticated:()=>!!get().accessToken
}))


export default useAuthStore