// import {useState} from 'react'

import { useNavigate } from "react-router-dom"
import axios from "axios"
import { API_BASE_URL } from "../utils/api"

export const Logout = () => {

  const nav = useNavigate()

  const handleLogout = async () => {
    const refresh = localStorage.getItem('refresh')
    const access = localStorage.getItem('access')
    const data = JSON.stringify({ refresh });

    try {

      const response = await axios.post(`${API_BASE_URL}/auth/logout/`, data, {
        headers: {
          Authorization: `Bearer ${access}`,
        },
      })
      if (response.status == 205) {
        nav('/auth/signin/')
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
            nav(-1)
          }} className="White_btn">No</span>
        </div>
      </article>
    </div>
  )
}
