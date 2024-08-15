// import {useState} from 'react'

import { useNavigate } from "react-router-dom"
import axios from "axios"

export const Logout = () => {

  const Nav = useNavigate()



  const handleLogout = async () => {


    const refresh = localStorage.getItem('refreshToken')
    const data = JSON.stringify({ refresh });
    try {

      const response = await axios.post('http://localhost:8000/auth/logout/', data)
      if (response.status == 205) {
        Nav('/auth/signin')
      }

    } catch (error) {

      console.log(error)
    }
  }


  return (
    <div className="Logout_Container">
      <article>
        <h1>Log Out?</h1>
        <div>
          <span onClick={handleLogout} className="Blue_btn">Yes</span>
          <span onClick={() => {
            Nav('/dashboard')
            window.location.reload()
          }} className="White_btn">No</span>
        </div>
      </article>
    </div>
  )
}
