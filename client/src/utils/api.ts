export const API_BASE_URL = 'http://localhost:8000';



// const api = axios.create({
//   baseURL: API_BASE_URL,
//   headers: {
//     'Content-Type': 'application/json',
//   },
// });

// api.interceptors.request.use((config) => {
//   const token = localStorage.getItem('token');
//   if (token) {
//     config.headers.Authorization = `Bearer ${JSON.parse(token)}`;
//   }
//   return config;
// });

// export default api;