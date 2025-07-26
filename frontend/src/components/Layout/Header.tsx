// Enhanced header component with notifications and workspace controls
import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { 
  BellIcon, 
  Cog6ToothIcon, 
  ChevronDownIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
  SunIcon,
  MoonIcon
} from '@heroicons/react/24/outline';
import { Button } from '../UI/Button';

interface HeaderProps {
  user?: {
    id: number;
    username: string;
    email: string;
  };
  onLogout?: () => void;
  currentWorkspace?: string;
}

export const Header: React.FC<HeaderProps> = ({ 
  user, 
  onLogout, 
  currentWorkspace = "Main Workspace" 
}) => {
  const { isDark, toggleTheme } = useTheme();
  
  return (
    <header className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} shadow-sm border-b px-6 py-4`}>
      <div className="flex items-center justify-between">
        {/* Left side - Logo and Workspace */}
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">EC</span>
            </div>
            <h1 className={`text-xl font-semibold ${isDark ? 'text-white' : 'text-gray-800'}`}>
              EmbeddedChat
            </h1>
          </div>
          
          {/* Workspace Selector */}
          <div className={`flex items-center space-x-2 ${isDark ? 'bg-gray-700' : 'bg-gray-50'} px-3 py-2 rounded-lg`}>
            <span className={`text-sm ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>Workspace:</span>
            <button className={`flex items-center space-x-1 text-sm font-medium ${isDark ? 'text-gray-200 hover:text-blue-400' : 'text-gray-800 hover:text-blue-600'}`}>
              <span>{currentWorkspace}</span>
              <ChevronDownIcon className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Right side - Actions and User */}
        <div className="flex items-center space-x-4">
          {/* Dark Mode Toggle */}
          <button 
            onClick={toggleTheme}
            className={`p-2 ${isDark ? 'text-gray-400 hover:text-gray-200' : 'text-gray-500 hover:text-gray-700'} transition-colors`}
            title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {isDark ? <SunIcon className="w-5 h-5" /> : <MoonIcon className="w-5 h-5" />}
          </button>

          {/* Notifications */}
          <button className={`relative p-2 ${isDark ? 'text-gray-400 hover:text-gray-200' : 'text-gray-400 hover:text-gray-600'} transition-colors`}>
            <BellIcon className="w-5 h-5" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
          </button>

          {/* Settings */}
          <button className={`p-2 ${isDark ? 'text-gray-400 hover:text-gray-200' : 'text-gray-400 hover:text-gray-600'} transition-colors`}>
            <Cog6ToothIcon className="w-5 h-5" />
          </button>

          {/* User Menu */}
          {user && (
            <div className="flex items-center space-x-3 border-l border-gray-200 pl-4">
              <div className="flex items-center space-x-2">
                <UserCircleIcon className="w-8 h-8 text-gray-400" />
                <div className="text-sm">
                  <div className="font-medium text-gray-800">{user.username}</div>
                  <div className="text-gray-500">{user.email}</div>
                </div>
              </div>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={onLogout}
                className="text-red-600 hover:bg-red-50 flex items-center space-x-1"
              >
                <ArrowRightOnRectangleIcon className="w-4 h-4" />
                <span>Logout</span>
              </Button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
