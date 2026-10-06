import {useState} from 'react'
import {useNavigate} from 'react-router-dom'
import {createProduct} from '../../api/products'



function ProductForm(){
    const [form,setForm]=useState({
        name:'',
        description:'',
        price:'',
        stock_qty:'',
    })
    
    const [error,setError]=useState('')
    const navigate=useNavigate()



    const handleChange=(e)=>{
        setForm({...form,[e.target.name]:e.target.value})
    }

    const handleSubmit=async (e)=>{
        e.preventDefault()
        try{
            await createProduct(form)
            navigate('/')

        }catch(err){
            setError('Failed to create product - check you are logged in as admin')
        }
    }



    return (
        <form onSubmit={handleSubmit} style={{padding:'1rem',maxWidth:'400px'}}> 
               <h1>Add Product</h1>
               {error && <p style={{color:'red'}}>{error}</p>}

               <input
               name='name'
               placeholder='Product Name'
               value={form.name}
               onChange={handleChange}
               style={{display:'block',marginBottom:'0.5rem',width:'100%'}}
               />

               <textarea
               name="description"
               placeholder='Description'
               value={form.description}
               onChange={handleChange}
               style={{display:'block',marginBottom:'0.5rem',width:'100%'}}
               />

               <input
                   name="price"
                   type='number'
                   step="0.01"
                   placeholder="Price"
                   value={form.price}
                   onChange={handleChange}
                   style={{display:'block',marginBottom:'0.5rem',width:'100%'}}
               />

                 <input
                   name="stock_qty"
                   type='number'
                   placeholder="Stock Quantity"
                   value={form.stock_qty}
                   onChange={handleChange}
                   style={{display:'block',marginBottom:'0.5rem',width:'100%'}}
               />
          
          <button type='submit'>Create Product</button>

        </form>
    )
}

export default ProductForm