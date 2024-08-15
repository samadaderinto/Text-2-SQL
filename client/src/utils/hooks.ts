import {useEffect, FC} from "react";
import {useNavigate} from "react-router-dom";
import { ProtectedRouteProps } from "../types/protected-route";



const ProtectedRoute: FC<ProtectedRouteProps> = ({children}) => {
  const navigate = useNavigate();

  useEffect(() => {
    const accessToken = localStorage.getItem("access");
    if (!accessToken) {
      navigate("/auth/signin");
    }
  }, [navigate]);

  return children;
};

export default ProtectedRoute;
