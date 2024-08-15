import { useState } from "react";
import axios from "axios";
import Sidebar from '../layouts/SideBar'


export const Settings = () => {
  const [active, setActive] = useState('General');
  const [newpassword, setNewpassword] = useState(false);

  // State for form inputs
  const [formData, setFormData] = useState({
    storeName: '',
    storeEmail: '',
    currency: '$',
    adminName: '',
    adminEmail: '',
    password: '',
    oldPassword: '',
    newPassword: '',
    confirmPassword: '',
    emailNotifications: false,
    smsNotifications: false,
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value} = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async () => {
    try {
      let response;

      if (active === 'General') {
        // API endpoint for updating general information
        response = await axios.post('http://localhost:8000/api/settings/general/', {
          storeName: formData.storeName,
          storeEmail: formData.storeEmail,
          currency: formData.currency,
        });
      } else if (active === 'Account') {
        // API endpoint for updating account information
        response = await axios.post('http://localhost:8000/api/settings/account/', {
          adminName: formData.adminName,
          adminEmail: formData.adminEmail,
          password: formData.password,
        });
      } else if (active === 'Notifications') {
        // API endpoint for updating notification settings
        response = await axios.post('http://localhost:8000/api/settings/notifications/', {
          emailNotifications: formData.emailNotifications,
          smsNotifications: formData.smsNotifications,
        });
      }

     
      alert('Settings updated successfully!');
    } catch (error) {
      console.error('Error updating settings:', error);
      alert('Failed to update settings.');
    }
  };

  const handlePasswordChange = async () => {
    try {
      // API endpoint for changing password
      const response = await axios.post('http://localhost:8000/api/settings/change-password/', {
        oldPassword: formData.oldPassword,
        newPassword: formData.newPassword,
        confirmPassword: formData.confirmPassword,
      });

      console.log('Password Change Response:', response.data);
      alert('Password changed successfully!');
      setNewpassword(false); // Close the password change modal
    } catch (error) {
      console.error('Error changing password:', error);
      alert('Failed to change password.');
    }
  };

  return (
    <div className="Settings_Container">
      <Sidebar/>
      <h1>Settings</h1>
      <ul>
        <li className={active === 'General' ? 'Active' : ''} onClick={() => setActive('General')}>General</li>
        <li className={active === 'Account' ? 'Active' : ''} onClick={() => setActive('Account')}>Account</li>
        <li className={active === 'Notifications' ? 'Active' : ''} onClick={() => setActive('Notifications')}>Notifications</li>
      </ul>

      <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
        {
          active === 'General' ?
            <>
              <h3>General Information</h3>
              <label htmlFor="Store_Name">Store Name</label>
              <input
                type="text"
                placeholder="Input store Name"
                id="Store_Name"
                name="storeName"
                value={formData.storeName}
                onChange={handleInputChange}
              />
              <label htmlFor="Store_Email">Store Email</label>
              <input
                type="email"
                placeholder="Input store email"
                id="Store_Email"
                name="storeEmail"
                value={formData.storeEmail}
                onChange={handleInputChange}
              />
              <label htmlFor="currency">Currency</label>
              <select
                id="currency"
                name="currency"
                value={formData.currency}
                onChange={handleInputChange}
              >
                <option value="$">$</option>
                <option value="£">£</option>
                <option value="€">€</option>
              </select>
            </> : active === 'Account' ?
              <>
                <h3>Account Information</h3>
                <label htmlFor="Admin_Name">Admin Name</label>
                <input
                  type="text"
                  placeholder="Input Admin Name"
                  id="Admin_Name"
                  name="adminName"
                  value={formData.adminName}
                  onChange={handleInputChange}
                />
                <label htmlFor="Admin_Email">Email Address</label>
                <input
                  type="email"
                  placeholder="Input email"
                  id="Admin_Email"
                  name="adminEmail"
                  value={formData.adminEmail}
                  onChange={handleInputChange}
                />
                <label htmlFor="password">Password
                  <p onClick={() => setNewpassword(true)}>change password</p>
                </label>
                <input
                  type="password"
                  placeholder="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                />
              </> :
              <>
                <h3>Notifications</h3>
                <section className="Notify_Section">
                  <input
                    type="checkbox"
                    id="emailNotifications"
                    name="emailNotifications"
                    checked={formData.emailNotifications}
                    onChange={handleInputChange}
                  />
                  <p>Enable Email Notifications</p>
                  <input
                    type="checkbox"
                    id="smsNotifications"
                    name="smsNotifications"
                    checked={formData.smsNotifications}
                    onChange={handleInputChange}
                  />
                  <p>Enable SMS Notifications</p>
                </section>
              </>
        }
        <div>
          <span className="White_Btn">Cancel</span>
          <span className="Blue_Btn" onClick={handleSubmit}>Save Changes</span>
        </div>
      </form>

      {
        newpassword &&
        <div className="Settings_forgot_password">
          <section>
            <p onClick={() => setNewpassword(false)}>X</p>
            <h1>Change Password</h1>
            <label htmlFor="old_password">Old Password</label>
            <input
              type="password"
              placeholder="Old Password"
              id="old_password"
              name="oldPassword"
              value={formData.oldPassword}
              onChange={handleInputChange}
            />
            <label htmlFor="new_password">New Password</label>
            <input
              type="password"
              placeholder="New Password"
              id="new_password"
              name="newPassword"
              value={formData.newPassword}
              onChange={handleInputChange}
            />
            <label htmlFor="confirm_password">Confirm Password</label>
            <input
              type="password"
              placeholder="Confirm Password"
              id="confirm_password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleInputChange}
            />
            <span className="Update_Status" onClick={handlePasswordChange}>Update Password</span>
          </section>
        </div>
      }
    </div>
  );
};
