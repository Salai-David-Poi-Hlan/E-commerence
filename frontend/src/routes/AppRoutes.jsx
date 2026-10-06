import {Route,Routes} from 'react-router-dom'
import Home from '../pages/Home'
import ProductDetails from '../pages/ProductDetails'
import Cart from '../pages/Cart'
import Login from'../pages/Login'
import ProductForm from '../pages/admin/ProductForm'
import PrivateRoute  from './PrivateRoute'

function AppRoutes(){
     

    return (
        <Routes>
            <Route path="/" element={<Home/>}/>
            <Route path="/products/:id"  element={<ProductDetails/>}/>
            <Route path="/cart"  element={<Cart/>}/>
            <Route path='/login' element={<Login/>}/>
            <Route path='/admin/products/new'
             element={
                <PrivateRoute>
                       <ProductForm/>
                </PrivateRoute>
           }/>
        </Routes>
    )
  
}


export default AppRoutes