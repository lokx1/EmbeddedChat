/**
 * User Switcher for Testing
 * Allows switching between different mock users to test isolation
 */
import { useState } from 'react';

interface User {
  id: number;
  username: string;
  email: string;
}

const MOCK_USERS: User[] = [
  { id: 1, username: 'test_user', email: 'test@example.com' },
  { id: 16, username: 'long', email: 'longbaoluu68@gmail.com' },
  { id: 17, username: 'admin', email: 'awuwu68@gmail.com' },
  { id: 18, username: 'chat_user', email: 'chat@example.com' },
];

interface UserSwitcherProps {
  currentUserId: number;
  onUserChange: (user: User) => void;
}

export default function UserSwitcher({ currentUserId, onUserChange }: UserSwitcherProps) {
  const [isOpen, setIsOpen] = useState(false);
  
  const currentUser = MOCK_USERS.find(u => u.id === currentUserId) || MOCK_USERS[0];

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 text-sm bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
      >
        <div className="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center text-white text-xs font-medium">
          {currentUser.username.charAt(0).toUpperCase()}
        </div>
        <span className="text-gray-700 dark:text-gray-300">{currentUser.username}</span>
        <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-1 w-48 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg z-50">
          <div className="p-2">
            <div className="text-xs text-gray-500 dark:text-gray-400 px-2 py-1 mb-1">
              Switch User (Testing)
            </div>
            {MOCK_USERS.map((user) => (
              <button
                key={user.id}
                onClick={() => {
                  onUserChange(user);
                  setIsOpen(false);
                }}
                className={`w-full flex items-center gap-2 px-2 py-2 text-sm rounded hover:bg-gray-100 dark:hover:bg-gray-700 ${
                  user.id === currentUserId 
                    ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300' 
                    : 'text-gray-700 dark:text-gray-300'
                }`}
              >
                <div className="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center text-white text-xs font-medium">
                  {user.username.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 text-left">
                  <div className="font-medium">{user.username}</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">{user.email}</div>
                </div>
                {user.id === currentUserId && (
                  <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
