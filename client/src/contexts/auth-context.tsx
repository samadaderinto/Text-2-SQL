import { createContext, ReactNode, useState } from "react";
import { AuthContextType } from "../types/auth-context";
import { UserProps } from "../types/user";



export const AuthContext = createContext<AuthContextType>({
    isSignedIn: false,
    setIsSignedIn: () => {}, // Default implementation that does nothing
    user: undefined, // Start with undefined if no user is signed in initially
    setUser: () => {}, // Default implementation that does nothing
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
