import {useState} from 'react'
import {Link,useNavigate} from  'react-router-dom'
import {login,register} from '../api/auth'
import useAuthStore from '../store/authStore'



function Register(){
      const [form,setForm]=useState({'username':'','email':'','password':'','confirm':''})
      const [errors,setErrors]=useState([])
      const [submitting,setSubmitting]=useState(false)
      const setTokens=useAuthStore((s)=>s.setTokens)
      const navigate=useNavigate()

      const handleChange=(e)=>setForm({...form,[e.target.name]:e.target.value})
      const handleSubmit=async (e)=>{
        e.preventDefault()
        setErrors([])
        if(form.password != form.confirm){
            setErrors(['Password do not match'])
            return 
        }
        setSubmitting(true)
        try{
            const {username,email,password}=form
            await register({username,email,password})
            const data=await login(username,password)
            setTokens(data.access,data.refresh)
            navigate('/')
        }catch(err){
            const data=err.response?.data
            setErrors(data && typeof data==='object' ? Object.values(data).flat():['Something went wrong.'])
        }finally{
            setSubmitting(false)
        }
      }

      const field={display:'block',width:'100%',marginBottom:'0.5rem'}


      return (
        <form onSubmit={handleSubmit} style={{padding:'1rem',maxWidth:'320px'}}> 
        <h1>Create Account</h1>
        {errors.length > 0 &&(
              <ul style={{color:'red'}}>
                  {errors.map((m,i)=><li key={i}>{m}</li>)}
              </ul>
        )}

        <input name="username" placeholder='Username' value={form.username} onChange={handleChange} required style={field}/>
        <input name="email" type='email' placeholder='Email' value={form.email} onChange={handleChange} required style={field}/>
        <input name="password" type='password' placeholder='Password' value={form.password} onChange={handleChange} required style={field}/>
        <input name="confirm" type='password' placeholder='Confirm Password' value={form.confirm} onChange={handleChange} required style={field}/>
        <button type='submit' disabled={submitting}>{submitting ? 'Creating ...':'Register'}</button>
        <p>Already have an account? <Link to="/login">Login</Link></p>
        </form>
      )
}

export default Register