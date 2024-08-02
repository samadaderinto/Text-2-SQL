import { PiDiamondsFourFill } from "react-icons/pi"
import { useState } from "react"
import { IoEye, IoEyeOff } from 'react-icons/io5'

// import { useNavigate } from "react-router-dom"
export const Newpassword = () => {
    

    // const Nav = useNavigate()
  const [show, setShow] = useState(false)
  const [pass, setPass] = useState('password')
  const [confirm, setConfirm ] = useState('password')
  const [Show2, setShow2 ] = useState(false)
  const [value, setValue] = useState('')
  const [class1, setClass1] = useState('')
  const [class2, setClass2] = useState('')
  const [class3, setClass3] = useState('')
  const [class4, setClass4] = useState('')
  const [check1, setCheck1] = useState(false)
  const [check2, setCheck2] = useState(false)
  const [check3, setCheck3] = useState(false)
  const [strength, setStrength] = useState('')



  const checkStrength = (password: string) => {
    // Regular expressions to check for special characters and digits
    const specialCharsRegex = /[!@#$%&*]/;
    const digitsRegex = /[0-9]/;
  
    // Check for special characters
    if (specialCharsRegex.test(password)) {
      setCheck1(true);
      console.log(check1);
    }
  
    // Check for password length
    if (password.length >= 8) {
      setCheck3(true);
      console.log(check3);
    }
  
    // Check for digits
    if (digitsRegex.test(password)) {
      setCheck2(true);
      console.log(check2);
    }

    if (check1 || check2 || check3) {
        class1 !== 'filled_div_green'? setClass1('filled_div_green'): null
    }  if(check1 && check2 || check1 && check3 || check2 && check3) {
        class2 !== 'filled_div_green'? setClass2('filled_div_green'): null
    } if(check1 && check2 && check3) {
        class3 !== 'filled_div_green'? setClass3('filled_div_green'): null
        class4 !== 'filled_div_green'? setClass4('filled_div_green'): null
    }
}

const Qualified = ()=> {
if(class3 === '') {
    setStrength('weak')
} else if(class1 === '') {
    setStrength('')
} else if (class3 !== ''){
    setStrength('strong')
    console.log(strength)
}
}


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
                Qualified()
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
            <span className={ class4}></span>


          {
            strength === 'weak'? <h3 className="Red_color">weak</h3>: strength === 'strong'? <h3>strong</h3>: <h3></h3>
          }
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

