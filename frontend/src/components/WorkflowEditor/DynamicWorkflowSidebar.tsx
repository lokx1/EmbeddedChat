/**
 * Dynamic Workflow Sidebar - sử dụng components từ backend
 */
import React, { useState } from 'react';
import { useWorkflowComponents } from '../../hooks/useEnhancedWorkflow';
import {
  PlayIcon,
  ClockIcon,
  LinkIcon,
  TableCellsIcon,
  CircleStackIcon,
  GlobeAltIcon,
  CpuChipIcon,
  ArrowsRightLeftIcon,
  MagnifyingGlassIcon,
  EnvelopeIcon,
  CogIcon,
  XMarkIcon,
  ChevronDownIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';

// Icon mapping cho các component types
const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  PlayIcon: PlayIcon,
  ClockIcon: ClockIcon,
  LinkIcon: LinkIcon,
  TableCellsIcon: TableCellsIcon,
  CircleStackIcon: CircleStackIcon,
  GlobeAltIcon: GlobeAltIcon,
  CpuChipIcon: CpuChipIcon,
  ArrowsRightLeftIcon: ArrowsRightLeftIcon,
  MagnifyingGlassIcon: MagnifyingGlassIcon,
  EnvelopeIcon: EnvelopeIcon,
  CogIcon: CogIcon,
};

interface DynamicWorkflowSidebarProps {
  isOpen?: boolean;
  onToggle?: () => void;
}

export default function DynamicWorkflowSidebar({ 
  isOpen = true, 
  onToggle 
}: DynamicWorkflowSidebarProps) {
  const { components, loading, error } = useWorkflowComponents();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategories, setSelectedCategories] = useState<string[]>(['triggers', 'data_sources', 'ai_processing', 'control_flow', 'output_actions']);
  const [expandedCategories, setExpandedCategories] = useState<string[]>(['triggers', 'data_sources', 'ai_processing']);

  // Lọc components theo search và category
  const filteredComponents = components.filter(component => {
    const matchesSearch = component.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         component.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategories.includes(component.category);
    return matchesSearch && matchesCategory;
  });

  // Group components theo category
  const groupedComponents = filteredComponents.reduce((acc, component) => {
    if (!acc[component.category]) {
      acc[component.category] = [];
    }
    acc[component.category].push(component);
    return acc;
  }, {} as Record<string, typeof components>);

  // Category labels mapping
  const categoryLabels: Record<string, string> = {
    triggers: 'Triggers',
    data_sources: 'Data Sources',
    ai_processing: 'AI & Processing',
    control_flow: 'Control Flow',
    output_actions: 'Output & Actions'
  };

  const onDragStart = (event: React.DragEvent, componentType: string) => {
    event.dataTransfer.setData('application/reactflow', componentType);
    event.dataTransfer.effectAllowed = 'move';
  };

  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => 
      prev.includes(category) 
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  const toggleCategoryFilter = (category: string) => {
    setSelectedCategories(prev => 
      prev.includes(category) 
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  if (!isOpen) {
    return (
      <div className="w-16 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col items-center py-4">
        <button
          onClick={onToggle}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          <CogIcon className="w-6 h-6 text-gray-600 dark:text-gray-400" />
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 p-4">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-600 rounded mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} className="h-16 bg-gray-200 dark:bg-gray-600 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 p-4">
        <div className="text-red-600 dark:text-red-400">
          <h3 className="font-medium">Error loading components</h3>
          <p className="text-sm mt-1">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
              <CogIcon className="w-5 h-5 text-white" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Components
            </h2>
          </div>
          {onToggle && (
            <button
              onClick={onToggle}
              className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <XMarkIcon className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            </button>
          )}
        </div>

        <div className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Drag components to build your workflow
        </div>

        {/* Search */}
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search components..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />
        </div>

        {/* Category filters */}
        <div className="mt-3">
          <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">Categories:</div>
          <div className="flex flex-wrap gap-1">
            {Object.entries(categoryLabels).map(([category, label]) => (
              <button
                key={category}
                onClick={() => toggleCategoryFilter(category)}
                className={`px-2 py-1 text-xs rounded transition-colors ${
                  selectedCategories.includes(category)
                    ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                    : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        <div className="text-xs text-gray-500 dark:text-gray-400 mt-2">
          {filteredComponents.length} component{filteredComponents.length !== 1 ? 's' : ''} available
        </div>
      </div>

      {/* Components list */}
      <div className="flex-1 overflow-y-auto">
        {Object.entries(groupedComponents).map(([category, categoryComponents]) => (
          <div key={category} className="border-b border-gray-100 dark:border-gray-700 last:border-b-0">
            <button
              onClick={() => toggleCategory(category)}
              className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors"
            >
              <span className="font-medium text-gray-900 dark:text-white text-sm">
                {categoryLabels[category]} ({categoryComponents.length})
              </span>
              {expandedCategories.includes(category) ? (
                <ChevronDownIcon className="w-4 h-4 text-gray-500" />
              ) : (
                <ChevronRightIcon className="w-4 h-4 text-gray-500" />
              )}
            </button>

            {expandedCategories.includes(category) && (
              <div className="pb-2">
                {categoryComponents.map((component) => {
                  const IconComponent = iconMap[component.icon] || CogIcon;
                  
                  return (
                    <div
                      key={component.type}
                      draggable
                      onDragStart={(event) => onDragStart(event, component.type)}
                      className="mx-2 mb-2 p-3 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg cursor-move hover:shadow-md hover:border-blue-300 dark:hover:border-blue-600 transition-all duration-200 group"
                    >
                      <div className="flex items-start gap-3">
                        <div className={`w-10 h-10 rounded-lg bg-gradient-to-r ${component.color} flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform`}>
                          <IconComponent className="w-5 h-5 text-white" />
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                            {component.name}
                          </h4>
                          <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
                            {component.description}
                          </p>
                          
                          {/* Component info badges */}
                          <div className="flex gap-1 mt-2">
                            {component.is_trigger && (
                              <span className="px-1.5 py-0.5 text-xs bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 rounded">
                                Trigger
                              </span>
                            )}
                            {component.is_async && (
                              <span className="px-1.5 py-0.5 text-xs bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 rounded">
                                Async
                              </span>
                            )}
                            {component.parameters.length > 0 && (
                              <span className="px-1.5 py-0.5 text-xs bg-gray-100 text-gray-700 dark:bg-gray-600 dark:text-gray-300 rounded">
                                {component.parameters.length} param{component.parameters.length !== 1 ? 's' : ''}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
          💡 Tip: Drag components to the canvas to start building your workflow
        </div>
      </div>
    </div>
  );
}
