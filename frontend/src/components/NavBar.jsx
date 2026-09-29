import {Link} from  'react-router-dom'
import useCartStore from '../store/cartStore'


function Navbar(){
    const items=useCartStore((state)=>state.items)
    const itemsCount=items.reduce((sum,item)=>sum+item.quantity,0);
   
    

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



                 </div>

            </nav>
    )
}


export default Navbar