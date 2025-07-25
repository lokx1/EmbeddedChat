// Interactive toggle switch component
import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';

interface ToggleProps {
  enabled: boolean;
  onChange: (enabled: boolean) => void;
  size?: 'sm' | 'md' | 'lg';
  label?: string;
  description?: string;
}

export const Toggle: React.FC<ToggleProps> = ({
  enabled,
  onChange,
  size = 'md',
  label,
  description
}) => {
  const { isDark } = useTheme();

  const sizes = {
    sm: {
      container: 'w-8 h-4',
      circle: 'w-3 h-3',
      translate: 'translate-x-4'
    },
    md: {
      container: 'w-11 h-6',
      circle: 'w-5 h-5',
      translate: 'translate-x-5'
    },
    lg: {
      container: 'w-14 h-7',
      circle: 'w-6 h-6',
      translate: 'translate-x-7'
    }
  };

  const sizeConfig = sizes[size];

  return (
    <div className="flex items-center justify-between">
      {(label || description) && (
        <div className="flex-1 mr-4">
          {label && (
            <div className={`text-sm font-medium ${
              isDark ? 'text-gray-200' : 'text-gray-900'
            }`}>
              {label}
            </div>
          )}
          {description && (
            <div className={`text-xs ${
              isDark ? 'text-gray-400' : 'text-gray-500'
            }`}>
              {description}
            </div>
          )}
        </div>
      )}
      
      <button
        type="button"
        className={`
          relative inline-flex flex-shrink-0 ${sizeConfig.container} 
          border-2 border-transparent rounded-full cursor-pointer 
          transition-colors ease-in-out duration-200 focus:outline-none 
          focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
          ${enabled 
            ? 'bg-blue-600' 
            : isDark 
              ? 'bg-gray-600' 
              : 'bg-gray-200'
          }
        `}
        onClick={() => onChange(!enabled)}
      >
        <span
          className={`
            ${sizeConfig.circle} pointer-events-none inline-block 
            rounded-full bg-white shadow transform ring-0 
            transition ease-in-out duration-200
            ${enabled ? sizeConfig.translate : 'translate-x-0'}
          `}
        />
      </button>
    </div>
  );
};
