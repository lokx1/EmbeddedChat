// Main App component with enhanced workspace integration
import React from 'react';
import { AuthProvider, useAuth } from './components/Auth/AuthContext.tsx';
import { AuthPage } from './components/Auth/AuthPage.tsx';
import { WorkspaceManager } from './components/Workspace/WorkspaceManager.tsx';

const AppContent: React.FC = () => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="mt-4 text-gray-600">Loading EmbeddedChat...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AuthPage />;
  }

  return <WorkspaceManager />;
};

// Root App component with AuthProvider
export const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;
