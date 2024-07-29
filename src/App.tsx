// import './App.css'
import Dashboard from './Components/Dashboard'
import SignIn from './Components/SignIn'
import Signup from './Components/SignUp'
import './SCSS/Signin.scss'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

function App() {

  return (
    <>
    
     <BrowserRouter>
     
     <Routes>
      <Route path='/' element={<Dashboard/>}/>
      <Route path='SignUp' element={<Signup/>}/>
      <Route path='SignIn' element={<SignIn/> }/>
     </Routes>
     </BrowserRouter>
    </>
  )
}

export default App
