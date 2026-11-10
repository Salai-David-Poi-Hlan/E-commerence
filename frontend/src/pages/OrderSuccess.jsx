import {useEffect,useState} from  'react'
import {useParams,Link} from'react-router-dom'
import {getOrder} from '../api/orders'
import  useCartStore from '../store/cartStore'



function OrderSuccess(){
       const {id} =useParams()
       const clearCart = useCartStore((s)=>s.clearCart);
       const [order,setOrder]=useState(null)

       useEffect(()=>{
        let tries=0
        let timer;

        const check= async () =>{
              tries+=1
              try{
                  const {data} = await getOrder(id)                  
                  setOrder(data)
                  if (data.status === 'paid') clearCart()
                    if (data.status !== 'pending' || tries >=10) clearInterval(timer)
              }
            catch(err){
                 clearInterval(timer)
            }
        }
        check()


        timer=setInterval(check,100)
        return ()=>clearInterval(timer)
       },[id,clearCart])

       if(!order) return <p style={{padding:'1rem'}}>Loading...</p>


       return(
        <div style={{padding:'1rem'}}>
             <h1>Order #{order.id}</h1>
             {
                order.status === 'pending'?(
                    <p>Confirming your payment... this can take a few seconds.</p>
                ):(
                    <p>Status: {order.status}. Thank you!</p>
                )
             }
             <Link to="/">Continue shopping</Link>
        </div>
       )
}



export default OrderSuccess