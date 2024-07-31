import { useNavigate } from "react-router-dom"
import { PiDiamondsFourFill } from "react-icons/pi"
import { FaArrowLeft } from 'react-icons/fa6'


export const Forgotpassword = () => {
    const Nav = useNavigate()
  return (
    <div className="Forgot_Container">
        <section className="Forgot_White">
        <span><PiDiamondsFourFill/> EchoCart</span>
        <p onClick={()=> Nav('/auth/sign-in')}><FaArrowLeft/></p>
        <h1>Forgot Your Password?</h1>
        <h3>Send your email address to reset password & make new password</h3>
        <label htmlFor="email">Email</label>
            <div className="Input_Container" tabIndex={0}>
             <input type="text" placeholder="input your registered email" />
            </div>
            <div className="Login_Btn" onClick={()=> Nav('/auth/new-password')}>LOGIN</div>
        </section>
        <section className="Forgot_Blue">
            <h1>Easiest Way To Manage Your Store</h1>
        </section>
    </div>
  )
}
