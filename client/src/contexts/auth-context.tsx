import { createContext, ReactNode, useState } from "react";
import { AuthContextType } from "../types/auth-context";
import { UserProps } from "../types/user";



export const AuthContext = createContext<AuthContextType>({
  isSignedIn: false,
  setIsSignedIn: () => { },
  user: undefined,
  setUser: () => { },
});


export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isSignedIn, setIsSignedIn] = useState<boolean>(false);
  const [user, setUser] = useState<null | undefined | UserProps>(null);

  return (
    <AuthContext.Provider
      value={{
        isSignedIn,
        setIsSignedIn,
        user,
        setUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
