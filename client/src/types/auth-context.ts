import { UserProps } from "./user";

export interface AuthContextType {
    isSignedIn: boolean;
    setIsSignedIn: (signedIn: boolean) => void;
    user: UserProps | undefined | null;
    setUser: (user: UserProps | undefined | null) => void;
    queryResponse: any[];
    setQueryResponse: (query: any[]) => void;
}
