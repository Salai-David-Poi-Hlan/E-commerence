import {useEffect,useState}  from 'react'
import { useParams } from 'react-router-dom'
import {getProduct} from '../api/products'
import useCartStore from '../store/cartStore.js'

function ProductDetails(){
    const {id}=useParams()
    const [product,setProduct]=useState(null)
    const [loading,setLoading]=useState(true)
    const [error,SetError]=useState(null)
    const addItem=useCartStore((state)=>state.addItem) 

    useEffect(()=>{
      getProduct(id)
      .then((res)=>{
        console.log(res);
        
        setProduct(res.data)})
      .catch((err)=>SetError(err))
      .finally(()=>setLoading(false))
    },[id])


    if (loading) return <p>Loading ... </p>
    if (error) return <p>Product Not Found</p>
    return (
    <div style={{padding:'1rem'}}>
              <h1>{product.name}</h1>
              <p>{product.description}</p>
              <p><strong>{product.price}</strong></p>
              <p>In stock: {product.stock_qty}</p>
              <button onClick={() => addItem(product)}>Add to Cart</button>
    </div>)
} 


export default ProductDetails;