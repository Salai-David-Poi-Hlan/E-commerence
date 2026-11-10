import useCartStore from '../store/cartStore'
import {useNavigate} from 'react-router-dom'


function Cart(){
    const items=useCartStore((state)=>state.items);
    const removeItem=useCartStore((state)=>state.removeItem)
    const updateQuantity=useCartStore((store)=>store.updateQuantity)
    const getTotal=useCartStore((state)=>state.getTotal)
    const navigate=useNavigate()

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


                        <span>Bhat {(item.price * item.quantity).toFixed(2)}</span>
                       <button onClick={()=>removeItem(item.id)}>Remove</button>

                     </div>
                ))}


                <h3 style={{marginTop:'1rem'}}>Total Bhat {getTotal().toFixed(2)}</h3>
                <button onClick={()=>navigate('/checkout')} style={{marginTop:'1rem'}}>
                    Proceed To Checkout
                    </button>
         </div>
     )
}

export default Cart