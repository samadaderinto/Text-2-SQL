// import {useState} from 'react'

import { useNavigate } from "react-router-dom"
import axios from "axios"

export const Logout = () => {
    
    const Nav = useNavigate()

    
  const Storedtoken  = localStorage.getItem('token')


  const Logout = async()=> {

    
    const token = Storedtoken? JSON.parse(Storedtoken): null

    try {

      const response = await axios.post('http://localhost:8000/auth/logout/', token)
      alert('logout successful')
      console.log(response.data)
    } catch (error) {
      alert('logout failed')
      console.log(error)
    }
  }

  return (
<div className="Logout_Container">
          <article>
          <h1>Log Out?</h1>
          <div>
              <span onClick={Logout} className="Blue_btn">Yes</span>
              <span onClick={()=> {
                Nav('/dashboard')
                window.location.reload()
                }} className="White_btn">No</span>
          </div>
          </article>
      </div>
  )
}
