'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface AuthContextType {
  isLoggedIn: boolean;
  username: string | null;
  apiKey: string | null;
  login: (username: string, apiKey: string) => void;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_KEY_STORAGE_KEY = 'forum_api_key';
const USERNAME_STORAGE_KEY = 'forum_username';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [username, setUsername] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Load from localStorage on mount
    const storedApiKey = localStorage.getItem(API_KEY_STORAGE_KEY);
    const storedUsername = localStorage.getItem(USERNAME_STORAGE_KEY);

    if (storedApiKey && storedUsername) {
      setApiKey(storedApiKey);
      setUsername(storedUsername);
    }
    setIsLoading(false);
  }, []);

  const login = (user: string, key: string) => {
    localStorage.setItem(API_KEY_STORAGE_KEY, key);
    localStorage.setItem(USERNAME_STORAGE_KEY, user);
    setApiKey(key);
    setUsername(user);
  };

  const logout = () => {
    localStorage.removeItem(API_KEY_STORAGE_KEY);
    localStorage.removeItem(USERNAME_STORAGE_KEY);
    setApiKey(null);
    setUsername(null);
  };

  return (
    <AuthContext.Provider
      value={{
        isLoggedIn: !!apiKey,
        username,
        apiKey,
        login,
        logout,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
