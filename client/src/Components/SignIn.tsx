import { useState } from 'react'
import { PiDiamondsFourFill } from 'react-icons/pi'
import { IoEye, IoEyeOff } from 'react-icons/io5'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'


export const SignIn = () => {
  const Nav = useNavigate()
  const [show, setShow ] = useState(false)
  const [pass, setPass ] = useState('password')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  
  const infoArray = {
    email: '',
    password: '',
  
  }

  const Signin = async()=>{
  if(email ==='' || password === '') {
    alert('email and password required')
    return
  } else {
    infoArray.email = email
    infoArray.password = password

    


    const TokenArray = []
    try {
      const response = await axios.post('http://localhost:8000/auth/login/', infoArray)

      console.log('Sign Up successful:', response.data)
      const refreshToken = response.headers['getAuthorization']
      TokenArray.push(refreshToken)
      localStorage.setItem('token', JSON.stringify(refreshToken))

      alert('Sign Up successful')
      setEmail('')
      setPassword('')
      console.log(response.data)
      
      console.log(infoArray)

      // Handle successful sign-up (e.g., navigate to a different page)
      // navigate('/some-other-page')
    } catch (error) {
      console.error('Error during sign-up:', error)
      alert('Sign up failed. Please try again.')
    }
  }
  }

  
  return (
    <div className="Signup_Container">
        <section className="White_Section">
            <span><PiDiamondsFourFill/> EchoCart</span>
            <h1>Welcome Back, To EchoCart</h1>
            <article><span>New User?</span> <p onClick={()=> Nav('/auth/signup')}>Create an account</p>
            </article>
            <label htmlFor="email">Email</label>
            <div className="Input_Container" tabIndex={0}>
             <input type="text" id='email' value={email} onChange={(e)=>setEmail(e.target.value)} placeholder="input your registered email" />
            </div>
            <label htmlFor="email">password</label>
            <div className="Input_Container"  tabIndex={0}>
            <input type={pass} value={password} onChange={(e)=>setPassword(e.target.value)} placeholder="input your password" />
            {
              show? <p onClick={()=>{ 
                setPass('password')
                 setShow(false)}
                }><IoEyeOff/></p> : <p onClick={()=> {
                  setPass('text')
                  setShow(true)}
                }><IoEye/></p>
            }
            </div>
            <p onClick={()=> Nav('/auth/forgot-password')}>forgot password?</p>
            <div className="Bottom_Container">
              <div onClick={Signin} className="Login_Btn">LOGIN</div>
            </div>
        </section>
        <section className="Blue_Section">
        <span><PiDiamondsFourFill/> EchoCart</span>

        </section>
    </div>
  )
}
