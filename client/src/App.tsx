import { Routes, Route } from 'react-router-dom'
import './styles/main.scss'


import { PageNotFound } from './pages/PageNotFound'
import { SignIn } from './components/SignIn'
import { Signup } from './components/Signup'
import { ForgotPassword } from './components/ForgotPassword'
import { Dashboard } from './components/Dashboard'
import { Orders } from './components/Orders'
import { Product } from './components/Product'
import { Settings } from './components/Settings'
import { Logout } from './components/Logout'
import { NewPassword } from './components/NewPassword'
import { Customers } from './components/Customers'
import { NewCustomer } from './components/NewCustomer'

import ProtectedRoute from './utils/hooks'

import Home from './pages/Home'
import Query from './components/Query'


import { Slide, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { NewProduct } from './components/NewProduct'







function App() {


  return (
    <>

      <ToastContainer
        position="bottom-right"
        autoClose={2600}
        hideProgressBar
        newestOnTop={false}
        closeOnClick
        pauseOnFocusLoss={false}
        pauseOnHover
        draggable={false}
        limit={3}
        transition={Slide}
        theme="light"
        toastClassName="App_Toast"
        bodyClassName="App_Toast_Body"
      />
      <Routes>

        <Route path='/' element={<Home />}></Route>
        <Route index path='/dashboard' element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path='/product' element={<ProtectedRoute><Product /></ProtectedRoute>} />
        <Route path='/product/add' element={<ProtectedRoute><NewProduct /></ProtectedRoute>} />
        <Route path='/orders' element={<ProtectedRoute><Orders /></ProtectedRoute>} />
        <Route path='/customers' element={<ProtectedRoute><Customers /></ProtectedRoute>} />
        <Route path='/customers/add' element={<ProtectedRoute><NewCustomer /></ProtectedRoute>} />
        <Route path='/settings' element={<ProtectedRoute><Settings /></ProtectedRoute>} />
        <Route path='/query' element={<ProtectedRoute><Query /></ProtectedRoute>} />



        <Route path='logout' element={<ProtectedRoute><Logout /></ProtectedRoute>} />
        <Route path='auth/signup' element={<Signup />} />
        <Route path='auth/signin' element={<SignIn />} />
        <Route path='auth/forgot-password' element={<ForgotPassword />} />
        <Route path='auth/reset-password/:uidb64/:token' element={<NewPassword />} />

        <Route path="*" element={<PageNotFound />} />
      </Routes>


    </>
  )
}

export default App
