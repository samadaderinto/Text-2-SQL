import { useNavigate } from "react-router-dom"
import { PiDiamondsFourFill } from "react-icons/pi"
import { FaArrowLeft } from 'react-icons/fa6'
import { useState, useEffect } from "react"
import axios from "axios"
import { API_BASE_URL } from "../utils/api"



export const Forgotpassword = () => {
  const [pop, setPop] = useState(false)
  const [email, setEmail] = useState('')
    const Nav = useNavigate()


    const Reset = async()=> {
     
      try {
        if(email !== '') {
          const data = JSON.stringify({email});
          const Response =  await axios.post(`${API_BASE_URL}/auth/reset-password/request/`, data)
          console.log(Response.data)
        }
        

      } catch (error) {
      
       
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

  
              <span onClick={()=> setPop(false)} className="Login_Btn">Go Back</span>

            </div>
          </section>
          ): null
        }
    </div>
  )
}
