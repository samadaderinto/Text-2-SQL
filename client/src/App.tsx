import { BrowserRouter, Routes, Route } from 'react-router-dom'

import Home from './pages/home'
import PageNotFound from './pages/PageNotFound'

import { SignIn } from './Components/SignIn'
import { Signup } from './Components/Signup'
import { Forgotpassword } from './Components/Forgotpassword'
import { Newpassword } from './Components/Newpassword'
import { Dashboard } from './Components/Dashboard'


import './SCSS/Main.scss'



function App() {

  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path='/' element={<Home />}>
            <Route index path='/dashboard' element={<Dashboard />} />
            <Route path='/product' element={<SignIn />} />
            <Route path='/orders' element={<SignIn />} />
            <Route path='/customers' element={<SignIn />} />
          </Route>

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
