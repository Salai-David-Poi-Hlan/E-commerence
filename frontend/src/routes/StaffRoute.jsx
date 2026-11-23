import {Navigate,useLocation} from 'react-router-dom'
import useAuthStore from '../store/authStore'

function SatffRoute({children}){
     const refreshToken=useAuthStore((s)=>s.refreshToken)
     const me=useAuthStore((s)=>s.me)
     const location=useLocation()

     if(!refreshToken) return <Navigate to="/login" replace state={{from:location}}/>
     if (!me) return <p style={{padding:'1rem'}}>Loading...</p>
     if (!me.is_staff) return <Navigate to="/" replace/>
     return children
}


export default SatffRoute