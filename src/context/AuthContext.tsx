import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import type { User } from '@/types';
import { api } from '@/services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, password: string, name?: string) => Promise<boolean>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('jl_token'));
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (token) {
      api.getCurrentUser()
        .then(data => {
          if (data.user) {
            setUser(data.user);
          } else {
            logout();
          }
        })
        .catch(() => logout())
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, [token]);

  const login = async (email: string, password: string): Promise<boolean> => {
    const data = await api.login(email, password);
    if (data.success && data.token) {
      localStorage.setItem('jl_token', data.token);
      setToken(data.token);
      setUser(data.user ?? null);
      return true;
    }
    return false;
  };

  const register = async (email: string, password: string, name?: string): Promise<boolean> => {
    const data = await api.register(email, password, name);
    if (data.success && data.token) {
      localStorage.setItem('jl_token', data.token);
      setToken(data.token);
      setUser(data.user ?? null);
      return true;
    }
    return false;
  };

  const logout = () => {
    localStorage.removeItem('jl_token');
    setToken(null);
    setUser(null);
  };

  const refreshUser = async () => {
    if (!token) return;
    try {
      const data = await api.getCurrentUser();
      if (data.user) {
        setUser(data.user);
      }
    } catch (error) {
      // ignore
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, refreshUser, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
