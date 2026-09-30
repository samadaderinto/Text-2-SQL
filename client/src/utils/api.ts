import axios from "axios";
import { decryptJWT, encryptJWT } from "./hooks";
import { secretKey } from "./constants";
import { reportClientError } from "./error-reporting";
import { API_BASE_URL } from "./api-config";

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
    if (axios.isAxiosError(error) && error.response?.status && error.response.status >= 500) {
      reportClientError({
        level: "error",
        event_type: "api_error",
        message: `API request failed with status ${error.response.status}`,
        method: error.config?.method,
        route: error.config?.url,
        status_code: error.response.status,
      });
    }

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
