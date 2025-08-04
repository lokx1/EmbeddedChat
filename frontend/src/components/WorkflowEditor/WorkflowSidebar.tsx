/**
 * Workflow Sidebar - Modern Component Palette
 */
import React, { useState } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import {
  PlayIcon,
  ClockIcon,
  LinkIcon,
  TableCellsIcon,
  CircleStackIcon,
  GlobeAltIcon,
  BoltIcon,
  ArrowsRightLeftIcon,
  MagnifyingGlassIcon,
  CodeBracketSquareIcon,
  PauseIcon,
  ArrowPathIcon,
  CloudIcon,
  BellIcon,
  CloudArrowUpIcon,
  ChartBarIcon,
  FlagIcon
} from '@heroicons/react/24/outline';

interface WorkflowSidebarProps {
  isOpen?: boolean;
  onToggle?: () => void;
}

interface ComponentItem {
  type: string;
  label: string;
  description: string;
  IconComponent: React.ComponentType<{ className?: string }>;
  category: string;
  color: string;
}

const workflowComponents: ComponentItem[] = [
  // Trigger nodes
  {
    type: 'start',
    label: 'Manual Trigger',
    description: 'Workflow trigger point',
    IconComponent: PlayIcon,
    category: 'Triggers',
    color: 'from-emerald-500 via-emerald-600 to-teal-600'
  },
  {
    type: 'schedule',
    label: 'Schedule',
    description: 'Time-based trigger',
    IconComponent: ClockIcon,
    category: 'Triggers',
    color: 'from-blue-500 via-blue-600 to-cyan-600'
  },
  {
    type: 'webhook',
    label: 'Webhook',
    description: 'HTTP trigger',
    IconComponent: LinkIcon,
    category: 'Triggers',
    color: 'from-violet-500 via-purple-500 to-purple-600'
  },

  // Data sources
  {
    type: 'google_sheets',
    label: 'Google Sheets',
    description: 'Read data from Google Sheets',
    IconComponent: TableCellsIcon,
    category: 'Data Sources',
    color: 'from-green-500 via-emerald-600 to-green-700'
  },
  {
    type: 'google_sheets_write',
    label: 'Google Sheets Write',
    description: 'Write data to Google Sheets',
    IconComponent: TableCellsIcon,
    category: 'Output & Actions',
    color: 'from-blue-500 via-blue-600 to-indigo-700'
  },
  {
    type: 'google_drive_write',
    label: 'Google Drive Write',
    description: 'Save files to Google Drive',
    IconComponent: CloudArrowUpIcon,
    category: 'Output & Actions',
    color: 'from-purple-500 via-purple-600 to-purple-700'
  },
  {
    type: 'database',
    label: 'Database',
    description: 'Database operations',
    IconComponent: CircleStackIcon,
    category: 'Data Sources',
    color: 'from-slate-500 via-gray-600 to-slate-700'
  },
  {
    type: 'api',
    label: 'HTTP Request',
    description: 'Make HTTP requests',
    IconComponent: GlobeAltIcon,
    category: 'Data Sources',
    color: 'from-sky-500 via-blue-600 to-indigo-600'
  },

  // AI & Processing
  {
    type: 'ai',
    label: 'AI Processing',
    description: 'OpenAI, Claude, Ollama',
    IconComponent: BoltIcon,
    category: 'AI & Processing',
    color: 'from-indigo-500 via-purple-600 to-violet-700'
  },
  {
    type: 'transform',
    label: 'Data Transform',
    description: 'Transform and manipulate data',
    IconComponent: ArrowsRightLeftIcon,
    category: 'AI & Processing',
    color: 'from-amber-500 via-orange-500 to-orange-600'
  },
  {
    type: 'filter',
    label: 'Filter',
    description: 'Filter data based on conditions',
    IconComponent: MagnifyingGlassIcon,
    category: 'AI & Processing',
    color: 'from-yellow-400 via-amber-500 to-orange-500'
  },

  // Control Flow
  {
    type: 'condition',
    label: 'If/Condition',
    description: 'Conditional logic (if/then/else)',
    IconComponent: CodeBracketSquareIcon,
    category: 'Control Flow',
    color: 'from-purple-500 via-violet-600 to-indigo-600'
  },
  {
    type: 'delay',
    label: 'Wait/Delay',
    description: 'Wait for specified time',
    IconComponent: PauseIcon,
    category: 'Control Flow',
    color: 'from-gray-400 via-slate-500 to-gray-600'
  },
  {
    type: 'loop',
    label: 'Loop',
    description: 'Iterate over data',
    IconComponent: ArrowPathIcon,
    category: 'Control Flow',
    color: 'from-cyan-400 via-cyan-500 to-blue-600'
  },

  // Output & Actions
  {
    type: 'drive',
    label: 'Google Drive',
    description: 'Save files to Google Drive',
    IconComponent: CloudIcon,
    category: 'Output & Actions',
    color: 'from-blue-600 via-indigo-600 to-blue-800'
  },
  {
    type: 'notification',
    label: 'Send Notification',
    description: 'Email or Slack notification',
    IconComponent: BellIcon,
    category: 'Output & Actions',
    color: 'from-rose-500 via-pink-500 to-rose-600'
  },
  {
    type: 'analytics',
    label: 'Analytics',
    description: 'Track and analyze workflow data',
    IconComponent: ChartBarIcon,
    category: 'Output & Actions',
    color: 'from-pink-500 via-rose-500 to-red-500'
  },
  {
    type: 'end',
    label: 'End',
    description: 'Workflow completion point',
    IconComponent: FlagIcon,
    category: 'Output & Actions',
    color: 'from-red-500 via-rose-600 to-red-700'
  },

  // Additional test components to ensure scrolling
  {
    type: 'email',
    label: 'Send Email',
    description: 'Send email notifications',
    IconComponent: BellIcon,
    category: 'Output & Actions',
    color: 'from-blue-500 via-indigo-500 to-purple-500'
  },
  {
    type: 'slack',
    label: 'Slack Message',
    description: 'Send Slack messages',
    IconComponent: BellIcon,
    category: 'Output & Actions',
    color: 'from-green-500 via-emerald-500 to-teal-500'
  },
  {
    type: 'webhook-send',
    label: 'Send Webhook',
    description: 'Send HTTP webhook',
    IconComponent: LinkIcon,
    category: 'Output & Actions',
    color: 'from-orange-500 via-red-500 to-pink-500'
  },
  {
    type: 'file-upload',
    label: 'File Upload',
    description: 'Upload files to storage',
    IconComponent: CloudIcon,
    category: 'Output & Actions',
    color: 'from-violet-500 via-purple-500 to-indigo-500'
  },
  {
    type: 'database-write',
    label: 'Database Write',
    description: 'Write data to database',
    IconComponent: CircleStackIcon,
    category: 'Data Sources',
    color: 'from-gray-500 via-slate-600 to-gray-700'
  }
];

