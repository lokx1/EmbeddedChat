import React from 'react';

interface NodeTemplate {
  type: 'ollama' | 'openai' | 'claude' | 'input' | 'output' | 'transform';
  label: string;
  description: string;
  icon: string;
}

interface WorkflowSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  onDragStart: (event: React.DragEvent, nodeType: string) => void;
  theme?: any;
}

const nodeTemplates: NodeTemplate[] = [
  {
    type: 'input',
    label: 'Input',
    description: 'Khởi tạo dữ liệu đầu vào',
    icon: '📝'
  },
  {
    type: 'ollama',
    label: 'Ollama AI',
    description: 'Sử dụng mô hình AI từ Ollama',
    icon: '🤖'
  },
  {
    type: 'openai',
    label: 'OpenAI',
    description: 'Sử dụng GPT từ OpenAI',
    icon: '🧠'
  },
  {
    type: 'claude',
    label: 'Claude AI',
    description: 'Sử dụng Claude từ Anthropic',
    icon: '🎭'
  },
  {
    type: 'transform',
    label: 'Transform',
    description: 'Chuyển đổi và xử lý dữ liệu',
    icon: '⚙️'
  },
  {
    type: 'output',
    label: 'Output',
    description: 'Xuất kết quả cuối cùng',
    icon: '📤'
  }
];

export const WorkflowSidebar: React.FC<WorkflowSidebarProps> = ({
  isOpen,
  onToggle,
  onDragStart,
  theme = {
    primary: '#2a8af6',
    surface: '#1a1a2e',
    background: '#0f0f23',
    nodeBackground: '#1a1a2e',
    border: '#292a47',
    borderColor: '#292a47',
    text: '#ffffff',
    textColor: '#ffffff',
    textSecondary: '#94a3b8',
    accent: '#ae53ba',
    accentColor: '#ae53ba',
    shadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
    shadowColor: 'rgba(0, 0, 0, 0.3)',
    shadowLg: '0 10px 15px -3px rgba(0, 0, 0, 0.3)',
    node: {
      ai: 'linear-gradient(135deg, #ae53ba 0%, #2a8af6 100%)',
      trigger: 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
      action: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
      default: 'linear-gradient(135deg, #2a8af6 0%, #1d4ed8 100%)'
    }
  }
}) => {
  return (
    <>
      {/* Toggle Button - Modern floating style */}
      <button
        onClick={onToggle}
        style={{
          position: 'absolute',
          top: '20px',
          left: isOpen ? '280px' : '20px',
          zIndex: 1001,
          width: '48px',
          height: '48px',
          borderRadius: '12px',
          background: theme.accent,
          border: 'none',
          boxShadow: theme.shadow,
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '18px',
          color: 'white',
          transition: 'all 0.3s ease'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'scale(1.05)';
          e.currentTarget.style.boxShadow = theme.shadowLg;
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'scale(1)';
          e.currentTarget.style.boxShadow = theme.shadow;
        }}
      >
        {isOpen ? '✕' : '☰'}
      </button>

      {/* Sidebar Panel - Modern floating style */}
      {isOpen && (
        <div
          style={{
            position: 'absolute',
            top: '20px',
            left: '20px',
            width: '260px',
            maxHeight: 'calc(100vh - 120px)',
            background: `${theme.surface}f5`,
            borderRadius: '16px',
            border: `1px solid ${theme.border}`,
            boxShadow: theme.shadowLg,
            zIndex: 1000,
            overflow: 'hidden',
            backdropFilter: 'blur(16px)'
          }}
        >
          {/* Header */}
          <div style={{
            padding: '20px 20px 16px',
            borderBottom: `1px solid ${theme.border}`,
            background: `${theme.background}99`
          }}>
            <h3 style={{
              margin: 0,
              fontSize: '18px',
              fontWeight: '600',
              color: theme.text,
              letterSpacing: '-0.025em'
            }}>
              Workflow Nodes
            </h3>
            <p style={{
              margin: '4px 0 0',
              fontSize: '14px',
              color: theme.textSecondary,
              lineHeight: '1.4'
            }}>
              Kéo thả để thêm node vào workflow
            </p>
          </div>

          {/* Nodes Grid */}
          <div style={{
            padding: '16px',
            maxHeight: 'calc(100vh - 220px)',
            overflowY: 'auto',
            display: 'grid',
            gap: '12px'
          }}>
            {nodeTemplates.map((template) => (
              <div
                key={template.type}
                draggable
                onDragStart={(event) => onDragStart(event, template.type)}
                style={{
                  padding: '16px',
                  border: `2px solid ${theme.border}`,
                  borderRadius: '12px',
                  cursor: 'grab',
                  transition: 'all 0.2s ease',
                  background: theme.surface,
                  userSelect: 'none'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = theme.accent;
                  e.currentTarget.style.background = `${theme.accent}11`;
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = `0 4px 12px ${theme.accent}40`;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = theme.border;
                  e.currentTarget.style.background = theme.surface;
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
                onMouseDown={(e) => {
                  e.currentTarget.style.cursor = 'grabbing';
                }}
                onMouseUp={(e) => {
                  e.currentTarget.style.cursor = 'grab';
                }}
              >
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  marginBottom: '8px'
                }}>
                  <span style={{ 
                    fontSize: '24px',
                    lineHeight: 1 
                  }}>
                    {template.icon}
                  </span>
                  <span style={{
                    fontSize: '15px',
                    fontWeight: '600',
                    color: theme.text,
                    letterSpacing: '-0.025em'
                  }}>
                    {template.label}
                  </span>
                </div>
                <p style={{
                  margin: 0,
                  fontSize: '13px',
                  color: theme.textSecondary,
                  lineHeight: '1.4'
                }}>
                  {template.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
};

export default WorkflowSidebar;
