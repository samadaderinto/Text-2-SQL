import { useState } from 'react'
import { PiDiamondsFourFill } from 'react-icons/pi'
import { IoEye, IoEyeOff } from 'react-icons/io5'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'


export const Signup = () => {
  const [show, setShow] = useState(false)
  const [show1, setShow1] = useState(false)
  const [pass, setPass] = useState('password')
  const [confirm, setConfirm] = useState('password')
  const [password, setPassword] = useState('')
  const [email, setEmail] = useState('')
  const [confirmpassword, setConfirmpassword] = useState('')
  const Nav = useNavigate()

  const infoArray = {
    email: '',
    password: '',
    confirmpassword: ''
  }
  const SignUp  = async()=> {
    if(email ==='' || password === '') {
    alert('email and password required')
    return
  } else if(password!== confirmpassword){
    alert('passwords do not match')
    return
  } else {
    infoArray.email = email
    infoArray.password = password
    infoArray.confirmpassword = confirmpassword

    try {
      const response = await axios.post('http://localhost:8000/auth/signup/', infoArray)
      console.log('Sign Up successful:', response.data)
      setEmail('')
      setPassword('')
      setConfirmpassword('')
      console.log(infoArray)

      // Handle successful sign-up (e.g., navigate to a different page)
      // navigate('/some-other-page')
    } catch (error) {
      console.error('Error during sign-up:', error)
      alert('Sign in failed. Please try again.')
    }
  }
    
  }

  
  

  
  return (
    <div className="Signup_Container">
      <section className="White_Section">
        <span><PiDiamondsFourFill /> EchoCart</span>
        <h1>Welcome To EchoCart</h1>
        <article>
          <span>Registered User?</span>
          <p onClick={()=> Nav('/auth/signin')}>Sign In</p>
        </article>
        <label htmlFor="email">Email</label>
        <div className="Input_Container" tabIndex={0}>
          <input type="text" value={email}  onChange={(e)=>setEmail(e.target.value)} placeholder="input your  email" />
        </div>
        <label htmlFor="password">password</label>
        <div className="Input_Container" tabIndex={0}>
          <input type={pass} value={password} onChange={(e)=> setPassword(e.target.value)} placeholder="input your password" />
          {
            show ? <p onClick={() => {
              setPass('password')
              setShow(false)
            }
            }><IoEyeOff /></p> : <p onClick={() => {
              setPass('text')
              setShow(true)
            }
            }><IoEye /></p>
          }
        </div>
        <label htmlFor="confirm-password">confirm password</label>
        <div className="Input_Container" tabIndex={0}>
          <input type={confirm} value={confirmpassword} onChange={(e)=>setConfirmpassword(e.target.value)} placeholder="confirm your password" />
          {
            show1 ? <p onClick={() => {
              setConfirm('password')
              setShow1(false)
            }
            }><IoEyeOff /></p> : <p onClick={() => {
              setConfirm('text')
              setShow1(true)
            }
            }><IoEye /></p>
          }
        </div>
        <div onClick={SignUp} className="Signup_Btn">Sign Up</div>

      </section>
      <section className="Blue_Section">
        <span><PiDiamondsFourFill /> EchoCart</span>

      </section>
    </div>
  )
}