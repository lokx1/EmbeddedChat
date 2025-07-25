// Enhanced animated card component
import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';

interface AnimatedCardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  onClick?: () => void;
  gradient?: boolean;
}

export const AnimatedCard: React.FC<AnimatedCardProps> = ({
  children,
  className = '',
  hover = true,
  onClick,
  gradient = false
}) => {
  const { isDark } = useTheme();

  const baseClasses = `
    rounded-xl border transition-all duration-300 ease-in-out
    ${isDark 
      ? 'bg-gray-800 border-gray-700' 
      : 'bg-white border-gray-200'
    }
    ${hover ? 'hover:shadow-lg hover:scale-[1.02] hover:-translate-y-1' : ''}
    ${onClick ? 'cursor-pointer' : ''}
    ${gradient ? (isDark 
      ? 'bg-gradient-to-br from-gray-800 to-gray-900' 
      : 'bg-gradient-to-br from-white to-gray-50'
    ) : ''}
  `;

  return (
    <div 
      className={`${baseClasses} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
};
