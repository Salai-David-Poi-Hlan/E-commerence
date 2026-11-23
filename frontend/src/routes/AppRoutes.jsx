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
import SatffRoute from './StaffRoute'
import AdminOrders from '../pages/admin/AdminOrders'

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
           <Route path='/admin/orders' element={
                <SatffRoute>
                    <AdminOrders/>
                </SatffRoute>
           }>

           </Route>
        </Routes>
    )
  
}


export default AppRoutes