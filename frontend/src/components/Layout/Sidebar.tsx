// Enhanced sidebar with navigation and feature modules
import React, { useState } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import {
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  Cog6ToothIcon,
  RectangleGroupIcon,
  PlayIcon,
  CloudArrowUpIcon,
  ChartBarIcon,
  UserGroupIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  HomeIcon,
  CommandLineIcon,
  PuzzlePieceIcon
} from '@heroicons/react/24/outline';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  activeModule?: string;
  onModuleChange?: (module: string) => void;
}

interface MenuItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: number;
  submenu?: MenuItem[];
}

const menuItems: MenuItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: HomeIcon,
  },
  {
    id: 'chat',
    label: 'Chat',
    icon: ChatBubbleLeftRightIcon,
    badge: 3,
  },
  {
    id: 'documents',
    label: 'Documents',
    icon: DocumentTextIcon,
    submenu: [
      { id: 'upload', label: 'Upload', icon: CloudArrowUpIcon },
      { id: 'manage', label: 'Manage', icon: RectangleGroupIcon },
    ]
  },
  {
    id: 'workflows',
    label: 'Workflows',
    icon: PlayIcon,
    submenu: [
      { id: 'designer', label: 'Designer', icon: RectangleGroupIcon },
      { id: 'executions', label: 'Executions', icon: ChartBarIcon },
    ]
  },
  {
    id: 'mcp',
    label: 'MCP Plugins',
    icon: PuzzlePieceIcon,
    submenu: [
      { id: 'registry', label: 'Registry', icon: CommandLineIcon },
      { id: 'installed', label: 'Installed', icon: Cog6ToothIcon },
    ]
  },
  {
    id: 'analytics',
    label: 'Analytics',
    icon: ChartBarIcon,
  },
  {
    id: 'team',
    label: 'Team',
    icon: UserGroupIcon,
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: Cog6ToothIcon,
  },
];

export const Sidebar: React.FC<SidebarProps> = ({ 
  collapsed, 
  onToggle, 
  activeModule = 'dashboard',
  onModuleChange = () => {}
}) => {
  const { isDark } = useTheme();
  const [expandedItems, setExpandedItems] = useState<string[]>(['documents']);

  const toggleExpanded = (itemId: string) => {
    setExpandedItems(prev => 
      prev.includes(itemId) 
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  const renderMenuItem = (item: MenuItem, depth = 0) => {
    const isActive = activeModule === item.id;
    const isExpanded = expandedItems.includes(item.id);
    const hasSubmenu = item.submenu && item.submenu.length > 0;

    return (
      <div key={item.id}>
        <div
          className={`
            group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg cursor-pointer transition-all duration-200
            ${depth > 0 ? 'ml-6' : ''}
            ${isActive 
              ? (isDark ? 'bg-blue-900/50 text-blue-300 border-r-2 border-blue-300' : 'bg-blue-100 text-blue-700 border-r-2 border-blue-700')
              : (isDark ? 'text-gray-300 hover:bg-gray-700/50 hover:text-white' : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900')
            }
          `}
          onClick={() => {
            if (hasSubmenu) {
              toggleExpanded(item.id);
            } else {
              onModuleChange(item.id);
            }
          }}
        >
          <div className="flex items-center justify-center w-6 h-6 mr-3 flex-shrink-0">
            <item.icon 
              className={`
                w-5 h-5
                ${isActive ? (isDark ? 'text-blue-300' : 'text-blue-700') : (isDark ? 'text-gray-400' : 'text-gray-500')}
                group-hover:${isDark ? 'text-white' : 'text-gray-900'}
                transition-colors
              `} 
            />
          </div>
          
          {!collapsed && (
            <>
              <span className="flex-1 text-left">{item.label}</span>
              
              {item.badge && (
                <span className="ml-2 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-red-500 rounded-full">
                  {item.badge}
                </span>
              )}
              
              {hasSubmenu && (
                <ChevronRightIcon 
                  className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
                />
              )}
            </>
          )}
        </div>

        {/* Submenu */}
        {hasSubmenu && !collapsed && isExpanded && (
          <div className="mt-1 space-y-1">
            {item.submenu?.map(subItem => renderMenuItem(subItem, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={`
      h-full transition-all duration-300 flex-shrink-0
      ${collapsed ? 'w-16' : 'w-64'}
      ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}
      border-r shadow-sm
    `}>
      {/* Toggle Button */}
      <button
        onClick={onToggle}
        className={`absolute -right-3 top-8 w-6 h-6 ${isDark ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-200'} border rounded-full flex items-center justify-center shadow-md hover:shadow-lg transition-shadow`}
      >
        {collapsed ? (
          <ChevronRightIcon className={`w-4 h-4 ${isDark ? 'text-gray-300' : 'text-gray-600'}`} />
        ) : (
          <ChevronLeftIcon className={`w-4 h-4 ${isDark ? 'text-gray-300' : 'text-gray-600'}`} />
        )}
      </button>

      {/* Navigation */}
      <nav className="mt-20 p-4">
        <div className="space-y-2">
          {menuItems.map(item => renderMenuItem(item))}
        </div>
      </nav>

      {/* Footer */}
      {!collapsed && (
        <div className={`absolute bottom-0 left-0 right-0 p-4 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
          <div className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
            <div>Version 1.0.0</div>
            <div className="mt-1">© 2025 EmbeddedChat</div>
          </div>
        </div>
      )}
    </div>
  );
};
