// Main App component with enhanced workspace integration
import React from 'react';
import { AuthProvider, useAuth } from './components/Auth/AuthContext.tsx';
import { AuthPage } from './components/Auth/AuthPage.tsx';
import { WorkspaceManager } from './components/Workspace/WorkspaceManager.tsx';
import { ThemeProvider } from './contexts/ThemeContext.tsx';
import { NotificationProvider } from './components/UI/NotificationSystem.tsx';

const AppContent: React.FC = () => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
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

// Root App component with all providers
export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <NotificationProvider>
        <AuthProvider>
          <AppContent />
        </AuthProvider>
      </NotificationProvider>
    </ThemeProvider>
  );
};

export default App;
