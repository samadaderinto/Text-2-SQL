import {useEffect, FC} from "react";
import {useNavigate} from "react-router-dom";
import { ProtectedRouteProps } from "../types/protected-route";



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
