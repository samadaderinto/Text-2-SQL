import axios from "axios";
import { decryptJWT, encryptJWT } from "./hooks";
import { secretKey } from "./constants";

const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_BASE_URL = configuredApiBaseUrl.includes("://")
  ? configuredApiBaseUrl
  : `https://${configuredApiBaseUrl}`;

const api = axios.create({ baseURL: API_BASE_URL });

api.interceptors.request.use((config) => {
  const access = localStorage.getItem("access");

  if (access) {
    try {
      const decryptedAccessToken = decryptJWT(access, secretKey);
      config.headers.Authorization = `Bearer ${decryptedAccessToken}`;
    } catch (error) {
      console.error("Error decrypting access token:", error);
    }
  }

  return config;
}, (error) => Promise.reject(error));

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refresh = localStorage.getItem("refresh");

        if (refresh) {
          const decryptedRefreshToken = decryptJWT(refresh, secretKey);

          const response = await axios.post(`${API_BASE_URL}/auth/refresh-token/`, {
            refresh: decryptedRefreshToken,
          });
          console.log(response)

          const encryptedAccessToken = encryptJWT(
            response.data.access,
            secretKey
          );

          localStorage.setItem("access", encryptedAccessToken);

          originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
          return api(originalRequest);
        } else {
          console.error("Refresh token missing. Redirecting to login...");
          localStorage.removeItem("access");
          localStorage.removeItem("refresh");
        
        }
      } catch (refreshError) {
        console.error("Token refresh failed:", refreshError);
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
      
      }
    }

    return Promise.reject(error);
  }
);

export default api;
