import axios from "axios";
import {useDecryptJWT, useEncryptJWT} from "./hooks";
import {secretKey} from "./constants";

const API_BASE_URL = "http://localhost:8000";

const api = axios.create({baseURL: API_BASE_URL});

api.interceptors.request.use((config) => {
  const access: string | any = localStorage.getItem("access");

  if (access) {
    const decryptedAccessToken = useDecryptJWT(access, secretKey);
    config.headers.Authorization = `Bearer ${decryptedAccessToken}`;
  }
  return config;
}, (error) => Promise.reject(error));

api.interceptors.response.use((response) => response, async (error) => {
  const originalRequest = error.config;
  if (error.response.status === 401 && !originalRequest._retry) {
    originalRequest._retry = true;
    try {
      const refresh: string | any = localStorage.getItem("refresh");
      const decryptedRefreshToken = useDecryptJWT(refresh, secretKey);
      const data = JSON.stringify({decryptedRefreshToken});
      const response = await axios.post(`${API_BASE_URL}/refresh-token/`, {data});

      const encryptedAccessToken = useEncryptJWT(response.data.token, secretKey);
      localStorage.setItem("access", encryptedAccessToken);
      api.defaults.headers.common["Authorization"] = `Bearer ${encryptedAccessToken}`;
      return api(originalRequest);
    } catch (refreshError) {
      console.error("Token refresh failed:", refreshError);
    }
  }
  return Promise.reject(error);
});

export default api;
