/**
 * Dynamic Node Configuration Panel
 * Sử dụng component metadata từ backend để render form động
 */
import { useState, useEffect } from 'react';
import { Node } from 'reactflow';
import { useWorkflowComponents } from '../../hooks/useEnhancedWorkflow';

interface DynamicNodeConfigPanelProps {
  node: Node;
  onUpdateNode: (nodeId: string, newData: any) => void;
  onDeleteNode: (nodeId: string) => void;
}

export default function DynamicNodeConfigPanel({ 
  node, 
  onUpdateNode, 
  onDeleteNode 
}: DynamicNodeConfigPanelProps) {
  const { components } = useWorkflowComponents();
  const [formData, setFormData] = useState(node.data?.config || {});

  // Tìm component metadata
  const componentMetadata = components.find(c => c.type === node.type);

  useEffect(() => {
    setFormData(node.data?.config || {});
  }, [node]);

  const handleInputChange = (field: string, value: any) => {
    const newFormData = { ...formData, [field]: value };
    setFormData(newFormData);
    
    // Update node với config mới
    const newData = {
      ...node.data,
      config: newFormData
    };
    onUpdateNode(node.id, newData);
  };

  const renderParameterInput = (parameter: any) => {
    const value = formData[parameter.name] ?? parameter.default_value ?? '';

    switch (parameter.type) {
      case 'string':
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => handleInputChange(parameter.name, e.target.value)}
            placeholder={parameter.description || `Enter ${parameter.label}`}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            required={parameter.required}
          />
        );

      case 'number':
        return (
          <input
            type="number"
            value={value}
            onChange={(e) => handleInputChange(parameter.name, parseFloat(e.target.value) || 0)}
            placeholder={parameter.description || `Enter ${parameter.label}`}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            required={parameter.required}
          />
        );

      case 'boolean':
        return (
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={value}
              onChange={(e) => handleInputChange(parameter.name, e.target.checked)}
              className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            />
            <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
              {parameter.description || 'Enable this option'}
            </span>
          </label>
        );

      case 'select':
        return (
          <select
            value={value}
            onChange={(e) => handleInputChange(parameter.name, e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            required={parameter.required}
          >
            {parameter.options?.map((option: any) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case 'textarea':
        return (
          <textarea
            value={value}
            onChange={(e) => handleInputChange(parameter.name, e.target.value)}
            placeholder={parameter.description || `Enter ${parameter.label}`}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            required={parameter.required}
          />
        );

      case 'json':
        return (
          <textarea
            value={typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
            onChange={(e) => {
              try {
                const jsonValue = JSON.parse(e.target.value);
                handleInputChange(parameter.name, jsonValue);
              } catch {
                // Nếu JSON không hợp lệ, giữ nguyên string
                handleInputChange(parameter.name, e.target.value);
              }
            }}
            placeholder={parameter.description || 'Enter valid JSON'}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white font-mono text-sm"
            required={parameter.required}
          />
        );

      case 'file':
        return (
          <input
            type="file"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) {
                // Trong thực tế, bạn sẽ upload file lên server
                handleInputChange(parameter.name, file.name);
              }
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            required={parameter.required}
          />
        );

      default:
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => handleInputChange(parameter.name, e.target.value)}
            placeholder={parameter.description || `Enter ${parameter.label}`}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            required={parameter.required}
          />
        );
    }
  };

  if (!componentMetadata) {
    return (
      <div className="p-4">
        <div className="text-yellow-600 bg-yellow-100 dark:bg-yellow-900 dark:text-yellow-300 p-3 rounded-lg">
          <h4 className="font-medium">Unknown Component Type</h4>
          <p className="text-sm mt-1">
            No metadata found for component type: {node.type}
          </p>
        </div>
        
        <div className="mt-4 space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Node Label
            </label>
            <input
              type="text"
              value={node.data?.label || ''}
              onChange={(e) => onUpdateNode(node.id, { ...node.data, label: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>
          
          <button
            onClick={() => onDeleteNode(node.id)}
            className="w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Delete Node
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Component Info */}
      <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
        <h4 className="font-medium text-gray-900 dark:text-white">
          {componentMetadata.name}
        </h4>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          {componentMetadata.description}
        </p>
      </div>

      {/* Node Label */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Node Label
        </label>
        <input
          type="text"
          value={node.data?.label || componentMetadata.name}
          onChange={(e) => onUpdateNode(node.id, { ...node.data, label: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
        />
      </div>

      {/* Dynamic Parameters */}
      {componentMetadata.parameters && componentMetadata.parameters.length > 0 && (
        <div className="space-y-4">
          <h5 className="font-medium text-gray-900 dark:text-white">Configuration</h5>
          
          {componentMetadata.parameters.map((parameter) => (
            <div key={parameter.name}>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {parameter.label}
                {parameter.required && <span className="text-red-500 ml-1">*</span>}
              </label>
              
              {renderParameterInput(parameter)}
              
              {parameter.description && (
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {parameter.description}
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Component Handles Info */}
      {(componentMetadata.input_handles.length > 0 || componentMetadata.output_handles.length > 0) && (
        <div className="bg-blue-50 dark:bg-blue-900 p-3 rounded-lg">
          <h5 className="font-medium text-blue-900 dark:text-blue-100 mb-2">Connection Points</h5>
          
          {componentMetadata.input_handles.length > 0 && (
            <div className="mb-2">
              <p className="text-sm text-blue-700 dark:text-blue-300 font-medium">Inputs:</p>
              <ul className="text-xs text-blue-600 dark:text-blue-400 ml-4">
                {componentMetadata.input_handles.map((handle) => (
                  <li key={handle.id}>• {handle.label || handle.id}</li>
                ))}
              </ul>
            </div>
          )}
          
          {componentMetadata.output_handles.length > 0 && (
            <div>
              <p className="text-sm text-blue-700 dark:text-blue-300 font-medium">Outputs:</p>
              <ul className="text-xs text-blue-600 dark:text-blue-400 ml-4">
                {componentMetadata.output_handles.map((handle) => (
                  <li key={handle.id}>• {handle.label || handle.id}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex space-x-2 pt-4 border-t border-gray-200 dark:border-gray-600">
        <button
          onClick={() => onDeleteNode(node.id)}
          className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Delete Node
        </button>
      </div>
    </div>
  );
}
