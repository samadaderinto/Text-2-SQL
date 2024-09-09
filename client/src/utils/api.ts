import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

const api = axios.create({baseURL: API_BASE_URL});

api.interceptors.request.use((config) => {
  const accessToken = localStorage.getItem("access");
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
}, (error) => Promise.reject(error));

api.interceptors.response.use((response) => response, async (error) => {
  const originalRequest = error.config;
  if (error.response.status === 401 && !originalRequest._retry) {
    originalRequest._retry = true;
    try {
      const refresh = localStorage.getItem("refresh");
      const response = await axios.post(`${API_BASE_URL}/refresh-token/`, {refresh});
      const {access} = response.data;
      localStorage.setItem("access", access);
      api.defaults.headers.common["Authorization"] = `Bearer ${access}`;
      return api(originalRequest);
    } catch (refreshError) {
      console.error("Token refresh failed:", refreshError);
    }
  }
  return Promise.reject(error);
});

export default api;
