import useCartStore from '../store/cartStore'



function Cart(){
    items=useCartStore((state)=>state.items);
    const removeItem=useCartStore((state)=>state.removeItem)
    const updateQuantity=useCartStore((store)=>store.updateQuantity)
    const getTotal=useCartStore((state)=>state.getTotal)


     if (items.length===0){
        return(
            <div style={{padding:'1rem'}}>
              <h1>Your Cart</h1>
              <p>Your cart is empty</p>
            </div>
        )
     }

     return (
         <div style={{padding:'1rem'}}>
                <h1>Your Cart</h1>
                {items.map((item)=>(
                    
                ))}
         </div>
     )
}