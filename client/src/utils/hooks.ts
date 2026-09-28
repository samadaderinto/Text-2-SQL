import {createElement, FC} from "react";
import {Navigate} from "react-router-dom";
import { ProtectedRouteProps } from "../types/protected-route";
import CryptoJS from "crypto-js";


const ProtectedRoute: FC<ProtectedRouteProps> = ({children}) => {
  const accessToken = localStorage.getItem("access");

  return accessToken ? children : createElement(Navigate, { to: "/auth/signin", replace: true });
};

export default ProtectedRoute;


export const encryptJWT = (token: string | CryptoJS.lib.WordArray, secretKey: string | CryptoJS.lib.WordArray) => {
  return CryptoJS.AES.encrypt(token, secretKey).toString();
};

export const decryptJWT = (encryptedToken: string | CryptoJS.lib.CipherParams, secretKey: string | CryptoJS.lib.WordArray) => {
  const bytes = CryptoJS.AES.decrypt(encryptedToken, secretKey);
  return bytes.toString(CryptoJS.enc.Utf8);
};
