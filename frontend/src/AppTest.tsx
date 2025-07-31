// Simple test App component
import React from 'react';

const App: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">EmbeddedChat Workflow</h1>
        <p className="text-gray-600 mb-4">Testing UI - If you see this, React is working!</p>
        <div className="space-y-4">
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg mr-4">
            Test Button
          </button>
          <button className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg">
            Another Button
          </button>
        </div>
        <div className="mt-8 p-4 bg-white rounded-lg shadow-md">
          <p className="text-sm text-gray-500">
            Current time: {new Date().toLocaleTimeString()}
          </p>
        </div>
      </div>
    </div>
  );
};

export default App;
