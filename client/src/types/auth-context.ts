import { User } from "./user";

export interface AuthContextType {
    isSignedIn: boolean;
    setIsSignedIn: (signedIn: boolean) => void;
    user: User | undefined | null;
}
