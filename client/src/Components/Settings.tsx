import { useEffect, useState } from "react";
import axios from "axios";
import Sidebar from '../layouts/SideBar';
import { API_BASE_URL } from "../utils/api";
import { useNavigate } from "react-router-dom";
import { Header } from "../layouts/Header";

export const Settings = () => {
  const [active, setActive] = useState('General');
  const [formData, setFormData] = useState({
    storeName: '',
    storeEmail: '',
    currency: '$',
    adminName: '',
    adminEmail: '',
    password: '',
    emailNotifications: false,
    smsNotifications: false,
  });

  const Nav = useNavigate();

  const access = localStorage.getItem('access')


  useEffect(() => {
    const fetchAdminData = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/settings/admin/get/`, {
          headers: {
            Authorization: `Bearer ${access}`,
          },
        });
        const adminData = response.data;

        setFormData((prevFormData) => ({
          ...prevFormData,
          adminName: adminData.adminName,
          adminEmail: adminData.adminEmail,
          password: adminData.password
        }));
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    const fetchStoreData = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/settings/store/get/`, {
          headers: {
            Authorization: `Bearer ${access}`,
          },
        });
        const storeData = response.data;

        setFormData((prevFormData) => ({
          ...prevFormData,
          storeName: storeData.storeName,
          storeEmail: storeData.storeEmail,
          currency: storeData.currency
        }));
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    const fetchNotificationData = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/settings/notifications/get/`, {
          headers: {
            Authorization: `Bearer ${access}`,
          },
        });
        const notificationData = response.data;

        setFormData((prevFormData) => ({
          ...prevFormData,
          emailNotifications: notificationData.emailNotifications || false,
          smsNotifications: notificationData.smsNotifications || false,
        }));


      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchAdminData();
    fetchStoreData();
    fetchNotificationData();
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
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
        response = await axios.put(`${API_BASE_URL}/settings/store/update/`, {
          name: formData.storeName,
          email: formData.storeEmail,
          currency: formData.currency,
        }, {
          headers: {
            Authorization: `Bearer ${access}`,
          },
        });
      } else if (active === 'Account') {
        // API endpoint for updating account information
        response = await axios.put(`${API_BASE_URL}/settings/admin/update/`, {
          adminName: formData.adminName,
          adminEmail: formData.adminEmail,
          password: formData.password,
        }, {
          headers: {
            Authorization: `Bearer ${access}`,
          },
        });
      } else if (active === 'Notifications') {
        // API endpoint for updating notification settings
        response = await axios.put(`${API_BASE_URL}/api/settings/notifications/`, {
          emailNotifications: formData.emailNotifications,
          smsNotifications: formData.smsNotifications,
        }, {
          headers: {
            Authorization: `Bearer ${access}`,
          },
        });
      }

      alert('Settings updated successfully!');
    } catch (error) {
      console.error('Error updating settings:', error);
      alert('Failed to update settings.');
    }
  };

  return (
    <>
      <Header />
      <div className="Settings_Container">
        <Sidebar />
        <h1>Settings</h1>
        <ul>
          <li className={active === 'General' ? 'Active' : ''} onClick={() => setActive('General')}>General</li>
          <li className={active === 'Account' ? 'Active' : ''} onClick={() => setActive('Account')}>Account</li>
          <li className={active === 'Notifications' ? 'Active' : ''} onClick={() => setActive('Notifications')}>Notifications</li>
        </ul>

        <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
          {active === 'General' ? (
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
            </>
          ) : active === 'Account' ? (
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
                <p onClick={() => Nav("/auth/forgot-password")}>change password</p>
              </label>
              <input
                type="password"
                placeholder="password"
                id="password"
                name="password"
                readOnly
                value={formData.password}
              />
            </>
          ) : (
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
          )}
          <div>
            <span className="White_Btn">Cancel</span>
            <span className="Blue_Btn" onClick={handleSubmit}>Save Changes</span>
          </div>
        </form>
      </div>
    </>
  );
};
