import React, { useState, useContext, createContext, ReactNode } from "react";

interface AuthContextType {
  user: { name: string, email: string } | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode; 
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  // Simple state for demo; replace with API/auth provider in production
    const [user, setUser] = useState<{name: string, email: string} | null>(null);

    const login = async (email: string, password: string) => {
    // Replace with real API call
        setUser({ name: "Rohan", email: email});
    };

    const signup = async (name: string, email: string, password: string) => {
    // Replace with real API call
        setUser({ name, email});
    };

    const logout = () => setUser(null);

    return (
        <AuthContext.Provider value={{user, login, signup, logout}}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) throw new Error("useAuth must be used within AuthProvider");
    return context;
};
