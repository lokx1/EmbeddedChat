/**
 * Test App for Enhanced Execution Panel with Persistent Storage
 */
import React from 'react';
import { ThemeProvider } from './contexts/ThemeContext';
import { EnhancedExecutionPanelDemo } from './components/WorkflowEditor';

const TestEnhancedExecutionPanel: React.FC = () => {
  return (
    <ThemeProvider>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <EnhancedExecutionPanelDemo />
      </div>
    </ThemeProvider>
  );
};

export default TestEnhancedExecutionPanel;
