import React, { useState, useEffect } from 'react';
import { Node } from 'reactflow';
import { WorkflowNodeData } from './WorkflowNode';

interface NodePropertiesPanelProps {
  isOpen: boolean;
  selectedNode: Node<WorkflowNodeData> | null;
  onClose: () => void;
  onUpdateNode: (nodeId: string, data: Partial<WorkflowNodeData>) => void;
  theme?: any;
}

interface NodeConfig {
  [key: string]: any;
}

export const NodePropertiesPanel: React.FC<NodePropertiesPanelProps> = ({
  isOpen,
  selectedNode,
  onClose,
  onUpdateNode,
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
    shadowColor: 'rgba(0, 0, 0, 0.3)',
    shadowLg: '0 10px 15px -3px rgba(0, 0, 0, 0.3)'
  }
}) => {
  const [config, setConfig] = useState<NodeConfig>({});
  const [label, setLabel] = useState('');

  useEffect(() => {
    if (selectedNode) {
      setLabel(selectedNode.data.label);
      setConfig(selectedNode.data.config || {});
    }
  }, [selectedNode]);

  const handleSave = () => {
    if (selectedNode) {
      onUpdateNode(selectedNode.id, {
        label,
        config
      });
    }
  };

  const renderConfigFields = () => {
    if (!selectedNode) return null;

    const { type } = selectedNode.data;

    switch (type) {
      case 'ollama':
        return (
          <>
            <div style={{ marginBottom: '16px' }}>
              <label style={{
                display: 'block',
                fontSize: '12px',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '4px'
              }}>
                Model Name
              </label>
              <input
                type="text"
                value={config.model || ''}
                onChange={(e) => setConfig({ ...config, model: e.target.value })}
                placeholder="llama2, codellama, mistral..."
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #d1d5db',
                  borderRadius: '4px',
                  fontSize: '14px'
                }}
              />
            </div>
            <div style={{ marginBottom: '16px' }}>
              <label style={{
                display: 'block',
                fontSize: '12px',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '4px'
              }}>
                Temperature
              </label>
              <input
                type="number"
                min="0"
                max="2"
                step="0.1"
                value={config.temperature || 0.7}
                onChange={(e) => setConfig({ ...config, temperature: parseFloat(e.target.value) })}
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #d1d5db',
                  borderRadius: '4px',
                  fontSize: '14px'
                }}
              />
            </div>
          </>
        );

      case 'openai':
        return (
          <>
            <div style={{ marginBottom: '16px' }}>
              <label style={{
                display: 'block',
                fontSize: '12px',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '4px'
              }}>
                Model
              </label>
              <select
                value={config.model || 'gpt-3.5-turbo'}
                onChange={(e) => setConfig({ ...config, model: e.target.value })}
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #d1d5db',
                  borderRadius: '4px',
                  fontSize: '14px'
                }}
              >
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-4-turbo">GPT-4 Turbo</option>
              </select>
            </div>
            <div style={{ marginBottom: '16px' }}>
              <label style={{
                display: 'block',
                fontSize: '12px',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '4px'
              }}>
                Max Tokens
              </label>
              <input
                type="number"
                value={config.max_tokens || 1000}
                onChange={(e) => setConfig({ ...config, max_tokens: parseInt(e.target.value) })}
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #d1d5db',
                  borderRadius: '4px',
                  fontSize: '14px'
                }}
              />
            </div>
          </>
        );

      case 'claude':
        return (
          <>
            <div style={{ marginBottom: '16px' }}>
              <label style={{
                display: 'block',
                fontSize: '12px',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '4px'
              }}>
                Model
              </label>
              <select
                value={config.model || 'claude-3-sonnet-20240229'}
                onChange={(e) => setConfig({ ...config, model: e.target.value })}
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #d1d5db',
                  borderRadius: '4px',
                  fontSize: '14px'
                }}
              >
                <option value="claude-3-sonnet-20240229">Claude 3 Sonnet</option>
                <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                <option value="claude-3-haiku-20240307">Claude 3 Haiku</option>
              </select>
            </div>
            <div style={{ marginBottom: '16px' }}>
              <label style={{
                display: 'block',
                fontSize: '12px',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '4px'
              }}>
                Max Tokens
              </label>
              <input
                type="number"
                value={config.max_tokens || 1000}
                onChange={(e) => setConfig({ ...config, max_tokens: parseInt(e.target.value) })}
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #d1d5db',
                  borderRadius: '4px',
                  fontSize: '14px'
                }}
              />
            </div>
          </>
        );

      case 'input':
        return (
          <div style={{ marginBottom: '16px' }}>
            <label style={{
              display: 'block',
              fontSize: '12px',
              fontWeight: '600',
              color: '#374151',
              marginBottom: '4px'
            }}>
              Input Type
            </label>
            <select
              value={config.inputType || 'text'}
              onChange={(e) => setConfig({ ...config, inputType: e.target.value })}
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid #d1d5db',
                borderRadius: '4px',
                fontSize: '14px'
              }}
            >
              <option value="text">Text</option>
              <option value="file">File</option>
              <option value="json">JSON</option>
            </select>
          </div>
        );

      case 'transform':
        return (
          <div style={{ marginBottom: '16px' }}>
            <label style={{
              display: 'block',
              fontSize: '12px',
              fontWeight: '600',
              color: '#374151',
              marginBottom: '4px'
            }}>
              Transform Function
            </label>
            <textarea
              value={config.function || ''}
              onChange={(e) => setConfig({ ...config, function: e.target.value })}
              placeholder="// JavaScript function to transform data
function transform(input) {
  return input.toUpperCase();
}"
              style={{
                width: '100%',
                minHeight: '120px',
                padding: '8px',
                border: '1px solid #d1d5db',
                borderRadius: '4px',
                fontSize: '12px',
                fontFamily: 'monospace',
                resize: 'vertical'
              }}
            />
          </div>
        );

      default:
        return null;
    }
  };

  if (!isOpen || !selectedNode) return null;

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div style={{
        padding: '20px 20px 16px',
        borderBottom: '1px solid rgba(0, 0, 0, 0.1)',
        background: 'rgba(255, 255, 255, 0.7)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <h3 style={{
          margin: 0,
          fontSize: '18px',
          fontWeight: '600',
          color: theme.textColor,
          letterSpacing: '-0.025em'
        }}>
          Node Properties
        </h3>
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            fontSize: '18px',
            cursor: 'pointer',
            color: `${theme.textColor}99`,
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.2s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(0, 0, 0, 0.05)';
            e.currentTarget.style.color = '#374151';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'none';
            e.currentTarget.style.color = '#6b7280';
          }}
        >
          ✕
        </button>
      </div>

      {/* Content */}
      <div style={{
        padding: '20px',
        flex: 1,
        overflowY: 'auto'
      }}>
        {/* Node Label */}
        <div style={{ marginBottom: '16px' }}>
          <label style={{
            display: 'block',
            fontSize: '12px',
            fontWeight: '600',
            color: '#374151',
            marginBottom: '4px'
          }}>
            Node Label
          </label>
          <input
            type="text"
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            style={{
              width: '100%',
              padding: '8px',
              border: '1px solid #d1d5db',
              borderRadius: '4px',
              fontSize: '14px'
            }}
          />
        </div>

        {/* Node Type */}
        <div style={{ marginBottom: '16px' }}>
          <label style={{
            display: 'block',
            fontSize: '12px',
            fontWeight: '600',
            color: '#374151',
            marginBottom: '4px'
          }}>
            Node Type
          </label>
          <div style={{
            padding: '8px',
            background: '#f3f4f6',
            borderRadius: '4px',
            fontSize: '14px',
            color: '#6b7280'
          }}>
            {selectedNode.data.type.toUpperCase()}
          </div>
        </div>

        {/* Node-specific Config */}
        {renderConfigFields()}

        {/* System Prompt for AI nodes */}
        {['ollama', 'openai', 'claude'].includes(selectedNode.data.type) && (
          <div style={{ marginBottom: '16px' }}>
            <label style={{
              display: 'block',
              fontSize: '12px',
              fontWeight: '600',
              color: '#374151',
              marginBottom: '4px'
            }}>
              System Prompt
            </label>
            <textarea
              value={config.system_prompt || ''}
              onChange={(e) => setConfig({ ...config, system_prompt: e.target.value })}
              placeholder="You are a helpful assistant..."
              style={{
                width: '100%',
                minHeight: '80px',
                padding: '8px',
                border: '1px solid #d1d5db',
                borderRadius: '4px',
                fontSize: '14px',
                resize: 'vertical'
              }}
            />
          </div>
        )}
      </div>

      {/* Footer */}
      <div style={{
        padding: '16px',
        borderTop: '1px solid #e5e7eb',
        background: '#f9fafb',
        display: 'flex',
        gap: '8px'
      }}>
        <button
          onClick={handleSave}
          style={{
            flex: 1,
            padding: '8px 16px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500'
          }}
        >
          Save Changes
        </button>
        <button
          onClick={onClose}
          style={{
            padding: '8px 16px',
            background: '#6b7280',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500'
          }}
        >
          Cancel
        </button>
      </div>
    </div>
  );
};

export default NodePropertiesPanel;
