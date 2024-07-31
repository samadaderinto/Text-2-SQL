// import './App.css'
import Dashboard from './Components/Dashboard'
import SignIn from './Components/SignIn'
import Signup from './Components/Signup'
import Forgotpassword from './Components/Forgotpassword'
import Newpassword from './Components/Newpassword'
import './SCSS/Main.scss'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

function App() {

  return (
    <>
    
     <BrowserRouter>
     
     <Routes>
      <Route path='/' element={<Dashboard/>}/>

      <Route path='auth/signup' element={<Signup/>}/>
      <Route path='auth/signin' element={<SignIn/> }/>
      <Route path='auth/forgot-password' element={<Forgotpassword/>}/>
      <Route path='auth/new-password' element={<Newpassword/>}/>
     </Routes>
     </BrowserRouter>
    </>
  )
}

export default App
