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
import { Header } from './layouts/Header'
// import { SideBar } from './layouts/SideBar'


import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { Logout } from './Components/Logout'
import ProtectedRoute from './utils/hooks'





function App() {

  return (
    <>
      <BrowserRouter>
        <Header />

        <Routes>
          <Route path='/' element={<Home />} />
          <Route index path='/dashboard' element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path='/product' element={<ProtectedRoute><Product /></ProtectedRoute>} />
          <Route path='/product/add' element={<ProtectedRoute><Newproduct /></ProtectedRoute>} />
          <Route path='/orders' element={<ProtectedRoute><Orders /></ProtectedRoute>} />
          <Route path='/customers' element={<ProtectedRoute><Customers /></ProtectedRoute>} />
          <Route path='/settings' element={<ProtectedRoute><Settings /></ProtectedRoute>} />
          

          <Route path='auth/signup' element={<Signup />} />
          <Route path='auth/signin' element={<SignIn />} />
          <Route path='auth/forgot-password' element={<Forgotpassword />} />
          <Route path='auth/reset-password/:mail' element={<Newpassword />} />
          <Route path='auth/logout' element={<ProtectedRoute><Logout /></ProtectedRoute>} />


          <Route path="*" element={<PageNotFound />} />
        </Routes>


      </BrowserRouter>
    </>
  )
}

export default App
