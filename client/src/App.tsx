import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './SCSS/Main.scss'


import Home from './pages/home'
import { PageNotFound } from './pages/PageNotFound'

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

import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';





function App() {

  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path='/' element={<Home />}/>
            <Route index path='/dashboard' element={<Dashboard />} />
            <Route path='/product' element={<Product />} />
            <Route path='/product/add' element={<Newproduct />} />
            <Route path='/orders' element={<Orders />} />
            <Route path='/customers' element={<Customers />} />
            <Route path='/settings' element={<Settings />} />
            
          <Route path='auth/signup' element={<Signup />} />
          <Route path='auth/signin' element={<SignIn />} />
          <Route path='auth/forgot-password' element={<Forgotpassword />} />
          <Route path='auth/reset-password/:mail' element={<Newpassword />} />


          <Route path="*" element={<PageNotFound />} />
        </Routes>


      </BrowserRouter>
    </>
  )
}

export default App
