import { useNavigate } from "react-router-dom";
import { PiDiamondsFourFill } from "react-icons/pi";
import { FaArrowLeft } from 'react-icons/fa6';
import { useState } from "react";
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import api from "../utils/api";
import { notifyApiError } from "../utils/api-errors";

export const ForgotPassword = () => {
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

      const response = await api.post(`/auth/reset-password/request/`, { email });

      if (response.status === 200) {
        toast.success('Password reset email sent successfully!');
        setPop(true);
      }
    } catch (error) {
      notifyApiError(error, "Could not request a password reset. Please try again.");
    }
  };

  return (
    <div className="Forgot_Container">
      <section className="White_Section">
        <span><PiDiamondsFourFill /> EchoCart</span>

        <button type="button" className="Back_Link" onClick={() => nav('/auth/signin')}>
          <FaArrowLeft /> Back to sign in
        </button>

        <h1>Forgot password?</h1>
        <p className="Subtitle">No stress — we'll send a secure reset link to your email.</p>

        <label htmlFor="email">Email address</label>
        <div className="Input_Container" tabIndex={0}>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your registered email"
          />
        </div>

        <div className="Bottom_Container">
          <div className="Login_Btn" onClick={Reset}>Send reset link</div>
        </div>
      </section>

      <section className="Blue_Section">
        <span><PiDiamondsFourFill /> EchoCart</span>
      </section>

      {pop && (
        <section className="Forgot_Pop">
          <div>
            <h3>Password reset sent</h3>
            <p>
              We’ve sent a reset email to <strong>{email}</strong> with instructions to get back into your account.
            </p>
            <span onClick={() => setPop(false)} className="Login_Btn">Go back</span>
          </div>
        </section>
      )}
    </div>
  );
};
