import {Route,Routes} from 'react-router-dom'
import Home from '../pages/Home'
import productDetails from '../pages/ProductDetails'


function AppRoutes(){
     

    return (
        <Routes>
            <Route path="/" element={<Home/>}/>
            <Route path=""
        </Routes>
    )
  
}


export default AppRoutes