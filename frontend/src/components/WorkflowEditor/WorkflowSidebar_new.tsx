/**
 * Workflow Sidebar - n8n Style Component Palette
 */
import React from 'react';

interface ComponentItem {
  type: string;
  label: string;
  description: string;
  icon: string;
  category: string;
  color: string;
}

const workflowComponents: ComponentItem[] = [
  // Trigger nodes
  {
    type: 'start',
    label: 'Manual Trigger',
    description: 'Workflow trigger point',
    icon: '▶️',
    category: 'Triggers',
    color: 'bg-green-500'
  },
  {
    type: 'schedule',
    label: 'Schedule',
    description: 'Time-based trigger',
    icon: '⏰',
    category: 'Triggers',
    color: 'bg-blue-500'
  },
  {
    type: 'webhook',
    label: 'Webhook',
    description: 'HTTP trigger',
    icon: '🔗',
    category: 'Triggers',
    color: 'bg-purple-500'
  },

  // Data sources
  {
    type: 'sheets',
    label: 'Google Sheets',
    description: 'Read data from Google Sheets',
    icon: '📊',
    category: 'Data Sources',
    color: 'bg-green-600'
  },
  {
    type: 'database',
    label: 'Database',
    description: 'Database operations',
    icon: '🗄️',
    category: 'Data Sources',
    color: 'bg-gray-600'
  },
  {
    type: 'api',
    label: 'HTTP Request',
    description: 'Make HTTP requests',
    icon: '🌐',
    category: 'Data Sources',
    color: 'bg-blue-600'
  },

  // AI & Processing
  {
    type: 'ai',
    label: 'AI Processing',
    description: 'OpenAI, Claude, Ollama',
    icon: '🧠',
    category: 'AI & Processing',
    color: 'bg-indigo-600'
  },
  {
    type: 'transform',
    label: 'Data Transform',
    description: 'Transform and manipulate data',
    icon: '🔄',
    category: 'AI & Processing',
    color: 'bg-orange-500'
  },
  {
    type: 'filter',
    label: 'Filter',
    description: 'Filter data based on conditions',
    icon: '🔍',
    category: 'AI & Processing',
    color: 'bg-yellow-500'
  },

  // Control Flow
  {
    type: 'condition',
    label: 'If/Condition',
    description: 'Conditional logic (if/then/else)',
    icon: '🔀',
    category: 'Control Flow',
    color: 'bg-purple-600'
  },
  {
    type: 'delay',
    label: 'Wait/Delay',
    description: 'Wait for specified time',
    icon: '⏸️',
    category: 'Control Flow',
    color: 'bg-gray-500'
  },
  {
    type: 'loop',
    label: 'Loop',
    description: 'Iterate over data',
    icon: '🔁',
    category: 'Control Flow',
    color: 'bg-cyan-500'
  },

  // Output & Actions
  {
    type: 'drive',
    label: 'Google Drive',
    description: 'Save files to Google Drive',
    icon: '💾',
    category: 'Output & Actions',
    color: 'bg-blue-700'
  },
  {
    type: 'notification',
    label: 'Send Notification',
    description: 'Email or Slack notification',
    icon: '📧',
    category: 'Output & Actions',
    color: 'bg-red-500'
  },
  {
    type: 'analytics',
    label: 'Analytics',
    description: 'Track and analyze workflow data',
    icon: '📈',
    category: 'Output & Actions',
    color: 'bg-pink-500'
  },
  {
    type: 'end',
    label: 'End',
    description: 'Workflow completion point',
    icon: '🏁',
    category: 'Output & Actions',
    color: 'bg-red-600'
  }
];

const categories = [
  'Triggers',
  'Data Sources', 
  'AI & Processing',
  'Control Flow',
  'Output & Actions'
];

const WorkflowSidebar: React.FC = () => {
  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <div className="w-80 h-full bg-white border-r border-gray-200 pt-16 overflow-y-auto">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded flex items-center justify-center">
            <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <h2 className="text-lg font-semibold text-gray-900">Workflow Components</h2>
        </div>
        <p className="text-sm text-gray-600">
          Drag components to the canvas to build your workflow
        </p>
      </div>

      {/* Search */}
      <div className="p-4 border-b border-gray-200">
        <div className="relative">
          <input
            type="text"
            placeholder="Search components..."
            className="w-full pl-8 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      {/* Components by Category */}
      <div className="p-4 space-y-6">
        {categories.map((category) => {
          const categoryComponents = workflowComponents.filter(comp => comp.category === category);
          
          return (
            <div key={category} className="space-y-3">
              <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider">
                {category}
              </h3>
              
              <div className="space-y-2">
                {categoryComponents.map((component) => (
                  <div
                    key={component.type}
                    draggable
                    onDragStart={(event) => onDragStart(event, component.type)}
                    className="group flex items-center p-3 bg-gray-50 hover:bg-gray-100 rounded-lg cursor-grab active:cursor-grabbing transition-all duration-200 border border-transparent hover:border-gray-200 hover:shadow-sm"
                  >
                    <div className={`w-8 h-8 ${component.color} rounded-lg flex items-center justify-center text-white text-sm font-semibold mr-3 group-hover:scale-105 transition-transform`}>
                      {component.icon}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-900 group-hover:text-gray-700">
                        {component.label}
                      </div>
                      <div className="text-xs text-gray-500 truncate">
                        {component.description}
                      </div>
                    </div>
                    
                    <svg className="w-4 h-4 text-gray-400 group-hover:text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Help Section */}
      <div className="p-4 mt-6 border-t border-gray-200">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div className="flex items-start gap-2">
            <svg className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <div className="text-sm font-medium text-blue-900 mb-1">
                How to use:
              </div>
              <ul className="text-xs text-blue-700 space-y-1">
                <li>• Drag components to canvas</li>
                <li>• Connect nodes with edges</li>
                <li>• Click nodes to configure</li>
                <li>• Save and execute workflows</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkflowSidebar;
