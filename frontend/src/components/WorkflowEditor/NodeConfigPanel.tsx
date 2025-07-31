/**
 * Node Configuration Panel
 */
import { useState, useEffect } from 'react';
import { Node } from 'reactflow';

interface NodeConfigPanelProps {
  node: Node;
  onUpdateNode: (nodeId: string, newData: any) => void;
  onDeleteNode: (nodeId: string) => void;
}

export default function NodeConfigPanel({ node, onUpdateNode, onDeleteNode }: NodeConfigPanelProps) {
  const [formData, setFormData] = useState(node.data || {});

  useEffect(() => {
    setFormData(node.data || {});
  }, [node]);

  const handleInputChange = (field: string, value: any) => {
    const newData = { ...formData, [field]: value };
    setFormData(newData);
    onUpdateNode(node.id, newData);
  };

  const renderConfigForm = () => {
    switch (node.type) {
      case 'googleSheets':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Sheet Name
              </label>
              <input
                type="text"
                value={formData.sheetName || ''}
                onChange={(e) => handleInputChange('sheetName', e.target.value)}
                placeholder="e.g., Product Data"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Sheet ID
              </label>
              <input
                type="text"
                value={formData.sheetId || ''}
                onChange={(e) => handleInputChange('sheetId', e.target.value)}
                placeholder="Google Sheets ID"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Range
              </label>
              <input
                type="text"
                value={formData.range || 'A1:Z1000'}
                onChange={(e) => handleInputChange('range', e.target.value)}
                placeholder="A1:Z1000"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        );

      case 'aiProcessing':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                AI Provider
              </label>
              <select
                value={formData.provider || 'openai'}
                onChange={(e) => handleInputChange('provider', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="openai">OpenAI</option>
                <option value="claude">Anthropic Claude</option>
                <option value="ollama">Ollama (Local)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Model
              </label>
              <input
                type="text"
                value={formData.model || 'gpt-4o'}
                onChange={(e) => handleInputChange('model', e.target.value)}
                placeholder="gpt-4o, claude-3-5-sonnet, llama3.2"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Output Format
              </label>
              <select
                value={formData.outputFormat || 'text'}
                onChange={(e) => handleInputChange('outputFormat', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="text">Text</option>
                <option value="png">Image (PNG)</option>
                <option value="jpg">Image (JPG)</option>
                <option value="mp3">Audio (MP3)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Prompt Template
              </label>
              <textarea
                value={formData.prompt || ''}
                onChange={(e) => handleInputChange('prompt', e.target.value)}
                placeholder="Create a product description for: {input_data}"
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        );

      case 'googleDrive':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Folder ID
              </label>
              <input
                type="text"
                value={formData.folderId || ''}
                onChange={(e) => handleInputChange('folderId', e.target.value)}
                placeholder="Google Drive folder ID"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                File Name Pattern
              </label>
              <input
                type="text"
                value={formData.fileNamePattern || ''}
                onChange={(e) => handleInputChange('fileNamePattern', e.target.value)}
                placeholder="output_{timestamp}.txt"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        );

      case 'notification':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Notification Type
              </label>
              <select
                value={formData.type || 'email'}
                onChange={(e) => handleInputChange('type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="email">Email</option>
                <option value="slack">Slack</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Recipients
              </label>
              <input
                type="text"
                value={formData.recipients || ''}
                onChange={(e) => handleInputChange('recipients', e.target.value)}
                placeholder="email@example.com or #channel"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Message Template
              </label>
              <textarea
                value={formData.message || ''}
                onChange={(e) => handleInputChange('message', e.target.value)}
                placeholder="Workflow completed successfully! Results: {output_data}"
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        );

      case 'condition':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Condition Type
              </label>
              <select
                value={formData.conditionType || 'equals'}
                onChange={(e) => handleInputChange('conditionType', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="equals">Equals</option>
                <option value="not_equals">Not Equals</option>
                <option value="contains">Contains</option>
                <option value="greater_than">Greater Than</option>
                <option value="less_than">Less Than</option>
                <option value="is_empty">Is Empty</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Value to Compare
              </label>
              <input
                type="text"
                value={formData.compareValue || ''}
                onChange={(e) => handleInputChange('compareValue', e.target.value)}
                placeholder="comparison value"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        );

      case 'delay':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Duration
              </label>
              <input
                type="number"
                value={formData.duration || 5}
                onChange={(e) => handleInputChange('duration', parseInt(e.target.value))}
                min="1"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Unit
              </label>
              <select
                value={formData.unit || 'minutes'}
                onChange={(e) => handleInputChange('unit', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="seconds">Seconds</option>
                <option value="minutes">Minutes</option>
                <option value="hours">Hours</option>
                <option value="days">Days</option>
              </select>
            </div>
          </div>
        );

      case 'start':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Trigger Type
              </label>
              <select
                value={formData.trigger || 'manual'}
                onChange={(e) => handleInputChange('trigger', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="manual">Manual</option>
                <option value="schedule">Scheduled</option>
                <option value="webhook">Webhook</option>
                <option value="file_upload">File Upload</option>
              </select>
            </div>
            {formData.trigger === 'schedule' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Cron Expression
                </label>
                <input
                  type="text"
                  value={formData.schedule || ''}
                  onChange={(e) => handleInputChange('schedule', e.target.value)}
                  placeholder="0 9 * * 1-5 (Daily at 9 AM, weekdays)"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            )}
          </div>
        );

      default:
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Label
              </label>
              <input
                type="text"
                value={formData.label || ''}
                onChange={(e) => handleInputChange('label', e.target.value)}
                placeholder="Node label"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        );
    }
  };

  return (
    <div className="w-80 bg-white border-l border-gray-200 p-4 overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">
          Configure Node
        </h3>
      </div>

      {/* Node Info */}
      <div className="mb-4 p-3 bg-gray-50 rounded-lg">
        <div className="text-sm font-medium text-gray-600">Node Type</div>
        <div className="text-sm text-gray-800 capitalize">{node.type?.replace(/([A-Z])/g, ' $1')}</div>
        <div className="text-xs text-gray-500 mt-1">ID: {node.id}</div>
      </div>

      {/* Configuration Form */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Configuration</h4>
        {renderConfigForm()}
      </div>

      {/* Actions */}
      <div className="space-y-2">
        <button
          onClick={() => onDeleteNode(node.id)}
          className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors flex items-center justify-center space-x-2"
        >
          <span>🗑️</span>
          <span>Delete Node</span>
        </button>
        
        <div className="text-xs text-gray-500 p-2 bg-gray-50 rounded">
          💡 Tip: Changes are saved automatically as you type
        </div>
      </div>
    </div>
  );
}
