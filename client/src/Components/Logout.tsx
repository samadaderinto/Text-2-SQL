import { useNavigate } from "react-router-dom";
import api from "../utils/api";
import { useContext } from "react";
import { AuthContext } from "../contexts/auth-context";
import { useDecryptJWT } from "../utils/hooks";
import { secretKey } from "../utils/constants";

export const Logout = () => {
  const { setIsSignedIn } = useContext(AuthContext);
  const nav = useNavigate();

  const handleLogout = async () => {
    const refresh: string | null = localStorage.getItem('refresh');

    if (refresh) {
      try {
        const decryptedRefreshToken = useDecryptJWT(refresh, secretKey);
        const data = JSON.stringify({ refresh: decryptedRefreshToken });

        const response = await api.post(`/auth/logout/`, data);

        if (response.status === 205) {
          localStorage.removeItem('access');
          localStorage.removeItem('refresh');
          setIsSignedIn(false);
          nav('/auth/signin/');
        }
      } catch (error: any) {
        console.log("Error during logout:", error);
      }
    } else {
      console.error('No refresh token found');
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
