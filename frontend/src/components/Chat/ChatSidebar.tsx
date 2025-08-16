/**
 * Chat Sidebar Component
 * Displays conversation history and navigation
 */
import { useState } from 'react';
import { Conversation } from './types';
import { formatDistanceToNow } from 'date-fns';
import { conversationService } from '../../services/conversationService';

interface ChatSidebarProps {
  isOpen: boolean;
  conversations: Conversation[];
  currentConversationId: string | null;
  onToggle: () => void;
  onNewConversation: () => void;
  onSelectConversation: (id: string) => void;
  onOpenSettings: () => void;
  onDeleteConversation?: (id: string) => void;
  onRenameConversation?: (id: string, newTitle: string) => void;
}

export default function ChatSidebar({
  isOpen,
  conversations,
  currentConversationId,
  onToggle,
  onNewConversation,
  onSelectConversation,
  onOpenSettings,
  onDeleteConversation,
  onRenameConversation
}: ChatSidebarProps) {
  const [searchQuery, setSearchQuery] = useState('');

  // Filter conversations based on search
  const filteredConversations = conversations.filter(conv =>
    conv.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (!isOpen) return null;

  return (
    <div className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col h-full">
      {/* Header */}
      <div className="flex-shrink-0 p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Chats</h2>
          <button
            onClick={onToggle}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* New Chat Button */}
        <button
          onClick={onNewConversation}
          className="w-full flex items-center gap-3 p-3 text-left text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span className="font-medium">New Chat</span>
        </button>

        {/* Search */}
        <div className="mt-4 relative">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search conversations..."
            className="w-full pl-10 pr-3 py-2 text-sm bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-gray-100"
          />
          <svg className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto">
        {filteredConversations.length === 0 ? (
          <div className="p-4 text-center text-gray-500 dark:text-gray-400">
            {searchQuery ? 'No conversations found' : 'No conversations yet'}
          </div>
        ) : (
          <div className="p-2">
            {filteredConversations.map((conversation) => (
              <ConversationItem
                key={conversation.id}
                conversation={conversation}
                isActive={conversation.id === currentConversationId}
                onClick={() => onSelectConversation(conversation.id)}
                onDelete={onDeleteConversation}
                onRename={onRenameConversation}
              />
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="flex-shrink-0 p-4 border-t border-gray-200 dark:border-gray-700">
        <button
          onClick={onOpenSettings}
          className="w-full flex items-center gap-3 p-3 text-left text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <span>Settings</span>
        </button>
      </div>
    </div>
  );
}

// Individual conversation item component
interface ConversationItemProps {
  conversation: Conversation;
  isActive: boolean;
  onClick: () => void;
  onDelete?: (id: string) => void;
  onRename?: (id: string, newTitle: string) => void;
}

function ConversationItem({ conversation, isActive, onClick, onDelete, onRename }: ConversationItemProps) {
  const [showMenu, setShowMenu] = useState(false);
  const [isRenaming, setIsRenaming] = useState(false);
  const [newTitle, setNewTitle] = useState(conversation.title);

  return (
    <div
      className={`group relative mb-1 p-3 rounded-lg cursor-pointer transition-colors ${
        isActive 
          ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800' 
          : 'hover:bg-gray-50 dark:hover:bg-gray-700'
      }`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          {isRenaming ? (
            <input
              type="text"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              onBlur={() => {
                if (onRename && newTitle.trim() !== conversation.title) {
                  onRename(conversation.id, newTitle.trim());
                }
                setIsRenaming(false);
              }}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  if (onRename && newTitle.trim() !== conversation.title) {
                    onRename(conversation.id, newTitle.trim());
                  }
                  setIsRenaming(false);
                }
                if (e.key === 'Escape') {
                  setNewTitle(conversation.title);
                  setIsRenaming(false);
                }
              }}
              className="text-sm font-medium bg-transparent border-none outline-none w-full text-gray-900 dark:text-gray-100"
              autoFocus
            />
          ) : (
            <h3 className={`text-sm font-medium truncate ${
              isActive 
                ? 'text-blue-700 dark:text-blue-300' 
                : 'text-gray-900 dark:text-gray-100'
            }`}>
              {conversation.title}
            </h3>
          )}
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {formatDistanceToNow(new Date(conversation.updatedAt), { addSuffix: true })}
          </p>
          {conversation.preview && (
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1 line-clamp-2">
              {conversation.preview}
            </p>
          )}
        </div>

        {/* Menu Button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            setShowMenu(!showMenu);
          }}
          className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded transition-opacity"
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
          </svg>
        </button>

        {/* Dropdown Menu */}
        {showMenu && (
          <div className="absolute right-0 top-8 w-32 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg z-10">
            <button 
              onClick={(e) => {
                e.stopPropagation();
                setIsRenaming(true);
                setShowMenu(false);
              }}
              className="w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-t-lg"
            >
              Rename
            </button>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                if (onDelete && window.confirm('Are you sure you want to delete this conversation?')) {
                  onDelete(conversation.id);
                }
                setShowMenu(false);
              }}
              className="w-full px-3 py-2 text-left text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-b-lg"
            >
              Delete
            </button>
          </div>
        )}
      </div>

      {/* Message Count Badge */}
      {conversation.messageCount && conversation.messageCount > 0 && (
        <div className="absolute top-2 right-8 w-5 h-5 bg-gray-300 dark:bg-gray-600 text-xs text-gray-700 dark:text-gray-300 rounded-full flex items-center justify-center">
          {conversation.messageCount}
        </div>
      )}
    </div>
  );
}
