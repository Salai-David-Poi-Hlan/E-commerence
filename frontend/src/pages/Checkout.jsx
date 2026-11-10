import {useState} from 'react'
import {Link} from 'react-router-dom'
import {validateCart,createOrder,payOrder} from  '../api/orders'
import useCartStore from '../store/cartStore'


function describeProblem(p){
    if (p.error === 'insufficient_stock'){
        return `${p.name} only ${p.available} left (you asked for ${p.requested})`
    }
    return `Product #${p.product} is no longer available`
}


function Checkout(){
    const items=useCartStore((s)=>s.items)
    const syncPrices=useCartStore((s)=>s.syncPrices)
    const getTotal=useCartStore((s)=>s.getTotal)
    const [address,setAddress]=useState('')
    const [problems,setProblems]=useState([])
    const [notice,setNotice]=useState('')
    const [submitting,setSUbmitting]=useState(false)
     
    if(items.length === 0){
        return(
            <div style={{padding:'1rem'}}>
                  <p>Your Cart is empty.</p>
                  <Link to="/">Back to Shop</Link>
            </div>
        )
    }


    const handleSubmit = async (e) =>{
         e.preventDefault()
         setProblems([])
         setNotice('')
         setSUbmitting(true)

         try{
             const {data:check}=await validateCart(items)
             if(!check.valid){
                setProblems(check.problems)
                return    
            }

            const priceChanged=check.items.some((v)=>{
                const local=items.find((i)=>i.id === v.product)
                return !local || Number(local.price) !== Number(v.price)
            })

            if(priceChanged){
                syncPrices(check.items)
                setNotice("Some prices changed. Please review your total and submit again. ")
                return
            }
            const {data:order} = await createOrder(items,address)
            const {data:pay}=await payOrder(order.id)
            window.location.href=pay.checkout_url
         }

         catch(err){
            console.log(err);
            
            if (err.response?.status === 400 && err.response.data.errors){
                setProblems(err.response.data.errors)
            }else{
                setNotice("Something went wrong. Please try again.")
            }
         }finally{
            setSUbmitting(false)
         }
    }


    return(
        <form onSubmit={handleSubmit} style={{padding:'1rem',maxWidth:'400px'}}>
               <h1>Checkout</h1>
               {items.map((i)=>(
                <p key={i.id }>
                     {i.quantity} x {i.name}: Baht {(i.price * i.quantity).toFixed(2)}
                </p>
               ))}
               <h3>Total: Baht {getTotal().toFixed(2)}</h3>

               {notice && <p style={{
                color:'darkorange'
               }}>{notice}</p>}

               {problems.length >0 &&(
                    <ul style={{color:'red'}}>
                {problems.map((p,idx)=>(
                    <li key={idx}>{describeProblem(p)}</li>
                ))}
                    </ul>
               )}

               <textarea
               required
               placeholder='Shipping Address'
               value={address}
               onChange={(e)=>setAddress(e.target.value)}
               style={{display:'block',width:'100%',marginBottom:'0.5rem'}}
               />

               <button type='submit' disabled={submitting}>
                     {submitting ? 'Processing...':'pay Now'}
               </button>
        </form>
    )
}
export default Checkout