// Enhanced sidebar with navigation and feature modules
import React, { useState } from 'react';
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
            group flex items-center px-3 py-2 text-sm font-medium rounded-lg cursor-pointer transition-colors
            ${depth > 0 ? 'ml-6' : ''}
            ${isActive 
              ? 'bg-blue-100 text-blue-700 border-r-2 border-blue-700' 
              : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
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
          <item.icon 
            className={`
              ${collapsed ? 'w-6 h-6' : 'w-5 h-5'} 
              ${isActive ? 'text-blue-700' : 'text-gray-400 group-hover:text-gray-500'}
              transition-colors
            `} 
          />
          
          {!collapsed && (
            <>
              <span className="ml-3 flex-1">{item.label}</span>
              
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
      fixed left-0 top-0 h-full bg-white border-r border-gray-200 shadow-sm transition-all duration-300 z-40
      ${collapsed ? 'w-16' : 'w-64'}
    `}>
      {/* Toggle Button */}
      <button
        onClick={onToggle}
        className="absolute -right-3 top-8 w-6 h-6 bg-white border border-gray-200 rounded-full flex items-center justify-center shadow-md hover:shadow-lg transition-shadow"
      >
        {collapsed ? (
          <ChevronRightIcon className="w-4 h-4 text-gray-600" />
        ) : (
          <ChevronLeftIcon className="w-4 h-4 text-gray-600" />
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
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <div className="text-xs text-gray-500">
            <div>Version 1.0.0</div>
            <div className="mt-1">© 2025 EmbeddedChat</div>
          </div>
        </div>
      )}
    </div>
  );
};
