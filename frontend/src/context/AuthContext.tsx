import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User, UserRole } from '../types';
import { authAPI } from '../services/api';
import { toast } from 'react-hot-toast';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  register: (email: string, username: string, password: string, role?: UserRole) => Promise<boolean>;
  logout: () => void;
  hasRole: (role: UserRole) => boolean;
  hasMinimumRole: (role: UserRole) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is authenticated on app start
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('access_token');
      const savedUser = localStorage.getItem('user');

      if (token && savedUser) {
        try {
          const currentUser = await authAPI.getCurrentUser();
          setUser(currentUser);
          localStorage.setItem('user', JSON.stringify(currentUser));
        } catch (error) {
          // Token is invalid, clear storage
          authAPI.logout();
        }
      }
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      const response = await authAPI.login({ username, password });
      
      localStorage.setItem('access_token', response.access_token);
      
      // Get user details
      const currentUser = await authAPI.getCurrentUser();
      setUser(currentUser);
      localStorage.setItem('user', JSON.stringify(currentUser));
      
      toast.success('Login successful!');
      return true;
    } catch (error) {
      toast.error('Login failed. Please check your credentials.');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, username: string, password: string, role: UserRole = UserRole.VIEWER): Promise<boolean> => {
    try {
      setIsLoading(true);
      const newUser = await authAPI.register({ email, username, password, role });
      
      toast.success('Registration successful! Please login.');
      return true;
    } catch (error) {
      toast.error('Registration failed. Please try again.');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    authAPI.logout();
    setUser(null);
    toast.success('Logged out successfully');
  };

  const hasRole = (role: UserRole): boolean => {
    if (!user) return false;
    return user.role === role || user.role === UserRole.ADMIN;
  };

  const hasMinimumRole = (role: UserRole): boolean => {
    if (!user) return false;
    
    const roleHierarchy = {
      [UserRole.VIEWER]: 1,
      [UserRole.EDITOR]: 2,
      [UserRole.ADMIN]: 3,
    };

    const userLevel = roleHierarchy[user.role] || 0;
    const requiredLevel = roleHierarchy[role] || 0;

    return userLevel >= requiredLevel;
  };

  const value: AuthContextType = {
    user,
    isLoading,
    login,
    register,
    logout,
    hasRole,
    hasMinimumRole,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 