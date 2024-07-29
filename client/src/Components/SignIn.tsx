import { PiDiamondsFourFill } from 'react-icons/pi'
import { useNavigate } from 'react-router-dom'
const SignIn = () => {
  const Nav = useNavigate()
  return (
    <div className="Signup_Container">
        <section className="White_Section">
            <span><PiDiamondsFourFill/> EchoCart</span>
            <h1>Welcome Back, To EchoCart</h1>
            <article>New User? <p onClick={()=> Nav('/SignUp')}>Create an account</p></article>
            <label htmlFor="email">Email</label>
            <input type="text" placeholder="input your registered email" />
            <label htmlFor="email">password</label>
            <input type="text" placeholder="input your password" />
            <div className="Login_Btn">LOGIN</div>

        </section>
        <section className="Blue_Section">
        <span><PiDiamondsFourFill/> EchoCart</span>

        </section>
    </div>
  )
}

export default SignIn