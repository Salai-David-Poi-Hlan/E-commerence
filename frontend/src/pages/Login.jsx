import {useState} from 'react'
import  {useNavigate} from 'react-router-dom'
import {login} from '../api/auth'
import useAuthStore  from '../store/authStore'



function Login(){
        const [username,setUsername]=useState('')
        const [password,setPassword]=useState('')
        const [error,setError]=useState('')
        const setToken=useAuthStore((state)=>state.setToken)
        const navigate=useNavigate()

        const handleSubmit=async (e)=>{
              e.preventDefault()
              try{
                const res=await login(username,password)
                setToken(res.data.access)
                navigate('/admin/products/new')
              }catch(err){
                   setError('Invalid Credentials')
              }
        }
        return (
            <form onSubmit={handleSubmit} style={{padding:'1rem',maxWidth:'300px'}}>
                <h1>Admin Login</h1>
                {error && <p style={{color:'red'}}>{error}</p>}
                <input
                placeholder='Username'
                value={username}
                onChange={(e)=>setUsername(e.target.value)}
                style={{display:'block',marginBottom:'0.5rem',width:'100%'}}
                />
                <input
                type="password"
                placeholder='Password'
                value={password}
                onChange={(e)=>setPassword(e.target.value)}
                style={{display:'block',marginBottom:'0.5rem',width:'100%'}}
                />
                <button type="submit">Login</button>
            </form>
        )
}
export default Login;