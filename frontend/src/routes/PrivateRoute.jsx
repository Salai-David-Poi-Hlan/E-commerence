import {Navigate, useLocation} from 'react-router-dom'
import useAuthStore from '../store/authStore'


function PrivateRoute({children}){
    const isAuthenticated=useAuthStore((s)=>!!s.refreshToken)
    const location=useLocation()
    if (!isAuthenticated){
        return <Navigate to="/login" replace state={{ from:location }}/>
    }

    return children
}


export default PrivateRoute