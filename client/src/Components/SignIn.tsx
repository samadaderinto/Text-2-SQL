import { useState } from 'react';
import { PiDiamondsFourFill } from 'react-icons/pi';
import { IoEye, IoEyeOff } from 'react-icons/io5';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import api from '../utils/api';
import { useEncryptJWT } from '../utils/hooks';
import { secretKey } from '../utils/constants';

export const SignIn = () => {
  const nav = useNavigate();

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

  const handleSignIn = async () => {
    const { email, password } = formState;

    if (email === '' || password === '') {
      toast.error('Email and password are required');
      return;
    }

    try {
      const response = await api.post(`/auth/login/`, {
        email,
        password,
      });

      const { token } = response.data;

      const encryptedAccessToken = useEncryptJWT(token.access, secretKey);
      const encryptedRefreshToken = useEncryptJWT(token.refresh, secretKey);

      localStorage.setItem('access', encryptedAccessToken);
      localStorage.setItem('refresh', encryptedRefreshToken);

      setFormState({
        show: false,
        pass: 'password',
        email: '',
        password: ''
      });

      toast.success('Sign in successful! Redirecting to dashboard...');
      nav('/dashboard');
    } catch (error: any) {
      console.log(error);

      if (error.response?.status === 403) {
        toast.error('Please verify your account before logging in.');
      } else {
        toast.error('Invalid user information. Please try again.');
      }
    }
  };

  return (
    <div className="Signup_Container">
      <section className="White_Section">
        <span><PiDiamondsFourFill /> EchoCart</span>
        <h1>Welcome Back, To EchoCart</h1>
        <article>
          <span>New User?</span>
          <p onClick={() => nav('/auth/signup')}>Create an account</p>
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
        <p onClick={() => nav('/auth/forgot-password')}>Forgot password?</p>
        <div className="Bottom_Container">
          <div onClick={handleSignIn} className="Login_Btn">LOGIN</div>
        </div>
      </section>
      <section className="Blue_Section">
        <span><PiDiamondsFourFill /> EchoCart</span>
      </section>
    </div>
  );
};
