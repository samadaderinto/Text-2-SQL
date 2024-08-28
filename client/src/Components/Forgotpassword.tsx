import { useNavigate } from "react-router-dom";
import { PiDiamondsFourFill } from "react-icons/pi";
import { FaArrowLeft } from 'react-icons/fa6';
import { useState } from "react";
import axios from "axios";
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import api from "../utils/api";

export const Forgotpassword = () => {
  const [pop, setPop] = useState(false);
  const [email, setEmail] = useState('');
  const nav = useNavigate();

  const validateEmail = (email: string) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  };

  const Reset = async () => {
    try {
      if (email === '') {
        toast.error('Please enter your email.');
        return;
      }

      if (!validateEmail(email)) {
        toast.error('Please enter a valid email address.');
        return;
      }

      const data = JSON.stringify({ email });
      const Response = await api.post(`/auth/reset-password/request/`, data);

      if (Response.status === 200) {
        toast.success('Password reset email sent successfully!');
        setPop(true);
      }
    } catch (error) {
      toast.error('Failed to send reset email. Please try again later.');
    }
  };

  return (
    <div className="Forgot_Container">
      <section className="Forgot_White">
        <span><PiDiamondsFourFill /> EchoCart</span>
        <p onClick={() => nav('/auth/signin')}><FaArrowLeft /></p>
        <h1>Forgot Your Password?</h1>
        <h3>Send your email address to reset your password & create a new one</h3>
        <label htmlFor="email">Email</label>
        <div className="Input_Container" tabIndex={0}>
          <input
            type="text"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Input your registered email"
          />
        </div>
        <div className="Login_Btn" onClick={Reset}>Reset Password</div>
      </section>
      <section className="Forgot_Blue">
        <h1>Easiest Way To Manage Your Store</h1>
      </section>

      {pop && (
        <section className="Forgot_Pop">
          <div>
            <h3>Password Reset</h3>
            <p>
              We have sent an email to <h4>{email}</h4>
              with instructions to reset your password. Please
              check your inbox to get started.
            </p>
            <span onClick={() => setPop(false)} className="Login_Btn">Go Back</span>
          </div>
        </section>
      )}
    </div>
  );
};
