import { PiDiamondsFourFill } from "react-icons/pi";
import { useState } from "react";
import { IoEye, IoEyeOff } from 'react-icons/io5';
import axios from "axios";
import { API_BASE_URL } from "../utils/api";

export const Newpassword = () => {
  const [formState, setFormState] = useState({
    showPassword: false,
    showConfirm: false,
    passwordType: 'password',
    confirmType: 'password',
    passwordValue: '',
    confirmPasswordValue: '',
    email: '',
    strength: '',
    class1: '',
    class2: '',
    class3: '',
    class4: '',
    check1: false,
    check2: false,
    check3: false
  });

  const checkStrength = (password: string) => {
    const specialCharsRegex = /[!@#$%&*]/;
    const digitsRegex = /[0-9]/;

    let newCheck1 = specialCharsRegex.test(password);
    let newCheck2 = digitsRegex.test(password);
    let newCheck3 = password.length >= 8;

    setFormState(prevState => {
      const class1 = newCheck1 ? 'filled_div_green' : '';
      const class2 = (newCheck1 && (newCheck2 || newCheck3)) ? 'filled_div_green' : '';
      const class3 = (newCheck1 && newCheck2 && newCheck3) ? 'filled_div_green' : '';
      const class4 = (newCheck1 && newCheck2 && newCheck3) ? 'filled_div_green' : '';

      return {
        ...prevState,
        check1: newCheck1,
        check2: newCheck2,
        check3: newCheck3,
        class1,
        class2,
        class3,
        class4,
        strength: (newCheck1 && newCheck2 && newCheck3) ? 'strong' : (newCheck1 || newCheck2 || newCheck3) ? 'weak' : ''
      };
    });
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;

    setFormState(prevState => ({
      ...prevState,
      [name]: value,
      ...(name === 'passwordValue' && { passwordValue: value }),
      ...(name === 'confirmPasswordValue' && { confirmPasswordValue: value })
    }));

    if (name === 'passwordValue') {
      checkStrength(value);
    }
  };

  const togglePasswordVisibility = (field: 'password' | 'confirm') => {
    setFormState(prevState => ({
      ...prevState,
      [`show${field.charAt(0).toUpperCase() + field.slice(1)}`]: !prevState[`show${field.charAt(0).toUpperCase() + field.slice(1)}`],
      [`${field}Type`]: prevState[`show${field.charAt(0).toUpperCase() + field.slice(1)}`] ? 'password' : 'text'
    }));
  };

  const Reset = async () => {
    const { email, passwordValue } = formState;

    try {
      const response = await axios.post(`${API_BASE_URL}/auth/reset-password/reset/`, { email, password: passwordValue });
      console.log(response.data);
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div className="Newpassword_Container">
      <section className="Newpassword_White">
        <span><PiDiamondsFourFill /> EchoCart</span>
        <h1>Create New Password</h1>
        <label htmlFor="email">Email</label>
        <input
          type="email"
          name="email"
          value={formState.email}
          onChange={handleInputChange}
          id="email"
          placeholder="input email"
        />
        <label htmlFor="passwordValue">Password</label>
        <div className="Input_Container" tabIndex={0}>
          <input
            type={formState.passwordType}
            name="passwordValue"
            value={formState.passwordValue}
            onChange={handleInputChange}
            id="password"
            placeholder="input your password"
          />
          <p onClick={() => togglePasswordVisibility('password')}>
            {formState.showPassword ? <IoEyeOff /> : <IoEye />}
          </p>
        </div>
        <h2>Min. of 8 characters with a combination of letters and numbers</h2>
        <div className="Password_strength">
          <span className={formState.class1}></span>
          <span className={formState.class2}></span>
          <span className={formState.class3}></span>
          <span className={formState.class4}></span>
          {formState.strength && <h3 className={formState.strength === 'weak' ? 'Red_color' : ''}>{formState.strength}</h3>}
        </div>
        <label htmlFor="confirmPasswordValue">Confirm Password</label>
        <div className="Input_Container" tabIndex={0}>
          <input
            type={formState.confirmType}
            name="confirmPasswordValue"
            value={formState.confirmPasswordValue}
            onChange={handleInputChange}
            id="confirm"
            placeholder="confirm password"
          />
          <p onClick={() => togglePasswordVisibility('confirm')}>
            {formState.showConfirm ? <IoEyeOff /> : <IoEye />}
          </p>
        </div>
        <div onClick={Reset} className="Login_Btn">Create Password</div>
      </section>
      <section className="Newpassword_Blue">
        <h1>Easiest Way To Manage Your Store</h1>
      </section>
    </div>
  );
};
