import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './SCSS/Main.scss'


import Home from './pages/home'
import PageNotFound from './pages/PageNotFound'

import { SignIn } from './Components/SignIn'
import { Signup } from './Components/Signup'
import { Forgotpassword } from './Components/Forgotpassword'
import { Newpassword } from './Components/Newpassword'
import { Dashboard } from './Components/Dashboard'
import { Orders } from './Components/Orders'
import { Customers } from './Components/Customers'
import { Product } from './Components/Product'
import { Settings } from './Components/Settings'
import { Newproduct } from './Components/Newproduct'
import { Header } from './layouts/Header'
import { SideBar } from './layouts/SideBar'
import { Logout } from './Components/Logout'







function App() {

  return (
    <>
    <Header/>
      <BrowserRouter>
    <SideBar/>

        <Routes>
          <Route path='/' element={<Home />}/>
            <Route index path='/dashboard' element={<Dashboard />} />
            <Route path='/product' element={<Product />} />
            <Route path='/product/new-product' element={<Newproduct />} />
            <Route path='/orders' element={<Orders />} />
            <Route path='/customers' element={<Customers />} />
            <Route path='/settings' element={<Settings />} />
            <Route path='/logout' element={<Logout/>} />
            
          <Route path='auth/signup' element={<Signup />} />
          <Route path='auth/signin' element={<SignIn />} />
          <Route path='auth/forgot-password' element={<Forgotpassword />} />
          <Route path='auth/new-password' element={<Newpassword />} />


          <Route path="*" element={<PageNotFound />}></Route>
        </Routes>
      </BrowserRouter>
    </>
  )
}

export default App
