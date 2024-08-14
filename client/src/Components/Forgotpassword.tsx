import { useNavigate } from "react-router-dom"
import { PiDiamondsFourFill } from "react-icons/pi"
import { FaArrowLeft } from 'react-icons/fa6'
import { useState } from "react"
import axios from "axios"


export const Forgotpassword = () => {
  const [pop, setPop] = useState(false)
  const [email, setEmail] = useState('')
    const Nav = useNavigate()


    const Reset = async()=> {
     
      try {
        if(email !== '') {
          const Response =  await axios.post('http://localhost:8000/auth/reset-password/request/', email)
          console.log(Response.data)
          alert('successful')
        }

      } catch (error) {
        alert('failed')
        console.log(error)
      }

    }


  return (
    <div className="Forgot_Container">
        <section className="Forgot_White">
        <span><PiDiamondsFourFill/> EchoCart</span>
        <p onClick={()=> Nav('/auth/signin')}><FaArrowLeft/></p>
        <h1>Forgot Your Password?</h1>
        <h3>Send your email address to reset password & make new password</h3>
        <label htmlFor="email">Email</label>
            <div className="Input_Container" tabIndex={0}>
             <input type="text" value={email} onChange={(e)=>setEmail(e.target.value)} placeholder="input your registered email" />
            </div>
            <div className="Login_Btn" onClick={()=> {
            Reset()
              {
                email!== ''?
                setPop(true): alert('No Valid Email')}}}>Reset Password</div>
        </section>
        <section className="Forgot_Blue">
            <h1>Easiest Way To Manage Your Store</h1>
        </section>

        {
          pop? (
            <section className="Forgot_Pop">
            <div>
              <h3>Password Reset</h3>
              <p>We have sent an email to <h4>{email}</h4>
                with instructions to reset your password.please
                check your inbox to get started.
              </p>
              <span onClick={()=>Nav('/auth/new-password')} className="Login_Btn">Go Back</span>
            </div>
          </section>
          ): null
        }
    </div>
  )
}
