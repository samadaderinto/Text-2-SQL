import { useNavigate } from "react-router-dom";
import api from "../utils/api";
import { useContext } from "react";
import { AuthContext } from "../contexts/auth-context";

export const Logout = () => {
  const { setIsSignedIn } = useContext(AuthContext);
  const nav = useNavigate();

  const handleLogout = async () => {
    const refresh = localStorage.getItem('refresh');
    const data = JSON.stringify({ refresh });

    try {
      const response = await api.post(`/auth/logout/`, data);

      if (response.status === 205) {
        setIsSignedIn(false);
        nav('/auth/signin/');
      }

    } catch (error: any) {
      if (error.response && error.response.status === 401) {
        try {
          const refreshResponse = await api.post(`/auth/login/refresh/`, data);
          localStorage.setItem('access', refreshResponse.data.access);

          const retryResponse = await api.post(`/auth/logout/`, data);

          if (retryResponse.status === 205) {
            setIsSignedIn(false);
            nav('/auth/signin/');
          }
        } catch (refreshError) {
          console.log('Token refresh failed:', refreshError);
          setIsSignedIn(false);
          nav('/auth/signin/');
        }
      } else {
        console.log(error);
      }
    }
  };

  return (
    <div className="Logout_Container">
      <article>
        <h1>Log Out?</h1>
        <div>
          <span onClick={handleLogout} className="Blue_btn">Yes</span>
          <span onClick={() => nav(-1)} className="White_btn">No</span>
        </div>
      </article>
    </div>
  );
};
