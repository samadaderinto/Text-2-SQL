import { PiDiamondsFourFill } from "react-icons/pi"
import { useState } from "react"
import { IoEye, IoEyeOff } from 'react-icons/io5'

// import { useNavigate } from "react-router-dom"
const Newpassword = () => {
    const checkStrength = (password: string) => {
        if(password.includes('!'|| '@' || '#' || '$' || '%' ||'&' || '*' )) {
            setStrength(strength + 1);
            console.log(strength)
        // }  if ( password.length >= 8){
        //      setStrength(strength + 1);
        //      console.log(strength)
        } if( password.includes('0' || '1' || '2' || '3' || '4'|| '5' || '6' || '7' || '8' || '9')){
            setStrength(strength + 1);
            console.log(strength)
            
        } if(password.length === 0) {
            setStrength(0)

        } 

        if (strength >= 0) {
            class1 !== 'filled_div'? setClass1('filled_div'): null
        }  if(strength >= 2 ) {
            class2 !== 'filled_div'? setClass2('filled_div'): null
        } if(strength >= 3) {
            class3 !== 'filled_div'? setClass3('filled_div'): null
            class4 !== 'filled_div'? setClass4('filled_div'): null
        }
    }

    // const Nav = useNavigate()
  const [show, setShow ] = useState(false)
  const [pass, setPass ] = useState('password')
  const [confirm, setConfirm ] = useState('password')
  const [Show2, setShow2 ] = useState(false)
  const [strength, setStrength] = useState(0)
  const [value, setValue] = useState('')
  const [class1, setClass1] = useState('')
  const [class2, setClass2] = useState('')
  const [class3, setClass3] = useState('')
  const [class4, setClass4] = useState('')

  return (
    <div className="Newpassword_Container">
        <section className="Newpassword_White">
        <span><PiDiamondsFourFill/> EchoCart</span>
        <h1>Create New Password</h1>
        <label htmlFor="password">password</label>
        <div className="Input_Container" tabIndex={0}>
             <input type={pass} onChange={(e)=>{
                setValue(e.target.value) 
                checkStrength(value)
             }} value={value} id="password" placeholder="input your password" />
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

            <h2>Min. of 8 characters with a combination of letters and numbers</h2>
            <div className="Password_strength">
              
            <span className={class1}></span>
                <span className={class2}></span>
                <span className={class3}></span>
                <span className={class4}></span>

          
                <h3>strong</h3>
            </div>

            <label htmlFor="confirm">confirm password</label>
            <div className="Input_Container"  tabIndex={0}>
            <input type={confirm} id="confirm" placeholder="confirm password" />
            {
              Show2? <p onClick={()=>{ 
                setConfirm('password')
                 setShow2(false)}
                }><IoEyeOff/></p> : <p onClick={()=> {
                  setConfirm('text')
                  setShow2(true)}
                }><IoEye/></p>
            }
            
            </div>

            <div className="Login_Btn">LOGIN</div>


        </section>
        <section className="Newpassword_Blue">
            <h1>Easiest Way To Manage Your Store</h1>
        </section>
    </div>
  )
}

export default Newpassword