import { UserProps } from "./user";

export interface AuthContextType {
    isSignedIn: boolean;
    setIsSignedIn: (signedIn: boolean) => void;
    user: UserProps | undefined | null;

}
