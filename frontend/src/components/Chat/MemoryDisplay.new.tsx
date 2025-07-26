import React, { useState } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { ClockIcon, ChatBubbleLeftIcon } from '@heroicons/react/24/outline';

interface MemoryItem {
  id: string;
  content: string;
  context: string;
  relevance_score?: number;
  created_at: string;
  conversation_id?: string;
}

interface ConversationSummary {
  id: string;
  summary: string;
  key_points: string[];
  created_at: string;
  conversation_id: string;
}

interface MemoryDisplayProps {
  memories: MemoryItem[];
  summaries: ConversationSummary[];
  onRefresh?: () => void;
}

export const MemoryDisplay: React.FC<MemoryDisplayProps> = ({ 
  memories = [], 
  summaries = [],
  onRefresh
}) => {
  const { isDark } = useTheme();
  const [activeTab, setActiveTab] = useState<'memory' | 'history'>('memory');

  const getTypeIcon = (score?: number) => {
    if (!score) return '🧠';
    if (score > 0.8) return '⭐';
    if (score > 0.6) return '💡';
    return '🔗';
  };

  const getTypeColor = (score?: number, isDark?: boolean) => {
    if (!score) return isDark ? 'text-gray-400' : 'text-gray-600';
    if (score > 0.8) return isDark ? 'text-yellow-400' : 'text-yellow-600';
    if (score > 0.6) return isDark ? 'text-blue-400' : 'text-blue-600';
    return isDark ? 'text-green-400' : 'text-green-600';
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className={`flex items-center justify-between p-4 border-b ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
        <div className="flex items-center gap-2">
          <ClockIcon className="w-5 h-5 text-gray-500" />
          <span className={`text-sm font-medium ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
            Memory & Context
          </span>
          <span className={`text-xs px-2 py-1 rounded-full ${isDark ? 'bg-gray-700 text-gray-400' : 'bg-gray-200 text-gray-600'}`}>
            {memories.length + summaries.length}
          </span>
        </div>
        {onRefresh && (
          <button
            onClick={onRefresh}
            className={`text-xs px-2 py-1 rounded ${isDark ? 'bg-gray-700 hover:bg-gray-600 text-gray-300' : 'bg-gray-200 hover:bg-gray-300 text-gray-600'}`}
          >
            Refresh
          </button>
        )}
      </div>

      {/* Tabs */}
      <div className={`flex border-b ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
        {[
          { key: 'memory', label: 'Memory', count: memories.length },
          { key: 'history', label: 'History', count: summaries.length }
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as 'memory' | 'history')}
            className={`flex-1 px-3 py-2 text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? isDark 
                  ? 'text-blue-400 border-b-2 border-blue-400 bg-gray-750' 
                  : 'text-blue-600 border-b-2 border-blue-600 bg-gray-100'
                : isDark 
                  ? 'text-gray-400 hover:text-gray-300' 
                  : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            {tab.label} ({tab.count})
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'memory' && (
          <div className="p-2">
            {memories.length === 0 ? (
              <div className={`text-center py-8 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                <p className="text-sm mb-2">No memories stored yet</p>
                <p className="text-xs">Start chatting to build context memory</p>
              </div>
            ) : (
              <div className="space-y-2">
                {memories.map((memory) => (
                  <div
                    key={memory.id}
                    className={`p-3 rounded-lg border ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-sm">{getTypeIcon(memory.relevance_score)}</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`text-xs font-medium ${getTypeColor(memory.relevance_score, isDark)}`}>
                            Memory
                          </span>
                          {memory.relevance_score && (
                            <span className={`text-xs px-1 rounded ${
                              memory.relevance_score > 0.7
                                ? 'bg-green-100 text-green-800'
                                : memory.relevance_score > 0.4
                                  ? 'bg-yellow-100 text-yellow-800'
                                  : 'bg-gray-100 text-gray-800'
                            }`}>
                              {Math.round(memory.relevance_score * 100)}% relevant
                            </span>
                          )}
                        </div>
                        <p className={`text-sm mb-2 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                          {memory.content}
                        </p>
                        <div className="flex items-center justify-between">
                          <small className={`${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                            {new Date(memory.created_at).toLocaleDateString()}
                          </small>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'history' && (
          <div className="p-2">
            {summaries.length === 0 ? (
              <div className={`text-center py-8 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                <p className="text-sm mb-2">No conversation history yet</p>
                <p className="text-xs">Chat summaries will appear here</p>
              </div>
            ) : (
              <div className="space-y-2">
                {summaries.map((summary) => (
                  <div
                    key={summary.id}
                    className={`p-3 rounded-lg border ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}
                  >
                    <div className="flex items-start gap-3">
                      <ChatBubbleLeftIcon className="w-4 h-4 text-gray-500 mt-1" />
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm mb-2 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                          {summary.summary}
                        </p>
                        {summary.key_points && summary.key_points.length > 0 && (
                          <div className="mb-2">
                            <div className="flex flex-wrap gap-1">
                              {summary.key_points.map((point, index) => (
                                <span
                                  key={index}
                                  className={`text-xs px-2 py-1 rounded-full ${isDark ? 'bg-gray-700 text-gray-300' : 'bg-gray-200 text-gray-600'}`}
                                >
                                  {point}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        <small className={`${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                          {new Date(summary.created_at).toLocaleDateString()}
                        </small>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
