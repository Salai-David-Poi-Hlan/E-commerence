import {Route,Routes} from 'react-router-dom'
import Home from '../pages/Home'
import ProductDetails from '../pages/ProductDetails'
import Cart from '../pages/Cart'

function AppRoutes(){
     

    return (
        <Routes>
            <Route path="/" element={<Home/>}/>
            <Route path="/products/:id"  element={<ProductDetails/>}/>
            <Route path="/cart"  element={<Cart/>}/>

        </Routes>
    )
  
}


export default AppRoutes