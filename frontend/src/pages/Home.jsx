import {useEffect,useState}  from 'react'
import {getProduct,getProducts} from '../api/products'
import {ProductCard} from '../components/ProductCard'

function Home(){
    const [products,setProducts]=useState([])
    const [loading,setLoading]=useState([])

    useEffect(()=>{
      getProducts()
      .then((res)=>setProducts(res))
      .catch((err)=>console.error(err))
      .finally(()=>setLoading(false))
    },[])

    if (loading) return <P>Loading ... </P>
    
    return(
        <div>
            <h1>Products</h1>
            {products.length===0?(
                <p>No Products yet</p>
            ):(
                products.map((p)=>{
                    <ProductCard key={p.id} product={p}/>
                })
            )}
        </div>
    )
}

export default Home