import { useState } from 'react'
import { PiDiamondsFourFill } from 'react-icons/pi'
import { IoEye, IoEyeOff } from 'react-icons/io5'
import { useNavigate } from 'react-router-dom'


export const Signup = () => {
  const [show, setShow] = useState(false)
  const [show1, setShow1] = useState(false)
  const [pass, setPass] = useState('password')
  const [confirm, setConfirm] = useState('password')
  const Nav = useNavigate()

  const SignUp = ()=> {
    
  }
  http://localhost:8000/auth/signup/
//   {
//     "email": "k@mail.com",
//     "password": "deded"
// }
  
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
          <input type="text" placeholder="input your registered email" />
        </div>
        <label htmlFor="password">password</label>
        <div className="Input_Container" tabIndex={0}>
          <input type={pass} placeholder="input your password" />
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
          <input type={confirm} placeholder="confirm your password" />
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
        <div className="Signup_Btn">Sign Up</div>

      </section>
      <section className="Blue_Section">
        <span><PiDiamondsFourFill /> EchoCart</span>

      </section>
    </div>
  )
}