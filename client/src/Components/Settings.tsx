import { useEffect, useState, useCallback } from "react";
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

  const navigate = useNavigate();
  const access = localStorage.getItem('access');

  const fetchData = useCallback(async (url: string, updateData: (data: any) => void) => {
    try {
      const response = await axios.get(url, {
        headers: { Authorization: `Bearer ${access}` },
      });
      updateData(response.data);
    } catch (error) {
      console.error(`Error fetching data from ${url}:`, error);
    }
  }, [access]);

  useEffect(() => {
    fetchData(`${API_BASE_URL}/settings/admin/get/`, (data) => {
      setFormData((prev) => ({
        ...prev,
        adminName: data.adminName,
        adminEmail: data.adminEmail,
        password: data.password,
      }));
    });

    fetchData(`${API_BASE_URL}/settings/store/get/`, (data) => {
      setFormData((prev) => ({
        ...prev,
        storeName: data.storeName,
        storeEmail: data.storeEmail,
        currency: data.currency,
      }));
    });

    fetchData(`${API_BASE_URL}/settings/notifications/get/`, (data) => {
      setFormData((prev) => ({
        ...prev,
        emailNotifications: data.emailNotifications || false,
        smsNotifications: data.smsNotifications || false,
      }));
    });
  }, [fetchData]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type, checked } = e.target as HTMLInputElement;
    
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async () => {
    const endpoints: any = {
      'General': `${API_BASE_URL}/settings/store/update/`,
      'Account': `${API_BASE_URL}/settings/admin/update/`,
      'Notifications': `${API_BASE_URL}/api/settings/notifications/`,
    };

    const dataMap: any = {
      'General': {
        name: formData.storeName,
        email: formData.storeEmail,
        currency: formData.currency,
      },
      'Account': {
        adminName: formData.adminName,
        adminEmail: formData.adminEmail,
        password: formData.password,
      },
      'Notifications': {
        emailNotifications: formData.emailNotifications,
        smsNotifications: formData.smsNotifications,
      },
    };

    try {
      await axios.put(endpoints[active], dataMap[active], {
        headers: { Authorization: `Bearer ${access}` },
      });

    } catch (error) {
      console.error('Error updating settings:', error);

    }
  };

  return (
    <>
      <Header />
      <div className="Settings_Container">
        <Sidebar />
        <h1>Settings</h1>
        <ul>
          {['General', 'Account', 'Notifications'].map((tab) => (
            <li
              key={tab}
              className={active === tab ? 'Active' : ''}
              onClick={() => setActive(tab)}
            >
              {tab}
            </li>
          ))}
        </ul>

        <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
          {active === 'General' && (
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
          )}
          {active === 'Account' && (
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
                <p onClick={() => navigate("/auth/forgot-password")}>change password</p>
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
          )}
          {active === 'Notifications' && (
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
