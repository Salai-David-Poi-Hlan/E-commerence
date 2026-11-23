import {BrowserRouter} from 'react-router-dom'
import AppRoutes from  './routes/AppRoutes'
import Navbar from'./components/NavBar'
import {useEffect}  from 'react'
import {getMe} from './api/auth'
import useAuthStore from './store/authStore'



function App(){
   const refreshToken=useAuthStore((s)=>s.refreshToken)
   const setMe = useAuthStore((s)=>s.setMe)


   useEffect(()=>{
        if(!refreshToken) return
        getMe().then(({data})=>setMe(data)).catch(()=>{})
   },[refreshToken,setMe])



    return(
        <BrowserRouter>
        <Navbar/>
        <AppRoutes/>
        </BrowserRouter>
    )
}

export default App