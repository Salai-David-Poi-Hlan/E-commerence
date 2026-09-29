import useCartStore from '../store/cartStore'



function Cart(){
    const items=useCartStore((state)=>state.items);
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
                     <div
                     key={item.id}
                     style={{
                        display:'flex',
                        justifyContent:'space-between',
                        alignItems:'center',
                        borderBottom:'1px solid #ddd',
                        padding:'0.5rem 0'
                     }}
                     >
                        <span>{item.name}</span>
                        <input
                        type="number"
                        min="1"
                        value={item.quantity}
                        onChange={(e)=>updateQuantity(item.id,parseInt(e.target.value,10))}
                        style={{width:'50px'}}
                        />


                        <span>${(item.price * item.quantity).toFixed(2)}</span>
                       <button onClick={()=>removeItem(item.id)}>Remove</button>

                     </div>
                ))}


                <h3 style={{marginTop:'1rem'}}>Total ${getTotal().toFixed(2)}</h3>
                <button style={{marginTop:'1rem'}}>Proceed To Checkout</button>
         </div>
     )
}

export default Cart