// Simple Dashboard for debugging
import React from 'react';

interface SimpleDashboardProps {
  user?: {
    id: number;
    username: string;
    email: string;
  };
}

export const SimpleDashboard: React.FC<SimpleDashboardProps> = ({ user }) => {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Simple Dashboard</h1>
      
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Welcome!</h2>
        {user ? (
          <div>
            <p>Hello, {user.username}!</p>
            <p>Email: {user.email}</p>
            <p>User ID: {user.id}</p>
          </div>
        ) : (
          <p>No user data available</p>
        )}
      </div>
      
      <div className="mt-6 bg-green-100 rounded-lg p-4">
        <p className="text-green-800">✅ Dashboard is working correctly!</p>
        <p className="text-green-600 text-sm mt-1">Backend connection: OK</p>
      </div>
    </div>
  );
};
