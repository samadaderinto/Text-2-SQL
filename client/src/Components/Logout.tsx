import { useNavigate } from "react-router-dom";
import api from "../utils/api";
import { useContext } from "react";
import { AuthContext } from "../contexts/auth-context";
import { decryptJWT } from "../utils/hooks";
import { secretKey } from "../utils/constants";
import { notifyApiError } from "../utils/api-errors";
import { PiDiamondsFourFill } from "react-icons/pi";
import { RiLogoutBoxLine } from "react-icons/ri";

export const Logout = () => {
  const { setIsSignedIn } = useContext(AuthContext);
  const nav = useNavigate();

  const handleLogout = async () => {
    const refresh: string | null = localStorage.getItem('refresh');

    if (refresh) {
      try {
        const decryptedRefreshToken = decryptJWT(refresh, secretKey);

        const response = await api.post(`/auth/logout/`, {
          refresh: decryptedRefreshToken,
        });

        if (response.status !== 205) {
          throw new Error("The server did not confirm logout.");
        }
      } catch (error) {
        notifyApiError(
          error,
          "Could not revoke the server session. You will be signed out on this device.",
        );
      }
    }

    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    setIsSignedIn(false);
    nav('/auth/signin/', { replace: true });
  };

  return (
    <div className="Logout_Container">
      <article>
        <span className="Logout_Brand"><PiDiamondsFourFill /> EchoCart</span>
        <div className="Logout_Icon" aria-hidden="true">
          <RiLogoutBoxLine />
        </div>
        <h1>Sign out of EchoCart?</h1>
        <p>You can sign back in at any time to continue managing your store.</p>
        <div className="Logout_Action_Row">
          <button type="button" onClick={handleLogout} className="Blue_btn">Sign out</button>
          <button type="button" onClick={() => nav(-1)} className="White_btn">Stay signed in</button>
        </div>
      </article>
    </div>
  );
};
