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
      <Route path='SignUp' element={<Signup/>}/>
      <Route path='SignIn' element={<SignIn/> }/>
      <Route path='ForgotPassword' element={<Forgotpassword/>}/>
      <Route path='Newpassword' element={<Newpassword/>}/>
     </Routes>
     </BrowserRouter>
    </>
  )
}

export default App
