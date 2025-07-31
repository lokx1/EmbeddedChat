import React from 'react';

interface WorkflowToolbarProps {
  onSave: () => void;
  onLoad: () => void;
  onClear: () => void;
  onRun: () => void;
  isRunning?: boolean;
  theme?: any;
}

export const WorkflowToolbar: React.FC<WorkflowToolbarProps> = ({
  onSave,
  onLoad,
  onClear,
  onRun,
  isRunning = false,
  theme = {
    primary: '#2a8af6',
    accent: '#ae53ba',
    surface: '#1a1a2e',
    background: '#0f0f23',
    nodeBackground: '#1a1a2e',
    border: '#292a47',
    borderColor: '#292a47',
    text: '#ffffff',
    textColor: '#ffffff',
    textSecondary: '#94a3b8',
    shadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
    shadowColor: 'rgba(0, 0, 0, 0.3)'
  }
}) => {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      padding: '16px 20px',
      background: theme.surface,
      borderBottom: `1px solid ${theme.border}`,
      backdropFilter: 'blur(8px)',
      boxShadow: theme.shadow
    }}>
      <button
        onClick={onSave}
        style={{
          padding: '10px 16px',
          background: theme.accent,
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer',
          fontSize: '14px',
          fontWeight: '600',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          transition: 'all 0.2s ease'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = '#2563eb';
          e.currentTarget.style.transform = 'translateY(-1px)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = '#3b82f6';
          e.currentTarget.style.transform = 'translateY(0)';
        }}
      >
        💾 Save
      </button>
      
      <button
        onClick={onLoad}
        style={{
          padding: '10px 16px',
          background: '#6b7280',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer',
          fontSize: '14px',
          fontWeight: '500',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          transition: 'all 0.2s ease'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = '#4b5563';
          e.currentTarget.style.transform = 'translateY(-1px)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = '#6b7280';
          e.currentTarget.style.transform = 'translateY(0)';
        }}
      >
        📁 Load
      </button>
      
      <button
        onClick={onClear}
        style={{
          padding: '10px 16px',
          background: '#dc2626',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer',
          fontSize: '14px',
          fontWeight: '500',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          transition: 'all 0.2s ease'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = '#b91c1c';
          e.currentTarget.style.transform = 'translateY(-1px)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = '#dc2626';
          e.currentTarget.style.transform = 'translateY(0)';
        }}
      >
        🗑️ Clear
      </button>
      
      <div style={{ marginLeft: 'auto' }}>
        <button
          onClick={onRun}
          disabled={isRunning}
          style={{
            padding: '10px 20px',
            background: isRunning ? '#9ca3af' : '#059669',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: isRunning ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            fontWeight: '500',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'all 0.2s ease'
          }}
          onMouseEnter={(e) => {
            if (!isRunning) {
              e.currentTarget.style.background = '#047857';
              e.currentTarget.style.transform = 'translateY(-1px)';
            }
          }}
          onMouseLeave={(e) => {
            if (!isRunning) {
              e.currentTarget.style.background = '#059669';
              e.currentTarget.style.transform = 'translateY(0)';
            }
          }}
        >
          {isRunning ? '⏳' : '▶️'} {isRunning ? 'Running...' : 'Run Workflow'}
        </button>
      </div>
    </div>
  );
};

export default WorkflowToolbar;
