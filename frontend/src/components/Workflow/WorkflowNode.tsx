import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';

export interface WorkflowNodeData {
  label: string;
  type: 'ollama' | 'openai' | 'claude' | 'input' | 'output' | 'transform';
  config?: Record<string, any>;
  selected?: boolean;
}

export interface WorkflowNodeProps extends NodeProps {
  data: WorkflowNodeData;
}

const nodeStyles = {
  ollama: {
    background: 'linear-gradient(135deg, #2a8af6 0%, #1d4ed8 100%)',
    color: 'white',
    borderColor: '#2a8af6'
  },
  openai: {
    background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
    color: 'white',
    borderColor: '#22c55e'
  },
  claude: {
    background: 'linear-gradient(135deg, #ae53ba 0%, #2a8af6 100%)',
    color: 'white',
    borderColor: '#ae53ba'
  },
  input: {
    background: 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
    color: 'white',
    borderColor: '#f59e0b'
  },
  output: {
    background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
    color: 'white',
    borderColor: '#ef4444'
  },
  transform: {
    background: 'linear-gradient(135deg, #64748b 0%, #475569 100%)',
    color: 'white',
    borderColor: '#64748b'
  }
};

export const WorkflowNode: React.FC<WorkflowNodeProps> = ({ data, selected }) => {
  const style = nodeStyles[data.type] || nodeStyles.transform;
  
  return (
    <div
      className={`workflow-node ${selected ? 'selected' : ''}`}
      style={{
        padding: '16px 20px',
        borderRadius: '12px',
        border: `2px solid ${style.borderColor}`,
        background: style.background,
        color: style.color,
        minWidth: '140px',
        textAlign: 'center',
        fontSize: '14px',
        fontWeight: '500',
        boxShadow: selected 
          ? '0 0 0 3px rgba(42, 138, 246, 0.3), 0 8px 25px rgba(0,0,0,0.25)' 
          : '0 4px 12px rgba(0,0,0,0.2)',
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {/* Gradient overlay for depth */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '50%',
        background: 'linear-gradient(180deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0) 100%)',
        pointerEvents: 'none'
      }} />
      
      {/* Input handle */}
      {data.type !== 'input' && (
        <Handle
          type="target"
          position={Position.Left}
          style={{
            background: '#ffffff',
            border: '3px solid #e5e7eb',
            width: '14px',
            height: '14px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}
        />
      )}
      
      {/* Node content */}
      <div className="node-content" style={{ position: 'relative', zIndex: 1 }}>
        <div className="node-type" style={{ 
          fontSize: '11px', 
          opacity: 0.9, 
          marginBottom: '6px',
          fontWeight: '600',
          letterSpacing: '0.5px'
        }}>
          {data.type.toUpperCase()}
        </div>
        <div className="node-label" style={{ 
          fontSize: '15px',
          fontWeight: '600',
          lineHeight: '1.2'
        }}>
          {data.label}
        </div>
      </div>
      
      {/* Output handle */}
      {data.type !== 'output' && (
        <Handle
          type="source"
          position={Position.Right}
          style={{
            background: '#ffffff',
            border: '3px solid #e5e7eb',
            width: '14px',
            height: '14px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}
        />
      )}
    </div>
  );
};

export default WorkflowNode;
