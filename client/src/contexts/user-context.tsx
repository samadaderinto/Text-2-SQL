import { createContext } from "react";
import { AuthContextType } from "../types/auth-context";



export const AuthContext = createContext<AuthContextType>({
    isSignedIn: false,
    setIsSignedIn: () => {},  // Default implementation that does nothing
    user: undefined,  // Start with undefined if no user is signed in initially
 // Default implementation that does nothing
});
