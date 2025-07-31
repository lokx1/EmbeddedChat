import React from 'react';
import { AuthProvider, useAuth } from './components/Auth/AuthContext';
import { AuthPage } from './components/Auth/AuthPage';
import { WorkspaceManager } from './components/Workspace/WorkspaceManager';
import { ThemeProvider } from './contexts/ThemeContext';
import { NotificationProvider } from './components/UI/NotificationSystem';

const AppContent: React.FC = () => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-300">Loading EmbeddedChat...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AuthPage />;
  }

  return <WorkspaceManager />;
};

export default function App() {
  return (
    <ThemeProvider>
      <NotificationProvider>
        <AuthProvider>
          <AppContent />
        </AuthProvider>
      </NotificationProvider>
    </ThemeProvider>
  );
}
