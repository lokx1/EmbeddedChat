/**
 * User Context for Managing Current User State
 * Simple context to track current user - replace with real auth later
 */
import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  id: number;
  username: string;
  email: string;
}

interface UserContextType {
  currentUser: User | null;
  setCurrentUser: (user: User) => void;
  clearUser: () => void;
  isAuthenticated: boolean;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const useUser = () => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

interface UserProviderProps {
  children: React.ReactNode;
}

export const UserProvider: React.FC<UserProviderProps> = ({ children }) => {
  const [currentUser, setCurrentUserState] = useState<User | null>(null);

  // Initialize with default user (mock)
  useEffect(() => {
    // In a real app, this would check localStorage, cookies, or make an API call
    const mockUser: User = {
      id: 1,
      username: 'test_user',
      email: 'test@example.com'
    };
    setCurrentUserState(mockUser);
  }, []);

  const setCurrentUser = (user: User) => {
    setCurrentUserState(user);
    // In a real app, you might save to localStorage or update session
  };

  const clearUser = () => {
    setCurrentUserState(null);
    // In a real app, you might clear localStorage or cookies
  };

  const value: UserContextType = {
    currentUser,
    setCurrentUser,
    clearUser,
    isAuthenticated: currentUser !== null
  };

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
};