const categories = [
  'Triggers',
  'Data Sources', 
  'AI & Processing',
  'Control Flow',
  'Output & Actions'
];

const WorkflowSidebar: React.FC<WorkflowSidebarProps> = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const { isDark } = useTheme() || { isDark: false }; // Fallback for theme

  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  // Filter components based on search term and selected category
  const filteredComponents = workflowComponents.filter(component => {
    const matchesSearch = component.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         component.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = !selectedCategory || component.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const filteredCategories = categories.filter(category => 
    workflowComponents.some(comp => 
      comp.category === category && 
      comp.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
      comp.description.toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  return (
    <div className={`w-80 h-full border-r flex flex-col flex-shrink-0 transition-all duration-300 ${
      isDark 
        ? 'bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900 border-gray-700/70' 
        : 'bg-gradient-to-b from-white via-gray-50 to-white border-gray-200/70'
    }`}>
      {/* Header */}
      <div className={`p-5 border-b transition-colors duration-300 flex-shrink-0 ${
        isDark ? 'border-gray-700/50 bg-gray-800/30' : 'border-gray-200/50 bg-white/50'
      } backdrop-blur-sm`}>
        <div className="flex items-center gap-3 mb-3">
          <div className="w-9 h-9 bg-gradient-to-br from-blue-500 via-purple-500 to-violet-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/25">
            <BoltIcon className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className={`text-lg font-bold transition-colors duration-300 ${
              isDark ? 'text-gray-100' : 'text-gray-900'
            }`}>
              Components
            </h2>
          </div>
        </div>
        <p className={`text-sm leading-relaxed transition-colors duration-300 ${
          isDark ? 'text-gray-400' : 'text-gray-600'
        }`}>
          Drag components to build your workflow
        </p>
        
        {/* Scroll indicator */}
        {workflowComponents.length > 8 && (
          <div className={`text-xs mt-2 flex items-center gap-2 transition-all duration-300 ${
            isDark ? 'text-blue-400/80' : 'text-blue-600/80'
          }`}>
            <svg className="w-3 h-3 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
            <span className="text-xs">Scroll for more ({workflowComponents.length} total)</span>
          </div>
        )}
      </div>

      {/* Search */}
      <div className={`p-4 border-b transition-colors duration-300 flex-shrink-0 ${
        isDark ? 'border-gray-700/50' : 'border-gray-200/50'
      }`}>
        <div className="relative">
          <input
            type="text"
            placeholder="Search components..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={`w-full pl-11 pr-4 py-3 border rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 ${
              isDark 
                ? 'bg-gray-800/50 border-gray-600/50 text-gray-100 placeholder-gray-400 focus:bg-gray-800' 
                : 'bg-white/80 border-gray-300/60 text-gray-900 placeholder-gray-500 focus:bg-white'
            } backdrop-blur-sm`}
          />
          <MagnifyingGlassIcon className={`absolute left-4 top-1/2 transform -translate-y-1/2 w-4 h-4 transition-colors duration-300 ${
            isDark ? 'text-gray-400' : 'text-gray-500'
          }`} />
        </div>

        {/* Category Filter */}
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedCategory(null)}
            className={`px-3 py-1.5 text-xs font-medium rounded-full transition-all duration-200 ${
              !selectedCategory
                ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/25'
                : isDark
                  ? 'bg-gray-700/60 text-gray-300 hover:bg-gray-600/60 border border-gray-600/30'
                  : 'bg-gray-100/80 text-gray-600 hover:bg-gray-200/80 border border-gray-200/50'
            }`}
          >
            All
          </button>
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-3 py-1.5 text-xs font-medium rounded-full transition-all duration-200 ${
                selectedCategory === category
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/25'
                  : isDark
                    ? 'bg-gray-700/60 text-gray-300 hover:bg-gray-600/60 border border-gray-600/30'
                    : 'bg-gray-100/80 text-gray-600 hover:bg-gray-200/80 border border-gray-200/50'
              }`}
            >
              {category}
            </button>
          ))}
        </div>
      </div>

      {/* Components by Category - Scrollable Area */}
      <div 
        className={`flex-1 overflow-y-scroll workflow-sidebar-scroll`}
        style={{
          maxHeight: 'calc(100vh - 280px)', // Increased scroll area even more
          minHeight: '350px'
        }}
      >
        <div className="px-4 pt-4 pb-24 space-y-6">
        {filteredCategories.map((category) => {
          const categoryComponents = filteredComponents.filter(comp => comp.category === category);
          
          if (categoryComponents.length === 0) return null;
          
          return (
            <div key={category} className="space-y-3">
              <div className="flex items-center gap-3">
                <h3 className={`text-sm font-bold uppercase tracking-wide transition-colors duration-300 ${
                  isDark ? 'text-gray-300' : 'text-gray-700'
                }`}>
                  {category}
                </h3>
                <div className={`flex-1 h-px transition-colors duration-300 ${
                  isDark ? 'bg-gradient-to-r from-gray-700 to-transparent' : 'bg-gradient-to-r from-gray-200 to-transparent'
                }`} />
                <span className={`text-xs font-medium px-2 py-1 rounded-full transition-colors duration-300 ${
                  isDark ? 'text-gray-400 bg-gray-700/50' : 'text-gray-500 bg-gray-100/80'
                }`}>
                  {categoryComponents.length}
                </span>
              </div>
              
              <div className="space-y-2">
                {categoryComponents.map((component) => {
                  const IconComponent = component.IconComponent;
                  return (
                    <div
                      key={component.type}
                      draggable
                      onDragStart={(event) => onDragStart(event, component.type)}
                      className={`group flex items-center p-3 rounded-xl cursor-grab active:cursor-grabbing transition-all duration-300 border backdrop-blur-sm hover:shadow-xl hover:shadow-black/10 hover:scale-[1.02] active:scale-[0.98] ${
                        isDark 
                          ? 'bg-gray-800/40 hover:bg-gray-700/60 border-gray-700/50 hover:border-gray-600/50' 
                          : 'bg-white/70 hover:bg-white/90 border-gray-200/60 hover:border-gray-300/60'
                      }`}
                    >
                      <div className={`w-10 h-10 bg-gradient-to-br ${component.color} rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-110 group-hover:rotate-3`}>
                        <IconComponent className="w-5 h-5 text-white drop-shadow-sm" />
                      </div>
                      
                      <div className="flex-1 min-w-0 ml-3">
                        <div className={`text-sm font-semibold mb-1 transition-colors duration-300 ${
                          isDark ? 'text-gray-100 group-hover:text-white' : 'text-gray-900 group-hover:text-gray-700'
                        }`}>
                          {component.label}
                        </div>
                        <div className={`text-xs leading-relaxed transition-colors duration-300 ${
                          isDark ? 'text-gray-400 group-hover:text-gray-300' : 'text-gray-500 group-hover:text-gray-600'
                        }`}>
                          {component.description}
                        </div>
                      </div>
                      
                      <div className={`w-6 h-6 rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-300 group-hover:scale-110 ${
                        isDark ? 'bg-gray-700/60 text-gray-300' : 'bg-gray-100/80 text-gray-600'
                      }`}>
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                        </svg>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}

        {/* Extra space to ensure last component is scrollable */}
        <div className="h-16"></div>

        {/* No results */}
        {filteredComponents.length === 0 && (
          <div className="text-center py-12">
            <div className={`w-16 h-16 mx-auto mb-4 rounded-2xl flex items-center justify-center ${
              isDark ? 'bg-gray-700/50' : 'bg-gray-100/80'
            }`}>
              <MagnifyingGlassIcon className={`w-8 h-8 transition-colors duration-300 ${
                isDark ? 'text-gray-500' : 'text-gray-400'
              }`} />
            </div>
            <p className={`text-base font-semibold mb-2 transition-colors duration-300 ${
              isDark ? 'text-gray-300' : 'text-gray-600'
            }`}>
              No components found
            </p>
            <p className={`text-sm transition-colors duration-300 ${
              isDark ? 'text-gray-500' : 'text-gray-500'
            }`}>
              Try adjusting your search or filter
            </p>
          </div>
        )}
        </div>
      </div>

      {/* Help Section - Fixed at bottom */}
      <div className={`p-3 border-t transition-colors duration-300 flex-shrink-0 ${
        isDark ? 'border-gray-700/50' : 'border-gray-200/50'
      }`}>
        <div className={`border rounded-lg p-3 transition-all duration-300 backdrop-blur-sm ${
          isDark 
            ? 'bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-indigo-900/20 border-blue-700/30' 
            : 'bg-gradient-to-br from-blue-50/80 via-indigo-50/80 to-purple-50/80 border-blue-200/60'
        }`}>
          <div className="flex items-start gap-2">
            <div className={`w-6 h-6 rounded-md flex items-center justify-center flex-shrink-0 transition-colors duration-300 ${
              isDark ? 'bg-blue-500/20 text-blue-400' : 'bg-blue-100/80 text-blue-600'
            }`}>
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="flex-1">
              <div className={`text-xs font-bold mb-1 transition-colors duration-300 ${
                isDark ? 'text-blue-300' : 'text-blue-900'
              }`}>
                Quick Guide
              </div>
              <ul className={`text-xs space-y-1 transition-colors duration-300 ${
                isDark ? 'text-blue-400/90' : 'text-blue-700/90'
              }`}>
                <li className="flex items-center gap-2">
                  <div className={`w-1 h-1 rounded-full ${
                    isDark ? 'bg-blue-400' : 'bg-blue-600'
                  }`} />
                  <span>Drag to canvas</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkflowSidebar;
