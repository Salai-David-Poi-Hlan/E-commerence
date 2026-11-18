import {Route,Routes} from 'react-router-dom'
import Home from '../pages/Home'
import ProductDetails from '../pages/ProductDetails'
import Cart from '../pages/Cart'
import Login from'../pages/Login'
import ProductForm from '../pages/admin/ProductForm'
import PrivateRoute  from './PrivateRoute'
import Checkout from '../pages/Checkout'
import OrderSuccess from '../pages/OrderSuccess'
import Register from  '../pages/Register'
import OrderHistory from '../pages/OrderHistory'
function AppRoutes(){
     

    return (
        <Routes>
            <Route path="/" element={<Home/>}/>

            <Route path="/products/:id"  element={<ProductDetails/>}/>
            <Route path="/cart"  element={<Cart/>}/>
            <Route path='/login' element={<Login/>}/>
            <Route path='/register' element={<Register/>}/>
            <Route path='/orders' 
            element={
                <PrivateRoute>
                    <OrderHistory/>
                </PrivateRoute>
            }
            />
            <Route path='/admin/products/new'
             element={
                <PrivateRoute>
                       <ProductForm/>
                </PrivateRoute>
           }/>
           <Route path="/checkout" element={<PrivateRoute>
                 <Checkout/>
           </PrivateRoute>}/>
           <Route path="/orders/:id/success" element={<PrivateRoute>
                   <OrderSuccess/>
           </PrivateRoute>}/>
        </Routes>
    )
  
}


export default AppRoutes