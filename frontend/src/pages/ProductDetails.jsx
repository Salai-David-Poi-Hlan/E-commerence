import {useEffect,useState}  from 'react'
import { useParams } from 'react-router-dom'
import {getProduct} from '../api/products'


function productDetails(){
    const {id}=useParams()
    const [product,setProduct]=useState(null)
    const [loading,setLoading]=useState(true)
    const [error,SetError]=useState(null)

    useEffect(()=>{
      getProduct()
      .then((res)=>setProduct(res))
      .catch((err)=>SetError(err))
      .finally(()=>setLoading(false))
    },[])


    if (loading) return <p>Loading ... </p>
    if (error) return <p>Product Not Found</p>
    return (
    <div style={{padding:'1rem'}}>
              <h1>{product.name}</h1>
              <p>{product.description}</p>
              <p><strong>{product.price}</strong></p>
              <p>In stock: {product.stock_qty}</p>
    </div>)
} 


export default productDetails;