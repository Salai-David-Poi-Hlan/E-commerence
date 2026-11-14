import {Link,useNavigate} from  'react-router-dom'
import useCartStore from '../store/cartStore'
import {revokeToken} from '../api/auth'
import useAuthStore from '../store/authStore'

function Navbar(){
    const items=useCartStore((state)=>state.items)
    const itemsCount=items.reduce((sum,item)=>sum+item.quantity,0);
    const loggedIn=useAuthStore((s)=>!!s.refreshToken)
    const navigate=useNavigate()

    console.log(loggedIn);
    
    const handlelogout=async () =>{
         const {refreshToken,logout} = useAuthStore.getState()
         try{
            await revokeToken(refreshToken)
         }
         catch{

         }
         logout()
         navigate('/')
    }

    

    return(
        <nav
        style={{
            display: 'flex',
            justifyContent:'space-between',
            alignItems:'center',
            padding:'1rem',
            borderBottom:'1px solid #ddd',
        }}
        >
                 <Link
                 to="/" style={{fontWeight:'bold',textDecoration:'none',color:'inherit'}}>
                  My Store
                 </Link>

                 <div>
                    <Link
                 to="/" style={{marginRight:'1rem'}}
                 >
                    Home
                                     </Link>


                                       <Link
                 to="/cart" 
                 >
                    Cart {itemsCount > 0 && `${itemsCount}`}
                                     </Link>

                 {loggedIn ? (
                    <button onClick={handlelogout}>Logout</button>
                 ):(
                    <>
                        <Link to="/login" style={{marginLeft:'1rem'}}>Login</Link>
                        <Link to="/register" style={{marginLeft:'1rem'}}>Register</Link>

                    </>
                 )}

                 </div>

            </nav>
    )
}


export default Navbar