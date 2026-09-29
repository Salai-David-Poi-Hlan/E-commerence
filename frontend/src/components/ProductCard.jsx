import {Link} from 'react-router-dom'



function ProductCard({product}){
      return(
         <Link to={`/products/${product.id}`} style={{textDecoration:'none',color:'inherit' }}> 
           <div style={{border:'1px solid #ddd',padding:'1rem',marginBottom:'0.5rem'}}>
             <h3>{product.name}</h3>
             <p>{product.price}</p>
        </div>
         </Link>
      )
}
export default ProductCard