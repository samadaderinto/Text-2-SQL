import { createContext, ReactNode, useState } from "react";
import { AuthContextType } from "../types/auth-context";
import { UserProps } from "../types/user";



export const AuthContext = createContext<AuthContextType>({
  isSignedIn: false,
  setIsSignedIn: () => { },
  user: undefined,
  setUser: () => { },
  queryResponse: [],
  setQueryResponse: () => { }
});


export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isSignedIn, setIsSignedIn] = useState<boolean>(false);
  const [user, setUser] = useState<null | undefined | UserProps>(null);
  const [queryResponse, setQueryResponse] = useState<any[]>([]);

  return (
    <AuthContext.Provider
      value={{
        isSignedIn,
        setIsSignedIn,
        user,
        setUser,
        queryResponse,
        setQueryResponse
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
