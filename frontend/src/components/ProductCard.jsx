function ProductCard(){
      return(
        <div style={{border:'1px solid #ddd',padding:'1rem',marginBottom:'0.5rem'}}>
             <h3>{product.name}</h3>
             <p>{product.price}</p>
        </div>
      )
}
export default ProductCard