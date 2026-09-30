import { useEffect, useState, useCallback } from "react";
import Sidebar from '../layouts/Sidebar';
import { useNavigate } from "react-router-dom";
import { Header } from "../layouts/Header";
import api from "../utils/api";
import { notifyApiError } from "../utils/api-errors";
import { registerPushNotifications } from "../utils/push-notifications";

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
    pushNotifications: false,
  });

  const nav = useNavigate();

  const fetchData = useCallback(async (url: string, updateData: (data: any) => void) => {
    try {
      const response = await api.get(url);
      updateData(response.data);

    } catch (error) {
      notifyApiError(error, "Could not load settings. Please try again.");
    }
  }, []);

  useEffect(() => {
    fetchData(`/settings/admin/get/`, ({ first_name, email }) => {

      setFormData((prev) => ({
        ...prev,

        adminName: first_name,
        adminEmail: email,
        password: '',
      }));
    });

    fetchData(`/settings/store/get/`, ({ name, email, currency }) => {

      setFormData((prev) => ({
        ...prev,
        storeName: name,
        storeEmail: email,
        currency: currency,
      }));
    });

    fetchData(`/settings/notifications/get/`, ({ email_notification, push_notification }) => {
      setFormData((prev) => ({
        ...prev,
        emailNotifications: email_notification,
        pushNotifications: push_notification,
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
      'General': `/settings/store/update/`,
      'Account': `/settings/admin/update/`,
      'Notifications': `/settings/notifications/update/`,
    };

    const dataMap: any = {
      'General': {
        name: formData.storeName,
        email: formData.storeEmail,
        currency: formData.currency,
      },
      'Account': {
        first_name: formData.adminName,
        email: formData.adminEmail,
        ...(formData.password ? { password: formData.password } : {}),
      },
      'Notifications': {
        email_notification: formData.emailNotifications,
        push_notification: formData.pushNotifications,
      },
    };

    try {
      await api.put(endpoints[active], dataMap[active]);
      if (active === 'Notifications' && formData.pushNotifications) {
        await registerPushNotifications();
      }
    } catch (error) {
      notifyApiError(error, "Could not save settings. Please try again.");
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
                <p onClick={() => nav("/auth/forgot-password")}>change password</p>
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
                  id="pushNotifications"
                  name="pushNotifications"
                  checked={formData.pushNotifications}
                  onChange={handleInputChange}
                />
                <p>Enable Push Notifications</p>
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
