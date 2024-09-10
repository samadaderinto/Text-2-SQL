import { Routes, Route } from 'react-router-dom'
import './SCSS/Main.scss'


import { PageNotFound } from './pages/PageNotFound'
import { SignIn } from './Components/SignIn'
import { Signup } from './Components/Signup'
import { Forgotpassword } from './Components/Forgotpassword'
import { Dashboard } from './Components/Dashboard'
import { Orders } from './Components/Orders'
import { Product } from './Components/Product'
import { Settings } from './Components/Settings'
import { Logout } from './Components/Logout'
import { NewPassword } from './Components/NewPassword'
import { NewProduct } from './Components/NewProduct'
import ProtectedRoute from './utils/hooks'
import Home from './pages/home'
import Query from './Components/Query'


import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { Customers } from './Components/Customers'
import { NewCustomer } from './Components/NewCustomer'







function App() {


  return (
    <>

      <ToastContainer />
      <Routes>
        
        <Route path='/' element={<Home/>}> 
          <Route index path='/dashboard' element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path='/product' element={<ProtectedRoute><Product /></ProtectedRoute>} /> 
          <Route path='/product/add' element={<ProtectedRoute><NewProduct /></ProtectedRoute>} />
          <Route path='/orders' element={<ProtectedRoute><Orders /></ProtectedRoute>} />
          <Route path='/customers' element={<ProtectedRoute><Customers /></ProtectedRoute>} />
          <Route path='/customers/add' element={<ProtectedRoute><NewCustomer /></ProtectedRoute>} />
          <Route path='/settings' element={<ProtectedRoute><Settings /></ProtectedRoute>} />
        </Route>

        <Route path='query' element={<ProtectedRoute><Query/></ProtectedRoute>} />

        <Route path='logout' element={<ProtectedRoute><Logout /></ProtectedRoute>} />
        <Route path='auth/signup' element={<Signup />} />
        <Route path='auth/signin' element={<SignIn />} />
        <Route path='auth/forgot-password' element={<Forgotpassword />} />
        <Route path='auth/reset-password/:mail' element={<NewPassword />} />



        <Route path="*" element={<PageNotFound />} />
      </Routes>


    </>
  )
}

export default App
