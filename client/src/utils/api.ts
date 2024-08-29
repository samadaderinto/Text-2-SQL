import axios from 'axios';


const API_BASE_URL = 'http://localhost:8000';


const api = axios.create({
  baseURL: API_BASE_URL,
});


api.interceptors.request.use(
  (config) => {

    const token = localStorage.getItem('access');
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
 
    return Promise.reject(error);
  }
);

export default api;
