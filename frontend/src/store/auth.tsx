"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
  type ReactNode,
} from "react";

interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
}

interface AuthContextType {
  isLoginOpen: boolean;
  isProfileOpen: boolean;
  isAuthenticated: boolean;
  user: User | null;
  openLogin: () => void;
  closeLogin: () => void;
  openProfile: () => void;
  closeProfile: () => void;
  login: (user: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);

  const openLogin = useCallback(() => setIsLoginOpen(true), []);
  const closeLogin = useCallback(() => setIsLoginOpen(false), []);
  const openProfile = useCallback(() => setIsProfileOpen(true), []);
  const closeProfile = useCallback(() => setIsProfileOpen(false), []);
  
  const login = useCallback((userData: User) => {
    setUser(userData);
    setIsAuthenticated(true);
    setIsLoginOpen(false);
  }, []);
  
  const logout = useCallback(() => {
    setUser(null);
    setIsAuthenticated(false);
    setIsProfileOpen(false);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        isLoginOpen,
        isProfileOpen,
        isAuthenticated,
        user,
        openLogin,
        closeLogin,
        openProfile,
        closeProfile,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
