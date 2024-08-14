import { useState } from 'react';
import { PiDiamondsFourFill } from 'react-icons/pi';
import { IoEye, IoEyeOff } from 'react-icons/io5';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { API_BASE_URL } from '../utils/api';

export const SignIn = () => {
  const Nav = useNavigate();

  const [formState, setFormState] = useState({
    show: false,
    pass: 'password',
    email: '',
    password: ''
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormState({ ...formState, [e.target.name]: e.target.value });
  };

  const togglePasswordVisibility = () => {
    setFormState({
      ...formState,
      show: !formState.show,
      pass: formState.show ? 'password' : 'text',
    });
  };

  const SignIn = async () => {
    const { email, password } = formState;

    if (email === '' || password === '') {
      toast.error('Email and password are required');
      return;
    }

    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login/`, {
        email,
        password,
      });
      
     
      const { access, refresh } = response.data.token;

      localStorage.setItem('refreshToken', refresh);
      localStorage.setItem('accessToken', access);


      setFormState({
        show: false,
        pass: 'password',
        email: '',
        password: ''
      });

      toast.success('Sign in successful! Redirecting to dashboard...');
      Nav('/dashboard'); 
    } catch (error) {
      console.error('Error during sign-in:', error);
      toast.error('Sign in failed. Please try again.');
    }
  };

  return (
    <div className="Signup_Container">
      <section className="White_Section">
        <span><PiDiamondsFourFill /> EchoCart</span>
        <h1>Welcome Back, To EchoCart</h1>
        <article>
          <span>New User?</span>
          <p onClick={() => Nav('/auth/signup')}>Create an account</p>
        </article>
        <label htmlFor="email">Email</label>
        <div className="Input_Container" tabIndex={0}>
          <input
            type="text"
            id="email"
            name="email"
            value={formState.email}
            onChange={handleChange}
            placeholder="Input your registered email"
          />
        </div>
        <label htmlFor="password">Password</label>
        <div className="Input_Container" tabIndex={0}>
          <input
            type={formState.pass}
            id="password"
            name="password"
            value={formState.password}
            onChange={handleChange}
            placeholder="Input your password"
          />
          {formState.show ? (
            <p onClick={togglePasswordVisibility}>
              <IoEyeOff />
            </p>
          ) : (
            <p onClick={togglePasswordVisibility}>
              <IoEye />
            </p>
          )}
        </div>
        <p onClick={() => Nav('/auth/forgot-password')}>Forgot password?</p>
        <div className="Bottom_Container">
          <div onClick={SignIn} className="Login_Btn">LOGIN</div>
        </div>
      </section>
      <section className="Blue_Section">
        <span><PiDiamondsFourFill /> EchoCart</span>
      </section>
    </div>
  );
};
