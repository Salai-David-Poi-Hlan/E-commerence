import {useEffect,useState} from 'react'
import apiClient from './api/client' 



function App(){
  const [products,setProducts]=useState([])
  const [loading,setLoading]=useState(true)


   useEffect(()=>{
    apiClient.get('/products/')
    .then((res)=>setProducts(res.data))
    .catch((err)=>console.error(err))
    .finally(()=>setLoading(false))
   },[]);

   if (loading) return <p>Loading ...</p>

   return (
      <div>
         <h1>Products</h1>
         {products.length===0?(
             <p>No Products Yet</p>
         ):(
            <ul>
              {products.map((p)=>(
                 <li key={p.id}>{p.name} - ${p.price}</li>
              ))}
            </ul>
         )}    
      </div>
   )
}

export default App