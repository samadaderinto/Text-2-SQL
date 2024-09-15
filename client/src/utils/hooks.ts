import {useEffect, FC} from "react";
import {useNavigate} from "react-router-dom";
import { ProtectedRouteProps } from "../types/protected-route";
import CryptoJS from "crypto-js";


const ProtectedRoute: FC<ProtectedRouteProps> = ({children}) => {
  const nav = useNavigate();

  useEffect(() => {
    const accessToken = localStorage.getItem("access");
    if (!accessToken) {
      nav("/auth/signin");
    }
  }, [nav]);

  return children;
};

export default ProtectedRoute;


export const useEncryptJWT = (token: string | CryptoJS.lib.WordArray, secretKey: string | CryptoJS.lib.WordArray) => {
  return CryptoJS.AES.encrypt(token, secretKey).toString();
};

export const useDecryptJWT = (encryptedToken: string | CryptoJS.lib.CipherParams, secretKey: string | CryptoJS.lib.WordArray) => {
  const bytes = CryptoJS.AES.decrypt(encryptedToken, secretKey);
  return bytes.toString(CryptoJS.enc.Utf8);
};
