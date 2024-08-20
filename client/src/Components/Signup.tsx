import { useState } from 'react';
import { PiDiamondsFourFill } from 'react-icons/pi';
import { IoEye, IoEyeOff } from 'react-icons/io5';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../utils/api';
import { toast } from 'react-toastify';



export const Signup = () => {
  const [pop, setPop] = useState(false)
  const [formState, setFormState] = useState({
    show: false,
    show1: false,
    pass: 'password',
    confirm: 'password',
    password: '',
    email: '',
    confirmpassword: '',
  });

  const [errors, setErrors] = useState({
    email: '',
    password: '',
    confirmpassword: '',
  });

  const Nav = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;

    // Update form state
    setFormState({ ...formState, [name]: value });

    // Perform real-time validation
    let errorMessages = { ...errors };

    if (name === 'email') {
      if (!value) {
        errorMessages.email = 'Email is required';
      } else {
        errorMessages.email = ''; // Clear error when valid
      }
    }

    if (name === 'password') {
      if (!value) {
        errorMessages.password = 'Password is required';
      } else if (!validatePassword(value)) {
        errorMessages.password = 'Password must be at least 8 characters long, include one uppercase letter, one lowercase letter, one digit, and one special character';
      } else {
        errorMessages.password = ''; // Clear error when valid
      }

      // Also validate confirm password if it's already entered
      if (formState.confirmpassword && value !== formState.confirmpassword) {
        errorMessages.confirmpassword = 'Passwords do not match';
      } else {
        errorMessages.confirmpassword = ''; // Clear error when valid
      }
    }

    if (name === 'confirmpassword') {
      if (!value) {
        errorMessages.confirmpassword = 'Confirmation password is required';
      } else if (value !== formState.password) {
        errorMessages.confirmpassword = 'Passwords do not match';
      } else {
        errorMessages.confirmpassword = ''; // Clear error when valid
      }
    }

    // Update error state
    setErrors(errorMessages);
  };


  const validatePassword = (password: string) => {
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return passwordRegex.test(password);
  };

  const togglePasswordVisibility = () => {
    setFormState({
      ...formState,
      show: !formState.show,
      pass: formState.show ? 'password' : 'text',
    });
  };

  const toggleConfirmPasswordVisibility = () => {
    setFormState({
      ...formState,
      show1: !formState.show1,
      confirm: formState.show1 ? 'password' : 'text',
    });
  };

  const validateForm = () => {
    const { email, password, confirmpassword } = formState;
    let valid = true;
    const newErrors = { email: '', password: '', confirmpassword: '' };

    if (!email) {
      newErrors.email = 'Email is required';
      valid = false;
    }
    if (!password) {
      newErrors.password = 'Password is required';
      valid = false;
    } else if (!validatePassword(password)) {
      newErrors.password = 'Password must be at least 8 characters long, include one uppercase letter, one lowercase letter, one digit, and one special character';
      valid = false;
    }
    if (password !== confirmpassword) {
      newErrors.confirmpassword = 'Passwords do not match';
      valid = false;
    }

    setErrors(newErrors);
    return valid;
  };

  const SignUp = async () => {
    if (validateForm()) {
      try {
        const { email, password } = formState;
        const data = JSON.stringify({ email, password });

        const response = await axios.post(`${API_BASE_URL}/auth/signup/`, data, {
          headers: {
            'Content-Type': 'application/json',
          },
        });

        console.log(response.data);

        // Clear form and show success message
        setFormState({
          ...formState,
          email: '',
          password: '',
          confirmpassword: '',
        });
        toast.success('Sign up successful! A verification link has been sent to your email address.');
        // setPop(true);

      } catch (error: any) {
        if (error.response && error.response.status === 400) {
          const errorData = error.response.data;
          console.log(errorData)

          // Check if the error is related to email already existing
          if (errorData.email && errorData.email.includes('exists')) {
            setErrors({ ...errors, email: 'Email already exists. Please use a different email.' });
            toast.error('Email already exists. Please use a different email.');
          } else {
            setErrors({ ...errors, ...errorData });
            toast.error('Invalid signup details, please check your input.');
          }
        } else {
          toast.error('Sign up failed. Please try again.');
        }
      }
    }

  };

  return (
    <div className="Signup_Container">
      <section className="White_Section">
        <span><PiDiamondsFourFill /> EchoCart</span>
        <h1>Welcome To EchoCart</h1>
        <article>
          <span>Registered User?</span>
          <p onClick={() => Nav('/auth/signin')}>Sign In</p>
        </article>
        <label htmlFor="email">Email</label>
        <div className="Input_Container" tabIndex={0}>
          <input
            type="text"
            name="email"
            value={formState.email}
            onChange={handleChange}
            placeholder="Input your email"
          />
          {errors.email && <div className="error">{errors.email}</div>}
        </div>
        <label htmlFor="password">Password</label>
        <div className="Input_Container" tabIndex={0}>
          <input
            type={formState.pass}
            name="password"
            value={formState.password}
            onChange={handleChange}
            placeholder="Input your password"
          />
          {errors.password && <div className="error">{errors.password}</div>}
          <p onClick={togglePasswordVisibility}>
            {formState.show ? <IoEyeOff /> : <IoEye />}
          </p>
        </div>
        <label htmlFor="confirm-password">Confirm Password</label>
        <div className="Input_Container" tabIndex={0}>
          <input
            type={formState.confirm}
            name="confirmpassword"
            value={formState.confirmpassword}
            onChange={handleChange}
            placeholder="Confirm your password"
          />
          {errors.confirmpassword && <div className="error">{errors.confirmpassword}</div>}
          <p onClick={toggleConfirmPasswordVisibility}>
            {formState.show1 ? <IoEyeOff /> : <IoEye />}
          </p>
        </div>
        <div onClick={SignUp} className="Signup_Btn">Sign Up</div>
      </section>
      <section className="Blue_Section">
        <span><PiDiamondsFourFill /> EchoCart</span>
      </section>
      {

        pop ? (
          <article className='Signup_Pop_Container'>
            <span className='Popup_span'>
              <h4 onClick={() => setPop(false)} className='Signup_Popup_Cancel'>X</h4>
              <h5>A verification mail has been sent to your email address.</h5>

            </span>
          </article>

        ) : null
      }
    </div>
  );
};
