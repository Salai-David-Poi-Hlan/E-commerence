import {useCallback,useEffect,useState} from 'react'
import {Link} from 'react-router-dom'
import {getMyOrders,cancelOrder,payOrder} from '../api/orders'

const STATUS_COLORS = {
     pending : 'darkorange',
     paid : 'green',
     shipped : 'royalblue',
     delivered : 'seagreen',
     cancelled : 'gray'
}


function OrderHistory(){
      const [orders,setOrders] = useState([])
      const [loading,setLoading] = useState(true)
      const [error,setError] = useState('')
      const [busyId,setBusyId] = useState(null)


      const load = useCallback(async () =>{
         try{
            const {data} = await getMyOrders()
            setOrders(data)
         } catch {
               setError('Could not load your orders')
         }finally {
            setLoading(false)
         }
      },[])


      useEffect(()=>{
            load()
      },[load])



      const handleCancel = async (order)=>{
             if (!window.confirm(`Cancel order #${order.id}`)) return
             setError('')
             setBusyId(order.id)
             try{
                const {data} = await cancelOrder (order.id)
                setOrders((prev)=>prev.map((o)=>(o.id === data.id ? data:o)))
             }catch{
                   setError(`Order #${order.id} could be cancelled. it's status may have changed`)
                   await load()
             } finally{
                setBusyId(null)
             }
      }


      const handlePay = async (order) =>{
        setError('')
        setBusyId(order.id)
        try{
            const {data} = await payOrder(order.id)
            window.location.href= data.checkout_url
        }catch{
            setError(`Could not start payment for order #${order.id}.`)
            await load()
            setBusyId(null)
        }  
      }



      if (loading) return <p style={{padding:'1rem'}}>Loading...</p>
      
      return(
        <div style={{padding:'1rem',maxWidth:'640px'}}>
              <h1>My Orders</h1>
              {error && 
              <p style={{color:'red'}}>
                   {error}
                </p>}


                {orders.length === 0?(
                   <p>
                       You have no orders yet. <Link to="/">Start shopping</Link>
                   </p>
                ):(
                    orders.map((order)=>(
                        <div key={order.id}
                             style={{border:'1px solid #ddd',padding:'1rem',marginBottom:'1rem'}}
                        >
                          <div style={{display:'flex',justifyContent:'space-between'}}>
                            <strong>Order #{order.id}</strong>
                            <span style={{color:STATUS_COLORS[order.status]}}>{order.status}</span>
                          </div>
                          <small>{new Date(order.created_at).toLocaleString()}</small>


                          <ul>
                               {order.items.map((item)=>(
                                 <li key={item.id}>
                                  {item.quantity} x {item.product_name}: Baht{' '}
                                  {(Number(item.price) * item.quantity).toFixed(2)}
                                 </li>
                               ))}
                          </ul>


                            <p>
                                <strong>Total: Baht {Number(order.total_prcie).toFixed(2)}</strong>
                            </p>
                            <p>Ship to: {order.shipping_address}</p>



                            {order.status === 'pending' && (
                                 <>
                                    <button onClick={()=>handlePay(order)} disabled={busyId === order.id}>
                                        Pay Now
                                    </button>  {' '}

                                    <button onClick={()=>handleCancel(order)} disabled={busyId=== order.id}>
                                        Cancel order
                                    </button>
                                 </>
                            )}
                        </div>
                    ))
                )}
        </div>
      )

    }

export default OrderHistory